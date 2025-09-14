from aura_v2.infrastructure.fusion.ufk_core import UFK


def test_ufk_weighted(tmp_path):
    cfg = tmp_path / "fusion.yaml"
    cfg.write_text(
        "strategy: weighted\nweights:\n  camera: 1.0\n  uwb: 0.0\nadapters:\n  camera: {enabled: true}\n  uwb: {enabled: true}\n"
    )
    ufk = UFK(str(cfg))
    out = ufk.fuse(
        camera_dets=[{"bbox": [0, 0, 10, 10], "score": 0.9}],
        uwb_pings=[{"x": 100, "y": 100, "r": 1.0}],
    )
    assert len(out) == 1
    assert out[0]["bbox"] == [0, 0, 10, 10]  # camera-only weight
