from __future__ import annotations

import asyncio
import time

import pytest
import pytest_asyncio

from aura_v2.infrastructure.persistence.mongo_client import MongoProvider

pytest_plugins = ("pytest_asyncio",)
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def ready() -> None:
    # Reuse the same readiness check as other tests
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            if await MongoProvider.ping():
                return
        except Exception:
            pass
        await asyncio.sleep(0.25)
    raise TimeoutError("Mongo provider did not become ready in time")


async def test_ttls_exist(ready) -> None:
    """Smoke check that TTL indexes are created (names/fields may vary by impl)."""
    db = MongoProvider.db()
    # Look for at least one TTL index in any collection
    found_ttl = False
    for name in await db.list_collection_names():
        idx_info = await db[name].index_information()
        if any("expireAfterSeconds" in v for v in idx_info.values()):
            found_ttl = True
            break
    assert found_ttl, "Expected at least one TTL index to be present"
