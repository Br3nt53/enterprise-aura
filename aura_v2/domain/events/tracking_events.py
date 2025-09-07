# aura_v2/domain/events/tracking_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..entities import Detection, Track
from ..value_objects import TrackID


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events"""

    occurred_at: datetime
    aggregate_id: str


@dataclass(frozen=True)
class TrackCreated(DomainEvent):
    track_id: TrackID
    initial_detection: Detection
    version: int = 1


@dataclass(frozen=True)
class TrackUpdated(DomainEvent):
    track_id: TrackID
    detection: Detection
    confidence: float
    version: int = 1


@dataclass(frozen=True)
class TrackDeleted(DomainEvent):
    track_id: TrackID
    reason: str
    version: int = 1


@dataclass(frozen=True)
class TracksFragmented(DomainEvent):
    """Indicates a track fragmentation occurred"""

    original_track_id: TrackID
    fragment_track_id: TrackID
    gap_frames: int
    version: int = 1