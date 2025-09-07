# aura_v2/application/services/threat_analyzer.py
from ...domain.entities.track import Track, ThreatLevel
from ...domain.services.threat_analysis import ThreatAnalyzer

class BasicThreatAnalyzer(ThreatAnalyzer):
    """Basic threat analysis implementation"""
    
    def analyze(self, track: Track) -> ThreatLevel:
        """Analyzes a track and returns a threat level based on confidence and velocity."""
        confidence = float(track.confidence)
        velocity_magnitude = track.state.velocity.magnitude if track.state.velocity else 0.0
        
        # High threat: high confidence + high speed
        if confidence > 0.9 and velocity_magnitude > 15.0:
            return ThreatLevel.CRITICAL
        elif confidence > 0.85 and velocity_magnitude > 10.0:
            return ThreatLevel.HIGH
        elif confidence > 0.7 and velocity_magnitude > 5.0:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW