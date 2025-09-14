from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from aura_v2.infrastructure.persistence.mongo import MongoTrackRepository
from aura_v2.infrastructure.persistence.mongo_client import MongoProvider

pytestmark = pytest.mark.asyncio


def _env_uri() -> str:
    # CI service exposes Mongo on localhost; keep this as the default.
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")


def _env_db() -> str:
    return os.getenv("MONGO_DB", "aura_ci")


async def _wait_ready(client: AsyncIOMotorClient, *, timeout: float = 20.0) -> None:
    """Poll ping until server is reachable or timeout."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        try:
            await client.admin.command("ping")
            return
        except Exception:
            if loop.time() >= deadline:
                raise RuntimeError("Mongo not reachable") from None
            await asyncio.sleep(0.5)


@pytest_asyncio.fixture
async def mongo_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[MongoTrackRepository, None]:
    """Clean MongoTrackRepository bound to the CI/local DB; drops data on teardown."""
    uri = _env_uri()
    db_name = _env_db()

    # Ensure the repo/provider read the intended env vars.
    monkeypatch.setenv("MONGO_URI", uri)
    monkeypatch.setenv("MONGO_DB", db_name)

    # Sanity: ensure server is up before constructing the repo
    sanity_client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
    await _wait_ready(sanity_client)

    # Initialize the shared provider used by the repo implementation (env-driven)
    MongoProvider.init()

    repo = MongoTrackRepository()  # ctor takes no args; uses MongoProvider + env
    await repo.delete_all()
    try:
        yield repo
    finally:
        try:
            await repo.delete_all()
        finally:
            sanity_client.close()
