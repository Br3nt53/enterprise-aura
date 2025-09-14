from __future__ import annotations

import asyncio
import time
from typing import List

import pytest
import pytest_asyncio

from aura_v2.domain.entities import Track, TrackState
from aura_v2.domain.value_objects import Position3D, Velocity3D
from aura_v2.infrastructure.persistence.mongo_client import MongoProvider

pytest_plugins = ("pytest_asyncio",)
pytestmark = pytest.mark.asyncio


async def _wait_ready(timeout_s: int = 30) -> None:
    """Wait until MongoProvider.ping() succeeds or timeout."""
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            if await MongoProvider.ping():
                return
        except Exception as e:  # noqa: PERF203
            last_err = e
        await asyncio.sleep(0.25)
    if last_err:
        raise last_err
    raise TimeoutError("Mongo provider did not become ready in time")


@pytest_asyncio.fixture
async def ready() -> None:
    await _wait_ready()


async def test_save_perf(mongo_repository, ready) -> None:
    latencies_ms: List[float] = []
    for i in range(50):  # keep the loop modest for CI; adjust as needed
        track = Track(
            id=f"perf_track_{i}",
            state=TrackState(
                position=Position3D(x=float(i), y=2.0, z=3.0),
                velocity=Velocity3D(vx=0.1, vy=0.2, vz=0.3),
            ),
        )
        t0 = time.perf_counter()
        await mongo_repository.save(track)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(dt_ms)

    avg = sum(latencies_ms) / len(latencies_ms)
    assert avg <= 5.0, f"avg save latency {avg:.2f}ms exceeds 5ms budget"
