from __future__ import annotations
from typing import List, Dict
import math

def iou_cost(b1: List[float], b2: List[float]) -> float:
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    xa, ya = max(x1, x2), max(y1, y2)
    xb, yb = min(x1 + w1, x2 + w2), min(y1 + h1, y2 + h2)
    inter = max(0.0, xb - xa) * max(0.0, yb - ya)
    union = w1 * h1 + w2 * h2 - inter
    iou = inter / union if union > 0 else 0.0
    return 1.0 - iou  # lower is better

def motion_cost(p1: List[float], p2: List[float]) -> float:
    # simple L2 on centers
    x1, y1, w1, h1 = p1
    x2, y2, w2, h2 = p2
    c1 = (x1 + w1 / 2.0, y1 + h1 / 2.0)
    c2 = (x2 + w2 / 2.0, y2 + h2 / 2.0)
    return math.dist(c1, c2)

def confidence_cost(conf: float) -> float:
    return 1.0 - max(0.0, min(1.0, conf))

def combined_cost(det_box, trk_box, det_conf, weights: Dict[str, float]) -> float:
    return (
        weights.get("iou", 0.5) * iou_cost(det_box, trk_box)
        + weights.get("motion", 0.4) * motion_cost(det_box, trk_box)
        + weights.get("confidence", 0.1) * confidence_cost(det_conf)
    )
