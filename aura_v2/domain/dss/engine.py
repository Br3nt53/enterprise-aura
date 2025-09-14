from __future__ import annotations
from typing import Dict, Any, List
import operator
import yaml
from datetime import datetime

OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
}


class DSSEngine:
    def __init__(self, policy_path: str):
        with open(policy_path, "r") as f:
            self.policies = yaml.safe_load(f) or {}
        self.rules = self.policies.get("rules", [])

    def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        for r in self.rules:
            conds = r.get("when", {}).get("any", [])
            fired = False
            for c in conds:
                metric = c["metric"]
                op = OPS[c["op"]]
                val = c["value"]
                cur = context.get(metric)
                if cur is not None and op(cur, val):
                    fired = True
                    break
            if fired:
                alerts.append(
                    {
                        "rule": r["id"],
                        "level": r["then"]["level"],
                        "message": r["then"]["message"],
                        "ts": context.get("ts") or datetime.utcnow().isoformat(),
                    }
                )
        return alerts
