import numpy as np

try:
    from numba import njit
except ImportError:
    njit = lambda *a, **k: (lambda f: f)


@njit(fastmath=True, cache=True)
def aabb_iou(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    a: (M,4) [x1,y1,x2,y2], b: (N,4)
    Returns IoU matrix (M,N)
    """
    M = a.shape[0]
    N = b.shape[0]
    out = np.zeros((M, N), dtype=np.float32)
    for i in range(M):
        ax1, ay1, ax2, ay2 = a[i]
        aw = max(0.0, ax2 - ax1)
        ah = max(0.0, ay2 - ay1)
        a_area = aw * ah
        for j in range(N):
            bx1, by1, bx2, by2 = b[j]
            bw = max(0.0, bx2 - bx1)
            bh = max(0.0, by2 - by1)
            b_area = bw * bh
            ix1 = ax1 if ax1 > bx1 else bx1
            iy1 = ay1 if ay1 > by1 else by1
            ix2 = ax2 if ax2 < bx2 else bx2
            iy2 = ay2 if ay2 < by2 else by2
            iw = ix2 - ix1
            ih = iy2 - iy1
            if iw <= 0 or ih <= 0:
                out[i, j] = 0.0
                continue
            inter = iw * ih
            denom = a_area + b_area - inter + 1e-9
            out[i, j] = inter / denom
    return out
