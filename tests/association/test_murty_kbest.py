import numpy as np

from aura_v2.domain.association.jpdaf.kbest_murty import MurtyKBest


def test_murty_orders_increasing_cost():
    C = np.array([[1, 4, 5], [2, 1, 6], [3, 2, 1]], dtype=float)
    solver = MurtyKBest(C)
    sols = solver.solve(5)
    assert len(sols) >= 2
    costs = [s.total_cost for s in sols]
    assert costs == sorted(costs), "k-best costs must be non-decreasing"
