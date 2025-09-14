import numpy as np

from aura_v2.domain.association.hungarian_solver import build_cost_matrix, solve_assignment


def test_assignment_simple():
    dets = [
        {"bbox": [0, 0, 10, 10], "score": 0.9},
        {"bbox": [100, 100, 10, 10], "score": 0.9},
    ]
    trks = [{"bbox": [1, 1, 10, 10]}, {"bbox": [102, 102, 10, 10]}]
    C = build_cost_matrix(dets, trks, {"iou": 0.6, "motion": 0.3, "confidence": 0.1}, max_cost=999)
    matches, umd, umt = solve_assignment(C, max_cost=5.0)
    assert len(matches) == 2
    assert umd == [] and umt == []
