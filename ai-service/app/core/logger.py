"""
Enterprise CX Guardian AI — Structured Logger
Covers all 4 logging categories:
  1. Database connections   — connect, ping, disconnect, health
  2. CRUD operations        — insert, find, update, delete with collection + timing
  3. Errors                 — exceptions, fallback mode, unexpected failures
  4. Latency                — per-operation ms timing, Groq API latency, prompt size
"""

import logging
import sys
import time
from functools import wraps
from typing import Optional, Any, Callable
from app.core.config import settings

# ──────────────────────────────────────────────────────────────────────
# Log Format
# ──────────────────────────────────────────────────────────────────────
LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)-8s] "
    "[%(name)s] "
    "%(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "ai_microservice") -> logging.Logger:
    """
    Creates and configures a named logger with stdout StreamHandler.
    Log level is driven by settings.LOG_LEVEL (default: INFO).
    """
    log = logging.getLogger(name)
    log.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not log.handlers:
        handler   = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log


# Shared application-wide logger instance
logger = setup_logger()


# ──────────────────────────────────────────────────────────────────────
# 1. Database Connection Logging
# ──────────────────────────────────────────────────────────────────────

def log_db_connecting(uri_masked: str, db_name: str) -> None:
    """Logs a MongoDB connection attempt."""
    logger.info(
        f"[DB Connect] Initiating connection | "
        f"DB: '{db_name}' | URI: {uri_masked}"
    )


def log_db_connected(db_name: str, pool_min: int, pool_max: int, latency_ms: float) -> None:
    """Logs a successful MongoDB connection with pool config and ping latency."""
    logger.info(
        f"[DB Connect] ✓ Connected to '{db_name}' | "
        f"Pool: {pool_min}–{pool_max} | "
        f"Ping Latency: {latency_ms:.2f}ms"
    )


def log_db_disconnected(db_name: str) -> None:
    """Logs graceful MongoDB disconnection."""
    logger.info(f"[DB Disconnect] Connection pool closed for '{db_name}'")


def log_db_error(operation: str, error: Exception) -> None:
    """Logs a MongoDB connection or operation error."""
    logger.error(
        f"[DB Error] Operation: '{operation}' | "
        f"Error: {type(error).__name__}: {error}"
    )


def log_db_fallback(reason: str) -> None:
    """Logs entry into resilient fallback mode when MongoDB is unreachable."""
    logger.warning(
        f"[DB Fallback] MongoDB unreachable — microservice running in resilient mode | "
        f"Reason: {reason}"
    )


def log_db_health(db_name: str, status: str, ping_latency_ms: Optional[float] = None, error: Optional[str] = None) -> None:
    """Logs a MongoDB health check result."""
    if status == "healthy":
        logger.info(
            f"[DB Health] ✓ Healthy | DB: '{db_name}' | "
            f"Ping: {ping_latency_ms:.2f}ms"
        )
    else:
        logger.warning(
            f"[DB Health] ✗ Unhealthy | DB: '{db_name}' | "
            f"Error: {error}"
        )


# ──────────────────────────────────────────────────────────────────────
# 2. CRUD Operation Logging
# ──────────────────────────────────────────────────────────────────────

def log_crud_insert(collection: str, doc_id: str, latency_ms: float) -> None:
    """Logs a MongoDB insert operation with latency."""
    logger.info(
        f"[CRUD Insert] Collection: '{collection}' | "
        f"ID: {doc_id} | "
        f"Latency: {latency_ms:.2f}ms"
    )


def log_crud_find(collection: str, query_key: str, found: bool, latency_ms: float) -> None:
    """Logs a MongoDB find/query operation with hit/miss result and latency."""
    result = "HIT" if found else "MISS"
    logger.info(
        f"[CRUD Find ] Collection: '{collection}' | "
        f"Key: {query_key} | "
        f"Result: {result} | "
        f"Latency: {latency_ms:.2f}ms"
    )


def log_crud_update(collection: str, doc_id: str, field: str, latency_ms: float) -> None:
    """Logs a MongoDB update operation."""
    logger.info(
        f"[CRUD Update] Collection: '{collection}' | "
        f"ID: {doc_id} | "
        f"Field: {field} | "
        f"Latency: {latency_ms:.2f}ms"
    )


def log_crud_delete(collection: str, doc_id: str, soft: bool, latency_ms: float) -> None:
    """Logs a MongoDB delete (hard or soft) operation."""
    mode = "SOFT" if soft else "HARD"
    logger.info(
        f"[CRUD Delete] Collection: '{collection}' | "
        f"ID: {doc_id} | "
        f"Mode: {mode} | "
        f"Latency: {latency_ms:.2f}ms"
    )


