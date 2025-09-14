from __future__ import annotations
from typing import Dict, Any, List

def fused_track_payload(track: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "trackId": track.get("id", ""),
        "bbox": track.get("bbox", []),
        "score": track.get("score", 1.0),
        "meta": track.get("meta", {}),
        "ts": track.get("ts"),
    }

def alert_payload(alert: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "level": alert["level"],
        "message": alert["message"],
        "context": alert.get("context", {}),
        "ts": alert["ts"],
    }
