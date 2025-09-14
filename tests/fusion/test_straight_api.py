from aura_v2.infrastructure.fusion.strategies.weighted import fuse

def test_weighted_fuse_shapes():
    camera = [{"bbox":[0,0,10,10]}]
    uwb = [{"bbox":[1,1,8,8]}]
    out = fuse({"camera":camera, "uwb":uwb}, {"camera":0.7,"uwb":0.3})
    assert len(out) == 1
    assert "bbox" in out[0]
