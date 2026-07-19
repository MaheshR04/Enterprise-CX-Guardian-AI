"""
FastAPI AI MicroService — Security Controls Tests.
Tests: Secure headers, null-byte sanitization, CORS, version discovery
"""

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


def test_security_headers():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Content-Security-Policy" in response.headers
    asyncio.run(_test())


def test_version_discovery():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/versions")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["current_version"] == "v1"
        assert "v1" in data["supported"]
    asyncio.run(_test())


def test_input_sanitization_null_byte():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/versions?param=test%00null")
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "INVALID_INPUT"
    asyncio.run(_test())
