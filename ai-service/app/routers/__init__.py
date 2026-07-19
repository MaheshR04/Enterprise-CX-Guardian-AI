from app.routers.api_v1 import api_v1_router
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.reasoning import router as reasoning_router
from app.routers.sentiment import router as sentiment_router
from app.routers.recommendation import router as recommendation_router
from app.routers.analyze import router as analyze_router

from app.routers.dashboard import router as dashboard_router

__all__ = [
    "api_v1_router",
    "health_router",
    "auth_router",
    "chat_router",
    "dashboard_router",
    "reasoning_router",
    "sentiment_router",
    "recommendation_router",
    "analyze_router"
]
