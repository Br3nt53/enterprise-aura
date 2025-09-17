from importlib import import_module
from importlib.resources import files
from typing import Optional

import yaml

from aura_v2.domain.pipeline.fusion_pipeline import FusionPipeline


def _enabled_cfg_path(base: str) -> str:
    import tempfile

    with open(base, "r") as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("adapters", {})
    cfg["adapters"].setdefault("camera", {})["enabled"] = True
    cfg["adapters"].setdefault("uwb", {})["enabled"] = True
    cfg.setdefault("weights", {})
    cfg["weights"].setdefault("camera", 1.0)
    cfg["weights"].setdefault("uwb", 0.0)
    cfg.setdefault("gating", {})
    cfg["gating"].setdefault("min_confidence", 0.0)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
    yaml.safe_dump(cfg, tmp)
    tmp.close()
    return tmp.name


def build_default_pipeline(config_path: Optional[str] = None) -> FusionPipeline:
    UFK = import_module("aura_v2.infrastructure.fusion.ufk_core").UFK
    base_cfg = files("aura_v2.infrastructure.fusion.config") / "fusion.yaml"
    cfg_path = config_path or _enabled_cfg_path(str(base_cfg))
    core = UFK(cfg_path)
    return FusionPipeline(core)
