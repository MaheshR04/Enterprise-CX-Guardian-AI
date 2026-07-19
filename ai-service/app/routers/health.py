"""
Enterprise CX Guardian AI — Health & Monitoring Endpoints.

Endpoints:
  GET /             — Root ping (liveness)
  GET /health       — Full health (DB + system + uptime)
  GET /health/live  — Kubernetes liveness probe (process running?)
  GET /health/ready — Kubernetes readiness probe (DB connected?)
  GET /metrics      — Request counts, latency percentiles, error rates, system info
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings, Settings
from app.core.metrics import metrics, _format_uptime, _uptime_seconds, _BOOT_TIME
from app.core.logger import logger
from app.database.connection import db_connection
from app.schemas.payload import HealthResponse, ErrorResponse

router    = APIRouter()
START_TIME = _BOOT_TIME      # same reference as metrics module


# ══════════════════════════════════════════════════════════════════
# 1. Root ping — liveness shortcut
# ══════════════════════════════════════════════════════════════════
@router.get(
    "/",
    tags=["Health"],
    summary="Root Ping",
    description="Minimal liveness check. Returns 200 if the process is running.",
    response_model=HealthResponse
)
async def root_ping() -> HealthResponse:
    return HealthResponse(
        status   = "ok",
        service  = settings.PROJECT_NAME,
        version  = settings.VERSION,
        uptime   = _format_uptime(_uptime_seconds()),
        timestamp= datetime.now(timezone.utc).isoformat(),
        python   = "running"
    )


# ══════════════════════════════════════════════════════════════════
# 2. Full Health — DB + system + metrics summary
# ══════════════════════════════════════════════════════════════════
@router.get(
    "/health",
    tags=["Health"],
    summary="Full Application Health Check",
    description=(
        "Returns comprehensive health status including:\n\n"
        "- MongoDB connection status and ping latency\n"
        "- Process uptime and environment\n"
        "- Request throughput summary\n"
        "- System memory and CPU snapshot\n\n"
        "Returns **200** if healthy, **503** if MongoDB is unreachable."
    ),
    responses={
        200: {"description": "Service is fully healthy and operational."},
        503: {"description": "Service is degraded — MongoDB unavailable."}
    }
)
async def full_health() -> JSONResponse:
    uptime_s  = _uptime_seconds()
    db_health = await db_connection.check_health()
    sys_info  = await metrics.get_system_info()
    req_info  = await metrics.get_request_metrics()

    is_healthy     = db_health.get("status") == "healthy"
    http_status    = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = {
        "success":     is_healthy,
        "status":      "healthy" if is_healthy else "degraded",
        "service":     settings.PROJECT_NAME,
        "version":     settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "uptime":      {
            "seconds": round(uptime_s, 1),
            "human":   _format_uptime(uptime_s)
        },
        "database": {
            "status":       db_health.get("status"),
            "database":     db_health.get("database"),
            "ping_latency": db_health.get("ping_latency"),
            "error":        db_health.get("error")
        },
        "requests": {
            "total":      req_info["total_requests"],
            "active":     req_info["active_requests"],
            "errors":     req_info["total_errors"],
            "error_rate": f"{req_info['error_rate_pct']}%"
        },
        "system": {
            "platform":       sys_info.get("platform"),
            "python_version": sys_info.get("python_version"),
            "memory_used_mb": sys_info.get("memory_used_mb"),
            "memory_pct":     sys_info.get("memory_percent"),
            "cpu_percent":    sys_info.get("cpu_percent"),
            "process_rss_mb": sys_info.get("process_rss_mb")
        }
    }

    if not is_healthy:
        logger.warning(
            f"[Health] Service DEGRADED — MongoDB unavailable: "
            f"{db_health.get('error')}"
        )

    return JSONResponse(content=payload, status_code=http_status)


# ══════════════════════════════════════════════════════════════════
# 3. Liveness Probe — is the process alive?
# ══════════════════════════════════════════════════════════════════
@router.get(
    "/health/live",
    tags=["Health"],
    summary="Liveness Probe",
    description=(
        "Kubernetes / Docker liveness probe.\n\n"
        "Returns **200** as long as the Python process is running. "
        "Does NOT check database connectivity. "
        "If this returns non-200, the container should be restarted."
    ),
    responses={
        200: {"description": "Process is alive."}
    }
)
async def liveness_probe() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":    "alive",
            "uptime":    _format_uptime(_uptime_seconds()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ══════════════════════════════════════════════════════════════════
# 4. Readiness Probe — is the service ready to serve traffic?
# ══════════════════════════════════════════════════════════════════
@router.get(
    "/health/ready",
    tags=["Health"],
    summary="Readiness Probe",
    description=(
        "Kubernetes / Docker readiness probe.\n\n"
        "Returns **200** only when the service is fully initialised and "
        "MongoDB is reachable. "
        "Returns **503** during startup or when MongoDB is unavailable. "
        "Load balancers should only route traffic to ready instances."
    ),
    responses={
        200: {"description": "Service is ready to accept traffic."},
        503: {"description": "Service is not ready — database unavailable."}
    }
)
async def readiness_probe() -> JSONResponse:
    db_health  = await db_connection.check_health()
    is_ready   = db_health.get("status") == "healthy"
    http_code  = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_code,
        content={
            "status":       "ready" if is_ready else "not_ready",
            "database":     db_health.get("status"),
            "ping_latency": db_health.get("ping_latency"),
            "error":        db_health.get("error"),
            "timestamp":    datetime.now(timezone.utc).isoformat()
        }
    )


# ══════════════════════════════════════════════════════════════════
# 5. Metrics — full telemetry snapshot
# ══════════════════════════════════════════════════════════════════
@router.get(
    "/metrics",
    tags=["Health"],
    summary="Application Metrics",
    description=(
        "Returns a full telemetry snapshot including:\n\n"
        "- **Request metrics**: total, active, error rate, by method/status/route\n"
        "- **Latency metrics**: p50 / p90 / p99 / avg / max per route\n"
        "- **Error tracking**: counts by error_code, 4xx vs 5xx breakdown\n"
        "- **System info**: CPU %, memory MB, process RSS, threads, uptime\n\n"
        "Powered by an in-process ring-buffer (last 1000 requests). "
        "For persistent metrics, wire into Prometheus / Grafana."
    ),
    responses={
        200: {"description": "Metrics snapshot returned successfully."}
    }
)
async def application_metrics() -> JSONResponse:
    req_metrics     = await metrics.get_request_metrics()
    latency_metrics = await metrics.get_latency_metrics()
    sys_info        = await metrics.get_system_info()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success":   True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service":   settings.PROJECT_NAME,
            "version":   settings.VERSION,
            "uptime": {
                "seconds": round(_uptime_seconds(), 1),
                "human":   _format_uptime(_uptime_seconds())
            },
            "requests":  req_metrics,
            "latency":   latency_metrics,
            "system":    sys_info
        }
    )
