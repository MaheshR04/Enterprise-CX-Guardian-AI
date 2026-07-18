from fastapi.responses import JSONResponse
from typing import Any, Optional
from app.schemas.payload import StandardResponse, ErrorResponse

def success_response(
    data: Optional[Any] = None,
    message: str = "",
    status_code: int = 200
) -> JSONResponse:
    """
    Builds a standard JSON success response matching:
    { "success": true, "message": "...", "data": {} }
    """
    payload = StandardResponse(
        success=True,
        message=message,
        data=data if data is not None else {}
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())

def error_response(
    message: str = "",
    error: str = "",
    status_code: int = 500
) -> JSONResponse:
    """
    Builds a standard JSON error response matching:
    { "success": false, "message": "...", "error": "..." }
    """
    payload = ErrorResponse(
        success=False,
        message=message,
        error=error
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())
