import logging
import sys
from app.core.config import settings

def setup_logger():
    """
    Configures standard Python logging handler outputting to stdout.
    """
    logger = logging.getLogger("ai_microservice")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = setup_logger()

def log_ai_call(model_name: str, prompt_tokens: int, completion_tokens: int, latency_ms: float):
    """
    Logs AI execution telemetry.
    """
    logger.info(
        f"[AI Telemetry] Model: {model_name} | Prompt Tokens: {prompt_tokens} | "
        f"Completion Tokens: {completion_tokens} | Latency: {latency_ms:.2f}ms"
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
):
    """
    Logs detailed conversation telemetry metrics.
    """
    err_suffix = f" | ERROR: {error}" if error else ""
    logger.info(
        f"[Conversation Telemetry] ConvID: {conversation_id} | MsgID: {message_id} | "
        f"Prompt Size: {prompt_size} chars | Latency: {execution_time_ms:.2f}ms | "
        f"Tokens: [prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}]{err_suffix}"
    )
