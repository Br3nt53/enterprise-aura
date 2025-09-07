import asyncio
from fastapi.testclient import TestClient
from aura_v2.main import AURAApplication

def test_health():
    app = AURAApplication()
    asyncio.get_event_loop().run_until_complete(app.initialize())
    client = TestClient(app.app)
    r = client.get("/health")
    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok"}

def test_track_roundtrip():
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
    r = client.post("/track", json=payload)
    assert r.status_code == 200, r.text
