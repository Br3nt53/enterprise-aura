"""
Domain track entities and state.

Tracks represent hypotheses about moving objects that persist over time.  Each
track maintains its own state estimate (position and velocity), status
indicating whether it is tentative, active, lost or deleted, threat level
based on estimated behaviour, and confidence.  Tracks are updated when
associated with new detections and decay when missed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from ..value_objects import Position3D, Velocity3D, Confidence

class TrackStatus(str, Enum):
    """Possible lifecycle states of a track."""
    TENTATIVE = "tentative"
    ACTIVE = "active"
    LOST = "lost"
    DELETED = "deleted"

class ThreatLevel(int, Enum):
    """Threat level of a track, increasing from low (0) to critical (3)."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass(frozen=True, slots=True)
class TrackState:
    """State of a track consisting of position and velocity."""
    position: Position3D
    velocity: Velocity3D

@dataclass
class Track:
    """A track representing a moving object hypothesis."""
    id: str
    state: TrackState
    status: TrackStatus = TrackStatus.TENTATIVE
    confidence: Confidence = field(default_factory=lambda: Confidence(1.0))
    threat_level: ThreatLevel = ThreatLevel.LOW
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    hits: int = 1  # number of times associated with a detection
    missed: int = 0  # consecutive misses

    def update(self, detection: "Detection", score: float) -> None:
        """Update track state and metrics given a matched detection.

        The detection's position is used as the new state position, velocity
        is estimated from the difference over time if possible.  Confidence
        is updated as a weighted combination of previous confidence and score.
        """
        dt_seconds = (detection.timestamp - self.updated_at).total_seconds()
        if dt_seconds > 0:
            dx = detection.position.x - self.state.position.x
            dy = detection.position.y - self.state.position.y
            dz = detection.position.z - self.state.position.z
            vx = dx / dt_seconds
            vy = dy / dt_seconds
            vz = dz / dt_seconds
        else:
            vx = self.state.velocity.vx
            vy = self.state.velocity.vy
            vz = self.state.velocity.vz

        self.state = TrackState(position=detection.position, velocity=Velocity3D(vx, vy, vz))

        # Update confidence using exponential smoothing
        alpha = 0.5
        new_conf = alpha * float(self.confidence) + (1 - alpha) * score
        self.confidence = Confidence(min(1.0, max(0.0, new_conf)))

        # Reset missed count and increment hits
        self.missed = 0
        self.hits += 1

        # Update timestamps
        self.updated_at = detection.timestamp

        # Update threat level
        self.threat_level = self.assess_threat()

        # Promote from tentative to active if sufficient hits
        if self.status == TrackStatus.TENTATIVE and self.hits >= 3:
            self.status = TrackStatus.ACTIVE

    def mark_missed(self) -> None:
        """Mark the track as missed for the current frame."""
        self.missed += 1
        if self.missed > 0 and self.status == TrackStatus.ACTIVE:
            self.status = TrackStatus.LOST

    @property
    def time_since_update(self) -> int:
        """Number of consecutive frames since last update."""
        return self.missed

    def assess_threat(self) -> ThreatLevel:
        """Simple threat assessment based on speed."""
        speed = self.state.velocity.magnitude
        if speed > 50:
            return ThreatLevel.CRITICAL
        elif speed > 30:
            return ThreatLevel.HIGH
        elif speed > 10:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
