from aura_v2.infrastructure.fusion.adapters.camera import normalize as cam_norm
from aura_v2.infrastructure.fusion.adapters.uwb import normalize as uwb_norm

def test_camera_normalize():
    d = {"bbox":[0,0,10,10], "score":0.8}
    n = cam_norm(d)
    assert n["modality"] == "camera"
    assert n["bbox"] == [0,0,10,10]

def test_uwb_normalize():
    p = {"x":5,"y":5,"r":1.0}
    n = uwb_norm(p)
    assert n["modality"] == "uwb"
    assert n["bbox"] == [4.0,4.0,2.0,2.0]
