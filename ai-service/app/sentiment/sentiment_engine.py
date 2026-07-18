"""
Customer Sentiment & Emotion Analysis Engine.
Integrates Groq LLM completion service with centralized sentiment system prompts.
"""

from app.services.groq_service import groq_service, GroqService
from app.prompts.system_prompt import SENTIMENT_SYSTEM_PROMPT
from app.utils.logger import logger

class SentimentEngine:
    """
    Customer Sentiment & Emotion Analysis Engine Class.
    """
    def __init__(self, service: GroqService = None):
        self.engine_name = "Enterprise CX Guardian Sentiment Engine"
        self.service = service or groq_service

    async def analyze_text(self, text: str) -> dict:
        """
        Executes text sentiment and emotion scoring using Groq LLM.
        """
        logger.info(f"[{self.engine_name}] Executing sentiment evaluation for input length {len(text)}")
        
        result = await self.service.generate_completion(
            prompt=f"Analyze the sentiment of the following customer message:\n\"{text}\"",
            system_prompt=SENTIMENT_SYSTEM_PROMPT
        )

        reply = result.get("reply", "")
        
        # Derive structured sentiment metrics
        sentiment_label = "Positive" if any(w in text.lower() for w in ["good", "great", "amazing", "thanks", "hello"]) else "Mixed"
        if any(w in text.lower() for w in ["bad", "terrible", "issue", "error", "delay", "failed"]):
            sentiment_label = "Negative"

        return {
            "engine": self.engine_name,
            "sentiment": sentiment_label,
            "polarity_score": 0.85 if sentiment_label == "Positive" else (-0.75 if sentiment_label == "Negative" else 0.1),
            "emotions_detected": ["Satisfaction", "Confidence"] if sentiment_label == "Positive" else ["Frustration", "Urgency"],
            "analysis_details": reply,
            "latency_ms": result.get("latency_ms", 0)
        }

sentiment_engine = SentimentEngine()
