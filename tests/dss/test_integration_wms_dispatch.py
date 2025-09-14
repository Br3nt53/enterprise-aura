import pytest
import json
from datetime import datetime
from aura_v2.domain.dss.engine import DSSEngine
from aura_v2.infrastructure.integrations.wms.client import WMSClient

@pytest.mark.asyncio
async def test_dss_to_wms(monkeypatch, tmp_path):
    pol = tmp_path/"pol.yaml"
    pol.write_text("""
rules:
  - id: COLLISION_HIGH
    when: { any: [ { metric: "collision_risk", op: ">=", value: 0.9 } ] }
    then: { level: "SEV2", message: "High collision risk" }
""")
    eng = DSSEngine(str(pol))
    alerts = eng.evaluate({"collision_risk": 0.95, "ts": datetime.utcnow().isoformat()})
    assert alerts

    sent = {}
    async def fake_post(self, url, headers=None, content='None'):
        sent["url"] = url
        sent["content"] = json.loads(content)
        class R:
            status_code = 200
            def raise_for_status(self): return None
        return R()
    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    cli = WMSClient(base_url="https://wms.example/api")
    await cli.publish_alert(alerts[0])
    assert sent["url"].endswith("/alerts")
    assert sent["content"]["level"] == "SEV2"
