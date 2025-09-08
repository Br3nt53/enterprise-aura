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

    def prune(self, active_track_ids: List[str]):
        """Remove histories for inactive tracks - MISSING METHOD THAT BREAKS COORDINATOR"""
        inactive_ids = set(self._histories.keys()) - set(active_track_ids)
        for track_id in inactive_ids:
            del self._histories[track_id]
