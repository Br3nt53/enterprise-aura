# aura_v2/infrastructure/container.py
import os
from dependency_injector import containers, providers

from aura_v2.application.use_cases.process_detections import ProcessDetectionsUseCase
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker
from aura_v2.infrastructure.persistence.mongo import MongoTrackRepository
from aura_v2.infrastructure.persistence.in_memory import InMemoryTrackRepository


class Container(containers.DeclarativeContainer):
    """Dependency Injection container for the AURA v2 application."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "aura_v2.application.use_cases.process_detections",
        ]
    )

    # Configuration provider to read environment variables
    config = providers.Configuration()
    config.from_dict({"persistence": {"backend": os.getenv("AURA_TRACK_REPO", "IN_MEMORY")}})

    # --- Persistence Layer ---

    # Singleton provider for the in-memory repository (default)
    in_memory_repo = providers.Singleton(InMemoryTrackRepository)

    # Singleton provider for the MongoDB repository
    mongo_repo = providers.Singleton(MongoTrackRepository)

    # Selector to choose the repository based on configuration
    track_repository = providers.Selector(
        config.persistence.backend,
        MONGO=mongo_repo,
        IN_MEMORY=in_memory_repo,
    )

    # --- Tracking Layer ---

    # The ModernTracker now receives the selected repository as a dependency
    tracker = providers.Factory(
        ModernTracker,
        track_repository=track_repository,
    )

    # --- Application Layer ---

    # The use case pipeline receives the configured tracker
    tracking_pipeline = providers.Factory(
        ProcessDetectionsUseCase,
        tracker=tracker,
    )

    def init_resources(self) -> None:
        """Initializes resources for the container."""
        # This hook can be used for async initializations if needed in the future
        return