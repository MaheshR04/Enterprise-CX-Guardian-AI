"""
Enterprise CX Guardian AI — Python AI Microservice
FastAPI Application Entry Point

Registers:
  - MongoDB connection lifecycle (startup / shutdown)
  - All domain exception handlers (DB, validation, not found, LLM)
  - Swagger / OpenAPI documentation with examples
  - CORS and request logging middleware
  - API v1 router and health router
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import logger, log_unexpected_error, log_error, log_validation_error
from app.core.metrics import metrics
from app.database.connection import db_connection
from app.repositories.factory import RepositoryFactory
from app.utils.response import error_response
from app.utils.exceptions import (
    BaseAppException,
    MongoUnavailableException,
    MongoConnectionTimeoutException,
    MongoOperationException,
    DuplicateConversationIdException,
    ConversationNotFoundException,
    CustomValidationException,
    LLMServiceException,
    LLMTimeoutException,
)
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.security import (
    SecureHeadersMiddleware,
    RateLimitMiddleware,
    RequestSizeLimitMiddleware,
    InputSanitizationMiddleware,
    validate_environment,
    get_cors_config
)
from app.middleware.performance import (
    CacheMiddleware,
    GZipMiddleware,
    task_queue
)
from app.routers import health_router
from app.routers.version_router import api_router, register_all_versions

# Validate environment variables at import/boot
validate_environment()


# ══════════════════════════════════════════════════════════════════
# Application Lifecycle
# ══════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"  {settings.PROJECT_NAME}  v{settings.VERSION}")
    logger.info(f"  {settings.TAGLINE}")
    logger.info(f"  Environment : {settings.ENVIRONMENT}")
    logger.info(f"  Docs        : /docs  |  ReDoc: /redoc")
    logger.info("=" * 60)
    # 1. Connect to MongoDB
    await db_connection.connect_to_mongo()
    # 2. Initialize Repository Factory (resolves storage backend)
    RepositoryFactory.initialize()
    logger.info(
        f"[Startup] Storage backend: '{RepositoryFactory.get_active_backend()}' — "
        f"Clean Architecture layer active"
    )
    # 3. Register all API versions
    register_all_versions()
    # 4. Start background task queue
    await task_queue.start()
    yield
    # ── Shutdown ──────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"  Shutting down {settings.PROJECT_NAME}")
    logger.info("=" * 60)
    await task_queue.stop()
    await db_connection.close_connection()


# ══════════════════════════════════════════════════════════════════
# FastAPI Application + Swagger / OpenAPI Config
# ══════════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## Enterprise CX Guardian AI — Python AI Microservice

A production-ready, MongoDB-backed conversational AI platform built with:
- **FastAPI** for async REST API
- **Motor** (Async MongoDB Driver) for persistent storage
- **Groq** (llama3-70b-8192) for LLM completions
- **Pydantic v2** for schema validation

---

### Key Features
- ✅ Full conversation memory with MongoDB persistence
- ✅ Sliding context window (MAX_HISTORY configurable)
- ✅ Prompt logging for debugging and analytics
- ✅ Token usage telemetry on every AI call
- ✅ Soft delete with ACTIVE / ARCHIVED / DELETED lifecycle
- ✅ Pagination and search on conversations
- ✅ Structured logging with latency tracking
- ✅ Resilient fallback mode if MongoDB is unreachable

---

### Collections
| Collection | Purpose |
|---|---|
| `conversations` | Conversation session headers |
| `messages` | Individual user/assistant messages |
| `prompt_logs` | Full LLM prompt payloads (audit trail) |
| `ai_usage` | Token consumption and latency telemetry |
    """,
    version=settings.VERSION,
    contact={
        "name":  "Enterprise CX Guardian AI",
        "email": "support@enterprise-cx.ai"
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name":        "Health",
            "description": "Service health checks and readiness probes."
        },
        {
            "name":        "Chat",
            "description": (
                "Core AI chat endpoint. Runs the full 10-step Chat Flow: "
                "receive → persist → build prompt → Groq → persist → return."
            )
        },
        {
            "name":        "Conversations",
            "description": (
                "Conversation lifecycle management. "
                "List, search, get, soft-delete, archive, and restore conversations. "
                "All operations are MongoDB-backed."
            )
        }
    ],
    lifespan=lifespan
)


