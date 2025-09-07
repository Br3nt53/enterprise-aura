# aura_v2/infrastructure/persistence/in_memory.py
from typing import Dict, List
from ...domain.entities import Track
from ...domain.events import DomainEvent

class InMemoryTrackRepository:
    """In-memory repository for storing tracks"""

    def __init__(self):
        self._tracks: Dict[str, Track] = {}

    async def get_active_tracks(self) -> List[Track]:
        return list(self._tracks.values())

    async def save(self, track: Track) -> None:
        self._tracks[track.id] = track

    async def save_all(self, tracks: List[Track]) -> None:
        for track in tracks:
            await self.save(track)

    async def mark_deleted(self, tracks: List[Track]) -> None:
        for track in tracks:
            if track.id in self._tracks:
                del self._tracks[track.id]

class InMemoryEventPublisher:
    """In-memory event publisher for testing"""

    def __init__(self):
        self.events: List[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.events.append(event)

        # aura_v2/infrastructure/persistence/in_memory.py

# ... (Keep the existing InMemoryTrackRepository and InMemoryEventPublisher classes)

class InMemoryDetectionSource:
    """In-memory source for providing detections for tests"""
    def __init__(self):
        pass

    async def get_detections(self):
        return []

class InMemoryEvaluationUseCase:
    """In-memory evaluation use case for tests"""
    def __init__(self):
        pass

    async def execute(self, command):
        pass

class InMemoryOutputSink:
    """In-memory output sink for tests"""
    def __init__(self):
        self.output = []

    async def send(self, data):
        self.output.append(data)
# aura_v2/infrastructure/persistence/in_memory.py

# ... (Keep the existing InMemoryTrackRepository and InMemoryEventPublisher classes)

class InMemoryDetectionSource:
    """In-memory source for providing detections for tests"""
    def __init__(self):
        pass

    async def get_detections(self):
        return []

class InMemoryEvaluationUseCase:
    """In-memory evaluation use case for tests"""
    def __init__(self):
        pass

    async def execute(self, command):
        pass

class InMemoryOutputSink:
    """In-memory output sink for tests"""
    def __init__(self):
        self.output = []

    async def send(self, data):
        self.output.append(data)