"""
FastAPI AI MicroService — Dashboard Endpoints Tests.
Tests: /api/v1/dashboard/* (health, model-usage, conversations, users, documents, summary)
"""

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.auth_service import auth_service


def get_auth_headers():
    token = auth_service.create_access_token({"sub": "usr_test_admin", "email": "admin@test.com", "role": "ADMIN"})
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_summary():
    async def _test():
        headers = get_auth_headers()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "system_status" in data["data"]
    asyncio.run(_test())


def test_dashboard_system_health():
    async def _test():
        headers = get_auth_headers()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/health", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cpu_percent" in data["data"]["system"]
    asyncio.run(_test())


def test_dashboard_model_usage():
    async def _test():
        headers = get_auth_headers()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/model-usage", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "active_model" in data["data"]
    asyncio.run(_test())


def test_dashboard_conversations():
    async def _test():
        headers = get_auth_headers()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/conversations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ACTIVE" in data["data"]["status_breakdown"]
    asyncio.run(_test())


def test_dashboard_users():
    async def _test():
        headers = get_auth_headers()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "role_breakdown" in data["data"]
    asyncio.run(_test())


def test_dashboard_documents():
    async def _test():
        headers = get_auth_headers()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/documents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "knowledge_base" in data["data"]
    asyncio.run(_test())
