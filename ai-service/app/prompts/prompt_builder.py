from typing import List, Dict, Optional
from app.prompts.system_prompt import BASE_SYSTEM_PROMPT
from app.prompts.prompt_loader import prompt_loader, PromptLoader

class PromptBuilder:
    """
    Prompt Builder Engine for Enterprise CX Guardian AI.
    Combines System Prompt, Conversation History, and Latest User Message into the final LLM prompt payload.
    Guarantees API Controllers never build prompts directly.
    """
    def __init__(self, loader: PromptLoader = None):
        self.loader = loader or prompt_loader

    def build_chat_prompt(
        self,
        user_message: str,
        history_text: Optional[str] = None,
        system_prompt_type: str = "base"
    ) -> dict:
        """
        Combines System Prompt, Conversation History, and User Message into a final prompt payload.
        """
        system_prompt = self.loader.get_system_prompt(system_prompt_type)
        formatted_user_prompt = self.loader.format_chat_prompt(user_message, history_text)

        return {
            "system_prompt": system_prompt,
            "user_prompt": formatted_user_prompt,
            "full_combined_prompt": f"System: {system_prompt}\n\nUser: {formatted_user_prompt}"
        }

    def build_messages_array(
        self,
        user_message: str,
        history_messages: Optional[List[Dict[str, str]]] = None,
        system_prompt_type: str = "base"
    ) -> List[Dict[str, str]]:
        """
        Builds a structured OpenAI/Groq message role dictionary array:
        [
          {"role": "system", "content": "..."},
          {"role": "user" / "assistant", "content": "..."},
          ...
          {"role": "user", "content": "latest message"}
        ]
        """
        system_prompt = self.loader.get_system_prompt(system_prompt_type)
        messages = [{"role": "system", "content": system_prompt}]

        if history_messages:
            for msg in history_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content and role in ["user", "assistant", "system"]:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_message.strip()})
        return messages

prompt_builder = PromptBuilder()
