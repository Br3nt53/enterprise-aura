from abc import ABC, abstractmethod
from typing import Any, List, Optional

from aura_v2.domain.entities.track import Track


class Tracker(ABC):
    @abstractmethod
    async def update(self, detections: List[Any], timestamp: Any) -> Any:
        pass

    @abstractmethod
    def get_active_tracks(self) -> List[Track]:
        pass


class TrackHistoryRepository(ABC):
    @abstractmethod
    async def save(self, track: Track) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, track_id: str) -> Optional[Track]:
        pass

    @abstractmethod
    async def list(self) -> List[Track]:
        pass

    @abstractmethod
    async def delete(self, track_id: str) -> int:
        pass

    @abstractmethod
    def update(self, track: Track) -> None:
        pass

    @abstractmethod
    def prune(self, active_track_ids: List[str]) -> None:
        pass
