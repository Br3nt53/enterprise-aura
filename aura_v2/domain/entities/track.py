from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from ..value_objects import (
    TrackID,
    Position3D,
    Velocity3D,
    Confidence,
    Covariance,
    ThreatLevel,
)

__all__ = ["TrackState", "Track"]


class TrackState(str, Enum):
    ACTIVE = "active"
    LOST = "lost"
    ENDED = "ended"


class Track(BaseModel):
    id: TrackID = Field(default_factory=lambda: TrackID(0))
    state: TrackState = TrackState.ACTIVE
    position: Position3D
    velocity: Velocity3D = Field(default_factory=Velocity3D)
    confidence: Confidence = Field(default_factory=lambda: Confidence(value=1.0))
    covariance: Optional[Covariance] = None
    sensor_id: Optional[str] = None
    threat: ThreatLevel = ThreatLevel.LOW

    def is_active(self) -> bool:
        return self.state == TrackState.ACTIVE
