
import json
from fastapi.testclient import TestClient

# Import as module path users will have after placing main.py inside aura_v2/
# For this sandbox test, we import directly if path differs.
try:
    from aura_v2.main import AURAApplication
except Exception:
    from main import AURAApplication  # fallback for sandbox run

def test_health():
    import asyncio
    app = AURAApplication()
    asyncio.get_event_loop().run_until_complete(app.initialize())
    client = TestClient(app.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_track_roundtrip():
    import asyncio
    app = AURAApplication()
    asyncio.get_event_loop().run_until_complete(app.initialize())
    client = TestClient(app.app)

    payload = {
        "radar_detections": [
            {
                "timestamp": "2024-01-01T12:00:00Z",
                "position": {"x": 10.5, "y": 20.3, "z": 0},
                "confidence": 0.85,
                "sensor_id": "radar_1",
                "attributes": {"rcs": 1.0},
            }
        ],
        "camera_detections": [],
        "lidar_detections": []
    }
    r = client.post("/api/v1/track", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "active_tracks" in data
    assert data["processing_time_ms"] >= 0
    assert data["frame_id"] == 1
    assert data["active_tracks"][0]["position"]["x"] == 10.5

    r2 = client.get("/api/v1/tracks?limit=10&page=1")
    assert r2.status_code == 200
    assert r2.json()["total"] >= 1
