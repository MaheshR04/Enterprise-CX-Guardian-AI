import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import log_request, log_response, log_error

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Log incoming request
        log_request(request.method, request.url.path, client_ip)

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log outgoing response
            log_response(request.method, request.url.path, response.status_code, duration_ms)
            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            log_error(f"Uncaught Exception during {request.method} {request.url.path}", exc)
            raise exc
