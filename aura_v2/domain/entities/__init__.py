from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, TypedDict, Union

from pydantic import BaseModel, Field, validator


# ---- Basic types ----

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrackStatus(str, Enum):
    ACTIVE = "active"
    LOST = "lost"
    ENDED = "ended"


TrackID = Union[int, str]


class Position3D(BaseModel):
    x: float
    y: float
    z: float = 0.0


class Velocity3D(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Covariance(BaseModel):
    # minimal diagonal covariance representation for stubbing
    xx: float = 1.0
    yy: float = 1.0
    zz: float = 1.0


class BoundingBox(BaseModel):
    # xywh in pixels (minimal stub)
    x: float
    y: float
    w: float
    h: float


Confidence = float


# ---- Detections & Tracks ----

class Detection(BaseModel):
    timestamp: datetime
    position: Position3D
    confidence: Confidence = Field(ge=0.0, le=1.0, default=1.0)
    sensor_id: Optional[str] = None
    attributes: Dict[str, Union[int, float, str]] = {}
    bbox: Optional[BoundingBox] = None

    @validator("timestamp", pre=True)
    def _parse_ts(cls, v):
        if isinstance(v, str):
            # allow ISO-8601 strings
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class Track(BaseModel):
    track_id: TrackID
    position: Position3D
    velocity: Velocity3D = Velocity3D()
    status: TrackStatus = TrackStatus.ACTIVE
    threat_level: ThreatLevel = ThreatLevel.LOW
    confidence: Confidence = 1.0
    last_update: Optional[datetime] = None


# ---- Optional higher-level structs (used by tests/pipeline) ----

class TrackingHistoryPoint(BaseModel):
    timestamp: datetime
    position: Position3D
    confidence: Confidence = 1.0


class TrackingTimeline(BaseModel):
    points: List[TrackingHistoryPoint] = []


class DomainEvent(BaseModel):
    name: str
    payload: Dict[str, Union[str, int, float, dict]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CollisionWarning(BaseModel):
    track_id: TrackID
    probability: float = Field(ge=0.0, le=1.0, default=0.0)
    horizon_seconds: float = 1.0


class ThreatAssessment(BaseModel):
    track_id: TrackID
    level: ThreatLevel
    rationale: Optional[str] = None


__all__ = [
    "ThreatLevel",
    "TrackStatus",
    "TrackID",
    "Position3D",
    "Velocity3D",
    "Covariance",
    "BoundingBox",
    "Confidence",
    "Detection",
    "Track",
    "TrackingHistoryPoint",
    "TrackingTimeline",
    "DomainEvent",
    "CollisionWarning",
    "ThreatAssessment",
]
