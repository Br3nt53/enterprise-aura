from __future__ import annotations

import heapq
import math
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(order=True)
class HypothesisNode:
    sort_key: float
    score: float = field(compare=False)
    id: str = field(compare=False)
    parent_id: Optional[str] = field(compare=False)
    depth: int = field(compare=False)
    associations: list = field(compare=False)  # list[(track_id, det_id)]
    missed: list = field(compare=False)
    children: list = field(default_factory=list, compare=False)


class MHTManager:
    def __init__(self, beam_width: int = 50, decay: float = 0.99):
        self.beam_width = beam_width
        self.decay = decay
        self.leaves: Dict[str, HypothesisNode] = {}

        root = HypothesisNode(
            sort_key=-0.0,
            score=0.0,
            id="root",
            parent_id=None,
            depth=0,
            associations=[],
            missed=[],
        )
        self.leaves[root.id] = root

    def expand(self, global_solutions: List[Dict]):
        new_nodes: List[HypothesisNode] = []
        # Each solution is a dict with "pairs", "likelihood"
        for leaf in self.leaves.values():
            for sol in global_solutions:
                score = leaf.score + math.log(sol["likelihood"] + 1e-15)
                node = HypothesisNode(
                    sort_key=-score,
                    score=score,
                    id=str(uuid.uuid4()),
                    parent_id=leaf.id,
                    depth=leaf.depth + 1,
                    associations=sol["pairs"],
                    missed=sol["missed"],
                )
                new_nodes.append(node)

        # Beam prune
        heapq.heapify(new_nodes)
        kept = []
        for _ in range(min(self.beam_width, len(new_nodes))):
            kept.append(heapq.heappop(new_nodes))
        self.leaves = {n.id: n for n in kept}

    def best_hypothesis(self) -> HypothesisNode:
        return max(self.leaves.values(), key=lambda n: n.score)
