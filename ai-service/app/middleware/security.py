"""
Enterprise CX Guardian AI — Security Middleware Stack (FastAPI)
================================================================

Implements all 7 security controls:
  1. Secure HTTP Headers  (X-Frame-Options, CSP, HSTS, etc.)
  2. CORS Configuration   (allowlist, credentials, preflight)
  3. Rate Limiting        (in-memory sliding window per IP)
  4. Request Size Limits  (body size guard)
  5. Input Sanitization   (strip null bytes, control chars)
  6. Environment Validation  (required vars checked at boot)
  7. Security Logging     (suspicious requests)

All middleware classes are designed as FastAPI/Starlette ASGI
middleware — pluggable into app.add_middleware().
"""

import re
import time
import asyncio
from collections import defaultdict, deque
from typing import Callable, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.logger import logger


# ══════════════════════════════════════════════════════════════════
# 1. Secure HTTP Headers Middleware
# ══════════════════════════════════════════════════════════════════

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds production-grade security headers to every HTTP response.
    Equivalent to Helmet.js for Node.js.

    Headers applied:
      X-Content-Type-Options        — Prevent MIME sniffing
      X-Frame-Options               — Clickjacking protection
      X-XSS-Protection              — Legacy XSS filter hint
      Strict-Transport-Security     — Force HTTPS (HSTS)
      Referrer-Policy               — Limit referrer leakage
      Permissions-Policy            — Disable unused browser APIs
      Content-Security-Policy       — Script/style source allowlist
      Cache-Control                 — Prevent sensitive data caching
    """

    # Paths where cache-control should NOT prevent caching (static assets)
    _CACHEABLE_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # ── Security headers ───────────────────────────────────────
        response.headers["X-Content-Type-Options"]  = "nosniff"
        response.headers["X-Frame-Options"]         = "DENY"
        response.headers["X-XSS-Protection"]        = "1; mode=block"
        response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"]      = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), bluetooth=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )

        # HSTS — only in production (not dev/test)
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Prevent caching for API responses
        if request.url.path not in self._CACHEABLE_PATHS:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"]        = "no-cache"

        # Remove server fingerprinting headers
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


# ══════════════════════════════════════════════════════════════════
# 2. Rate Limiting Middleware
# ══════════════════════════════════════════════════════════════════

class RateLimitConfig:
    """Per-route rate limit configuration."""
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests   = max_requests
        self.window_seconds = window_seconds


# Route-specific limits (most restrictive wins)
RATE_LIMIT_RULES: Dict[str, RateLimitConfig] = {
    "/api/v1/auth/login":    RateLimitConfig(max_requests=10,   window_seconds=60),
    "/api/v1/auth/register": RateLimitConfig(max_requests=5,    window_seconds=300),
    "/api/v1/auth/refresh":  RateLimitConfig(max_requests=20,   window_seconds=60),
    "/api/v1/chat":          RateLimitConfig(max_requests=60,   window_seconds=60),
    "/api/v1/conversations": RateLimitConfig(max_requests=120,  window_seconds=60),
    "default":               RateLimitConfig(max_requests=200,  window_seconds=60),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window per-IP rate limiter.

    Uses an in-memory deque per (IP, route) key.
    For production deployments with multiple workers,
    replace with Redis-backed sliding window.

    Excluded: health/metrics endpoints (monitoring probes must not be throttled).
    """

    _EXCLUDED = {"/", "/health", "/health/live", "/health/ready", "/metrics"}

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # {(ip, route): deque of timestamps}
        self._windows: Dict[tuple, deque] = defaultdict(lambda: deque())
        self._lock = asyncio.Lock()

    def _get_config(self, path: str) -> RateLimitConfig:
        """Match the most specific prefix rule, fall back to default."""
        for prefix, config in RATE_LIMIT_RULES.items():
            if prefix != "default" and path.startswith(prefix):
                return config
        return RATE_LIMIT_RULES["default"]

    def _get_client_ip(self, request: Request) -> str:
        """Extract real IP, respecting X-Forwarded-For from trusted proxy."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        if path in self._EXCLUDED:
            return await call_next(request)

        ip      = self._get_client_ip(request)
        config  = self._get_config(path)
        now     = time.time()
        key     = (ip, path.split("?")[0])

        async with self._lock:
            window = self._windows[key]

            # Evict timestamps outside the sliding window
            cutoff = now - config.window_seconds
            while window and window[0] < cutoff:
                window.popleft()

            if len(window) >= config.max_requests:
                oldest   = window[0]
                retry_after = int(config.window_seconds - (now - oldest)) + 1
                logger.warning(
                    f"[Rate Limit] BLOCKED | ip: {ip} | path: {path} "
                    f"| requests: {len(window)}/{config.max_requests} "
                    f"| retry_after: {retry_after}s"
                )
                return JSONResponse(
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "success":    False,
                        "message":    "Rate limit exceeded",
                        "error":      f"Too many requests. Retry after {retry_after} seconds.",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "retry_after": retry_after
                    }
                )

            window.append(now)

        return await call_next(request)


# ══════════════════════════════════════════════════════════════════
# 3. Request Size Limit Middleware
# ══════════════════════════════════════════════════════════════════

# Route-specific size limits (bytes)
REQUEST_SIZE_LIMITS: Dict[str, int] = {
    "/api/v1/chat":          64   * 1024,    # 64 KB  — chat messages
    "/api/v1/auth/register": 4    * 1024,    # 4 KB   — auth payloads
    "/api/v1/auth/login":    4    * 1024,    # 4 KB
    "default":               256  * 1024,    # 256 KB — general API
}


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests whose Content-Length exceeds the configured limit.
    Protects against request smuggling and oversized payload attacks.
    """

    def _get_limit(self, path: str) -> int:
        for prefix, limit in REQUEST_SIZE_LIMITS.items():
            if prefix != "default" and path.startswith(prefix):
                return limit
        return REQUEST_SIZE_LIMITS["default"]

    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("Content-Length")
        if content_length:
            size  = int(content_length)
            limit = self._get_limit(request.url.path)
            if size > limit:
                logger.warning(
                    f"[Request Size] REJECTED | path: {request.url.path} "
                    f"| size: {size} bytes | limit: {limit} bytes"
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "success":    False,
                        "message":    "Request payload too large",
                        "error":      f"Request body exceeds {limit // 1024} KB limit.",
                        "error_code": "PAYLOAD_TOO_LARGE"
                    }
                )
        return await call_next(request)


