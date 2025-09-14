import random
import time

from aura_v2.domain.services.hungarian_assoc import HungarianAssociationStrategy


class _T:
    def __init__(self, id, pos):
        self.id = id
        self.state = type("S", (), {"position": pos})


class _D:
    def __init__(self, id, pos):
        self.id = id
        self.position = pos


def _pairs(matched):
    return {(t.id, d.id) for t, d in matched}


def test_one_to_one_exact():
    tracks = [_T("t1", (0, 0, 0)), _T("t2", (10, 0, 0))]
    dets = [_D("d1", (0, 0, 0)), _D("d2", (10, 0, 0))]
    s = HungarianAssociationStrategy(max_distance=5.0)
    matched, u_d, u_t = s.associate(tracks, dets)
    assert _pairs(matched) == {("t1", "d1"), ("t2", "d2")}
    assert not u_d and not u_t


def test_cutoff_blocks_far_pairs():
    tracks = [_T("t1", (0, 0, 0))]
    dets = [_D("d1", (10, 0, 0))]
    s = HungarianAssociationStrategy(max_distance=1.0)
    matched, u_d, u_t = s.associate(tracks, dets)
    assert not matched
    assert [d.id for d in u_d] == ["d1"]
    assert [t.id for t in u_t] == ["t1"]


def test_perf_50x50():
    random.seed(0)
    tracks = [_T(f"t{i}", (i * 2.0, 0, 0)) for i in range(50)]
    dets = [_D(f"d{i}", (i * 2.0 + 0.3, 0, 0)) for i in range(50)]
    s = HungarianAssociationStrategy(max_distance=5.0)
    t0 = time.perf_counter()
    matched, _, _ = s.associate(tracks, dets)
    dt = time.perf_counter() - t0
    assert len(matched) == 50 and dt < 0.05
