"""
Enterprise CX Guardian AI — Domain Exception Classes.

Covers all error scenarios:
  - MongoDB unavailable / connection timeout
  - Duplicate IDs (upsert conflicts)
  - Document not found
  - Request validation errors
  - LLM service failures
  - History overflow
  - Unexpected server errors
"""

from app.core.logger import log_error, log_not_found, log_validation_error


# ══════════════════════════════════════════════════════════════════
# Base
# ══════════════════════════════════════════════════════════════════

class BaseAppException(Exception):
    """
    Base exception for all Enterprise CX Guardian AI domain errors.
    All custom exceptions inherit from this class.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: str = None,
        error_code: str = None
    ):
        self.message    = message
        self.status_code = status_code
        self.detail     = detail
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)


# ══════════════════════════════════════════════════════════════════
# 1. MongoDB Unavailable / Connection Errors
# ══════════════════════════════════════════════════════════════════

class MongoUnavailableException(BaseAppException):
    """
    Raised when MongoDB Atlas is unreachable or the Motor client
    is not initialized at request time.
    """
    def __init__(self, detail: str = "MongoDB is currently unavailable."):
        log_error("MongoUnavailableException", self, None)
        super().__init__(
            message="Database Unavailable",
            status_code=503,
            detail=detail,
            error_code="DB_UNAVAILABLE"
        )


class MongoConnectionTimeoutException(BaseAppException):
    """
    Raised when a MongoDB operation exceeds the configured timeout.
    """
    def __init__(
        self,
        operation: str = "unknown",
        detail: str = None
    ):
        msg = detail or f"MongoDB connection timed out during '{operation}' operation."
        super().__init__(
            message="Database Connection Timeout",
            status_code=504,
            detail=msg,
            error_code="DB_TIMEOUT"
        )


class MongoOperationException(BaseAppException):
    """
    Raised when a MongoDB CRUD operation fails unexpectedly
    (write error, network blip, etc.).
    """
    def __init__(
        self,
        operation: str = "unknown",
        collection: str = "unknown",
        detail: str = None
    ):
        msg = detail or (
            f"MongoDB '{operation}' failed on collection '{collection}'."
        )
        super().__init__(
            message="Database Operation Failed",
            status_code=500,
            detail=msg,
            error_code="DB_OPERATION_FAILED"
        )


# ══════════════════════════════════════════════════════════════════
# 2. Duplicate IDs
# ══════════════════════════════════════════════════════════════════

class DuplicateConversationIdException(BaseAppException):
    """
    Raised when attempting to create a conversation with an ID
    that already exists in MongoDB.
    """
    def __init__(self, conversation_id: str):
        super().__init__(
            message="Duplicate Conversation ID",
            status_code=409,
            detail=(
                f"A conversation with ID '{conversation_id}' already exists. "
                "Use the existing conversation or provide a unique ID."
            ),
            error_code="DUPLICATE_CONVERSATION_ID"
        )


class DuplicateMessageIdException(BaseAppException):
    """
    Raised on message ID collision (extremely rare — UUID-based IDs).
    """
    def __init__(self, message_id: str):
        super().__init__(
            message="Duplicate Message ID",
            status_code=409,
            detail=f"A message with ID '{message_id}' already exists.",
            error_code="DUPLICATE_MESSAGE_ID"
        )


# ══════════════════════════════════════════════════════════════════
# 3. Document Not Found
# ══════════════════════════════════════════════════════════════════

class ConversationNotFoundException(BaseAppException):
    """
    Raised when a requested conversation ID does not exist in MongoDB
    or has been soft-deleted (status=deleted).
    """
    def __init__(self, conversation_id: str):
        log_not_found(resource="Conversation", resource_id=conversation_id)
        super().__init__(
            message="Conversation Not Found",
            status_code=404,
            detail=(
                f"Conversation '{conversation_id}' does not exist "
                "or has been deleted."
            ),
            error_code="CONVERSATION_NOT_FOUND"
        )


class MessageNotFoundException(BaseAppException):
    """
    Raised when a requested message ID does not exist in MongoDB.
    """
    def __init__(self, message_id: str):
        log_not_found(resource="Message", resource_id=message_id)
        super().__init__(
            message="Message Not Found",
            status_code=404,
            detail=f"Message '{message_id}' does not exist.",
            error_code="MESSAGE_NOT_FOUND"
        )


class NotFoundException(BaseAppException):
    """Generic 404 Not Found exception for any resource type."""
    def __init__(self, message: str = "Requested resource not found", detail: str = None):
        super().__init__(
            message=message,
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND"
        )


# ══════════════════════════════════════════════════════════════════
# 4. Validation Errors
# ══════════════════════════════════════════════════════════════════

class CustomValidationException(BaseAppException):
    """
    Raised when business-level payload validation fails
    (e.g., empty message, invalid status value).
    """
    def __init__(self, message: str = "Payload validation failed", detail: str = None):
        log_validation_error(
            field="payload",
            value="(see detail)",
            reason=detail or message
        )
        super().__init__(
            message=message,
            status_code=400,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class InvalidConversationIdException(BaseAppException):
    """
    Raised when a conversationId path/query parameter is malformed,
    empty, or exceeds the maximum allowed length.
    """
    def __init__(self, detail: str = "Invalid Conversation ID format."):
        super().__init__(
            message="Invalid Conversation ID",
            status_code=400,
            detail=detail,
            error_code="INVALID_CONVERSATION_ID"
        )


class EmptyMessageException(BaseAppException):
    """
    Raised when the chat message body is blank or whitespace-only.
    """
    def __init__(self):
        super().__init__(
            message="Empty Message",
            status_code=400,
            detail="Message content cannot be blank or empty whitespace.",
            error_code="EMPTY_MESSAGE"
        )


class InvalidStatusException(BaseAppException):
    """
    Raised when an invalid status value is provided to a search or update.
    """
    def __init__(self, provided: str):
        super().__init__(
            message="Invalid Status Value",
            status_code=400,
            detail=(
                f"'{provided}' is not a valid conversation status. "
                "Allowed values: active | archived | deleted."
            ),
            error_code="INVALID_STATUS"
        )


class HistoryOverflowException(BaseAppException):
    """
    Raised when the conversation history exceeds the configured
    MAX_HISTORY limit and cannot be further extended.
    """
    def __init__(self, max_history: int):
        super().__init__(
            message="History Overflow",
            status_code=400,
            detail=(
                f"Conversation history has reached the maximum limit "
                f"of {max_history} messages. Start a new conversation."
            ),
            error_code="HISTORY_OVERFLOW"
        )


# ══════════════════════════════════════════════════════════════════
# 5. LLM / Groq Service Errors
# ══════════════════════════════════════════════════════════════════

class LLMServiceException(BaseAppException):
    """
    Raised when the Groq API call fails or returns an unexpected error.
    """
    def __init__(self, message: str = "LLM service failed", detail: str = None):
        super().__init__(
            message=message,
            status_code=502,
            detail=detail,
            error_code="LLM_SERVICE_ERROR"
        )


class LLMTimeoutException(BaseAppException):
    """
    Raised when the Groq API call exceeds the configured timeout.
    """
    def __init__(self, timeout_ms: int = 30000):
        super().__init__(
            message="LLM Request Timeout",
            status_code=504,
            detail=(
                f"Groq API did not respond within {timeout_ms}ms. "
                "Please retry your request."
            ),
            error_code="LLM_TIMEOUT"
        )
