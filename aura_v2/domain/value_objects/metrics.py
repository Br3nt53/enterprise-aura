"""Domain value object for metrics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MahalanobisDistance:
    value: float
