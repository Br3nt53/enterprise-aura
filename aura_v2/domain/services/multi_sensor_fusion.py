"""
Multi‑sensor fusion service.

Provides a basic fusion algorithm that combines detections from different
sensors based on their accuracy and detection confidence.  This
implementation uses a weighted average of positions, where the weight of
each detection is proportional to the inverse of the sensor's accuracy and
the detection's own confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np  # type: ignore

from ..entities.detection import Detection
from ..entities.track import Track, TrackState
from ..value_objects import Position3D, Velocity3D, Confidence

@dataclass(frozen=True, slots=True)
class SensorCharacteristics:
    """Defines the intrinsic properties of a sensor."""
    sensor_id: str
    accuracy: float  # metres (smaller is better)
    update_rate: float  # Hz
    detection_probability: float
    false_alarm_rate: float
    covariance: np.ndarray

class MultiSensorFusion:
    """Simple multi‑sensor fusion using weighted averaging."""

    def __init__(self, sensor_configs: Dict[str, SensorCharacteristics]):
        self.sensor_configs = sensor_configs

    def fuse(self, track: Track, detections: List[Detection]) -> Tuple[Track, float]:
        """Fuse multiple detections into a unified track state.

        :param track: The track to update.
        :param detections: List of detections associated with the track in the current frame.
        :returns: (updated track, fusion confidence)
        """
        if not detections:
            # no detections: degrade confidence slightly
            degraded = float(track.confidence) * 0.95
            track.confidence = Confidence(degraded)
            return track, degraded

        weights: List[float] = []
        positions: List[np.ndarray] = []

        for det in detections:
            base_id = (det.sensor_id or "").split("_")[0]
            cfg = self.sensor_configs.get(base_id)
            acc = cfg.accuracy if cfg else 1.0
            weight = (1.0 / acc) * det.confidence.value
            weights.append(weight)
            positions.append(det.position.to_array())

        weights_array = np.array(weights, dtype=float)
        weights_array /= weights_array.sum()
        positions_array = np.array(positions, dtype=float)
        fused = weights_array @ positions_array  # shape (3,)

        # Update track position; velocity remains unchanged for now
        track.state = TrackState(position=Position3D(*fused.tolist()), velocity=track.state.velocity)

        # Fusion confidence: combine sensor detection probabilities and false alarm rates
        conf_val = 1.0
        for det in detections:
            base_id = (det.sensor_id or "").split("_")[0]
            cfg = self.sensor_configs.get(base_id)
            if cfg:
                conf_val *= cfg.detection_probability * (1.0 - cfg.false_alarm_rate) * det.confidence.value
            else:
                conf_val *= det.confidence.value
        conf_val = min(0.99, conf_val)
        track.confidence = Confidence(conf_val)
        return track, conf_val
