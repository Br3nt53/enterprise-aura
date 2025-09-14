from __future__ import annotations

from typing import Any, Dict


def normalize(det: Dict[str, Any]) -> Dict[str, Any]:
    # Assume det has bbox [x,y,w,h] and score
    return {
        "modality": "camera",
        "bbox": det["bbox"],
        "score": det.get("score", 1.0),
        "meta": det.get("meta", {}),
    }
