# aura_v2/infrastructure/container.py
from dependency_injector import containers, providers

from aura_v2.application.pipelines.tracking_pipeline import TrackingPipeline
from aura_v2.application.use_cases.process_detections import ProcessDetectionsUseCase
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker
from aura_v2.infrastructure.persistence.in_memory import (
    InMemoryTrackRepository,
    InMemoryDetectionSource,
    InMemoryEvaluationUseCase,
    InMemoryOutputSink,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # --- Domain & Infra Services ---
    track_manager = providers.Factory(ModernTracker)
    track_repository = providers.Singleton(InMemoryTrackRepository)
    # These are needed for the pipeline but not the simplified use case
    detection_source = providers.Singleton(InMemoryDetectionSource)
    evaluation_use_case = providers.Singleton(InMemoryEvaluationUseCase)
    output_sink = providers.Singleton(InMemoryOutputSink)

    # --- Application Use Cases ---
    process_detections_use_case = providers.Factory(
        ProcessDetectionsUseCase,
        track_repository=track_repository,
        track_manager=track_manager,  # No longer provides association_service
    )

    # --- Application Pipelines ---
    tracking_pipeline = providers.Factory(
        TrackingPipeline,
        detection_source=detection_source,
        process_detections_use_case=process_detections_use_case,
        evaluation_use_case=evaluation_use_case,
        output_sink=output_sink,
    )

    def init_resources(self):
        """Initializes container resources."""
        self.wire(modules=["aura_v2.main", "aura_v2.application.pipelines.tracking_pipeline"])
