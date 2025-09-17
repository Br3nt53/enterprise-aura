from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..domain.ports.sensor_port import SensorReading
else:
    SensorReading = Any  # type: ignore


from aura_v2.ml.model.inference import load_quality_model, score_reading


class DataQualityGate:
    def __init__(self, min_score: float):
        self.min_score = min_score
        self.model = load_quality_model()

    def accept(self, reading: "SensorReading") -> bool:
        s = score_reading(reading, self.model)
        return s >= self.min_score

    @classmethod
    def default(cls):
        return cls(min_score=0.5)
