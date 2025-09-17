from aura_v2.application.pipeline.fusion_pipeline_factory import build_default_pipeline


class SensorReading:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def test_new_tracks_created():
    pipe = build_default_pipeline()
    tracks = []
    readings = [SensorReading(1, 2), SensorReading(5, 6)]
    out = pipe.process_batch(readings, tracks)
    assert len(out) == 2


def test_association_reduces_new_tracks():
    pipe = build_default_pipeline()
    tracks = []
    pipe.process_batch([SensorReading(1, 2)], tracks)
    out2 = pipe.process_batch([SensorReading(1.2, 2.1)], tracks)
    assert len(out2) == 1
