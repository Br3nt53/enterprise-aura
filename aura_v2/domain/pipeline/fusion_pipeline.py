from __future__ import annotations

from typing import Any, Optional


class FusionPipeline:
    """Thin adapter that owns a fusion core and exposes a stable process_batch()."""

    def __init__(self, core: Any):
        if not hasattr(core, "process_batch"):
            raise AttributeError("Fusion core must implement process_batch(batch, tracks=None)")
        self._core = core

    def process_batch(self, batch: Any, tracks: Optional[list[dict]] = None) -> list[dict]:
        return self._core.process_batch(batch, tracks)


# NOTE: build_default_pipeline and infrastructure imports have been moved to
# aura_v2.application.pipeline.fusion_pipeline_factory. Import from there.
