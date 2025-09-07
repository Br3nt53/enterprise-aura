import asyncio
from httpx import AsyncClient
from aura_v2.main import get_app


async def _probe():
    app = get_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_health():
    asyncio.run(_probe())
