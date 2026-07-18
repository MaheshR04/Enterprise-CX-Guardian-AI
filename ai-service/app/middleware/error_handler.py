from fastapi import Request, status
from fastapi.responses import JSONResponse
import groq
import httpx
from app.utils.logger import logger

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handling middleware for FastAPI.
    Maps Groq SDK exceptions to standardized JSON error responses.
    """
    logger.error(f"[FastAPI Exception] {request.method} {request.url.path} -> {type(exc).__name__}: {str(exc)}")

    if isinstance(exc, groq.AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Invalid API Key",
                "error": "The Groq API key provided is invalid or unauthorized."
            }
        )

    if isinstance(exc, groq.RateLimitError):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "message": "Rate Limit Exceeded",
                "error": "Groq AI service request limit exceeded. Please retry after a brief pause."
            }
        )

    if isinstance(exc, (groq.APITimeoutError, httpx.TimeoutException)):
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "success": False,
                "message": "Timeout Error",
                "error": "The request to Groq AI service timed out."
            }
        )

    if isinstance(exc, groq.NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Model Not Found",
                "error": "The specified Groq LLM model was not found."
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Unexpected Server Error",
            "error": str(exc) or "An internal error occurred."
        }
    )
