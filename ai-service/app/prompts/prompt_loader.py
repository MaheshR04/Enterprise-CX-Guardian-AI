"""
Centralized Prompt Loader for Enterprise CX Guardian AI.
Encapsulates system prompts and prompt template formatting. Zero hardcoded prompts in API routers.
"""

from app.prompts.system_prompt import (
    BASE_SYSTEM_PROMPT,
    SENTIMENT_SYSTEM_PROMPT,
    REASONING_SYSTEM_PROMPT,
    RECOMMENDATION_SYSTEM_PROMPT
)
from app.prompts.chat_prompt import CHAT_USER_TEMPLATE, CHAT_CONTEXT_TEMPLATE

class PromptLoader:
    """
    Centralized Prompt Manager Class.
    """
    @staticmethod
    def get_system_prompt(prompt_type: str = "base") -> str:
        """
        Retrieves a system prompt string by type identifier.
        """
        prompts_map = {
            "base": BASE_SYSTEM_PROMPT,
            "chat": BASE_SYSTEM_PROMPT,
            "sentiment": SENTIMENT_SYSTEM_PROMPT,
            "reasoning": REASONING_SYSTEM_PROMPT,
            "recommendation": RECOMMENDATION_SYSTEM_PROMPT
        }
        return prompts_map.get(prompt_type.lower(), BASE_SYSTEM_PROMPT)

    @staticmethod
    def format_chat_prompt(message: str, history: str = None) -> str:
        """
        Formats user message and conversation history into a structured prompt.
        """
        if history and history.strip():
            return CHAT_CONTEXT_TEMPLATE.format(history=history.strip(), message=message.strip())
        return CHAT_USER_TEMPLATE.format(message=message.strip())

    @staticmethod
    def format_sentiment_prompt(text: str) -> str:
        """
        Formats text for sentiment evaluation.
        """
        return f"Analyze the sentiment of the following customer text:\n\"{text.strip()}\""

    @staticmethod
    def format_reasoning_prompt(issue_description: str, ticket_id: str = None) -> str:
        """
        Formats issue context for root-cause reasoning evaluation.
        """
        tid = ticket_id or "CX-4912"
        return f"Ticket ID: {tid}\nIssue Description: {issue_description.strip()}"

    @staticmethod
    def format_recommendation_prompt(customer_tier: str, context: dict = None) -> str:
        """
        Formats customer context for next-best-action recommendation prediction.
        """
        ctx_str = f", Context: {context}" if context else ""
        return f"Customer Tier: {customer_tier}{ctx_str}"

prompt_loader = PromptLoader()