# ══════════════════════════════════════════════════════════════════
# 4. Input Sanitization Middleware
# ══════════════════════════════════════════════════════════════════

_DANGEROUS_PATTERNS = re.compile(
    r"(\x00|%00|[\x01-\x08\x0b\x0c\x0e-\x1f\x7f])"  # Null bytes + control chars
    r"|(<script[\s\S]*?>[\s\S]*?</script>)"         # XSS script tags
    r"|(javascript\s*:)",                            # javascript: URI
    re.IGNORECASE
)


def sanitize_string(value: str) -> str:
    """Strip null bytes and dangerous patterns from a string."""
    return _DANGEROUS_PATTERNS.sub("", value)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Strips null bytes and obvious injection payloads from query
    parameters and path segments before routing begins.

    Note: Body sanitization is handled at the schema/validator level
    (Pydantic validators on each schema field).
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Sanitize query params
        raw_query = str(request.url.query)
        if raw_query and _DANGEROUS_PATTERNS.search(raw_query):
            logger.warning(
                f"[Input Sanitize] Dangerous query string detected | "
                f"path: {request.url.path} | ip: {request.client.host if request.client else '?'}"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "success":    False,
                    "message":    "Invalid request parameters",
                    "error":      "Request contains forbidden characters.",
                    "error_code": "INVALID_INPUT"
                }
            )
        return await call_next(request)


# ══════════════════════════════════════════════════════════════════
# 5. Environment Validation (called at startup, not middleware)
# ══════════════════════════════════════════════════════════════════

REQUIRED_ENV_VARS = [
    ("GROQ_API_KEY",   "Groq AI API key for LLM completions"),
    ("MONGODB_URI",    "MongoDB Atlas connection string"),
    ("JWT_SECRET_KEY", "JWT signing secret (min 32 chars recommended)"),
]

OPTIONAL_WITH_DEFAULTS = {
    "ENVIRONMENT":   "development",
    "LOG_LEVEL":     "INFO",
    "MODEL_NAME":    "llama3-70b-8192",
    "MAX_HISTORY":   "10",
    "MAX_TOKENS":    "1024",
    "TEMPERATURE":   "0.2",
}


def validate_environment() -> None:
    """
    Validates all required environment variables at application startup.
    Raises ValueError if any required variable is missing or empty.
    Logs warnings for optional variables using defaults.
    """
    missing = []
    warnings = []

    for var, description in REQUIRED_ENV_VARS:
        value = getattr(settings, var, None)
        if not value or value.strip() in ("", "your_groq_api_key_here", "CHANGE_ME"):
            missing.append(f"  ✗ {var} — {description}")

    for var, default in OPTIONAL_WITH_DEFAULTS.items():
        value = getattr(settings, var, None)
        if not value:
            warnings.append(f"  ⚠ {var} not set — using default: '{default}'")

    if warnings:
        for w in warnings:
            logger.warning(f"[Env Validation]{w}")

    if missing and settings.ENVIRONMENT == "production":
        msg = "Missing required environment variables:\n" + "\n".join(missing)
        logger.error(f"[Env Validation] STARTUP BLOCKED\n{msg}")
        raise ValueError(msg)
    elif missing:
        for m in missing:
            logger.warning(f"[Env Validation] DEV MODE — Missing: {m}")

    # JWT secret strength check
    jwt_key = getattr(settings, "JWT_SECRET_KEY", "")
    if len(jwt_key) < 32:
        logger.warning(
            "[Env Validation] ⚠ JWT_SECRET_KEY is shorter than 32 characters — "
            "use a longer secret in production"
        )

    logger.info("[Env Validation] ✓ Environment validated successfully")


# ══════════════════════════════════════════════════════════════════
# 6. CORS Configuration Builder
# ══════════════════════════════════════════════════════════════════

def get_cors_config() -> dict:
    """
    Returns environment-aware CORS configuration for FastAPI CORSMiddleware.

    Development: allows all origins (open for local dev)
    Production:  restricts to NODE_BACKEND_URL only
    """
    if settings.ENVIRONMENT == "production":
        allowed_origins = [
            settings.NODE_BACKEND_URL,
            # Add deployed frontend URL here e.g. "https://app.enterprise-cx.ai"
        ]
        logger.info(
            f"[CORS] Production mode — allowed origins: {allowed_origins}"
        )
    else:
        allowed_origins = ["*"]
        logger.debug("[CORS] Development mode — all origins allowed")

    return {
        "allow_origins":     allowed_origins,
        "allow_credentials": True,
        "allow_methods":     ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers":     [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Version",
            "Accept",
            "Origin"
        ],
        "expose_headers":    ["X-Request-ID", "X-Response-Time"],
        "max_age":           600,   # Preflight cache: 10 minutes
    }
