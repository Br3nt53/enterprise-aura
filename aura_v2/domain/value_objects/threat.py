from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import Track, ThreatLevel
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import Track, ThreatLevel
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import Track, ThreatLevel
# aura_v2/domain/value_objects/threat.py
from dataclasses import dataclass
from ...domain.entities.track import Track, ThreatLevel


@dataclass(frozen=True)
class Threat:
    """Represents a potential threat."""

    track: "Track"
    threat_level: ThreatLevel
    confidence: float
