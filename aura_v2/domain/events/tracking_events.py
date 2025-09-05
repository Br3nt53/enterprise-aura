# aura_v2/domain/events/tracking_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..entities import Track, Detection, TrackID

@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events"""
    occurred_at: datetime
    aggregate_id: str
    version: int = 1

@dataclass(frozen=True)
class TrackCreated(DomainEvent):
    track_id: TrackID
    initial_detection: Detection

@dataclass(frozen=True)
class TrackUpdated(DomainEvent):
    track_id: TrackID
    detection: Detection
    confidence: float

@dataclass(frozen=True)
class TrackDeleted(DomainEvent):
    track_id: TrackID
    reason: str

@dataclass(frozen=True)
class TracksFragmented(DomainEvent):
    """Indicates a track fragmentation occurred"""
    original_track_id: TrackID
    fragment_track_id: TrackID
    gap_frames: int