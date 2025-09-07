import logging

# aura_v2/infrastructure/adapters/ros2/detection_adapter.py
import asyncio
from typing import AsyncIterator, List
from ....domain.entities import Detection, Position
from ....domain.ports import DetectionSource


class ROS2DetectionAdapter(DetectionSource):
    """Adapter to receive detections from ROS2"""

    def __init__(self, node_name: str, topic: str):
        self.queue = asyncio.Queue(maxsize=100)
        self.node = None
        self.topic = topic
        self._setup_ros2_node(node_name)

    def _setup_ros2_node(self, node_name: str):
        """Initialize ROS2 node if available"""
        try:
            import rclpy
            from rclpy.node import Node
            from std_msgs.msg import Float32MultiArray

            class DetectionNode(Node):
                def __init__(self, queue, topic):
                    super().__init__(node_name)
                    self.queue = queue
                    self.subscription = self.create_subscription(
                        Float32MultiArray, topic, self._detection_callback, 10
                    )

                def _detection_callback(self, msg):
                    # Convert ROS message to domain Detection
                    detection = self._msg_to_detection(msg)
                    try:
                        self.queue.put_nowait(detection)
                    except asyncio.QueueFull:
                        self.get_logger().warning(
                            "Detection queue full, dropping message"
                        )

                def _msg_to_detection(self, msg) -> Detection:
                    # Preserve existing conversion logic
                    data = msg.data
                    return Detection(
                        timestamp=self.get_clock().now().to_msg(),
                        position=Position(
                            x=data[0], y=data[1], z=data[2] if len(data) > 2 else 0
                        ),
                        confidence=data[3] if len(data) > 3 else 1.0,
                        sensor_id="ros2_sensor",
                    )

            self.node = DetectionNode(self.queue, self.topic)

        except ImportError:
            logging.warning("ROS2 not available, using mock detection source")
            self.node = None

    async def stream(self) -> AsyncIterator[List[Detection]]:
        """Stream detections from ROS2"""
        batch = []
        batch_timeout = 0.1  # 100ms batching

        while True:
            try:
                # Collect batch of detections
                deadline = asyncio.get_event_loop().time() + batch_timeout
                while asyncio.get_event_loop().time() < deadline:
                    timeout = deadline - asyncio.get_event_loop().time()
                    if timeout > 0:
                        detection = await asyncio.wait_for(
                            self.queue.get(), timeout=timeout
                        )
                        batch.append(detection)
                    else:
                        break

                if batch:
                    yield batch
                    batch = []

            except asyncio.TimeoutError:
                if batch:
                    yield batch
                    batch = []
