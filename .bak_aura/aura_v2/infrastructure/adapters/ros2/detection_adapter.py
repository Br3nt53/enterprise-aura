# aura_v2/infrastructure/adapters/ros2/detection_adapter.py
import logging
import asyncio
from typing import AsyncIterator, List
from datetime import datetime, timezone

from ....domain.entities import Detection
from ....domain.value_objects import Position3D



class ROS2DetectionAdapter:
    """Adapter to receive detections from ROS2."""

    def __init__(self, node_name: str, topic: str):
        self.queue: asyncio.Queue[Detection] = asyncio.Queue(maxsize=100)
        self.node = None
        self.topic = topic
        self._setup_ros2_node(node_name)

    def _setup_ros2_node(self, node_name: str) -> None:
        """Initialize ROS2 node if available."""
        try:
            import rclpy
            from rclpy.node import Node
            from std_msgs.msg import Float32MultiArray

            class DetectionNode(Node):
                def __init__(self, queue: asyncio.Queue[Detection], topic: str):
                    super().__init__(node_name)
                    self.queue = queue
                    self.subscription = self.create_subscription(
                        Float32MultiArray, topic, self._detection_callback, 10
                    )

                def _now_dt(self) -> datetime:
                    t = self.get_clock().now().to_msg()  # builtin_interfaces/Time
                    return datetime.fromtimestamp(
                        t.sec + t.nanosec / 1e9, tz=timezone.utc
                    )

                def _detection_callback(self, msg: Float32MultiArray) -> None:
                    data = msg.data or []
                    pos = Position3D(
                        x=float(data[0]) if len(data) > 0 else 0.0,
                        y=float(data[1]) if len(data) > 1 else 0.0,
                        z=float(data[2]) if len(data) > 2 else 0.0,
                    )
                    conf = float(data[3]) if len(data) > 3 else 1.0
                    det = Detection(
                        timestamp=self._now_dt(),
                        position=pos,
                        confidence=conf,
                        sensor_id="ros2_sensor",
                    )
                    try:
                        self.queue.put_nowait(det)
                    except asyncio.QueueFull:
                        self.get_logger().warning("Detection queue full, dropping")

            self.node = DetectionNode(self.queue, self.topic)

        except ImportError:
            logging.warning("ROS2 not available, using mock detection source")
            self.node = None

    async def stream(self) -> AsyncIterator[List[Detection]]:
        """Stream detections from ROS2."""
        batch: List[Detection] = []
        batch_timeout = 0.1  # 100ms batching
        loop = asyncio.get_running_loop()

        while True:
            deadline = loop.time() + batch_timeout
            while True:
                timeout = deadline - loop.time()
                if timeout <= 0:
                    break
                try:
                    det = await asyncio.wait_for(self.queue.get(), timeout=timeout)
                    batch.append(det)
                except asyncio.TimeoutError:
                    break

            if batch:
                yield batch
                batch = []
