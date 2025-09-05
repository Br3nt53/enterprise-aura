# aura_v2/domain/entities/track.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import numpy as np

from ..value_objects import (
    TrackID, Position3D, Velocity3D, 
    Covariance, BoundingBox, Confidence
)

class TrackStatus(Enum):
    TENTATIVE = "tentative"
    CONFIRMED = "confirmed"
    DELETED = "deleted"

class ThreatLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TrackState:
    """Represents the kinematic state of a tracked object"""
    position: Position3D
    velocity: Velocity3D
    acceleration: Optional[np.ndarray] = None
    covariance: Optional[Covariance] = None
    
    def predict(self, dt: float) -> 'TrackState':
        """Predict future state using motion model"""
        # State transition matrix
        F = np.eye(6)
        F[0:3, 3:6] = np.eye(3) * dt
        
        # Process noise
        Q = np.eye(6) * 0.1
        
        # Predict state
        x = np.hstack([self.position.to_array(), self.velocity.to_array()])
        x_pred = F @ x
        
        # Predict covariance
        P_pred = F @ self.covariance.matrix @ F.T + Q if self.covariance else None
        
        return TrackState(
            position=Position3D.from_array(x_pred[0:3]),
            velocity=Velocity3D.from_array(x_pred[3:6]),
            covariance=Covariance(P_pred) if P_pred is not None else None
        )

@dataclass
class Track:
    """Core domain entity representing a tracked object"""
    id: TrackID
    state: TrackState
    status: TrackStatus
    confidence: Confidence
    created_at: datetime
    updated_at: datetime
    
    # Track characteristics
    classification: Optional[str] = None  # "person", "vehicle", "drone"
    threat_level: ThreatLevel = ThreatLevel.NONE
    
    # Motion history
    trajectory: List[Position3D] = field(default_factory=list)
    measurements: List['Detection'] = field(default_factory=list)
    
    # Appearance features (for re-identification)
    appearance_descriptor: Optional[np.ndarray] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Track quality metrics
    hits: int = 0
    age: int = 0
    time_since_update: int = 0
    
    def update(self, detection: 'Detection', match_score: float) -> None:
        """Update track with new detection"""
        self.measurements.append(detection)
        self.trajectory.append(detection.position)
        self.updated_at = detection.timestamp
        self.hits += 1
        self.time_since_update = 0
        
        # Update confidence based on match quality
        self.confidence = Confidence(
            min(0.99, self.confidence.value * 0.9 + match_score * 0.1)
        )
        
        # Promote to confirmed if enough hits
        if self.status == TrackStatus.TENTATIVE and self.hits >= 3:
            self.status = TrackStatus.CONFIRMED
    
    def mark_missed(self) -> None:
        """Mark track as missed in current frame"""
        self.time_since_update += 1
        self.age += 1
        
        # Decay confidence
        self.confidence = Confidence(self.confidence.value * 0.95)
        
        # Delete if too many misses
        if self.time_since_update > 30:
            self.status = TrackStatus.DELETED
    
    def assess_threat(self) -> ThreatLevel:
        """Assess threat level based on track characteristics"""
        threat_score = 0.0
        
        # Speed-based threat
        speed = self.state.velocity.magnitude()
        if speed > 30:  # m/s - very fast
            threat_score += 0.3
        
        # Trajectory-based threat (heading toward protected zone)
        if self._is_approaching_protected_zone():
            threat_score += 0.4
        
        # Classification-based threat
        if self.classification in ["drone", "missile"]:
            threat_score += 0.5
        
        # Convert to threat level
        if threat_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            return ThreatLevel.HIGH
        elif threat_score >= 0.4:
            return ThreatLevel.MEDIUM
        elif threat_score >= 0.2:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.NONE
    
    def _is_approaching_protected_zone(self) -> bool:
        """Check if track is heading toward protected area"""
        # This would check against defined protected zones
        return False  # Placeholder