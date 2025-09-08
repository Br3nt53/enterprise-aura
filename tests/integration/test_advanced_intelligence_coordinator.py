# aura_v2/tests/integration/test_advanced_intelligence_coordinator.py
import pytest
import logging

from ...application.coordinators.advanced_intelligence_coordinator import (
    AdvancedIntelligenceCoordinator,
)
from ...domain.entities import (
    Track,
    TrackState,
    Position3D,
    Velocity3D,
    Confidence,
    ThreatLevel,
)
from ...domain.value_objects import Collision
from ...infrastructure.persistence.in_memory import TrackHistoryRepository


# Mocks for dependencies
class MockThreatAnalyzer:
    def analyze(self, track: Track):
        if track.confidence.value > 0.9:
            return ThreatLevel.HIGH
        if track.confidence.value > 0.7:
            return ThreatLevel.MEDIUM
        return ThreatLevel.LOW


class MockCollisionPredictor:
    def predict(self, tracks: list[Track]):
        if len(tracks) < 2:
            return []
        return [
            Collision(
                track1=tracks[0],
                track2=tracks[1],
                time_to_collision=10.5,
                probability=0.88,
            )
        ]


@pytest.fixture
def coordinator():
    return AdvancedIntelligenceCoordinator(
        threat_analyzer=MockThreatAnalyzer(),
        collision_predictor=MockCollisionPredictor(),
        track_history=TrackHistoryRepository(),
        logger=logging.getLogger(__name__),
    )


@pytest.mark.asyncio
async def test_process_tracks_and_create_alerts(coordinator):
    """
    Tests that the coordinator correctly processes tracks, identifies priority threats,
    predicts collisions, and fuses them into a sorted list of tactical alerts.
    """
    tracks = [
        Track(
            id="1",
            state=TrackState(
                position=Position3D(x=1, y=1, z=1),
                velocity=Velocity3D(vx=1, vy=1, vz=1),
            ),
            confidence=Confidence(0.95),
        ),  # High Threat
        Track(
            id="2",
            state=TrackState(
                position=Position3D(x=2, y=2, z=2),
                velocity=Velocity3D(vx=1, vy=1, vz=1),
            ),
            confidence=Confidence(0.85),
        ),  # Medium Threat
        Track(
            id="3",
            state=TrackState(
                position=Position3D(x=3, y=3, z=3),
                velocity=Velocity3D(vx=1, vy=1, vz=1),
            ),
            confidence=Confidence(0.5),
        ),  # Low Threat
    ]

    alerts = await coordinator.process_tracks(tracks)

    # Assertions
    assert len(alerts) == 2  # Low threat track was filtered out
    assert alerts[0].urgency > alerts[1].urgency  # Alerts are sorted by urgency

    # Check the highest urgency alert
    high_alert = alerts[0]
    assert high_alert.threat.track.id in ["1", "2"]
    assert high_alert.threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.MEDIUM]
    assert high_alert.collision is not None
    assert high_alert.collision.time_to_collision == 10.5
