from typing import Dict, List, Optional
from ...domain.entities import Track


class InMemoryTrackRepository:
    def __init__(self):
        self._tracks: Dict[str, Track] = {}

    def get(self, track_id: str) -> Optional[Track]:
        return self._tracks.get(track_id)

    def save(self, track: Track):
        self._tracks[track.id] = track


class TrackHistoryRepository:
    def __init__(self):
        self._histories: Dict[str, List[Track]] = {}

    def update(self, track: Track):
        if track.id not in self._histories:
            self._histories[track.id] = []
        self._histories[track.id].append(track)
