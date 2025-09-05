# aura_v2/domain/entities/detection.py
from dataclasses import dataclass
from typing import Optional, NewType
from datetime import datetime

TrackID = NewType('TrackID', str)
SensorID = NewType('SensorID', str)
Confidence = NewType('Confidence', float)

@dataclass(frozen=True)
class Position:
    """Value object for 3D position"""
    x: float
    y: float
    z: float = 0.0
    
    def distance_to(self, other: 'Position') -> float:
        return ((self.x - other.x)**2 + 
                (self.y - other.y)**2 + 
                (self.z - other.z)**2) ** 0.5

@dataclass(frozen=True)
class Velocity:
    """Value object for velocity"""
    vx: float
    vy: float
    vz: float = 0.0
    
    @property
    def magnitude(self) -> float:
        return (self.vx**2 + self.vy**2 + self.vz**2) ** 0.5

@dataclass
class Detection:
    """Domain entity for a single detection"""
    timestamp: datetime
    position: Position
    confidence: Confidence
    sensor_id: Optional[SensorID] = None
    attributes: dict = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be in [0,1], got {self.confidence}")