"""
API v1 — All stable production routes.
Mounted at: /api/v1

To create v2, copy this file to versions/v2.py and modify accordingly.
Services and controllers remain unchanged — only this file needs updating.
"""

from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.routers import auth, chat, conversation, reasoning, sentiment, recommendation, analyze, dashboard

api_v1_router = APIRouter()

# Public routes (no auth required)
api_v1_router.include_router(auth.router,           prefix="/auth",           tags=["v1 · Authentication"])

# Protected routes (JWT required)
api_v1_router.include_router(chat.router,           prefix="/chat",           tags=["v1 · Chat"],           dependencies=[Depends(get_current_user)])
api_v1_router.include_router(conversation.router,   prefix="/conversations",  tags=["v1 · Conversations"],  dependencies=[Depends(get_current_user)])
api_v1_router.include_router(dashboard.router,      prefix="/dashboard",      tags=["v1 · Dashboard"],      dependencies=[Depends(get_current_user)])
api_v1_router.include_router(reasoning.router,      prefix="/reasoning",      tags=["v1 · Reasoning"],      dependencies=[Depends(get_current_user)])
api_v1_router.include_router(sentiment.router,      prefix="/sentiment",      tags=["v1 · Sentiment"],      dependencies=[Depends(get_current_user)])
api_v1_router.include_router(recommendation.router, prefix="/recommendation", tags=["v1 · Recommendation"], dependencies=[Depends(get_current_user)])
api_v1_router.include_router(analyze.router,        prefix="/analyze",        tags=["v1 · Analysis"],       dependencies=[Depends(get_current_user)])
