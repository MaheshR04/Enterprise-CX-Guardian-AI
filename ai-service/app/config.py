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
    
    # AI & Service Parameters
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3-70b-8192")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.2))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1024))
    NODE_BACKEND_URL: str = os.getenv("NODE_BACKEND_URL", "http://localhost:5000")
    CONFIDENCE_THRESHOLD: float = 0.85

settings = Settings()
