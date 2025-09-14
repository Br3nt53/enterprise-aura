from dataclasses import dataclass

import numpy as np

from aura_v2.domain.association.hungarian_solver_refactored import HungarianAssociator
from aura_v2.domain.filters.ukf import UKF, UKFConfig


@dataclass
class MockTrack:
    id: str
    filter: UKF

    def __post_init__(self):
        self.filter.x[0, 0] = 0.0
        self.filter.x[1, 0] = 0.0

    @property
    def position(self):
        return (float(self.filter.x[0, 0]), float(self.filter.x[1, 0]))


@dataclass
class MockDetection:
    id: str
    position: tuple
    bbox: tuple
    score: float
    sensor: str = "cam"


def test_association_with_ukf_prediction():
    track = MockTrack(id="t1", filter=UKF(UKFConfig()))
    # Predict so state changes
    track.filter.predict()
    det = MockDetection(id="d1", position=(0.2, 0.1), bbox=(0.2, 0.1, 1, 1), score=0.9)

    associator = HungarianAssociator(
        weights={"iou": 0.4, "motion": 0.5, "confidence": 0.1}, max_cost=5.0
    )
    outcome = associator.associate([det], [track])
    assert len(outcome.matches) == 1
    match = outcome.matches[0]
    z = np.array([[det.position[0]], [det.position[1]]])
    pre = track.filter.x.copy()
    track.filter.update(z)
    post = track.filter.x
    assert (post - pre).any(), "State should update after measurement"