# ══════════════════════════════════════════════════════════════════
# Middleware
# ══════════════════════════════════════════════════════════════════

# ── 1. Secure HTTP Headers (Helmet equivalent) ───────────────────
app.add_middleware(SecureHeadersMiddleware)

# ── 2. Response Compression (GZip > 512 bytes) ─────────────────────
app.add_middleware(GZipMiddleware, minimum_size=512)

# ── 3. HTTP Response Caching (ETag + 304 support) ──────────────────
app.add_middleware(CacheMiddleware)

# ── 4. Request Size Limit (Payload size guard) ────────────────────
app.add_middleware(RequestSizeLimitMiddleware)

# ── 5. Input Sanitization (Null-byte & XSS strip) ────────────────
app.add_middleware(InputSanitizationMiddleware)

# ── 6. Per-IP Sliding Window Rate Limiting ────────────────────────
app.add_middleware(RateLimitMiddleware)

# ── 7. Request & Response Latency Logging ─────────────────────────
app.add_middleware(RequestLoggingMiddleware)

# ── 8. Environment-aware CORS ──────────────────────────────────────
cors_cfg = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_cfg["allow_origins"],
    allow_credentials=cors_cfg["allow_credentials"],
    allow_methods=cors_cfg["allow_methods"],
    allow_headers=cors_cfg["allow_headers"],
    expose_headers=cors_cfg["expose_headers"],
    max_age=cors_cfg["max_age"],
)


# ══════════════════════════════════════════════════════════════════
# Exception Handlers
# ══════════════════════════════════════════════════════════════════

# ── 1. All domain BaseAppException subclasses ────────────────────
@app.exception_handler(BaseAppException)
async def base_app_exception_handler(request: Request, exc: BaseAppException):
    log_error(
        context=f"{request.method} {request.url.path}",
        error=exc
    )
    import asyncio
    asyncio.ensure_future(metrics.record_error(exc.error_code))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success":    False,
            "message":    exc.message,
            "error":      exc.detail or exc.message,
            "error_code": exc.error_code
        }
    )


# ── 2. MongoDB Unavailable ───────────────────────────────────────
@app.exception_handler(MongoUnavailableException)
async def mongo_unavailable_handler(request: Request, exc: MongoUnavailableException):
    logger.error(
        f"[DB Unavailable] {request.method} {request.url.path} — "
        f"MongoDB unreachable: {exc.detail}"
    )
    return JSONResponse(
        status_code=503,
        content={
            "success":    False,
            "message":    "Database Unavailable",
            "error":      exc.detail,
            "error_code": "DB_UNAVAILABLE"
        }
    )


# ── 3. MongoDB Connection Timeout ────────────────────────────────
@app.exception_handler(MongoConnectionTimeoutException)
async def mongo_timeout_handler(request: Request, exc: MongoConnectionTimeoutException):
    logger.error(
        f"[DB Timeout] {request.method} {request.url.path} — {exc.detail}"
    )
    return JSONResponse(
        status_code=504,
        content={
            "success":    False,
            "message":    "Database Connection Timeout",
            "error":      exc.detail,
            "error_code": "DB_TIMEOUT"
        }
    )


# ── 4. MongoDB Operation Error ───────────────────────────────────
@app.exception_handler(MongoOperationException)
async def mongo_operation_handler(request: Request, exc: MongoOperationException):
    logger.error(
        f"[DB Operation Error] {request.method} {request.url.path} — {exc.detail}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "success":    False,
            "message":    "Database Operation Failed",
            "error":      exc.detail,
            "error_code": "DB_OPERATION_FAILED"
        }
    )


