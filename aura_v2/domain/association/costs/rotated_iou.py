from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np


# boxes: array shape (N,5) = (cx,cy,w,h,theta)
def approximate_rotated_iou_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Approximation: rotate B boxes into each A box's frame individually is expensive.
    Instead rotate both sets to axis-aligned ignoring small angle error (if angles small).
    For large angle differences, fallback to per-pair exact or mark for refinement.
    """
    # This is a placeholder. Real version would implement multi-frame rotation grouping.
    # Use center distance gating as interim.
    ious = np.zeros((A.shape[0], B.shape[0]), dtype=np.float32)
    for i, a in enumerate(A):
        for j, b in enumerate(B):
            # Fallback: treat them axis-aligned ignoring rotation (AABB approximation)
            wa, ha = a[2], a[3]
            wb, hb = b[2], b[3]
            ax1, ay1 = a[0] - wa / 2, a[1] - ha / 2
            ax2, ay2 = a[0] + wa / 2, a[1] + ha / 2
            bx1, by1 = b[0] - wb / 2, b[1] - hb / 2
            bx2, by2 = b[0] + wb / 2, b[1] + hb / 2
            ix1 = max(ax1, bx1)
            iy1 = max(ay1, by1)
            ix2 = min(ax2, bx2)
            iy2 = min(ay2, by2)
            iw = max(0.0, ix2 - ix1)
            ih = max(0.0, iy2 - iy1)
            inter = iw * ih
            union = wa * ha + wb * hb - inter + 1e-9
            ious[i, j] = inter / union
    return ious
