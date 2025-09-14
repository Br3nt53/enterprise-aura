from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, Tuple


class Position2D(Protocol):
    def to_array(self) -> Any: ...


class TrackLike(Protocol):
    id: str
    state: Any  # refine once state shape is standardized

    @property
    def position(self) -> Tuple[float, float]: ...


class DetectionLike(Protocol):
    id: str
    position: Tuple[float, float]  # or a VO with to_array()
    bbox: Sequence[float]  # [x, y, w, h]
    score: float
    sensor: str
