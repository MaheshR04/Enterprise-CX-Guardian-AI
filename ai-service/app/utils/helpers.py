import uuid
from datetime import datetime

def generate_uuid() -> str:
    """Generates a random UUID string."""
    return str(uuid.uuid4())

def get_current_timestamp() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat()

def sanitize_text(text: str) -> str:
    """Strips leading/trailing whitespace and removes raw control characters."""
    if not text:
        return ""
    return text.strip()
