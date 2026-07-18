import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Enterprise CX Guardian AI"
    TAGLINE: str = "An AI-powered Autonomous Customer Experience Agent."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # MongoDB Parameters
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", os.getenv("DB_NAME", "cx_guardian_db"))
    DB_NAME: str = DATABASE_NAME
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "mongodb")
    CONVERSATION_COLLECTION: str = os.getenv("CONVERSATION_COLLECTION", "conversations")
    MESSAGE_COLLECTION: str = os.getenv("MESSAGE_COLLECTION", "messages")
    PROMPT_LOG_COLLECTION: str = os.getenv("PROMPT_LOG_COLLECTION", "prompt_logs")
    AI_USAGE_COLLECTION: str = os.getenv("AI_USAGE_COLLECTION", "ai_usage")
    
    # AI & Service Parameters
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3-70b-8192")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.2))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1024))
    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", 10))
    MAX_CONVERSATIONS: int = int(os.getenv("MAX_CONVERSATIONS", 100))
    AUTO_DELETE_EMPTY: bool = os.getenv("AUTO_DELETE_EMPTY", "True").lower() in ("true", "1", "t", "yes")
    
    NODE_BACKEND_URL: str = os.getenv("NODE_BACKEND_URL", "http://localhost:5000")
    CONFIDENCE_THRESHOLD: float = 0.85

settings = Settings()
