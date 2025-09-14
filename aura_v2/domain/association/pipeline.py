from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from domain.association.jpdaf.jpdaf_solver import cluster_jpda
from domain.association.jpdaf.kbest_jpda_solver import kbest_to_marginals
from domain.association.jpdaf.kbest_murty import MurtyKBest
from tracking.imm_integration import convert_hard_assignment_to_probs, extract_track_probabilities
from tracking.track import Track


class AssociationPipeline:
    def __init__(
        self,
        jpda_small_cluster_max: int = 6,
        kbest_cluster_max: int = 12,
        kbest_K: int = 25,
        beta_cost: float = 1.0,
    ):
        self.jpda_small_cluster_max = jpda_small_cluster_max
        self.kbest_cluster_max = kbest_cluster_max
        self.kbest_K = kbest_K
        self.beta_cost = beta_cost

    def associate(
        self,
        tracks: List[Track],
        detections: List[Dict[str, Any]],
        gating_mask: np.ndarray,
        lh_matrix: np.ndarray,
        clusters: List[Dict[str, Any]],
        dt: float,
        measurement_getter,
    ):
        """
        clusters: list of dicts:
            {
              'det_indices': [...],
              'track_indices': [...],
              'local_mask': (Md,Nc) binary,
              'local_lh': (Md,Nc) detection likelihood matrix
            }
        measurement_getter(global_det_index) -> np.ndarray measurement vector
        """
        # Phase 1: Predict all tracks (IMM predict)
        for tr in tracks:
            tr.predict(dt)

        # We'll build global P_miss; initialize with 1 (fully missed) then reduce
        N = len(tracks)
        global_P_miss = np.ones(N, dtype=float)
        # We also build an association tensor (sparse) optional
        # For cluster-limited solution, we process each cluster separately
        for cluster in clusters:
            det_ids = cluster["det_indices"]
            trk_ids = cluster["track_indices"]
            local_mask = cluster["local_mask"]
            local_lh = cluster["local_lh"]

            Md = len(det_ids)
            Nt = len(trk_ids)

            if Nt == 0:
                continue

            # Map global track index -> local index
            trk_map = {g_idx: li for li, g_idx in enumerate(trk_ids)}

            # Decide solving strategy
            size_sum = Md + Nt
            if size_sum <= self.jpda_small_cluster_max:
                # Exact JPDA
                out = cluster_jpda(
                    det_indices=list(range(Md)),
                    trk_indices=list(range(Nt)),
                    lh_matrix=local_lh,
                    gating_mask=local_mask,
                    P_D=0.9,
                    lambda_FA=1.2,
                    max_hypotheses=300,
                )
                P_assoc_local = out["P_assoc"]  # shape (Md,Nt)
                P_miss_local = out["P_miss"]  # shape (Nt,)
            elif size_sum <= self.kbest_cluster_max:
                # k-best Murty approximate JPDA using cost = -log(likelihood + eps)
                # Build cost matrix: only where mask=1, else large
                eps = 1e-12
                C = -np.log(local_lh + eps)
                C[local_mask == 0] = 10.0  # large penalty
                k_out = kbest_to_marginals(C, k=self.kbest_K, beta=self.beta_cost)
                P_assoc_local = k_out["P"]  # (Md,Nt)
                # Estimate miss probability: P_miss = 1 - Σ_d P(d|t)
                P_miss_local = 1.0 - P_assoc_local.sum(axis=0)
                P_miss_local = np.clip(P_miss_local, 0.0, 1.0)
            else:
                # Fallback Hungarian: single best assignment deterministic
                from scipy.optimize import linear_sum_assignment

                eps = 1e-12
                C = -np.log(local_lh + eps)
                C[local_mask == 0] = 20.0
                row_ind, col_ind = linear_sum_assignment(C)
                P_assoc_local = np.zeros((Md, Nt), dtype=float)
                # Hard set each assigned pair probability 1
                for r, c in zip(row_ind, col_ind):
                    if local_mask[r, c]:
                        P_assoc_local[r, c] = 1.0
                P_miss_local = 1.0 - P_assoc_local.sum(axis=0)
                P_miss_local = np.clip(P_miss_local, 0.0, 1.0)

            # Merge local track miss probabilities into global (track-level)
            for li, gtrk in enumerate(trk_ids):
                global_P_miss[gtrk] = P_miss_local[li]

            # Store local association matrix per cluster for per-track extraction
            cluster["P_assoc_local"] = P_assoc_local
            cluster["P_miss_local"] = P_miss_local
            cluster["trk_map"] = trk_map

        # Phase 2: Track updates (IMM + JPDA mixture)
        for gtrk_idx, track in enumerate(tracks):
            # Find cluster containing this track
            cluster = None
            for c in clusters:
                if gtrk_idx in c.get("track_indices", []):
                    cluster = c
                    break

            if cluster is None:
                # No detections cluster includes this track: pure miss
                track.mark_miss()
                track.update_from_imm()
                continue

            det_ids = cluster["det_indices"]
            P_assoc_local = cluster["P_assoc_local"]
            trk_map = cluster["trk_map"]
            P_miss = global_P_miss

            kept_det_indices, assoc_probs, miss_prob = extract_track_probabilities(
                track_index=gtrk_idx,
                cluster_det_indices=det_ids,
                P_assoc_cluster=P_assoc_local,
                P_miss_global=P_miss,
                global_track_index_map=trk_map,
            )

            # Build measurement vectors
            det_measurements = [measurement_getter(did) for did in kept_det_indices]

            # Measurement update function:
            def meas_update(wrapper_clone, z):
                wrapper_clone.ukf.update(z)
                x = wrapper_clone.ukf.x
                P = wrapper_clone.ukf.S @ wrapper_clone.ukf.S.T
                return x, P

            # If no detections assigned with non-trivial probability -> treat as miss
            if sum(assoc_probs) < 1e-12:
                track.mark_miss()
                # No state change beyond predicted mixture (IMM already predicted)
                track.update_from_imm()
                continue

            # Run IMM JPDA mixture update
            track.imm.update_with_jpda(
                detections=det_measurements,
                assoc_probs=assoc_probs,
                miss_prob=miss_prob,
                measurement_update_func=meas_update,
            )

            track.update_from_imm()
            track.mark_hit()

        return tracks
