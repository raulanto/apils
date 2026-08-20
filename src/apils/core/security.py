import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from apils.core.config import settings
import secrets
import hashlib

ph = PasswordHasher()

def get_password_hash(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def create_access_token(data: dict, permissions: list[str] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Asegurar el formato requerido
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(secrets.token_hex(16)),
        "type": "access",
        "permissions": permissions or []
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token_payload() -> tuple[str, str]:
    """Generates a plain refresh token and its hash."""
    plain_token = secrets.token_hex(32)
    # The hash will be stored in DB
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    return plain_token, token_hash

def hash_refresh_token(plain_token: str) -> str:
    return hashlib.sha256(plain_token.encode()).hexdigest()
