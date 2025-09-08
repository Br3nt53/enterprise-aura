# aura_v2/infrastructure/persistence/in_memory.py
import asyncio
from typing import AsyncIterator, List, Optional, TYPE_CHECKING, Dict

from ...domain.entities import Detection  # runtime import only

if TYPE_CHECKING:
    from ...domain.entities.track import Track
    from ...domain.value_objects import TrackID  # alias is fine; used as str here


# ---- In-memory detection source ---------------------------------------------
class InMemoryDetectionSource:
    """Simple in-memory source. Push detections, consume as async stream."""
    def __init__(self, maxsize: int = 100, batch_timeout: float = 0.1) -> None:
        self._q: asyncio.Queue[Detection] = asyncio.Queue(maxsize=maxsize)
        self._batch_timeout = batch_timeout

    def push(self, det: Detection) -> None:
        try:
            self._q.put_nowait(det)
        except asyncio.QueueFull:
            pass

    async def stream(self) -> AsyncIterator[List[Detection]]:
        batch: List[Detection] = []
        loop = asyncio.get_running_loop()
        while True:
            deadline = loop.time() + self._batch_timeout
            while True:
                timeout = deadline - loop.time()
                if timeout <= 0:
                    break
                try:
                    batch.append(await asyncio.wait_for(self._q.get(), timeout=timeout))
                except asyncio.TimeoutError:
                    break
            if batch:
                yield batch
                batch = []


# ---- In-memory Track repository ---------------------------------------------
class InMemoryTrackRepository:
    """Simple in-memory repo keyed by TrackID."""
    def __init__(self) -> None:
        self._store: Dict[str, "Track"] = {}

    def save(self, track: "Track") -> None:
        tid = getattr(track, "id", None) or getattr(track, "track_id", None)
        if tid is None:
            return
        self._store[str(tid)] = track

    def get(self, track_id: "TrackID") -> Optional["Track"]:
        return self._store.get(str(track_id))

    def list(self) -> List["Track"]:
        return list(self._store.values())

    def delete(self, track_id: "TrackID") -> None:
        self._store.pop(str(track_id), None)

    def clear(self) -> None:
        self._store.clear()


# ---- In-memory Track history repository -------------------------------------
class TrackHistoryRepository:
    """Keeps a simple append-only history of tracks by id."""
    def __init__(self) -> None:
        self._hist: Dict[str, List["Track"]] = {}

    def append(self, track: "Track") -> None:
        tid = getattr(track, "id", None) or getattr(track, "track_id", None)
        if tid is None:
            return
        self._hist.setdefault(str(tid), []).append(track)

    def get(self, track_id: "TrackID") -> List["Track"]:
        return list(self._hist.get(str(track_id), []))

    def clear(self) -> None:
        self._hist.clear()


# ---- In-memory Evaluation use case ------------------------------------------
class InMemoryEvaluationUseCase:
    """No-op evaluator that records the last batch size."""
    def __init__(self) -> None:
        self.last_count: int = 0

    def evaluate(self, tracks: List["Track"]) -> None:
        self.last_count = len(tracks)


# ---- In-memory Output sink ---------------------------------------------------
class InMemoryOutputSink:
    """No-op sink that records the last write size."""
    def __init__(self) -> None:
        self.last_count: int = 0

    def write(self, tracks: List["Track"]) -> None:
        self.last_count = len(tracks)
