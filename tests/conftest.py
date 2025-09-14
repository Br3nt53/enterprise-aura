from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from aura_v2.infrastructure.persistence.mongo import MongoTrackRepository
from aura_v2.infrastructure.persistence.mongo_client import MongoProvider

# All async tests/fixtures run on the same loop managed by pytest-asyncio
pytestmark = pytest.mark.asyncio

# Defaults suitable for docker-compose.mongo.yml in this repo
_DEFAULT_URI = "mongodb://root:example@mongo:27017/?authSource=admin&directConnection=true"
_DEFAULT_DB = "aura_test"


def _env_uri() -> str:
    return os.getenv("MONGO_URI", _DEFAULT_URI)


def _env_db() -> str:
    return os.getenv("MONGO_DB", _DEFAULT_DB)


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
from motor.motor_asyncio import AsyncIOMotorClient
from aura_v2.infrastructure.persistence import MongoTrackRepository

async def _wait_ready(client):
    for _ in range(20):
        try:
            await client.admin.command("ping")
            return
        except Exception:
            import asyncio; await asyncio.sleep(0.2)
    raise RuntimeError("Mongo not reachable")

import os, pytest
@pytest.fixture
async def mongo_repository():
    uri = os.getenv("MONGO_URI", "mongodb://root:example@mongo:27017/aura_test?authSource=admin")
    dbn = os.getenv("MONGO_DB", "aura_test")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
    await _wait_ready(client)
    repo = MongoTrackRepository(client, db_name=dbn)
    await repo.delete_all()
    try:
        yield repo
    finally:
        await repo.delete_all()

    # Ensure the repository reads the intended env vars
    monkeypatch.setenv("MONGO_URI", uri)
    monkeypatch.setenv("MONGO_DB", db_name)

    # Sanity: ensure server is up before constructing the repo
    sanity_client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
    await _wait_ready(sanity_client)

    # Initialize the shared provider used by the repo implementation
    MongoProvider.init()

    repo = MongoTrackRepository()  # ctor takes no args; uses MongoProvider + env
    try:
        yield repo
    finally:
        # Teardown: drop the entire test database the repo was using
        try:
            db = repo._collection.database  # type: ignore[attr-defined]
            await db.client.drop_database(db.name)
        finally:
            sanity_client.close()
