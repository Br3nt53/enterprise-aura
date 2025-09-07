from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import Track
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import Track
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.track import Track
# aura_v2/domain/value_objects/collision.py
from dataclasses import dataclass
from ...domain.entities.track import Track


@dataclass(frozen=True)
class Collision:
    """Represents a potential collision between two tracks."""

    track1: "Track"
    track2: "Track"
    time_to_collision: float  # in seconds
    probability: float
