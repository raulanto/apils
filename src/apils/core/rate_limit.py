from fastapi import Request, HTTPException, status
from typing import Dict, List
from datetime import datetime, timezone, timedelta
import asyncio

# In-memory store for rate limiting
# Key: client IP, Value: list of attempt timestamps
_login_attempts: Dict[str, List[datetime]] = {}
_lock = asyncio.Lock()

# Separate in-memory store for per-account lockout (keyed by email, not IP).
# Catches credential-stuffing/brute-force against a single account from many IPs,
# which the per-IP limiter above can't see.
_account_attempts: Dict[str, List[datetime]] = {}
_account_lock = asyncio.Lock()
ACCOUNT_LOCKOUT_WINDOW_MINUTES = 15
ACCOUNT_LOCKOUT_MAX_ATTEMPTS = 5

async def rate_limit_login(request: Request):
    """
    In-memory rate limiting dependency for login endpoint.
    Limits to 5 attempts per minute per IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)
    
    async with _lock:
        # Get attempts for this IP
        attempts = _login_attempts.get(client_ip, [])
        
        # Filter out attempts older than 1 minute
        attempts = [timestamp for timestamp in attempts if timestamp > window_start]
        
        if len(attempts) >= 5:
            # Update the list to save memory
            _login_attempts[client_ip] = attempts
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )
        
        # Add current attempt
        attempts.append(now)
        _login_attempts[client_ip] = attempts

async def check_account_lockout(email: str):
    """
    In-memory per-account lockout. Call before verifying the password so repeated
    attempts against one account are throttled regardless of which IP they come from.
    """
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=ACCOUNT_LOCKOUT_WINDOW_MINUTES)

    async with _account_lock:
        attempts = _account_attempts.get(email, [])
        attempts = [timestamp for timestamp in attempts if timestamp > window_start]

        if len(attempts) >= ACCOUNT_LOCKOUT_MAX_ATTEMPTS:
            _account_attempts[email] = attempts
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos para esta cuenta. Intenta más tarde."
            )

        attempts.append(now)
        _account_attempts[email] = attempts

async def reset_account_lockout(email: str):
    """Clear the attempt counter for an account after a successful login."""
    async with _account_lock:
        _account_attempts.pop(email, None)
