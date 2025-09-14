# aura_v2/domain/services/threat_analysis.py
from abc import ABC, abstractmethod

from ...domain.entities.track import ThreatLevel, Track


class ThreatAnalyzer(ABC):
    """Abstract base class for threat analysis strategies."""

    @abstractmethod
    def analyze(self, track: Track) -> ThreatLevel:
        """Analyzes a track and returns a threat level."""
        pass
