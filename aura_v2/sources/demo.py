import asyncio
import math

from .base import DetectionSource, batch


class DemoSource(DetectionSource):
    def __init__(self, fps: float = 2.0):
        self.dt = 1.0 / max(0.1, fps)

    async def frames(self):
        t = 0
        while True:
            x = 10.0 + 0.1 * math.sin(t / 5)
            y = 20.0 + 0.1 * math.cos(t / 5)
            dets = [
                {
                    "sensor_id": "camera_1",
                    "timestamp": "1970-01-01T00:00:00Z",
                    "position": {"x": x, "y": y},
                    "confidence": 0.95,
                }
            ]
            yield batch(camera=dets)
            t += 1
            await asyncio.sleep(self.dt)
