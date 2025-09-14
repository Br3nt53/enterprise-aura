from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

TRACK_TTL_SECONDS = 5.0


@dataclass
class InternalState:
    x: float
    y: float
    vx: float
    vy: float
    P: float = 1.0  # Covariance scalar placeholder


@dataclass
class TrackState:
    id: str
    state: InternalState
    created_at: float
    updated_at: float
    measurements: int = 0

    @classmethod
    def new_from_reading(cls, r: "SensorReading") -> "TrackState":
        return cls(
            id=str(uuid.uuid4()),
            state=InternalState(x=r.x, y=r.y, vx=0.0, vy=0.0),
            created_at=time.time(),
            updated_at=time.time(),
            measurements=1,
        )

    def touch(self):
        self.updated_at = time.time()
        self.measurements += 1

    def delta_t(self) -> float:
        return max(1e-3, time.time() - self.updated_at)

    def is_expired(self) -> bool:
        return (time.time() - self.updated_at) > TRACK_TTL_SECONDS
