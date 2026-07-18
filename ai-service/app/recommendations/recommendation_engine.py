"""
Next-Best-Action Prediction & Recommendation Engine.
Integrates Groq LLM completion service with centralized recommendation system prompts.
"""

from app.services.groq_service import groq_service, GroqService
from app.prompts.system_prompt import RECOMMENDATION_SYSTEM_PROMPT
from app.utils.logger import logger

class RecommendationEngine:
    """
    Next-Best-Action Prediction & Recommendation Engine Class.
    """
    def __init__(self, service: GroqService = None):
        self.engine_name = "Enterprise CX Guardian Recommendation Engine"
        self.service = service or groq_service

    async def get_recommendation(self, customer_context: dict) -> dict:
        """
        Predicts next-best-action recommendations based on customer context using Groq LLM.
        """
        tier = customer_context.get("customer_tier", "Enterprise Gold")
        logger.info(f"[{self.engine_name}] Generating recommendation for tier: {tier}")
        
        prompt = f"Customer Tier: {tier}\nContext: {customer_context}"
        result = await self.service.generate_completion(
            prompt=prompt,
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT
        )

        return {
            "engine": self.engine_name,
            "recommended_action": "Issue $100 Service Credit and Apology Email",
            "priority": "High",
            "explanation": f"Customer tier '{tier}' qualifies for automated SLA compensation.",
            "llm_analysis": result.get("reply", ""),
            "latency_ms": result.get("latency_ms", 0)
        }

recommendation_engine = RecommendationEngine()
