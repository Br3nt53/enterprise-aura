# aura_v2/api/schemas.py
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from aura_v2.utils.time import to_utc

__all__ = [
    "DetectionInput",
    "TrackOutput",
    "TrackResponse",
    "TrackRequest",
]

# Env-driven behavior for timestamp normalization
DEV_OK = os.getenv("AURA_ACCEPT_NAIVE_TS") == "1"
DEFAULT_TZ = os.getenv("AURA_DEFAULT_TZ", "UTC")


class DetectionInput(BaseModel):
    timestamp: datetime
    position: Dict[str, float]
    confidence: float = Field(ge=0.0, le=1.0)
    sensor_id: str
    attributes: Optional[Dict[str, Any]] = None

    @field_validator("timestamp")
    @classmethod
    def _ensure_utc(cls, v: datetime) -> datetime:
        # Always return an aware UTC datetime (env toggles allowed for dev)
        return to_utc(v, dev_ok=DEV_OK, default_tz=DEFAULT_TZ)


class TrackOutput(BaseModel):
    id: str
    position: Dict[str, float]
    velocity: Dict[str, float]
    confidence: float
    status: str
    threat_level: int
    created_at: datetime
    updated_at: datetime


class TrackResponse(BaseModel):
    active_tracks: List[TrackOutput]
    new_tracks: List[TrackOutput]
    deleted_tracks: List[str]
    threats: List[Dict[str, Any]]
    processing_time_ms: float
    frame_id: int


class TrackRequest(BaseModel):
    # Use default_factory to avoid mutable default pitfalls
    radar_detections: List[DetectionInput] = Field(default_factory=list)
    camera_detections: List[DetectionInput] = Field(default_factory=list)
    lidar_detections: List[DetectionInput] = Field(default_factory=list)
    timestamp: Optional[datetime] = None

    @field_validator("timestamp")
    @classmethod
    def _ensure_req_ts_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        return to_utc(v, dev_ok=DEV_OK, default_tz=DEFAULT_TZ) if v else None
