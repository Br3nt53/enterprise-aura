from __future__ import annotations

import pytest

from aura_v2.domain.entities import Track, TrackState
from aura_v2.domain.value_objects import Position3D, Velocity3D

pytestmark = pytest.mark.asyncio


async def test_writer_reader_roundtrip(mongo_repository) -> None:
    t = Track(
        id="roundtrip-1",
        state=TrackState(
            position=Position3D(x=1.0, y=2.0, z=3.0),
            velocity=Velocity3D(vx=0.1, vy=0.2, vz=0.3),
        ),
    )

    await mongo_repository.save(t)
    got = await mongo_repository.get_by_id("roundtrip-1")

    assert got is not None
    assert got.id == t.id
    assert got.state.position.x == 1.0
