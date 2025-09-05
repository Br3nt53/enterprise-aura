# aura_v2/domain/entities/track.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from .detection import Detection, TrackID, Position, Velocity

@dataclass
class TrackState:
    """Represents the current state of a track"""
    position: Position
    velocity: Velocity
    covariance: Optional[np.ndarray] = None
    
    def predict(self, dt: float) -> 'TrackState':
        """Predict state after dt seconds"""
        new_position = Position(
            x=self.position.x + self.velocity.vx * dt,
            y=self.position.y + self.velocity.vy * dt,
            z=self.position.z + self.velocity.vz * dt
        )
        return TrackState(new_position, self.velocity, self.covariance)

@dataclass
class Track:
    """Domain entity representing a tracked object"""
    id: TrackID
    state: TrackState
    confidence: float
    created_at: datetime
    updated_at: datetime
    history: List[Detection] = field(default_factory=list)
    _is_confirmed: bool = False
    _is_deleted: bool = False
    
    def update(self, detection: Detection, association_score: float) -> None:
        """Update track with new detection"""
        self.history.append(detection)
        self.updated_at = detection.timestamp
        # Update state using Kalman filter or similar
        self._update_state(detection)
        self._update_confidence(association_score)
    
    def time_since_update(self, current_time: datetime) -> timedelta:
        return current_time - self.updated_at
    
    def mark_deleted(self) -> None:
        self._is_deleted = True
    
    @property
    def is_active(self) -> bool:
        return self._is_confirmed and not self._is_deleted