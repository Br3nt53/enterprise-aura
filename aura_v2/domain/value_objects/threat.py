from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import ThreatLevel, Track


@dataclass(frozen=True)
class Threat:
    track: "Track"
    threat_level: "ThreatLevel"
    confidence: float
