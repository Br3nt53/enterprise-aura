# aura_v2/domain/ports/sensor_port.py
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator, List
from ..entities import Detection


class SensorPort(ABC):
    @abstractmethod
    async def get_detections(self) -> AsyncIterator[Detection]:
        pass


class SensorStream(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    async def read(self) -> List[Detection]:
        pass


class SensorAdapter(ABC):
    @abstractmethod
    async def stream(self) -> AsyncIterator[List[Detection]]:
        pass
