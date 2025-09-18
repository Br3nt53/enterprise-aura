from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


# bboxes: shape (M,4) and (N,4), format: [x, y, w, h] with x,y = center coords (or adapt)
def aabb_iou_matrix(b1: NDArray[np.floating], b2: NDArray[np.floating]) -> NDArray[np.floating]:
    # Convert center (cx, cy, w, h) -> corners (x1,y1,x2,y2)
    b1_xy1 = b1[:, :2] - b1[:, 2:] / 2
    b1_xy2 = b1[:, :2] + b1[:, 2:] / 2
    b2_xy1 = b2[:, :2] - b2[:, 2:] / 2
    b2_xy2 = b2[:, :2] + b2[:, 2:] / 2

    # Broadcast shapes: (M,1,2) vs (1,N,2)
    inter_xy1 = np.maximum(b1_xy1[:, None, :], b2_xy1[None, :, :])
    inter_xy2 = np.minimum(b1_xy2[:, None, :], b2_xy2[None, :, :])
    inter_wh = np.clip(inter_xy2 - inter_xy1, a_min=0.0, a_max=None)
    inter_area = inter_wh[..., 0] * inter_wh[..., 1]

    b1_area = (b1[:, 2] * b1[:, 3])[:, None]
    b2_area = (b2[:, 2] * b2[:, 3])[None, :]
    union = b1_area + b2_area - inter_area + 1e-9
    return inter_area / union
