class BaseAppException(Exception):
    """Base exception class for Enterprise CX Guardian AI microservice."""
    def __init__(self, message: str, status_code: int = 500, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

class LLMServiceException(BaseAppException):
    """Exception raised when an external LLM API service fails."""
    def __init__(self, message: str = "LLM Service processing failed", detail: str = None):
        super().__init__(message=message, status_code=502, detail=detail)

class CustomValidationException(BaseAppException):
    """Exception raised when payload validation checks fail."""
    def __init__(self, message: str = "Payload validation failed", detail: str = None):
        super().__init__(message=message, status_code=400, detail=detail)

class NotFoundException(BaseAppException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, message: str = "Requested resource not found", detail: str = None):
        super().__init__(message=message, status_code=404, detail=detail)

class ConversationNotFoundException(BaseAppException):
    """Exception raised when a requested conversation ID does not exist."""
    def __init__(self, conversation_id: str):
        super().__init__(
            message="Conversation not found",
            status_code=404,
            detail=f"Conversation ID '{conversation_id}' does not exist or has expired."
        )

class InvalidConversationIdException(BaseAppException):
    """Exception raised when a conversation ID string is malformed or invalid."""
    def __init__(self, detail: str = "Invalid Conversation ID format"):
        super().__init__(
            message="Invalid Conversation ID",
            status_code=400,
            detail=detail
        )
