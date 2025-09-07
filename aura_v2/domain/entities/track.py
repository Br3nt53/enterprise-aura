from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
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

@dataclass(frozen=True, slots=True)
class TrackState:
    position: Position3D
    velocity: Velocity3D

@dataclass
class Track:
    id: str
    state: TrackState
    status: TrackStatus = TrackStatus.TENTATIVE
    confidence: Confidence = field(default_factory=lambda: Confidence(1.0))
    threat_level: ThreatLevel = ThreatLevel.LOW
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    hits: int = 1
    missed: int = 0

    def update(self, detection, score: float) -> None:
        dt = (detection.timestamp - self.updated_at).total_seconds()
        if dt > 0:
            vx = (detection.position.x - self.state.position.x) / dt
            vy = (detection.position.y - self.state.position.y) / dt
            vz = (detection.position.z - self.state.position.z) / dt
        else:
            vx, vy, vz = self.state.velocity.vx, self.state.velocity.vy, self.state.velocity.vz
        self.state = TrackState(detection.position, Velocity3D(vx, vy, vz))
        alpha = 0.5
        new_conf = alpha * float(self.confidence) + (1 - alpha) * score
        self.confidence = Confidence(min(1.0, max(0.0, new_conf)))
        self.missed = 0
        self.hits += 1
        self.updated_at = detection.timestamp
        self.threat_level = self.assess_threat()
        if self.status == TrackStatus.TENTATIVE and self.hits >= 3:
            self.status = TrackStatus.ACTIVE

    def mark_missed(self) -> None:
        self.missed += 1
        if self.missed > 0 and self.status == TrackStatus.ACTIVE:
            self.status = TrackStatus.LOST

    @property
    def time_since_update(self) -> int:
        return self.missed

    def assess_threat(self) -> ThreatLevel:
        speed = self.state.velocity.magnitude
        if speed > 50: return ThreatLevel.CRITICAL
        if speed > 30: return ThreatLevel.HIGH
        if speed > 10: return ThreatLevel.MEDIUM
        return ThreatLevel.LOW
