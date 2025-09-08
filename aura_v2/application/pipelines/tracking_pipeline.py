# aura_v2/application/pipelines/tracking_pipeline.py

from typing import TYPE_CHECKING, AsyncIterator, Iterable, List, Optional

from ...domain.entities import Detection  # runtime import only

if TYPE_CHECKING:
    from ...domain.entities.track import Track  # type-only to avoid cycles


class Config:
    max_batch_size: int = 256
    telemetry_events: bool = True


class TelemetryClient:
    def emit(self, event: str, **kv: object) -> None:
        return


class DetectionSource:
    async def stream(self) -> AsyncIterator[List[Detection]]:  # pragma: no cover
        if False:
            yield []


class AssociationStrategy:
    def associate(self, detections: List[Detection]) -> List["Track"]:
        return []  # no-op; replace with real tracker later


class Evaluator:
    def evaluate(self, tracks: List["Track"]) -> None:
        return  # no-op; replace with metrics writer later


class Sink:
    def write(self, tracks: List["Track"]) -> None:
        return  # no-op; replace with bus/DB/HTTP publisher later


class TrackingPipeline:
    """
    Minimal working pipeline:
    - process(): one batch -> tracks (empty by default)
    - run_batch(): iterable of batches
    - run_stream(): round-robin async across sources
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        telemetry: Optional[TelemetryClient] = None,
        sources: Optional[List[DetectionSource]] = None,
        associator: Optional[AssociationStrategy] = None,
        evaluator: Optional[Evaluator] = None,
        sink: Optional[Sink] = None,
    ) -> None:
        self.config = config or Config()
        self.telemetry = telemetry or TelemetryClient()
        self.sources = sources or []
        self.associator = associator or AssociationStrategy()
        self.evaluator = evaluator or Evaluator()
        self.sink = sink or Sink()

    def process(self, detections: List[Detection]) -> List["Track"]:
        if self.config.telemetry_events:
            self.telemetry.emit("process_batch", count=len(detections))
        tracks = self.associator.associate(detections)
        self.evaluator.evaluate(tracks)
        self.sink.write(tracks)
        return tracks

    def run_batch(self, batches: Iterable[List[Detection]]) -> List["Track"]:
        out: List["Track"] = []
        for batch in batches:
            out.extend(self.process(batch[: self.config.max_batch_size]))
        return out

    async def run_stream(self) -> AsyncIterator[List["Track"]]:
        if not self.sources:
            return
        iters = [s.stream() for s in self.sources]
        while True:
            progressed = False
            for it in iters:
                try:
                    dets = await it.__anext__()
                except StopAsyncIteration:
                    continue
                progressed = True
                yield self.process(dets[: self.config.max_batch_size])
            if not progressed:
                break
