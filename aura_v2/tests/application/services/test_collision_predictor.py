# aura_v2/tests/application/services/test_collision_predictor.py
import pytest
from aura_v2.application.services.collision_predictor import BasicCollisionPredictor
from aura_v2.domain.entities import Track, TrackState, Position3D, Velocity3D, Confidence

@pytest.fixture
def collision_predictor():
    return BasicCollisionPredictor()

def test_predict_no_collisions(collision_predictor):
    tracks = [
        Track(id="1", state=TrackState(position=Position3D(x=1, y=1, z=1), velocity=Velocity3D(vx=1, vy=1, vz=1)), confidence=Confidence(0.9)),
        Track(id="2", state=TrackState(position=Position3D(x=10, y=10, z=10), velocity=Velocity3D(vx=1, vy=1, vz=1)), confidence=Confidence(0.9))
    ]
    assert collision_predictor.predict(tracks) == []