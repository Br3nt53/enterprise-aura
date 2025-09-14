from __future__ import annotations
from typing import Dict, Any

def normalize(ping: Dict[str, Any]) -> Dict[str, Any]:
    # Map UWB ping to bbox-like envelope for fusion
    # Expect center (x,y) and radius r → approximate bbox
    x, y, r = ping["x"], ping["y"], ping.get("r", 0.5)
    return {
        "modality": "uwb",
        "bbox": [x - r, y - r, 2 * r, 2 * r],
        "score": ping.get("score", 0.9),
        "meta": ping.get("meta", {}),
    }
