# aura_v2/application/use_cases/detect_and_track_command.py
from datetime import datetime
from typing import List


class DetectAndTrackCommand:
    def __init__(self, detections: List, timestamp: datetime, sequence_id: int):
        self.detections = detections
        self.timestamp = timestamp
        self.sequence_id = sequence_id
