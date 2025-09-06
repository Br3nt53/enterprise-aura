from __future__ import annotations

# Minimal, dependency-free container stub used by tests/pipeline.
# If you later reintroduce dependency_injector, you can replace this file.

from dataclasses import dataclass
from typing import Any, Callable, Optional

from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker


@dataclass
class Container:
    tracker_factory: Callable[[], ModernTracker]

    @classmethod
    def create_default(cls) -> "Container":
        return cls(tracker_factory=lambda: ModernTracker())

    # convenience accessors for code that expects attributes
    def tracker(self) -> ModernTracker:
        return self.tracker_factory()


# Singleton-style helper some code may expect:
container: Optional[Container] = None

def get_container() -> Container:
    global container
    if container is None:
        container = Container.create_default()
    return container
