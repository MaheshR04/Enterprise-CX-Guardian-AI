"""
API v2 — Future version stub.
Mounted at: /api/v2  (when register_all_versions enables it)

Instructions to activate v2:
  1. Add new route modules to this file
  2. Uncomment v2 in app/routers/version_router.py
  3. Set CURRENT_VERSION = "v2" in version_router.py when stable
  4. Add "v1" to DEPRECATED_VERSIONS to start sunset clock

Breaking changes in v2 (planned):
  - Streaming chat responses (SSE)
  - Batch conversation import
  - Enhanced analytics endpoints
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.middleware.auth import get_current_user

api_v2_router = APIRouter()


@api_v2_router.get(
    "/status",
    tags=["v2 · Status"],
    summary="API v2 Status",
    description="Confirms v2 is mounted and provides migration guidance from v1."
)
async def v2_status() -> JSONResponse:
    return JSONResponse(content={
        "version":         "v2",
        "status":          "development",
        "stable":          False,
        "message":         "API v2 is under active development. Use /api/v1 for production.",
        "migration_guide": "https://docs.enterprise-cx.ai/migration/v1-to-v2",
        "breaking_changes": [
            "Chat responses use Server-Sent Events (SSE) streaming",
            "Conversation IDs now use ULID format instead of UUID",
            "Pagination uses cursor-based instead of page-based"
        ]
    })

# Future v2 routes will be added here:
# api_v2_router.include_router(chat_v2.router, prefix="/chat", ...)
