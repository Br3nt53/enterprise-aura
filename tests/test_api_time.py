from fastapi.testclient import TestClient
from aura_v2.main import get_app
from datetime import datetime, timezone

def test_track_accepts_utc():
    client = TestClient(get_app())
    body = {
      "radar_detections": [],
      "camera_detections": [{
        "sensor_id":"cam","timestamp": datetime.now(timezone.utc).isoformat(),
        "position":{"x":1,"y":2},"confidence":0.9
      }],
      "lidar_detections": []
    }
    r = client.post("/track", json=body)
    assert r.status_code == 200
