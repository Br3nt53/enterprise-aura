from abc import ABC, abstractmethod
from typing import AsyncIterator
from ..entities import Detection


class SensorStream(ABC):
    @abstractmethod
    async def detections(self) -> AsyncIterator[Detection]:
        raise NotImplementedError
        yield
