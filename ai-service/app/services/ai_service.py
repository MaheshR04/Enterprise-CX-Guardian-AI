"""
AI Service Manager for Enterprise CX Guardian AI Python FastAPI Microservice.

Executes the 10-step Chat Flow with full MongoDB persistence at every stage.
Controllers pass requests here — this service orchestrates all downstream
components: ConversationManager, MemptBuilder, GroqClient, and repositories.
"""

import uuid
from app.clients.groq_client import groq_client, GroqClient
from app.prompts.prompt_builder import prompt_builder, PromptBuilder
from app.conversation.conversation_manager import conversation_manager, ConversationManager
from app.repositories.interfaces import IPromptRepository, IUsageRepository
from app.repositories.factory import repository_factory
from app.core.config import settings
from app.core.logger import logger, log_conversation


class AIServiceManager:
    """
    Core AI Service Manager executing the 10-step Chat Flow
    with full MongoDB persistence at every stage.
    """

    def __init__(
        self,
        client:      GroqClient             = None,
        prompts:     PromptBuilder           = None,
        conv_mgr:    ConversationManager     = None,
        prompt_repo: IPromptRepository       = None,
        usage_repo:  IUsageRepository        = None
    ):
        self.client      = client      or groq_client
        self.prompts     = prompts     or prompt_builder
        self.conv_mgr    = conv_mgr    or conversation_manager
        # Resolve via factory — interface-typed for future backend swaps
        self.prompt_repo = prompt_repo or repository_factory.get_prompt_repo()
        self.usage_repo  = usage_repo  or repository_factory.get_usage_repo()

    async def process_message(
        self,
        message: str,
        conversation_id: str = None,
        temperature: float = None
    ) -> dict:
        """
        Executes the 10-step Chat Flow with MongoDB persistence.

        Step 1  — Receive request
        Step 2  — Create conversation if necessary
        Step 3  — Save user message to MongoDB
        Step 4  — Load previous history from MongoDB
        Step 5  — Build prompt (System + History + User Message)
        Step 6  — Send to Groq
        Step 7  — Receive AI response
        Step 8  — Save assistant response to MongoDB
        Step 9  — Save token usage to MongoDB
        Step 10 — Return standardized response payload
        """

        # ── Step 1: Receive request ──────────────────────────────────
        cid = conversation_id or f"conv_{uuid.uuid4()}"
        logger.info(f"[Chat Flow] Step 1 — Received request for conversation '{cid}'")

        # ── Step 2: Create conversation if necessary ─────────────────
        exists = await self.conv_mgr.conversation_exists(cid)
        if not exists:
            await self.conv_mgr.create_conversation(conversation_id=cid)
            logger.info(f"[Chat Flow] Step 2 — Created new conversation '{cid}' in MongoDB")
        else:
            logger.info(f"[Chat Flow] Step 2 — Conversation '{cid}' already exists")

        # ── Step 3: Save user message to MongoDB ─────────────────────
        await self.conv_mgr.save_message(
            conversation_id=cid,
            role="user",
            content=message
        )
        logger.info(f"[Chat Flow] Step 3 — Saved user message to MongoDB")

        # ── Step 4: Load previous history from MongoDB ───────────────
        formatted_history = await self.conv_mgr.format_history_for_prompt(cid)
        logger.info(f"[Chat Flow] Step 4 — Loaded conversation history from MongoDB")

        # ── Step 5: Build prompt ──────────────────────────────────────
        prompt_payload = self.prompts.build_chat_prompt(
            user_message=message,
            history_text=formatted_history,
            system_prompt_type="base"
        )
        prompt_size = len(prompt_payload["full_combined_prompt"])
        logger.info(f"[Chat Flow] Step 5 — Built prompt payload ({prompt_size} chars)")

        # ── Step 6: Send to Groq ──────────────────────────────────────
        logger.info(f"[Chat Flow] Step 6 — Sending prompt to Groq ({settings.MODEL_NAME})")
        result = await self.client.generate(
            prompt=prompt_payload["user_prompt"],
            system_prompt=prompt_payload["system_prompt"],
            temperature=temperature
        )

        # ── Step 7: Receive AI response ───────────────────────────────
        reply_text      = result.get("reply", "Hello from FastAPI")
        latency_ms      = result.get("latency_ms", 15.0)
        prompt_tokens   = result.get("prompt_tokens", 0)
        comp_tokens     = result.get("completion_tokens", 0)
        total_tokens    = prompt_tokens + comp_tokens
        model_name      = result.get("model", settings.MODEL_NAME)
        processing_time = f"{max(int(latency_ms), 15)}ms"
        error_msg       = result.get("error", None)
        logger.info(f"[Chat Flow] Step 7 — Received AI response ({comp_tokens} tokens, {processing_time})")

        # ── Step 8: Save assistant response to MongoDB ───────────────
        assistant_msg = await self.conv_mgr.save_message(
            conversation_id=cid,
            role="assistant",
            content=reply_text
        )
        mid = assistant_msg.get("message_id", f"msg_{uuid.uuid4()}")
        logger.info(f"[Chat Flow] Step 8 — Saved assistant response '{mid}' to MongoDB")

        # ── Step 9: Save token usage + prompt log to MongoDB ─────────
        await self.prompt_repo.insert_one(
            conversation_id=cid,
            system_prompt=prompt_payload["system_prompt"],
            user_prompt=prompt_payload["user_prompt"],
            final_prompt=prompt_payload["full_combined_prompt"],
            model=model_name
        )
        await self.usage_repo.insert_one(
            conversation_id=cid,
            model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=comp_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            processing_time=processing_time
        )
        logger.info(f"[Chat Flow] Step 9 — Saved prompt log and usage telemetry to MongoDB")

        # Structured telemetry log
        log_conversation(
            conversation_id=cid,
            message_id=mid,
            prompt_size=prompt_size,
            execution_time_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=comp_tokens,
            total_tokens=total_tokens,
            error=error_msg
        )

        # History length
        recent_msgs    = await self.conv_mgr.get_recent_messages(cid)
        history_length = len(recent_msgs)

        # ── Step 10: Return standardized response payload ─────────────
        logger.info(f"[Chat Flow] Step 10 — Returning response for conversation '{cid}'")
        return {
            "reply":           reply_text,
            "conversation_id": cid,
            "message_id":      mid,
            "model":           model_name,
            "historyLength":   history_length,
            "usage": {
                "prompt_tokens":     prompt_tokens,
                "completion_tokens": comp_tokens,
                "total_tokens":      total_tokens
            },
            "service":         "Python AI Service",
            "version":         settings.VERSION,
            "processingTime":  processing_time,
            "fallback":        result.get("fallback", False)
        }


ai_service = AIServiceManager()
