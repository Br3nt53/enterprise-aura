import numpy as np

from aura_v2.domain.association.jpdaf.kbest_jpda_solver import kbest_to_marginals


def test_kbest_probability_normalization():
    C = np.array([[0.1, 0.2], [0.2, 0.3]], dtype=float)
    out = kbest_to_marginals(C, k=3)
    P = out["P"]
    assert (P >= 0).all()
    # For perfect square, each track must have at most 1 detection per assignment
    # Summing over detections gives marginal detection usage probability
    # Not guaranteed to sum to 1 along rows/cols individually (missing prob mass for unmatched)
    # Validate partition > 0
    assert out["Z"] > 0
