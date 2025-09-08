# tests/integration/test_track_ttl.py
from fastapi.testclient import TestClient
from aura_v2.main import get_app

def _post(client, when):
    body = {
        "radar_detections": [],
        "camera_detections": [{
            "timestamp": when,
            "position": {"x": 10, "y": 20, "z": 0},
            "confidence": 0.9,
            "sensor_id": "camera_1",
        }],
        "lidar_detections": [],
        "timestamp": when,
    }
    return client.post("/track", json=body)

def _tick(client, when):
    body = {
        "radar_detections": [],
        "camera_detections": [],
        "lidar_detections": [],
        "timestamp": when,
    }
    return client.post("/track", json=body)

def test_track_persists_until_ttl_then_prunes():
    app = get_app()
    client = TestClient(app)

    t0 = "2025-09-08T12:00:00Z"
    r1 = _post(client, t0)
    assert r1.status_code == 200
    assert len(r1.json()["active_tracks"]) >= 1

    t1 = "2025-09-08T12:00:03Z"  # < TTL
    r2 = _tick(client, t1)
    assert len(r2.json()["active_tracks"]) >= 1

    t2 = "2025-09-08T12:00:06Z"  # > TTL (will fail until TTL exists)
    r3 = _tick(client, t2)
    assert len(r3.json()["active_tracks"]) == 0

def test_threat_level_is_int():
    app = get_app()
    client = TestClient(app)
    r = _post(client, "2025-09-08T12:00:00Z")
    j = r.json()
    if j["active_tracks"]:
        assert isinstance(j["active_tracks"][0]["threat_level"], int)
    for th in j.get("threats", []):
        assert isinstance(th["threat_level"], int)
