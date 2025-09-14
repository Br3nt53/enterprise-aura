# aura_v2/domain/services/collision_prediction.py
from abc import ABC, abstractmethod
from typing import List

from ...domain.entities.track import Track
from ...domain.value_objects.collision import Collision


class CollisionPredictor(ABC):
    """Abstract base class for collision prediction strategies."""

    @abstractmethod
    def predict(self, tracks: List[Track]) -> List[Collision]:
        """Predicts potential collisions between tracks."""
        pass
