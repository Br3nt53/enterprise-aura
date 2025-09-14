import os
from datetime import datetime

import pytest

from aura_v2.infrastructure.persistence.mongo_client import MongoProvider
from aura_v2.infrastructure.persistence.reader import iter_tracks
from aura_v2.infrastructure.persistence.schemas import TrackEvent
from aura_v2.infrastructure.persistence.writer import MongoWriter

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True, scope="module")
async def _mongo_setup():
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    os.environ.setdefault("MONGO_DB", "aura_test")
    MongoProvider.init()
    yield
    await MongoProvider.close()


async def test_roundtrip_track_event():
    ev = TrackEvent(
        ts=datetime.utcnow(),
        track_id="T1",
        assoc={"algo": "hungarian"},
        state={"v": [0, 0]},
    )
    await MongoWriter.write_track_event(ev)
    got = None
    async for d in iter_tracks():
        got = d
        break
    assert got is not None
    assert got["track_id"] == "T1"
    assert got["assoc"]["algo"] == "hungarian"
