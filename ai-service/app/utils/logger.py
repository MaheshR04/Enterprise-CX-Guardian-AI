"""
Legacy logger compatibility module — re-exports from app.core.logger.
"""

from app.core.logger import (
    logger,
    log_request_latency as log_request,
    log_request_latency as log_response,
    log_error,
    log_validation_error as log_warning,
    log_ai_call
)

__all__ = ["logger", "log_request", "log_response", "log_error", "log_warning", "log_ai_call"]
