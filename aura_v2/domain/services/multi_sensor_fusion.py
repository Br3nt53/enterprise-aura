from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from ..entities.detection import Detection
from ..entities.track import Track, TrackState
from ..value_objects import Position3D, Velocity3D, Confidence

@dataclass(frozen=True, slots=True)
class SensorCharacteristics:
    sensor_id: str
    accuracy: float
    update_rate: float
    detection_probability: float
    false_alarm_rate: float
    covariance: np.ndarray

class MultiSensorFusion:
    def __init__(self, sensor_configs: Dict[str, SensorCharacteristics]):
        self.sensor_configs = sensor_configs

    def fuse(self, track: Track, detections: List[Detection]) -> Tuple[Track, float]:
        if not detections:
            v = float(track.confidence) * 0.95
            track.confidence = Confidence(v)
            return track, v
        wts, pos = [], []
        for det in detections:
            key = (det.sensor_id or "").split("_")[0]
            acc = self.sensor_configs.get(key).accuracy if self.sensor_configs.get(key) else 1.0
            wts.append((1.0/acc) * det.confidence.value)
            pos.append(det.position.to_array())
        w = np.array(wts, float); w /= w.sum()
        fused = (w @ np.array(pos, float)).tolist()
        track.state = TrackState(Position3D(*fused), track.state.velocity)
        conf = 1.0
        for det in detections:
            key = (det.sensor_id or "").split("_")[0]
            cfg = self.sensor_configs.get(key)
            conf *= (cfg.detection_probability * (1.0 - cfg.false_alarm_rate) if cfg else 1.0) * det.confidence.value
        conf = min(0.99, conf)
        track.confidence = Confidence(conf)
        return track, conf
