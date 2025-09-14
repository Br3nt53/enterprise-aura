from __future__ import annotations

from typing import Sequence


class Decision:
    def __init__(self, track_id: str, action: str, score: float):
        self.track_id = track_id
        self.action = action
        self.score = score


class DecisionEngine:
    def evaluate(self, tracks) -> list[Decision]:
        decisions: list[Decision] = []
        for t in tracks:
            # placeholder: escalate high measurement count
            if t.measurements > 10:
                decisions.append(Decision(t.id, "ESCALATE_MONITORING", 0.9))
        return decisions
