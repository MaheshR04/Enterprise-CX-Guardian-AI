from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import logger
from app.utils.logger import log_error
from app.utils.response import error_response
from app.utils.exceptions import BaseAppException
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.routers import health_router, api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Event
    logger.info("==================================================")
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Description: {settings.TAGLINE}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("==================================================")
    yield
    # Shutdown Event
    logger.info("==================================================")
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    logger.info("==================================================")

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.TAGLINE,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Register Request & Response Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS Security Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# EXCEPTION HANDLERS (EXACT ERROR FORMAT ENFORCED)
# =====================================================

# 1. Custom Domain BaseAppException Handler
@app.exception_handler(BaseAppException)
async def custom_app_exception_handler(request: Request, exc: BaseAppException):
    log_error(f"App Exception during {request.method} {request.url.path}", exc)
    return error_response(
        message=exc.message,
        error="Application Exception",
        status_code=exc.status_code
    )

# 2. Pydantic Request Validation Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log_error(f"Validation Error during {request.method} {request.url.path}", exc)
    error_detail = ", ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    return error_response(
        message="Request validation failed",
        error=error_detail,
        status_code=422
    )

# 3. HTTP Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log_error(f"HTTP Exception during {request.method} {request.url.path}", exc)
    return error_response(
        message=str(exc.detail),
        error="HTTP Exception",
        status_code=exc.status_code
    )

# 4. Global Uncaught Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(f"Unhandled Server Error during {request.method} {request.url.path}", exc)
    return error_response(
        message="An unexpected internal server error occurred",
        error=str(exc),
        status_code=500
    )

# =====================================================
# ROUTER REGISTRATION
# =====================================================

# Health Check Router (/ and /health)
app.include_router(health_router, tags=["Health"])

# Master API v1 Router Mount (/api/v1)
app.include_router(api_v1_router, prefix="/api/v1")
