# aura_v2/domain/value_objects/threat.py
from dataclasses import dataclass
from ...domain.entities import Track, ThreatLevel

@dataclass(frozen=True)
class Threat:
    """Represents a potential threat."""
    track: Track
    threat_level: ThreatLevel
    confidence: float