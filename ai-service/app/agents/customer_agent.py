"""
Autonomous Customer Experience Agent Engine.
Integrates Groq LLM completion service with centralized system prompts.
"""

from app.services.groq_service import groq_service, GroqService
from app.prompts.system_prompt import BASE_SYSTEM_PROMPT
from app.utils.logger import logger

class CustomerAgent:
    """
    Autonomous Customer Experience Agent Class.
    """
    def __init__(self, service: GroqService = None):
        self.agent_name = "Enterprise CX Guardian Agent"
        self.service = service or groq_service

    async def run_agent(self, user_input: str, conversation_id: str = None) -> dict:
        """
        Executes autonomous customer agent interactions using Groq LLM.
        """
        logger.info(f"[{self.agent_name}] Executing agent invocation for input length {len(user_input)}")
        
        result = await self.service.generate_completion(
            prompt=user_input,
            system_prompt=BASE_SYSTEM_PROMPT
        )

        return {
            "agent": self.agent_name,
            "conversation_id": conversation_id or "conv_default_001",
            "reply": result.get("reply", ""),
            "model": result.get("model", ""),
            "latency_ms": result.get("latency_ms", 0),
            "fallback": result.get("fallback", False)
        }

customer_agent = CustomerAgent()
