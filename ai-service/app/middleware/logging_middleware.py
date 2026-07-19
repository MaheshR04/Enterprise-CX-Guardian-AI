"""
Request Logging & Metrics Middleware.

Instruments every HTTP request with:
  - Structured request/response logs (method, path, status, latency)
  - MetricsCollector updates (request counts, latency, error tracking)
  - Active request gauge (in-flight counter)
"""

import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import log_request_latency, logger
from app.core.metrics import metrics


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that runs on every request/response cycle.
    Feeds both the structured logger and the in-memory MetricsCollector.
    """

    # Paths excluded from metrics tracking (healthcheck noise reduction)
    _SKIP_METRICS_PATHS = {"/", "/health", "/health/live", "/health/ready", "/metrics"}

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        method     = request.method
        path       = request.url.path
        client_ip  = request.client.host if request.client else "unknown"

        track = path not in self._SKIP_METRICS_PATHS

        # ── Start ──────────────────────────────────────────────────
        if track:
            await metrics.record_request_start()

        logger.debug(
            f"[Request ] {method} {path} — client: {client_ip}"
        )

        # ── Dispatch ───────────────────────────────────────────────
        try:
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Normalise route path (strip query string)
            route = path.split("?")[0]

            # Structured log
            log_request_latency(
                method=method,
                path=route,
                status_code=response.status_code,
                latency_ms=latency_ms
            )

            # Metrics
            if track:
                await metrics.record_request_end(
                    method=method,
                    route=route,
                    status_code=response.status_code,
                    latency_ms=latency_ms
                )

            return response

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"[Middleware Error] {method} {path} "
                f"| {latency_ms:.2f}ms "
                f"| {type(exc).__name__}: {exc}"
            )
            if track:
                await metrics.record_request_end(
                    method=method,
                    route=path,
                    status_code=500,
                    latency_ms=latency_ms
                )
                await metrics.record_error("UNHANDLED_EXCEPTION")
            raise
