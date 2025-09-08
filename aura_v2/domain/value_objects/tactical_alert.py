from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .threat import Threat
    from .collision import Collision

@dataclass(frozen=True)
class TacticalAlert:
    threat: "Threat"
    collision: Optional["Collision"] = None
    message: str = ""
