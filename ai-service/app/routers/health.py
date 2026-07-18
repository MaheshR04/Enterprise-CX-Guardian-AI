from fastapi import APIRouter, Depends, status
import time
from datetime import datetime
from app.core.config import settings, Settings
from app.schemas.payload import HealthResponse, ErrorResponse

router = APIRouter()
START_TIME = time.time()

def get_settings() -> Settings:
    """Dependency injection provider for application settings."""
    return settings

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Explicit Service Health Check",
    description="Returns live system health status, python runtime state, ISO timestamp, and server uptime duration.",
    responses={
        200: {
            "model": HealthResponse,
            "description": "System is healthy and operational."
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal error occurred while compiling system health."
        }
    }
)
@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Root Health Check",
    description="Returns live system health status.",
    responses={
        200: {"model": HealthResponse}
    }
)
async def get_health(cfg: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Asynchronously compiles live process telemetry and health status metrics.
    """
    uptime_seconds = int(time.time() - START_TIME)
    return HealthResponse(
        status="healthy",
        service="Enterprise CX Guardian AI",
        version=cfg.VERSION,
        uptime=f"{uptime_seconds}s",
        timestamp=datetime.utcnow().isoformat(),
        python="running"
    )
