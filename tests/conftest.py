# tests/conftest.py
# pyright: reportMissingImports=false
from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from aura_v2.infrastructure.persistence.mongo import MongoTrackRepository

# All async tests run on the pytest-asyncio loop
pytestmark = pytest.mark.asyncio

# Defaults suitable for docker-compose.mongo.yml
_DEFAULT_URI = "mongodb://root:example@mongo:27017/?authSource=admin&directConnection=true"
_DEFAULT_DB = "aura_test"


async def _wait_ready(client: AsyncIOMotorClient, *, timeout: float = 10.0) -> None:
    """Poll ping until server is reachable or timeout."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        try:
            await client.admin.command("ping")
            return
        except Exception:
            if loop.time() >= deadline:
                raise RuntimeError("Mongo not reachable")
            await asyncio.sleep(0.2)


@pytest_asyncio.fixture
async def mongo_repository() -> AsyncGenerator[MongoTrackRepository, None]:
    uri = os.getenv("MONGO_URI", _DEFAULT_URI)
    dbn = os.getenv("MONGO_DB", _DEFAULT_DB)

    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    await _wait_ready(client)

    repo = MongoTrackRepository(client, db_name=dbn)

    # Ensure at least one TTL index exists for TTL tests
    try:
        await repo._collection.create_index("updated_at", expireAfterSeconds=3600)  # type: ignore[attr-defined]
    except Exception:
        pass

    await repo.delete_all()
    try:
        yield repo
    finally:
        try:
            await repo._collection.database.client.drop_database(dbn)  # type: ignore[attr-defined]
        finally:
            client.close()
