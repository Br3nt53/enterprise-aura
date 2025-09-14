from __future__ import annotations

from typing import Any, Dict, List


def fuse(
    tracks_by_modality: Dict[str, List[Dict[str, Any]]], weights: Dict[str, float]
) -> List[Dict[str, Any]]:
    """Simple weighted bbox fusion per track index. Assumes aligned lists per modality."""
    fused: List[Dict[str, Any]] = []
    keys = list(tracks_by_modality.keys())
    if not keys:
        return fused
    L = min(len(tracks_by_modality[k]) for k in keys)
    for i in range(L):
        accum = [0.0, 0.0, 0.0, 0.0]
        wsum = 0.0
        for k in keys:
            w = float(weights.get(k, 0.0))
            b = tracks_by_modality[k][i]["bbox"]
            accum = [a + w * v for a, v in zip(accum, b, strict=False)]
            wsum += w
        if wsum > 0:
            fused.append(
                {
                    "bbox": [v / wsum for v in accum],
                    "score": 1.0,
                    "meta": {"fused_from": keys},
                }
            )
    return fused
