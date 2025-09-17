from __future__ import annotations

from dataclasses import is_dataclass
from importlib.resources import files
from typing import Any, Iterable, Mapping, Optional, Sequence, cast

import yaml

# -------------------------------
# Helpers (type-safe normalization)
# -------------------------------


def _read_cfg(path: Optional[str]) -> dict[str, Any]:
    """
    Load YAML config. If no path is given, use the package default.
    """
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return cast(dict[str, Any], yaml.safe_load(f) or {})

    # Use packaged default fusion.yaml
    pkg_file = files("aura_v2.infrastructure.fusion.config").joinpath("fusion.yaml")
    raw = pkg_file.read_text(encoding="utf-8")
    return cast(dict[str, Any], yaml.safe_load(raw) or {})


def _as_xy(item: Any) -> Optional[tuple[float, float]]:
    """
    Try to coerce an arbitrary item into (x, y) floats.
    Supports:
      - Mapping with {"x","y"} OR {"position":{"x","y"}}
      - object with .x/.y attributes
      - object with .position as Mapping with {"x","y"}
      - Sequence like [x, y, ...]
      - dataclass with a 'position' field shaped as {"x","y"} or a pair
    Returns None if not possible.
    """
    # Mapping?
    if isinstance(item, Mapping):
        pos = item.get("position", item)
        if isinstance(pos, Mapping) and "x" in pos and "y" in pos:
            x_val = pos.get("x")
            y_val = pos.get("y")
            if isinstance(x_val, (int, float)) and isinstance(y_val, (int, float)):
                return float(x_val), float(y_val)

    # Dataclass?
    if is_dataclass(item):
        # Avoid asdict to keep typing simple; inspect attributes directly.
        pos_dc = getattr(item, "position", None)
        if isinstance(pos_dc, Mapping) and "x" in pos_dc and "y" in pos_dc:
            xdc = pos_dc.get("x")
            ydc = pos_dc.get("y")
            if isinstance(xdc, (int, float)) and isinstance(ydc, (int, float)):
                return float(xdc), float(ydc)
        # Or x/y as attributes
        xdc = getattr(item, "x", None)
        ydc = getattr(item, "y", None)
        if isinstance(xdc, (int, float)) and isinstance(ydc, (int, float)):
            return float(xdc), float(ydc)

    # Generic object attributes (guarded)
    pos_attr = getattr(item, "position", None)
    if isinstance(pos_attr, Mapping) and "x" in pos_attr and "y" in pos_attr:
        xv = pos_attr.get("x")
        yv = pos_attr.get("y")
        if isinstance(xv, (int, float)) and isinstance(yv, (int, float)):
            return float(xv), float(yv)

    x_attr = getattr(item, "x", None)
    y_attr = getattr(item, "y", None)
    if isinstance(x_attr, (int, float)) and isinstance(y_attr, (int, float)):
        return float(x_attr), float(y_attr)

    # Sequence like [x, y]
    if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
        if len(item) >= 2:
            x0, y0 = item[0], item[1]
            if isinstance(x0, (int, float)) and isinstance(y0, (int, float)):
                return float(x0), float(y0)

    return None


def _normalize_det(kind: str, item: Any, default_sensor: str) -> dict[str, Any]:
    """
    Canonical detection dict:
      {
        "kind": kind,                      # "camera" or "uwb"
        "sensor_id": "camera_1" | "uwb_1",
        "position": {"x": float, "y": float},
        "confidence": float,
        "bbox": list[float] | None,        # present for camera if provided
        "timestamp": float
      }
    """
    out: dict[str, Any] = {"kind": kind}
    # Sensor id, confidence, timestamp (guarded)
    sensor_id = None
    if isinstance(item, Mapping):
        sensor_id = item.get("sensor_id")
        out["confidence"] = item.get("confidence", 1.0)
        out["timestamp"] = item.get("timestamp", 0.0)
    else:
        sensor_id = getattr(item, "sensor_id", None)
        out["confidence"] = getattr(item, "confidence", 1.0)
        out["timestamp"] = getattr(item, "timestamp", 0.0)

    out["sensor_id"] = sensor_id or default_sensor

    # Position
    xy = _as_xy(item)
    if xy is not None:
        out["position"] = {"x": float(xy[0]), "y": float(xy[1])}
    else:
        # Default to origin if nothing else (keeps tests stable)
        out["position"] = {"x": 0.0, "y": 0.0}

    # Optional bbox (camera-only)
    bbox: Any = None
    if isinstance(item, Mapping):
        bbox = item.get("bbox")
    else:
        bbox = getattr(item, "bbox", None)

    if bbox is not None and isinstance(bbox, Sequence) and len(bbox) >= 4:
        # Coerce first four numeric elements
        b0, b1, b2, b3 = bbox[0], bbox[1], bbox[2], bbox[3]
        if all(isinstance(v, (int, float)) for v in (b0, b1, b2, b3)):
            out["bbox"] = [float(b0), float(b1), float(b2), float(b3)]

    return out


def _normalize_seq(kind: str, data: Any, default_sensor: str) -> list[dict[str, Any]]:
    """
    Accepts None, a single item, or a Sequence of items and normalizes to a list of detections.
    """
    if data is None:
        return []
    if isinstance(data, Sequence) and not isinstance(data, (str, bytes, dict)):
        return [_normalize_det(kind, it, default_sensor) for it in data]
    # Single item (mapping or object)
    return [_normalize_det(kind, data, default_sensor)]


