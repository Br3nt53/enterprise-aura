# aura_v2/infrastructure/persistence/in_memory.py
from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Dict, List, Optional

try:
    from aura_v2.domain.entities import Track
except Exception:
    from aura_v2.domain.entities.track import Track  # type: ignore[no-redef]

__all__ = ["InMemoryTrackRepository", "TrackHistoryRepository"]


class InMemoryTrackRepository:
    """Async in-memory store for current tracks."""

    def __init__(self) -> None:
        self._store: Dict[str, Track] = {}
        self._lock = RLock()

    async def save(self, track: Track) -> str:
        with self._lock:
            self._store[track.id] = track
            return track.id

    async def get_by_id(self, track_id: str) -> Optional[Track]:
        with self._lock:
            return self._store.get(str(track_id))

    async def list(self) -> List[Track]:
        with self._lock:
            return list(self._store.values())

    async def delete(self, track_id: str) -> int:
        with self._lock:
            return 1 if self._store.pop(str(track_id), None) is not None else 0

    async def delete_all(self) -> int:
        with self._lock:
            n = len(self._store)
            self._store.clear()
            return n


class TrackHistoryRepository:
    """Synchronous in-memory history used by the coordinator."""

    def __init__(self) -> None:
        self._hist: Dict[str, List[Track]] = {}
        self._lock = RLock()

    def update(self, track: Track) -> None:
        """Append a snapshot of the track to its history."""
        with self._lock:
            self._hist.setdefault(track.id, []).append(deepcopy(track))

    def prune(self, active_track_ids: List[str] | set[str]) -> int:
        """Drop histories for tracks not in the active set. Returns count removed."""
        active = set(map(str, active_track_ids))
        removed = 0
        with self._lock:
            for tid in list(self._hist.keys()):
                if tid not in active:
                    del self._hist[tid]
                    removed += 1
        return removed

    def get_history(self, track_id: str) -> List[Track]:
        with self._lock:
            return list(self._hist.get(str(track_id), []))

    def last(self, track_id: str) -> Optional[Track]:
        hist = self.get_history(track_id)
        return hist[-1] if hist else None

    def clear(self) -> None:
        with self._lock:
            self._hist.clear()
