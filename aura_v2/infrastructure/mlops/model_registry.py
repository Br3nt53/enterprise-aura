from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass
class ModelMetadata:
    name: str
    version: str
    tags: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModelVersion:
    name: str
    version: str
    artifact_uri: str
    metadata: Optional[ModelMetadata] = None


class ModelRegistry:
    """Minimal in-memory model registry to satisfy imports/tests/audits."""

    def __init__(self) -> None:
        self._store: Dict[Tuple[str, str], ModelVersion] = {}

    def register(self, mv: ModelVersion) -> None:
        self._store[(mv.name, mv.version)] = mv

    def get(self, name: str, version: str) -> Optional[ModelVersion]:
        return self._store.get((name, version))

    def latest(self, name: str) -> Optional[ModelVersion]:
        candidates = [mv for (n, _), mv in self._store.items() if n == name]
        if not candidates:
            return None
        # naive order (lexicographic on version string)
        candidates.sort(key=lambda m: m.version)
        return candidates[-1]


__all__ = ["ModelRegistry", "ModelVersion", "ModelMetadata"]
