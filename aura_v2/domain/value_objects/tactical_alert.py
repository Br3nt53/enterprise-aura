# aura_v2/domain/value_objects/tactical_alert.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .collision import Collision
from .threat import Threat


@dataclass(frozen=True)
class TacticalAlert:
    """Single fused alert from threat/collision analysis."""

    threat: Threat
    collision: Optional[Collision] = None
    urgency: float = 0.0
