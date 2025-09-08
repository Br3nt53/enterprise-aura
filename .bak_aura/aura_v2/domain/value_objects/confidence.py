from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Confidence:
    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(f"Confidence must be in [0,1], got {self.value}")

    def __float__(self) -> float:
        return self.value

    def __repr__(self) -> str:
        return f"Confidence({self.value:.3f})"
