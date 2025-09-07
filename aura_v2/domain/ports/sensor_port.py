import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

# domain/ports/sensor_port.py
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

class SensorPort(ABC):
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    @abstractmethod
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    async def get_detections(self) -> AsyncIterator[Detection]:
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        pass
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection


import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

# infrastructure/adapters/ros_sensor_adapter.py
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

class ROSSensorAdapter(SensorPort):
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    def __init__(self, node: Node, topic: str):
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        self.node = node
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        self.queue = asyncio.Queue()
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        self.node.create_subscription(
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            Float32MultiArray, 
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            topic, 
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            self._on_message, 
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            10
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        )
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    def _on_message(self, msg: Float32MultiArray):
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        # Convert ROS message to domain object
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        detection = self._msg_to_detection(msg)
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        self.queue.put_nowait(detection)
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    async def get_detections(self) -> AsyncIterator[Detection]:
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        while True:
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            yield await self.queue.get()
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection


import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

# infrastructure/adapters/mock_sensor_adapter.py
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

class MockSensorAdapter(SensorPort):
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

    async def get_detections(self) -> AsyncIterator[Detection]:
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        # For testing, returns synthetic data
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

        for detection in self.scenario_data:
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            yield detection
import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..entities import Detection

            await asyncio.sleep(0.1)
