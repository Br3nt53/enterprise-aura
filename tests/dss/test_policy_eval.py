from datetime import datetime
from aura_v2.domain.dss.engine import DSSEngine


def test_dss_fires_on_threshold(tmp_path):
    pol = tmp_path / "pol.yaml"
    pol.write_text(
        """
rules:
  - id: LATENCY_BREACH
    when: { any: [ { metric: "latency_p99_ms", op: ">", value: 750 } ] }
    then: { level: "SEV2", message: "Latency budget breach" }
"""
    )
    eng = DSSEngine(str(pol))
    alerts = eng.evaluate({"latency_p99_ms": 800, "ts": datetime.utcnow().isoformat()})
    assert alerts and alerts[0]["rule"] == "LATENCY_BREACH"
