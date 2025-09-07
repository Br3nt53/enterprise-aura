from abc import ABC, abstractmethod
from typing import List
from ..entities import Detection


class FusionService(ABC):
    @abstractmethod
    def fuse(self, detections: List[Detection]) -> List[Detection]:
        pass
