from dataclasses import dataclass
from typing import List, Protocol, Dict, Any
from ..entities import Detection, Track
from ..value_objects import TrackID


@dataclass
class TrackSet:
    id: TrackID
    tracks: List[Track]


@dataclass
class Metrics:
    mot_metrics: Dict[str, Any]


@dataclass
class EvaluationResult:
    is_success: bool
    metrics: Metrics
    details: Dict[str, Any]


class Tracker(Protocol):
    def update(self, detections: list[Detection]) -> TrackSet: ...


class Evaluation(Protocol):
    def evaluate(self, ground_truth: TrackSet, predictions: TrackSet) -> Metrics: ...
