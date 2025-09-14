import asyncio

from httpx import ASGITransport, AsyncClient

from aura_v2.main import get_app


async def _probe():
    app = get_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        j = r.json()
        assert j["status"] == "ok"


def test_health():
    asyncio.run(_probe())
