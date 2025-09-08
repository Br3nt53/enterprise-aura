# aura_v2/infrastructure/container.py
from dependency_injector import containers, providers

from aura_v2.application.use_cases.process_detections import ProcessDetectionsUseCase
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration()

    tracker = providers.Factory(ModernTracker)

    # tests expect: c.tracking_pipeline() -> object with .process(...)
    tracking_pipeline = providers.Factory(
        ProcessDetectionsUseCase,
        tracker=tracker,
    )

    # keep a no-op init hook for tests that call c.init_resources()
    def init_resources(self) -> None:  # type: ignore[override]
        return
