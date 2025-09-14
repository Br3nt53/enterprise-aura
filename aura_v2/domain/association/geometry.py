from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np

BoxC = Tuple[float, float, float, float, float]  # (cx, cy, w, h, theta)


def box_corners(box: BoxC) -> np.ndarray:
    cx, cy, w, h, th = box
    c, s = math.cos(th), math.sin(th)
    # Local half-extents
    hw, hh = w / 2.0, h / 2.0
    # Pre-rotation corners (clockwise)
    pts = np.array(
        [
            [hw, hh],
            [hw, -hh],
            [-hw, -hh],
            [-hw, hh],
        ],
        dtype=float,
    )
    R = np.array([[c, -s], [s, c]], dtype=float)
    return (pts @ R.T) + np.array([cx, cy])


def polygon_area(poly: np.ndarray) -> float:
    # poly shape: (N,2) closed or open (auto-close)
    x = poly[:, 0]
    y = poly[:, 1]
    # Shoelace
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def clip_polygon(subject: np.ndarray, clip: np.ndarray) -> np.ndarray:
    """
    Sutherland–Hodgman polygon clipping.
    subject, clip: (N,2), (M,2) assumed CCW.
    Returns possibly empty polygon.
    """

    def edge_iter(poly, a, b):
        out = []
        for i in range(len(poly)):
            p_curr = poly[i]
            p_prev = poly[i - 1]
            inside_curr = is_inside(p_curr, a, b)
            inside_prev = is_inside(p_prev, a, b)
            if inside_prev and inside_curr:
                out.append(p_curr)
            elif inside_prev and not inside_curr:
                out.append(intersect(p_prev, p_curr, a, b))
            elif (not inside_prev) and inside_curr:
                out.append(intersect(p_prev, p_curr, a, b))
                out.append(p_curr)
        return out

    def is_inside(p, a, b):
        # Left of edge a->b
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def intersect(p1, p2, a, b):
        # Line intersection parametric
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = a
        x4, y4 = b
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-12:
            return p2
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        return np.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])

    output = subject.tolist()
    for i in range(len(clip)):
        a = clip[i - 1]
        b = clip[i]
        if not output:
            break
        output = edge_iter(output, a, b)
    return np.array(output, dtype=float)


def rotated_iou(box_a: BoxC, box_b: BoxC) -> float:
    ca = box_corners(box_a)
    cb = box_corners(box_b)
    inter_poly = clip_polygon(ca, cb)
    if inter_poly.size == 0:
        # Try reverse clipping (robustness)
        inter_poly = clip_polygon(cb, ca)
        if inter_poly.size == 0:
            return 0.0
    inter_area = polygon_area(inter_poly)
    area_a = box_a[2] * box_a[3]
    area_b = box_b[2] * box_b[3]
    union = area_a + area_b - inter_area
    if union <= 1e-12:
        return 0.0
    return max(0.0, min(1.0, inter_area / union))
