from __future__ import annotations

from typing import Dict, List, Tuple


# Each hypothesis: list of (d_idx, t_idx) plus sets of unmatched
def enumerate_hypotheses(
    det_indices: List[int],
    trk_indices: List[int],
    allowed: Dict[int, List[int]],
    max_hypotheses: int = 200,
) -> List[Dict]:
    """
    allowed: mapping detection -> list of candidate tracks (gated)
    Very naive exponential enumerator with pruning on count.
    """
    results: List[Dict] = []

    def dfs(di: int, current_pairs: List[Tuple[int, int]], used_tracks: set):
        if len(results) >= max_hypotheses:
            return
        if di == len(det_indices):
            matched_tracks = {t for _, t in current_pairs}
            unmatched_tracks = [t for t in trk_indices if t not in matched_tracks]
            unmatched_dets = [d for d in det_indices if d not in [p[0] for p in current_pairs]]
            results.append(
                {
                    "pairs": list(current_pairs),
                    "unmatched_tracks": unmatched_tracks,
                    "unmatched_detections": unmatched_dets,
                }
            )
            return
        d = det_indices[di]
        candidates = allowed.get(d, [])
        # Option 1: skip detection (false alarm or new track candidate)
        dfs(di + 1, current_pairs, used_tracks)
        # Option 2: try assign
        for t in candidates:
            if t in used_tracks:
                continue
            current_pairs.append((d, t))
            used_tracks.add(t)
            dfs(di + 1, current_pairs, used_tracks)
            used_tracks.remove(t)
            current_pairs.pop()

    dfs(0, [], set())
    return results