def log_crud_count(collection: str, count: int, latency_ms: float) -> None:
    """Logs a MongoDB count operation."""
    logger.info(
        f"[CRUD Count ] Collection: '{collection}' | "
        f"Count: {count} | "
        f"Latency: {latency_ms:.2f}ms"
    )


# ──────────────────────────────────────────────────────────────────────
# 3. Error Logging
# ──────────────────────────────────────────────────────────────────────

def log_error(context: str, error: Exception, conversation_id: Optional[str] = None) -> None:
    """Logs an application-level error with full context."""
    conv_part = f" | ConvID: {conversation_id}" if conversation_id else ""
    logger.error(
        f"[Error] {context}{conv_part} | "
        f"{type(error).__name__}: {error}"
    )


def log_validation_error(field: str, value: Any, reason: str) -> None:
    """Logs a request validation failure."""
    logger.warning(
        f"[Validation Error] Field: '{field}' | "
        f"Value: '{value}' | "
        f"Reason: {reason}"
    )


def log_not_found(resource: str, resource_id: str) -> None:
    """Logs a 404-level resource not found event."""
    logger.warning(
        f"[Not Found] Resource: '{resource}' | "
        f"ID: '{resource_id}'"
    )


def log_unexpected_error(context: str, error: Exception) -> None:
    """Logs an unexpected/unhandled exception with stack trace."""
    logger.exception(
        f"[Unexpected Error] {context} | "
        f"{type(error).__name__}: {error}"
    )


# ──────────────────────────────────────────────────────────────────────
# 4. Latency Logging
# ──────────────────────────────────────────────────────────────────────

def log_request_latency(method: str, path: str, status_code: int, latency_ms: float) -> None:
    """Logs HTTP request-level latency."""
    level = logging.INFO if status_code < 400 else logging.WARNING
    logger.log(
        level,
        f"[HTTP] {method} {path} → {status_code} | "
        f"Latency: {latency_ms:.2f}ms"
    )


def log_groq_latency(model: str, latency_ms: float, total_tokens: int) -> None:
    """Logs Groq API call latency and token throughput."""
    tokens_per_sec = (total_tokens / latency_ms * 1000) if latency_ms > 0 else 0
    logger.info(
        f"[Groq Latency] Model: {model} | "
        f"Latency: {latency_ms:.2f}ms | "
        f"Tokens: {total_tokens} | "
        f"Throughput: {tokens_per_sec:.1f} tok/s"
    )


def log_prompt_build(conversation_id: str, prompt_size: int, history_turns: int) -> None:
    """Logs prompt assembly details."""
    logger.info(
        f"[Prompt Build] ConvID: {conversation_id} | "
        f"Size: {prompt_size} chars | "
        f"History Turns: {history_turns}"
    )


# ──────────────────────────────────────────────────────────────────────
# Decorator — Auto-log CRUD latency
# ──────────────────────────────────────────────────────────────────────

def log_latency(operation: str, collection: str = ""):
    """
    Decorator that automatically measures and logs execution latency
    of any async repository or service method.

    Usage:
        @log_latency("insert", "conversations")
        async def insert_one(self, ...): ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                logger.debug(
                    f"[Latency] {operation.upper()} "
                    f"{'| ' + collection if collection else ''} "
                    f"| {elapsed:.2f}ms"
                )
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                logger.error(
                    f"[Latency Error] {operation.upper()} "
                    f"{'| ' + collection if collection else ''} "
                    f"| {elapsed:.2f}ms | {type(e).__name__}: {e}"
                )
                raise
        return wrapper
    return decorator


# ──────────────────────────────────────────────────────────────────────
# Legacy helpers — preserved for backward compatibility
# ──────────────────────────────────────────────────────────────────────

def log_ai_call(model_name: str, prompt_tokens: int, completion_tokens: int, latency_ms: float) -> None:
    """Logs AI execution telemetry. Backward-compatible alias."""
    logger.info(
        f"[AI Telemetry] Model: {model_name} | "
        f"Prompt Tokens: {prompt_tokens} | "
        f"Completion Tokens: {completion_tokens} | "
        f"Latency: {latency_ms:.2f}ms"
    )


def log_conversation(
    conversation_id: str,
    message_id: str,
    prompt_size: int,
    execution_time_ms: float,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    error: str = None
) -> None:
    """Logs detailed conversation telemetry. Backward-compatible alias."""
    err_suffix = f" | ERROR: {error}" if error else ""
    logger.info(
        f"[Conversation Telemetry] "
        f"ConvID: {conversation_id} | MsgID: {message_id} | "
        f"Prompt: {prompt_size} chars | "
        f"Latency: {execution_time_ms:.2f}ms | "
        f"Tokens: [prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}]"
        f"{err_suffix}"
    )
