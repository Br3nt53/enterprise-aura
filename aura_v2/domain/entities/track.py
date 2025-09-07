# aura_v2/domain/entities/track.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from ..value_objects import Position3D, Velocity3D, Confidence


class TrackStatus(str, Enum):
    TENTATIVE = "tentative"
    ACTIVE = "active"
    LOST = "lost"
    DELETED = "deleted"


class ThreatLevel(int, Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass(slots=True)  # CRITICAL FIX: `frozen=True` has been removed.
class TrackState:
    """Represents the dynamic, mutable state of a track."""

    position: Position3D
    velocity: Velocity3D


@dataclass
class Track:
    """Represents a tracked object over time."""

    id: str
    state: TrackState
    status: TrackStatus = TrackStatus.TENTATIVE
    confidence: Confidence = field(default_factory=lambda: Confidence(1.0))
    threat_level: ThreatLevel = ThreatLevel.LOW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hits: int = 1
    missed: int = 0

    def update(self, detection, score: float) -> None:
        """Updates the track's state with a new detection."""
        self.state.position = detection.position
        self.confidence = Confidence(score)
        self.missed = 0
        self.hits += 1
        self.updated_at = detection.timestamp
        if self.status == TrackStatus.TENTATIVE and self.hits >= 3:
            self.status = TrackStatus.ACTIVE

    def mark_missed(self) -> None:
        """Increments the missed counter for the track."""
        self.missed += 1
        if self.missed > 5:  # More forgiving threshold
            self.status = TrackStatus.LOST
