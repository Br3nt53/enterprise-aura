# aura_v2/domain/entities/track.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any
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


@dataclass(slots=True)
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

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Track object to a dictionary for persistence."""
        return {
            "id": self.id,
            "state": {
                "position": {
                    "x": self.state.position.x,
                    "y": self.state.position.y,
                    "z": self.state.position.z,
                },
                "velocity": {
                    "vx": self.state.velocity.vx,
                    "vy": self.state.velocity.vy,
                    "vz": self.state.velocity.vz,
                },
            },
            "status": self.status.value,
            "confidence": float(self.confidence),
            "threat_level": self.threat_level.value,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": self.updated_at.isoformat().replace("+00:00", "Z"),
            "hits": self.hits,
            "missed": self.missed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Track":
        """Deserializes a dictionary into a Track object."""
        state_data = data["state"]
        position_data = state_data["position"]
        velocity_data = state_data["velocity"]

        track_state = TrackState(
            position=Position3D(
                x=position_data["x"],
                y=position_data["y"],
                z=position_data["z"],
            ),
            velocity=Velocity3D(
                vx=velocity_data["vx"],
                vy=velocity_data["vy"],
                vz=velocity_data["vz"],
            ),
        )

        # Handle different timestamp formats (float or string)
        def parse_timestamp(ts_data):
            if isinstance(ts_data, (int, float)):
                return datetime.fromtimestamp(ts_data, tz=timezone.utc)
            elif isinstance(ts_data, str):
                return datetime.fromisoformat(ts_data.replace("Z", "+00:00"))
            else:
                return datetime.now(timezone.utc)

        return cls(
            id=data["id"],
            state=track_state,
            status=TrackStatus(data["status"]),
            confidence=Confidence(data["confidence"]),
            threat_level=ThreatLevel(data["threat_level"]),
            created_at=parse_timestamp(data["created_at"]),
            updated_at=parse_timestamp(data["updated_at"]),
            hits=data["hits"],
            missed=data["missed"],
        )