from __future__ import annotations

from pathlib import Path

from ...infrastructure.fusion.ufk_core import UFK


def _default_cfg() -> str:
    return str(
        Path(__file__).resolve().parents[3]
        / "infrastructure"
        / "fusion"
        / "config"
        / "fusion.yaml"
    )


def build_default_pipeline(config_path: str | None = None):
    return UFK(config_path or _default_cfg())
