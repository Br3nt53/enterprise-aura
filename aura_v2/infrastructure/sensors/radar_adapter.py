"""Adapter for receiving and parsing data from a radar sensor."""

import asyncio
import json
from datetime import datetime
from typing import AsyncIterator, Dict, List
from ...domain.entities import Detection
from ...domain.ports import SensorStream
from ...domain.value_objects import Confidence, Position3D, SensorID, Velocity3D


class RadarAdapter(SensorStream):
    def __init__(self, sensor_id: SensorID, config: dict):
        self.sensor_id = sensor_id
        self.config = config

    async def detections(self) -> AsyncIterator[Detection]:
        for _ in range(5):
            for detection_data in self._simulate_raw_data_reception():
                yield self._parse_detection(detection_data)
            await asyncio.sleep(1)

    def _parse_detection(self, rd: dict) -> Detection:
        return Detection(
            sensor_id=self.sensor_id,
            timestamp=datetime.now(),
            position=Position3D(x=rd.get("x", 0), y=rd.get("y", 0), z=rd.get("z", 0)),
            velocity=Velocity3D(
                vx=rd.get("vx", 0), vy=rd.get("vy", 0), vz=rd.get("vz", 0)
            ),
            confidence=Confidence(rd.get("confidence", 0.5)),
            metadata={},
        )

    def _simulate_raw_data_reception(self) -> List[Dict]:
        return json.loads("""
        [
            {"x":10.5,"y":5.2,"z":1.0,"vx":2.1,"vy":-0.5,"vz":0.0,"confidence":0.9},
            {"x":-20.0,"y":15.8,"z":0.8,"vx":-5.0,"vy":2.3,"vz":0.1,"confidence":0.75}
        ]""")
