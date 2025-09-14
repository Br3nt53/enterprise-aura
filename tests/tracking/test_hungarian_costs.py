from aura_v2.domain.association.hungarian_costs import (
    iou_cost,
    motion_cost,
    confidence_cost,
    combined_cost,
)


def test_iou_cost_range():
    a = [0, 0, 10, 10]
    b = [0, 0, 10, 10]
    assert iou_cost(a, b) == 0.0
    c = [100, 100, 5, 5]
    assert 0.99 <= iou_cost(a, c) <= 1.0


def test_motion_cost_monotonic():
    a = [0, 0, 10, 10]
    b = [1, 1, 10, 10]
    c = [10, 10, 10, 10]
    assert motion_cost(a, b) < motion_cost(a, c)


def test_combined_cost_weights_work():
    a = [0, 0, 10, 10]
    b = [1, 1, 10, 10]
    w = {"iou": 0.6, "motion": 0.3, "confidence": 0.1}
    c1 = combined_cost(a, b, 1.0, w)
    c2 = combined_cost(a, b, 0.1, w)
    assert c2 > c1  # lower confidence increases cost
