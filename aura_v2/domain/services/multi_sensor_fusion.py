# aura_v2/domain/services/multi_sensor_fusion.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..entities import Detection


class FusionService(ABC):
    @abstractmethod
    def fuse(self, detections: List[Detection]) -> List[Detection]: ...


class BasicFusionService(FusionService):
    def __init__(self, sensors: Optional[Dict[str, Any]] = None, **kwargs: Any):
        # accepts a positional dict or sensors=...; stores any extra kwargs
        self.sensors: Dict[str, Any] = sensors or {}
        self.params: Dict[str, Any] = dict(kwargs)

    def fuse(self, detections: List[Detection]) -> List[Detection]:
        # pass-through for now
        return detections
