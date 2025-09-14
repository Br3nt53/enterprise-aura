# aura_v2/tests/application/services/test_threat_analyzer.py
import pytest

from aura_v2.application.services.threat_analyzer import BasicThreatAnalyzer
from aura_v2.domain.entities import (
    Confidence,
    Position3D,
    ThreatLevel,
    Track,
    TrackState,
    Velocity3D,
)


@pytest.fixture
def threat_analyzer():
    return BasicThreatAnalyzer()


def test_analyze_high_threat(threat_analyzer):
    track = Track(
        id="1",
        state=TrackState(
            position=Position3D(x=1, y=1, z=1), velocity=Velocity3D(vx=1, vy=1, vz=1)
        ),
        confidence=Confidence(0.95),
    )
    assert threat_analyzer.analyze(track) == ThreatLevel.HIGH


def test_analyze_medium_threat(threat_analyzer):
    track = Track(
        id="1",
        state=TrackState(
            position=Position3D(x=1, y=1, z=1), velocity=Velocity3D(vx=1, vy=1, vz=1)
        ),
        confidence=Confidence(0.8),
    )
    assert threat_analyzer.analyze(track) == ThreatLevel.MEDIUM


def test_analyze_low_threat(threat_analyzer):
    track = Track(
        id="1",
        state=TrackState(
            position=Position3D(x=1, y=1, z=1), velocity=Velocity3D(vx=1, vy=1, vz=1)
        ),
        confidence=Confidence(0.5),
    )
    assert threat_analyzer.analyze(track) == ThreatLevel.LOW
