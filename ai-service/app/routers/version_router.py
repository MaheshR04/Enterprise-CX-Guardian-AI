"""
Enterprise CX Guardian AI — API Version Registry (FastAPI)
==========================================================

Version routing architecture:
  /api/v1  — Current stable version (full feature set)
  /api/v2  — Future version stub (ready to extend)

Design Principles:
  • Controllers depend on VersionRouter, not on FastAPI directly
  • Each version is a self-contained APIRouter module
  • Version deprecation warnings can be added per-version
  • Mount both versions from main.py → zero breaking changes on upgrade

To add v3:
  1. Create app/routers/api_v3.py
  2. Import and register it in register_all_versions() below
  3. Add CURRENT_VERSION = "v3" when ready to promote
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logger import logger

# ── Version metadata ───────────────────────────────────────────────
CURRENT_VERSION    = "v1"
SUPPORTED_VERSIONS = ["v1"]       # Update when v2 is ready
DEPRECATED_VERSIONS: list = []    # e.g. ["v1"] when v2 becomes stable

# ══════════════════════════════════════════════════════════════════
# Master APIRouter — mounts all versions
# ══════════════════════════════════════════════════════════════════

api_router = APIRouter()


def register_all_versions() -> None:
    """
    Imports and mounts all versioned sub-routers onto api_router.
    Called once from main.py during application startup.

    Import is done lazily (inside function) to avoid circular imports
    and to keep version modules fully independent of each other.
    """
    # ── v1 ─────────────────────────────────────────────────────────
    from app.routers.versions.v1 import api_v1_router
    api_router.include_router(api_v1_router, prefix="/v1")
    logger.info("[API Version] Registered: /api/v1 — stable")

    # ── v2 (stub — uncomment when v2 routers are implemented) ──────
    # from app.routers.versions.v2 import api_v2_router
    # api_router.include_router(api_v2_router, prefix="/v2")
    # logger.info("[API Version] Registered: /api/v2 — beta")

    logger.info(
        f"[API Version] Current: {CURRENT_VERSION} | "
        f"Supported: {SUPPORTED_VERSIONS} | "
        f"Deprecated: {DEPRECATED_VERSIONS or 'none'}"
    )


# Automatically register versions at module load time
register_all_versions()


# ══════════════════════════════════════════════════════════════════
# Version Info Endpoint — GET /api/versions
# ══════════════════════════════════════════════════════════════════

@api_router.get(
    "/versions",
    tags=["API Versioning"],
    summary="API Version Discovery",
    description=(
        "Returns all supported API versions, the current stable version, "
        "any deprecated versions, and their changelog URLs.\n\n"
        "Use this endpoint to build version-aware API clients."
    )
)
async def get_api_versions() -> JSONResponse:
    return JSONResponse(content={
        "success":           True,
        "current_version":   CURRENT_VERSION,
        "supported":         SUPPORTED_VERSIONS,
        "deprecated":        DEPRECATED_VERSIONS,
        "base_url":          "/api",
        "versions": {
            "v1": {
                "status":     "stable",
                "prefix":     "/api/v1",
                "released":   "2026-07-01",
                "deprecated": False,
                "sunset_date": None,
                "endpoints": {
                    "auth":           "/api/v1/auth",
                    "chat":           "/api/v1/chat",
                    "conversations":  "/api/v1/conversations",
                    "reasoning":      "/api/v1/reasoning",
                    "sentiment":      "/api/v1/sentiment",
                    "recommendation": "/api/v1/recommendation",
                    "analyze":        "/api/v1/analyze"
                }
            },
            "v2": {
                "status":     "planned",
                "prefix":     "/api/v2",
                "released":   None,
                "deprecated": False,
                "sunset_date": None,
                "note":       "v2 is under development. Not available yet."
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