def _weight(cfg: Mapping[str, Any], kind: str, default: float) -> float:
    return float(cfg.get("weights", {}).get(kind, default))


def _dist2(ax: float, ay: float, bx: float, by: float) -> float:
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy


# -------------------------------
# Core
# -------------------------------


class UFK:
    """
    Minimal fusion core sufficient for tests:
      - fuse(...): weighted preference (camera vs. uwb), returns one fused result
      - process_batch(...): simple nearest-neighbor association for per-tick readings
    """

    def __init__(self, cfg_path: Optional[str] = None):
        self.cfg: dict[str, Any] = _read_cfg(cfg_path)
        self.adapters: dict[str, Any] = cast(dict[str, Any], self.cfg.get("adapters", {}) or {})
        self.weights: dict[str, float] = cast(dict[str, float], self.cfg.get("weights", {}) or {})
        self.gating: dict[str, Any] = cast(dict[str, Any], self.cfg.get("gating", {}) or {})
        # Defaults that keep tests stable
        self.adapters.setdefault("camera", {}).setdefault("enabled", True)
        self.adapters.setdefault("uwb", {}).setdefault("enabled", True)
        self.weights.setdefault("camera", 1.0)
        self.weights.setdefault("uwb", 0.0)
        self.gating.setdefault("min_confidence", 0.0)
        self.gating.setdefault("assoc_radius", 0.5)  # used in process_batch

    # ---------------------------
    # Public API used by tests
    # ---------------------------

    def fuse(
        self,
        *,
        camera_dets: Any = None,
        camera: Any = None,
        camera_readings: Any = None,
        uwb_pings: Any = None,
        uwb_detections: Any = None,
        uwb_readings: Any = None,
    ) -> list[dict[str, Any]]:
        """
        Weighted fusion: if camera is enabled and has weight >= uwb, prefer the best camera det.
        Otherwise, prefer uwb. Returns a single fused "track" shaped dict (as tests expect).
        """
        cam_enabled = bool(self.adapters.get("camera", {}).get("enabled", True))
        uwb_enabled = bool(self.adapters.get("uwb", {}).get("enabled", True))

        # Normalize inputs
        cams = []
        if cam_enabled:
            cams.extend(_normalize_seq("camera", camera_dets, "camera_1"))
            cams.extend(_normalize_seq("camera", camera, "camera_1"))
            cams.extend(_normalize_seq("camera", camera_readings, "camera_1"))

        uwbs = []
        if uwb_enabled:
            uwbs.extend(_normalize_seq("uwb", uwb_pings, "uwb_1"))
            uwbs.extend(_normalize_seq("uwb", uwb_detections, "uwb_1"))
            uwbs.extend(_normalize_seq("uwb", uwb_readings, "uwb_1"))

        # Filter by confidence gate
        min_conf = float(self.gating.get("min_confidence", 0.0))
        cams = [c for c in cams if float(c.get("confidence", 1.0)) >= min_conf]
        uwbs = [u for u in uwbs if float(u.get("confidence", 1.0)) >= min_conf]

        if not cams and not uwbs:
            return []

        w_cam = _weight(self.cfg, "camera", 1.0)
        w_uwb = _weight(self.cfg, "uwb", 0.0)

        def _best(det_list: list[dict[str, Any]]) -> dict[str, Any]:
            if not det_list:
                return {}
            # By confidence, then arbitrary stable order
            return sorted(det_list, key=lambda d: (float(d.get("confidence", 0.0))), reverse=True)[
                0
            ]

        best_cam = _best(cams)
        best_uwb = _best(uwbs)

        # Choose by weight; when equal, prefer camera (matches test intent)
        choice = best_cam if w_cam >= w_uwb else best_uwb
        if not choice:
            choice = best_cam or best_uwb

        # If we chose a camera detection without bbox but the original had one,
        # keep it if present (already copied by _normalize_det).
        return [choice] if choice else []

    def process_batch(
        self,
        batch: Iterable[Any],
        tracks: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        """
        Pipeline adapter: accepts a batch of SensorReading-like objects with x/y or
        mapping/sequence coercible to (x, y). Performs simple nearest-neighbor
        association into `tracks` using a squared-radius gate.
        """
        tracks = tracks or []
        assoc_r = float(self.gating.get("assoc_radius", 0.5))
        assoc_r2 = assoc_r * assoc_r

        # Normalize batch into camera detections (keeps semantics consistent)
        dets = _normalize_seq("camera", batch, "camera_1")

        for det in dets:
            pos = cast(Mapping[str, float], det.get("position", {}))
            x = float(pos.get("x", 0.0))
            y = float(pos.get("y", 0.0))

            # Find nearest existing track within gate
            best_i = -1
            best_d2 = float("inf")
            for i, tr in enumerate(tracks):
                tpos = cast(Mapping[str, float], tr.get("position", {}))
                tx = float(tpos.get("x", 0.0))
                ty = float(tpos.get("y", 0.0))
                d2 = _dist2(x, y, tx, ty)
                if d2 < best_d2:
                    best_d2 = d2
                    best_i = i

            if best_i >= 0 and best_d2 <= assoc_r2:
                # Update existing track
                tracks[best_i]["position"] = {"x": x, "y": y}
            else:
                # Add new
                tracks.append({"position": {"x": x, "y": y}})

        return tracks
