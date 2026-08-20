import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware de ejemplo para medir y registrar el tiempo de cada petición.
    Se mantiene en la capa 'api' como fue requerido.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Opcionalmente se puede inyectar un header con el tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)
        
        # logger.info(f"{request.method} {request.url.path} completed in {process_time:.4f}s")
        
        return response
