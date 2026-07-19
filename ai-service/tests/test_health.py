"""
FastAPI AI MicroService — Health & Monitoring Unit Tests.
Tests: /, /health, /health/live, /health/ready, /metrics
"""

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

HEADERS = {"Accept-Encoding": "identity"}


def test_root_ping():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["python"] == "running"
        assert "uptime" in data
    asyncio.run(_test())


def test_full_health():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health", headers=HEADERS)
        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "requests" in data
        assert "system" in data
    asyncio.run(_test())


def test_liveness_probe():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health/live", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    asyncio.run(_test())


def test_readiness_probe():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health/ready", headers=HEADERS)
        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data
        assert "database" in data
    asyncio.run(_test())


def test_application_metrics():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/metrics", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "requests" in data
        assert "latency" in data
        assert "system" in data
    asyncio.run(_test())
