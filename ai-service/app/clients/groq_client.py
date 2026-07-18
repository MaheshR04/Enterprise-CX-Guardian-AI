import time
import groq
from groq import Groq
import httpx
from app.core.config import settings
from app.core.logger import logger, log_ai_call

class GroqClient:
    """
    Groq LLM Connection Client Provider.
    Configures API client connections, timeouts, retries, and completion execution.
    """
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        
        # Configure custom HTTPX Client with timeout limits (15.0s timeout)
        self.httpx_client = httpx.Client(
            timeout=httpx.Timeout(15.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Initialize Groq SDK Client with API key, max retries (3 retries), and timeout settings
        self.has_key = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
        api_key = settings.GROQ_API_KEY if self.has_key else "gsk_dummy_placeholder_key"
        
        self.client = Groq(
            api_key=api_key,
            max_retries=3,
            timeout=15.0,
            http_client=self.httpx_client
        )
        logger.info(f"[Groq Client] Initialized Groq Client. Model: {self.model_name} | Max Retries: 3 | Timeout: 15.0s")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> dict:
        """
        Exposes the primary generate() entrypoint for Groq LLM completions.
        """
        start_time = time.time()
        temp = temperature if temperature is not None else self.temperature
        tokens_limit = max_tokens if max_tokens is not None else self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"[Groq Request] Sending completion request to model '{self.model_name}' (prompt length: {len(prompt)})")

        if not self.has_key:
            latency_ms = (time.time() - start_time) * 1000
            logger.info(f"[Groq Fallback] Returning simulated response for prompt length {len(prompt)} ({latency_ms:.2f}ms)")
            return {
                "reply": f"Groq AI Engine Response: Received input '{prompt}'",
                "model": self.model_name,
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 12,
                "latency_ms": latency_ms,
                "fallback": True
            }

        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=temp,
                max_tokens=tokens_limit
            )

            latency_ms = (time.time() - start_time) * 1000
            reply_text = response.choices[0].message.content if response.choices else ""
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0

            logger.info(f"[Groq Response] Received response choices: {len(response.choices)} ({latency_ms:.2f}ms)")
            log_ai_call(self.model_name, prompt_tokens, completion_tokens, latency_ms)

            return {
                "reply": reply_text,
                "model": self.model_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency_ms": latency_ms,
                "fallback": False
            }

        except groq.AuthenticationError as err:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"[Groq Invalid API Key] Authentication failed: {err}")
            return {
                "reply": "Error: Invalid or unauthorized Groq API key.",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "fallback": True,
                "error": "Invalid API Key"
            }

        except groq.RateLimitError as err:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"[Groq Rate Limit] Rate limit exceeded: {err}")
            return {
                "reply": "Error: Groq service rate limit exceeded. Please retry shortly.",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "fallback": True,
                "error": "Rate Limit Exceeded"
            }

        except (groq.APITimeoutError, httpx.TimeoutException) as err:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"[Groq Timeout] Request timed out: {err}")
            return {
                "reply": "Error: Groq AI service request timed out.",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "fallback": True,
                "error": "Timeout Error"
            }

        except groq.NotFoundError as err:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"[Groq Model Not Found] Specified model '{self.model_name}' not found: {err}")
            return {
                "reply": f"Error: Groq model '{self.model_name}' was not found.",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "fallback": True,
                "error": "Model Not Found"
            }

        except Exception as error:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"[Groq Unexpected Error] API call failed ({error}). Reverting to fallback response.")
            return {
                "reply": f"Groq AI Engine Response (Fallback): Evaluated message '{prompt}'",
                "model": self.model_name,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "latency_ms": latency_ms,
                "fallback": True,
                "error": str(error)
            }

groq_client = GroqClient()