# ── 5. Duplicate ID Conflict ─────────────────────────────────────
@app.exception_handler(DuplicateConversationIdException)
async def duplicate_id_handler(request: Request, exc: DuplicateConversationIdException):
    logger.warning(
        f"[Duplicate ID] {request.method} {request.url.path} — {exc.detail}"
    )
    return JSONResponse(
        status_code=409,
        content={
            "success":    False,
            "message":    "Duplicate Conversation ID",
            "error":      exc.detail,
            "error_code": "DUPLICATE_CONVERSATION_ID"
        }
    )


# ── 6. Not Found ─────────────────────────────────────────────────
@app.exception_handler(ConversationNotFoundException)
async def conversation_not_found_handler(request: Request, exc: ConversationNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "success":    False,
            "message":    "Conversation Not Found",
            "error":      exc.detail,
            "error_code": "CONVERSATION_NOT_FOUND"
        }
    )


# ── 7. LLM Service Error ─────────────────────────────────────────
@app.exception_handler(LLMServiceException)
async def llm_service_error_handler(request: Request, exc: LLMServiceException):
    logger.error(
        f"[LLM Error] {request.method} {request.url.path} — {exc.detail}"
    )
    return JSONResponse(
        status_code=502,
        content={
            "success":    False,
            "message":    "LLM Service Error",
            "error":      exc.detail,
            "error_code": "LLM_SERVICE_ERROR"
        }
    )


# ── 8. LLM Timeout ───────────────────────────────────────────────
@app.exception_handler(LLMTimeoutException)
async def llm_timeout_handler(request: Request, exc: LLMTimeoutException):
    logger.error(
        f"[LLM Timeout] {request.method} {request.url.path} — {exc.detail}"
    )
    return JSONResponse(
        status_code=504,
        content={
            "success":    False,
            "message":    "LLM Request Timeout",
            "error":      exc.detail,
            "error_code": "LLM_TIMEOUT"
        }
    )


# ── 9. Pydantic RequestValidationError ───────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_detail = "; ".join(
        f"{' → '.join(str(l) for l in err['loc'])}: {err['msg']}"
        for err in errors
    )
    log_validation_error(
        field=str(errors[0]["loc"][-1]) if errors else "unknown",
        value="(request body)",
        reason=error_detail
    )
    import asyncio
    asyncio.ensure_future(metrics.record_error("VALIDATION_ERROR"))
    return JSONResponse(
        status_code=422,
        content={
            "success":    False,
            "message":    "Request Validation Failed",
            "error":      error_detail,
            "error_code": "VALIDATION_ERROR"
        }
    )


# ── 10. Generic HTTP Exception ────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log_error(
        context=f"{request.method} {request.url.path}",
        error=exc
    )
    import asyncio
    asyncio.ensure_future(metrics.record_error(f"HTTP_{exc.status_code}"))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success":    False,
            "message":    str(exc.detail),
            "error":      "HTTP Exception",
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


# ── 11. Global Catch-All ─────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_unexpected_error(
        context=f"{request.method} {request.url.path}",
        error=exc
    )
    import asyncio
    asyncio.ensure_future(metrics.record_error("INTERNAL_SERVER_ERROR"))
    return JSONResponse(
        status_code=500,
        content={
            "success":    False,
            "message":    "An unexpected internal server error occurred",
            "error":      str(exc),
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# ══════════════════════════════════════════════════════════════════
# Router Registration
# ══════════════════════════════════════════════════════════════════

# Health Check — GET / and GET /health (public, no version prefix)
app.include_router(health_router, tags=["Health"])

# Versioned API — /api/v1/... and future /api/v2/...
# Also exposes GET /api/versions for version discovery
app.include_router(api_router, prefix="/api")
