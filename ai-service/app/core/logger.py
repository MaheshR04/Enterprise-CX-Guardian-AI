"""
Enterprise CX Guardian AI — Centralized Structured Logger
==========================================================

7 Logging Categories:
  1. Authentication  — login, logout, token events, auth failures
  2. AI Requests     — Groq API calls, model, tokens, latency
  3. Database        — connections, CRUD, health, fallback
  4. RAG Retrieval   — document fetch, similarity scores, chunk counts
  5. Tool Calls      — sentiment, reasoning, recommendation, analyze
  6. Errors          — domain errors, validation, unexpected failures
  7. Response Time   — HTTP requests, per-route latency, p-level alerts

All log lines share a uniform format:
  [YYYY-MM-DD HH:MM:SS] [LEVEL   ] [ai_microservice] [CATEGORY] message
"""

import logging
import sys
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Optional, Any, Callable
from app.core.config import settings

# ══════════════════════════════════════════════════════════════════
# Log Format
# ══════════════════════════════════════════════════════════════════

LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)-8s] "
    "[%(name)s] "
    "%(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Latency thresholds for automated WARN elevation (ms)
LATENCY_WARN_MS  = 1000     # 1 second
LATENCY_ERROR_MS = 5000     # 5 seconds


def setup_logger(name: str = "ai_microservice") -> logging.Logger:
    """
    Creates and returns a named logger backed by a stdout StreamHandler.
    Log level driven by settings.LOG_LEVEL (default: INFO).
    Idempotent — safe to call multiple times.
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


# ══════════════════════════════════════════════════════════════════
# 1. Authentication Logging
# ══════════════════════════════════════════════════════════════════

def log_auth_attempt(email: str, method: str = "password") -> None:
    """Logs a login attempt (before outcome is known)."""
    logger.info(
        f"[Auth] LOGIN ATTEMPT | email: {_mask_email(email)} | method: {method}"
    )


def log_auth_success(user_id: str, email: str, token_type: str = "access") -> None:
    """Logs a successful authentication event."""
    logger.info(
        f"[Auth] ✓ LOGIN SUCCESS | user_id: {user_id} "
        f"| email: {_mask_email(email)} | token: {token_type}"
    )


def log_auth_failure(email: str, reason: str, ip: str = "unknown") -> None:
    """Logs a failed authentication event."""
    logger.warning(
        f"[Auth] ✗ LOGIN FAILED | email: {_mask_email(email)} "
        f"| reason: {reason} | ip: {ip}"
    )


def log_auth_logout(user_id: str) -> None:
    """Logs a logout/token revocation event."""
    logger.info(f"[Auth] LOGOUT | user_id: {user_id}")


def log_token_refresh(user_id: str, success: bool, reason: str = "") -> None:
    """Logs a JWT refresh token usage event."""
    status = "✓ SUCCESS" if success else f"✗ FAILED ({reason})"
    logger.info(f"[Auth] TOKEN REFRESH | user_id: {user_id} | {status}")


def log_token_invalid(reason: str, ip: str = "unknown") -> None:
    """Logs an invalid/expired/forged JWT token event."""
    logger.warning(
        f"[Auth] INVALID TOKEN | reason: {reason} | ip: {ip}"
    )


def log_register(email: str, user_id: str) -> None:
    """Logs a new user registration event."""
    logger.info(
        f"[Auth] REGISTER | user_id: {user_id} | email: {_mask_email(email)}"
    )


# ══════════════════════════════════════════════════════════════════
# 2. AI Request Logging
# ══════════════════════════════════════════════════════════════════

def log_ai_request_start(
    conversation_id: str,
    model: str,
    history_turns: int,
    prompt_chars: int
) -> None:
    """Logs the start of a Groq AI request."""
    logger.info(
        f"[AI Request] → GROQ | conv_id: {conversation_id} "
        f"| model: {model} | history: {history_turns} turns "
        f"| prompt: {prompt_chars} chars"
    )


def log_ai_request_success(
    conversation_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: float
) -> None:
    """Logs a successful Groq AI response with full telemetry."""
    throughput = (total_tokens / latency_ms * 1000) if latency_ms > 0 else 0
    level = (
        logging.ERROR   if latency_ms >= LATENCY_ERROR_MS else
        logging.WARNING if latency_ms >= LATENCY_WARN_MS  else
        logging.INFO
    )
    logger.log(
        level,
        f"[AI Request] ← GROQ OK | conv_id: {conversation_id} "
        f"| model: {model} "
        f"| tokens: prompt={prompt_tokens} completion={completion_tokens} total={total_tokens} "
        f"| latency: {latency_ms:.0f}ms "
        f"| throughput: {throughput:.0f} tok/s"
    )


def log_ai_request_error(
    conversation_id: str,
    model: str,
    error: Exception,
    latency_ms: float
) -> None:
    """Logs a failed Groq AI call."""
    logger.error(
        f"[AI Request] ← GROQ ERROR | conv_id: {conversation_id} "
        f"| model: {model} | latency: {latency_ms:.0f}ms "
        f"| {type(error).__name__}: {error}"
    )


def log_prompt_build(
    conversation_id: str,
    prompt_size: int,
    history_turns: int
) -> None:
    """Logs prompt assembly details."""
    logger.info(
        f"[AI Prompt] BUILT | conv_id: {conversation_id} "
        f"| size: {prompt_size} chars | history: {history_turns} turns"
    )


# Aliases — backward compatible
def log_groq_latency(model: str, latency_ms: float, total_tokens: int) -> None:
    throughput = (total_tokens / latency_ms * 1000) if latency_ms > 0 else 0
    logger.info(
        f"[AI Latency] model: {model} | latency: {latency_ms:.2f}ms "
        f"| tokens: {total_tokens} | throughput: {throughput:.1f} tok/s"
    )

def log_ai_call(model_name: str, prompt_tokens: int, completion_tokens: int, latency_ms: float) -> None:
    logger.info(
        f"[AI Telemetry] model: {model_name} | prompt: {prompt_tokens} "
        f"| completion: {completion_tokens} | latency: {latency_ms:.2f}ms"
    )


# ══════════════════════════════════════════════════════════════════
# 3. Database Logging
# ══════════════════════════════════════════════════════════════════

def log_db_connecting(uri_masked: str, db_name: str) -> None:
    logger.info(
        f"[DB] CONNECTING | db: '{db_name}' | uri: {uri_masked}"
    )

def log_db_connected(db_name: str, pool_min: int, pool_max: int, latency_ms: float) -> None:
    logger.info(
        f"[DB] ✓ CONNECTED | db: '{db_name}' "
        f"| pool: {pool_min}–{pool_max} | ping: {latency_ms:.2f}ms"
    )

def log_db_disconnected(db_name: str) -> None:
    logger.info(f"[DB] DISCONNECTED | db: '{db_name}'")

def log_db_error(operation: str, error: Exception) -> None:
    logger.error(
        f"[DB] ERROR | op: '{operation}' | {type(error).__name__}: {error}"
    )

def log_db_fallback(reason: str) -> None:
    logger.warning(
        f"[DB] FALLBACK MODE | reason: {reason}"
    )

def log_db_health(
    db_name: str,
    status: str,
    ping_latency_ms: Optional[float] = None,
    error: Optional[str] = None
) -> None:
    if status == "healthy":
        logger.info(
            f"[DB] HEALTH ✓ | db: '{db_name}' | ping: {ping_latency_ms:.2f}ms"
        )
    else:
        logger.warning(
            f"[DB] HEALTH ✗ | db: '{db_name}' | error: {error}"
        )

def log_crud_insert(collection: str, doc_id: str, latency_ms: float) -> None:
    logger.info(
        f"[DB CRUD] INSERT | collection: '{collection}' "
        f"| id: {doc_id} | latency: {latency_ms:.2f}ms"
    )

def log_crud_find(collection: str, query_key: str, found: bool, latency_ms: float) -> None:
    result = "HIT" if found else "MISS"
    logger.info(
        f"[DB CRUD] FIND {result} | collection: '{collection}' "
        f"| key: {query_key} | latency: {latency_ms:.2f}ms"
    )

def log_crud_update(collection: str, doc_id: str, field: str, latency_ms: float) -> None:
    logger.info(
        f"[DB CRUD] UPDATE | collection: '{collection}' "
        f"| id: {doc_id} | field: {field} | latency: {latency_ms:.2f}ms"
    )

def log_crud_delete(collection: str, doc_id: str, soft: bool, latency_ms: float) -> None:
    mode = "SOFT" if soft else "HARD"
    logger.info(
        f"[DB CRUD] DELETE {mode} | collection: '{collection}' "
        f"| id: {doc_id} | latency: {latency_ms:.2f}ms"
    )

def log_crud_count(collection: str, count: int, latency_ms: float) -> None:
    logger.info(
        f"[DB CRUD] COUNT | collection: '{collection}' "
        f"| count: {count} | latency: {latency_ms:.2f}ms"
    )


# ══════════════════════════════════════════════════════════════════
# 4. RAG Retrieval Logging
# ══════════════════════════════════════════════════════════════════

def log_rag_query(query: str, collection: str, top_k: int) -> None:
    """Logs a RAG vector similarity query."""
    logger.info(
        f"[RAG] QUERY | collection: '{collection}' "
        f"| top_k: {top_k} | query_preview: '{_truncate(query, 60)}'"
    )


def log_rag_results(
    collection: str,
    retrieved: int,
    top_score: float,
    latency_ms: float
) -> None:
    """Logs RAG retrieval results with similarity score and latency."""
    score_flag = " ⚠ LOW RELEVANCE" if top_score < 0.5 else ""
    logger.info(
        f"[RAG] RETRIEVED | collection: '{collection}' "
        f"| docs: {retrieved} | top_score: {top_score:.3f}{score_flag} "
        f"| latency: {latency_ms:.2f}ms"
    )


def log_rag_cache_hit(query_hash: str, collection: str) -> None:
    """Logs a RAG cache hit (retrieved from cache instead of vector DB)."""
    logger.debug(
        f"[RAG] CACHE HIT | collection: '{collection}' | hash: {query_hash}"
    )


def log_rag_miss(query: str, collection: str, reason: str = "no results") -> None:
    """Logs a RAG retrieval miss — no relevant documents found."""
    logger.warning(
        f"[RAG] MISS | collection: '{collection}' | reason: {reason} "
        f"| query: '{_truncate(query, 60)}'"
    )


def log_rag_error(collection: str, error: Exception, latency_ms: float) -> None:
    """Logs a RAG retrieval failure."""
    logger.error(
        f"[RAG] ERROR | collection: '{collection}' "
        f"| latency: {latency_ms:.2f}ms | {type(error).__name__}: {error}"
    )


# ══════════════════════════════════════════════════════════════════
# 5. Tool Call Logging
# ══════════════════════════════════════════════════════════════════

def log_tool_call(
    tool_name: str,
    input_preview: str,
    conversation_id: Optional[str] = None
) -> None:
    """Logs the invocation of any AI tool (sentiment, reasoning, etc.)."""
    conv = f" | conv_id: {conversation_id}" if conversation_id else ""
    logger.info(
        f"[Tool] CALL | tool: '{tool_name}'{conv} "
        f"| input: '{_truncate(input_preview, 80)}'"
    )


def log_tool_result(
    tool_name: str,
    success: bool,
    latency_ms: float,
    result_preview: str = "",
    conversation_id: Optional[str] = None
) -> None:
    """Logs the result of an AI tool call."""
    conv   = f" | conv_id: {conversation_id}" if conversation_id else ""
    status = "✓ OK" if success else "✗ FAILED"
    preview = f" | result: '{_truncate(result_preview, 60)}'" if result_preview else ""
    level  = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        f"[Tool] {status} | tool: '{tool_name}'{conv} "
        f"| latency: {latency_ms:.2f}ms{preview}"
    )


def log_tool_error(
    tool_name: str,
    error: Exception,
    latency_ms: float,
    conversation_id: Optional[str] = None
) -> None:
    """Logs a tool call exception."""
    conv = f" | conv_id: {conversation_id}" if conversation_id else ""
    logger.error(
        f"[Tool] ERROR | tool: '{tool_name}'{conv} "
        f"| latency: {latency_ms:.2f}ms | {type(error).__name__}: {error}"
    )


# ══════════════════════════════════════════════════════════════════
# 6. Error Logging
# ══════════════════════════════════════════════════════════════════

def log_error(
    context: str,
    error: Exception,
    conversation_id: Optional[str] = None
) -> None:
    """Logs an application-level error with full context."""
    conv_part = f" | conv_id: {conversation_id}" if conversation_id else ""
    logger.error(
        f"[Error] {context}{conv_part} | {type(error).__name__}: {error}"
    )


def log_validation_error(field: str, value: Any, reason: str) -> None:
    """Logs a request validation failure."""
    logger.warning(
        f"[Error] VALIDATION | field: '{field}' | value: '{value}' | reason: {reason}"
    )


def log_not_found(resource: str, resource_id: str) -> None:
    """Logs a 404 resource not found event."""
    logger.warning(
        f"[Error] NOT FOUND | resource: '{resource}' | id: '{resource_id}'"
    )


def log_unexpected_error(context: str, error: Exception) -> None:
    """Logs an unexpected/unhandled exception with full stack trace."""
    logger.exception(
        f"[Error] UNEXPECTED | context: {context} | {type(error).__name__}: {error}"
    )


def log_domain_error(
    error_code: str,
    message: str,
    status_code: int,
    path: str
) -> None:
    """Logs a structured domain error (BaseAppException subclass)."""
    level = logging.WARNING if status_code < 500 else logging.ERROR
    logger.log(
        level,
        f"[Error] DOMAIN | code: {error_code} | status: {status_code} "
        f"| path: {path} | msg: {message}"
    )


# ══════════════════════════════════════════════════════════════════
# 7. Response Time Logging
# ══════════════════════════════════════════════════════════════════

def log_request_latency(
    method: str,
    path: str,
    status_code: int,
    latency_ms: float
) -> None:
    """
    Logs HTTP request-level latency.
    Automatically elevates log level if latency exceeds thresholds:
      > 1000ms  → WARNING
      > 5000ms  → ERROR
      4xx/5xx   → WARNING/ERROR
    """
    if latency_ms >= LATENCY_ERROR_MS:
        level = logging.ERROR
        perf  = f"🔴 SLOW"
    elif latency_ms >= LATENCY_WARN_MS:
        level = logging.WARNING
        perf  = f"🟡 SLOW"
    elif status_code >= 500:
        level = logging.ERROR
        perf  = "⚠"
    elif status_code >= 400:
        level = logging.WARNING
        perf  = "⚠"
    else:
        level = logging.INFO
        perf  = "✓"

    logger.log(
        level,
        f"[HTTP] {perf} {method} {path} → {status_code} "
        f"| latency: {latency_ms:.2f}ms"
    )


def log_slow_request(
    method: str,
    path: str,
    latency_ms: float,
    threshold_ms: float
) -> None:
    """Explicitly logs a slow request that exceeded a custom threshold."""
    logger.warning(
        f"[HTTP] SLOW REQUEST | {method} {path} "
        f"| latency: {latency_ms:.0f}ms > threshold: {threshold_ms:.0f}ms"
    )


# ══════════════════════════════════════════════════════════════════
# Decorator — @log_latency
# ══════════════════════════════════════════════════════════════════

def log_latency(operation: str, collection: str = ""):
    """
    Decorator for auto-measuring and logging the execution latency
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
                result  = await func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                logger.debug(
                    f"[DB CRUD] {operation.upper()} "
                    f"{'| ' + collection + ' ' if collection else ''}"
                    f"| {elapsed:.2f}ms"
                )
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                logger.error(
                    f"[DB CRUD] ERROR {operation.upper()} "
                    f"{'| ' + collection + ' ' if collection else ''}"
                    f"| {elapsed:.2f}ms | {type(e).__name__}: {e}"
                )
                raise
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════════════════
# Backward-Compatible Aliases
# ══════════════════════════════════════════════════════════════════

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
    """Logs conversation telemetry — backward-compatible alias."""
    err_suffix = f" | ERROR: {error}" if error else ""
    logger.info(
        f"[Conversation] conv_id: {conversation_id} | msg_id: {message_id} "
        f"| prompt: {prompt_size} chars | latency: {execution_time_ms:.2f}ms "
        f"| tokens: prompt={prompt_tokens} completion={completion_tokens} total={total_tokens}"
        f"{err_suffix}"
    )


# ══════════════════════════════════════════════════════════════════
# Private Helpers
# ══════════════════════════════════════════════════════════════════

def _mask_email(email: str) -> str:
    """Masks the local part of an email for safe logging: user@x.com → u***@x.com"""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}" if len(local) > 1 else f"***@{domain}"


def _truncate(text: str, max_len: int) -> str:
    """Truncates text for safe log line length."""
    if not text:
        return ""
    text = str(text).replace("\n", " ").strip()
    return text[:max_len] + "…" if len(text) > max_len else text
