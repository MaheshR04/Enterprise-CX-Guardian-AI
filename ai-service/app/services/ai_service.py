"""
AI Service Manager for Python FastAPI Microservice.
Coordinates prompt builder, memory context window management, Groq LLM execution, and response formatting.
"""

from app.clients.groq_client import groq_client, GroqClient
from app.prompts.prompt_builder import prompt_builder, PromptBuilder
from app.memory.memory_service import memory_service, MemoryService
from app.core.config import settings
from app.core.logger import logger, log_conversation

class AIServiceManager:
    """
    Core AI Service Manager executing the 9-step Chat Flow sequence.
    """
    def __init__(
        self,
        client: GroqClient = None,
        prompts: PromptBuilder = None,
        memory: MemoryService = None
    ):
        self.client = client or groq_client
        self.prompts = prompts or prompt_builder
        self.memory = memory or memory_service

    async def process_message(
        self,
        message: str,
        conversation_id: str = None,
        history: str = None,
        temperature: float = None
    ) -> dict:
        """
        Executes the Chat Flow and logs conversation metrics via log_conversation().
        """
        # 1. Receive Request & 2. Create conversation if missing
        cid = conversation_id or self.memory.conv_mgr.create_conversation_id()
        if not self.memory.conv_mgr.get_conversation(cid):
            self.memory.conv_mgr.create_conversation(conversation_id=cid)

        # 3. Load previous history (prior turns)
        formatted_history = history if history else self.memory.format_history_for_prompt(cid)

        # 4. Build prompt via PromptBuilder
        prompt_payload = self.prompts.build_chat_prompt(
            user_message=message,
            history_text=formatted_history,
            system_prompt_type="base"
        )
        prompt_size = len(prompt_payload["full_combined_prompt"])

        # 5. Append user message to memory
        self.memory.store_history(cid, "user", message)

        # 6. Send request to Groq Engine Client & 7. Receive AI response
        result = await self.client.generate(
            prompt=prompt_payload["user_prompt"],
            system_prompt=prompt_payload["system_prompt"],
            temperature=temperature
        )

        reply_text = result.get("reply", "Hello from FastAPI")

        # 8. Append assistant response to memory & retrieve messageId
        assistant_msg = self.memory.store_history(cid, "assistant", reply_text)
        mid = assistant_msg.get("message_id", self.memory.conv_mgr.create_message_id())

        # Calculate history length
        history_msgs = self.memory.load_history(cid)
        history_length = len(history_msgs)

        # Extract metrics
        latency_ms = result.get("latency_ms", 15.0)
        prompt_tokens = result.get("prompt_tokens", 0)
        completion_tokens = result.get("completion_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens
        error_msg = result.get("error", None)

        # 9. Conversation Logger Execution
        log_conversation(
            conversation_id=cid,
            message_id=mid,
            prompt_size=prompt_size,
            execution_time_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            error=error_msg
        )

        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

        processing_time = f"{max(int(latency_ms), 15)}ms"

        return {
            "reply": reply_text,
            "conversation_id": cid,
            "message_id": mid,
            "model": result.get("model", settings.MODEL_NAME),
            "historyLength": history_length,
            "usage": usage,
            "service": "Python AI Service",
            "version": settings.VERSION,
            "processingTime": processing_time,
            "fallback": result.get("fallback", False)
        }

ai_service = AIServiceManager()
