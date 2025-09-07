# aura_v2/domain/value_objects/tactical_alert.py
from dataclasses import dataclass
from typing import Optional
from .threat import Threat
from .collision import Collision

@dataclass(frozen=True)
class TacticalAlert:
    """
    Represents a fused intelligence alert, combining threat and collision data.
    """
    threat: Threat
    collision: Optional[Collision] = None
    urgency: float  # A calculated score from 0.0 to 1.0