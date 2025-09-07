"""
Confidence value object.

Encapsulates a probability‑like confidence value that must lie in the range
[0.0, 1.0].  This dataclass wraps a float to provide a stable public
interface.  It implements ``__float__`` so it behaves like a number in
most contexts.
"""

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Confidence:
    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(f"Confidence must be in [0, 1], got {self.value}")

    def __float__(self) -> float:
        return self.value

    def __repr__(self) -> str:
        return f"Confidence({self.value:.3f})"
