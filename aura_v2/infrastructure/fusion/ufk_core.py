from __future__ import annotations
from typing import Dict, Any, List
import yaml
from .adapters import camera as cam_adapt
from .adapters import uwb as uwb_adapt
from .strategies import weighted as strat_weighted

class UFK:
    def __init__(self, cfg_path: str):
        with open(cfg_path, "r") as f:
            self.cfg = yaml.safe_load(f)
        self.strategy = self.cfg.get("strategy", "weighted")
        self.weights = self.cfg.get("weights", {})

    def fuse(self, camera_dets: List[Dict[str, Any]], uwb_pings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tracks_by_modality: Dict[str, List[Dict[str, Any]]] = {}
        if self.cfg.get("adapters", {}).get("camera", {}).get("enabled", True):
            tracks_by_modality["camera"] = [cam_adapt.normalize(d) for d in camera_dets]
        if self.cfg.get("adapters", {}).get("uwb", {}).get("enabled", True):
            tracks_by_modality["uwb"] = [uwb_adapt.normalize(p) for p in uwb_pings]

        if self.strategy == "weighted":
            return strat_weighted.fuse(tracks_by_modality, self.weights)
        return []
