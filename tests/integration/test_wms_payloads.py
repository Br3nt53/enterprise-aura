import pytest
import json
from datetime import datetime
from aura_v2.infrastructure.integrations.wms.schemas import (
    fused_track_payload,
    alert_payload,
)
from aura_v2.infrastructure.integrations.wms.client import WMSClient


@pytest.mark.asyncio
async def test_wms_payload_and_client(monkeypatch):
    t = {
        "id": "A1",
        "bbox": [0, 0, 10, 10],
        "score": 0.9,
        "meta": {},
        "ts": datetime.utcnow().isoformat(),
    }
    p = fused_track_payload(t)
    assert p["trackId"] == "A1"
    assert p["bbox"] == [0, 0, 10, 10]

    sent = {}

    async def fake_post(self, url, headers=None, content=None):
        sent["url"] = url
        sent["headers"] = headers or {}
        sent["content"] = json.loads(content)

        class R:
            status_code = 200

            def raise_for_status(self):
                return None

        return R()

    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)
    cli = WMSClient(base_url="https://wms.example/api", api_key="k")
    n = await cli.publish_tracks([t])
    assert n == 1
    assert sent["url"].endswith("/tracks")
    assert sent["headers"]["Authorization"].startswith("Bearer ")
    assert isinstance(sent["content"], list)
