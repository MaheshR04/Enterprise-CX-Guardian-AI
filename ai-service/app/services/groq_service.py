from groq import Groq
import httpx
from app.config import settings
from app.utils.logger import logger

class GroqService:
    """
    Groq LLM Client Connection Manager.
    Configures API keys, model choices, timeouts, and retry limits.
    """
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        
        # Configure custom HTTPX Client with timeout limits
        self.httpx_client = httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Initialize Groq SDK Client with API key, max retries, and timeout settings
        api_key = settings.GROQ_API_KEY if settings.GROQ_API_KEY else "gsk_dummy_placeholder_key"
        
        self.client = Groq(
            api_key=api_key,
            max_retries=3,
            timeout=10.0,
            http_client=self.httpx_client
        )
        logger.info(f"[Groq Service] Initialized Groq Client connection. Model: {self.model_name} | Max Retries: 3 | Timeout: 10.0s")

    def get_model_info(self):
        """
        Returns model configuration parameters without executing prompt calls.
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "status": "configured" if settings.GROQ_API_KEY else "unconfigured_key_missing"
        }

groq_service = GroqService()
