import asyncio
import json
import pathlib

from .base import DetectionSource, batch


class JsonlSource(DetectionSource):
    def __init__(self, path: str, loop: bool = True, interval: float = 1.0):
        self.path = pathlib.Path(path)
        self.loop = loop
        self.interval = interval

    async def frames(self):
        while True:
            rows = [
                json.loads(line)
                for line in self.path.read_text().splitlines()
                if line.strip()
            ]
            # put all rows into camera_detections by default
            yield batch(camera=rows)
            if not self.loop:
                return
            await asyncio.sleep(self.interval)
