import logging
import sys
import time
from app.config import settings

def setup_logger():
    logger = logging.getLogger("ai_service")
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = setup_logger()

def log_request(method: str, path: str, client_ip: str):
    logger.info(f"[Request] {method} {path} - IP: {client_ip}")

def log_response(method: str, path: str, status_code: int, duration_ms: float):
    logger.info(f"[Response] {method} {path} {status_code} - {duration_ms:.2f}ms")

def log_error(context: str, error: Exception):
    logger.error(f"[Error] {context}: {str(error)}", exc_info=True)

def log_warning(context: str, message: str):
    logger.warning(f"[Warning] {context}: {message}")

def log_ai_call(model: str, prompt_tokens: int, completion_tokens: int, latency_ms: float):
    logger.info(
        f"[AI Call] Model: {model} | Prompt Tokens: {prompt_tokens} | "
        f"Completion Tokens: {completion_tokens} | Latency: {latency_ms:.2f}ms"
    )
