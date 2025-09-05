# domain/ports/sensor_port.py
class SensorPort(ABC):
    @abstractmethod
    async def get_detections(self) -> AsyncIterator[Detection]:
        pass

# infrastructure/adapters/ros_sensor_adapter.py
class ROSSensorAdapter(SensorPort):
    def __init__(self, node: Node, topic: str):
        self.node = node
        self.queue = asyncio.Queue()
        self.node.create_subscription(
            Float32MultiArray, 
            topic, 
            self._on_message, 
            10
        )
    
    def _on_message(self, msg: Float32MultiArray):
        # Convert ROS message to domain object
        detection = self._msg_to_detection(msg)
        self.queue.put_nowait(detection)
    
    async def get_detections(self) -> AsyncIterator[Detection]:
        while True:
            yield await self.queue.get()

# infrastructure/adapters/mock_sensor_adapter.py
class MockSensorAdapter(SensorPort):
    async def get_detections(self) -> AsyncIterator[Detection]:
        # For testing, returns synthetic data
        for detection in self.scenario_data:
            yield detection
            await asyncio.sleep(0.1)