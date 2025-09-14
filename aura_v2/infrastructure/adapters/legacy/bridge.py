import json
from typing import Any, Dict, List

# aura_v2/infrastructure/adapters/legacy/bridge.py
"""
Bridge adapter to use existing evaluator with new architecture
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from evaluation.mot_evaluator import EvalParams as LegacyParams
from evaluation.mot_evaluator import MOTEvaluator as LegacyEvaluator

from ....domain.entities import Track
from ....domain.ports import EvaluationService


class LegacyEvaluatorAdapter(EvaluationService):
    """Adapter to use existing MOTEvaluator with new architecture"""

    def __init__(self):
        self.legacy_evaluator = LegacyEvaluator()

    async def evaluate(self, tracks: List[Track], ground_truth: List[Track]) -> Dict[str, Any]:
        """Convert new domain objects to legacy format and evaluate"""

        # Convert tracks to legacy JSONL format
        pred_data = self._tracks_to_jsonl(tracks)
        gt_data = self._tracks_to_jsonl(ground_truth)

        # Write to temporary files (legacy evaluator needs files)
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl") as pred_file:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl") as gt_file:
                pred_file.write(pred_data)
                gt_file.write(gt_data)
                pred_file.flush()
                gt_file.flush()

                # Call legacy evaluator
                legacy_params = LegacyParams(
                    track_decay_sec=1.0,  # Get from config
                    fps=10.0,
                    fragment_gap_mode="strict",
                )
                result = self.legacy_evaluator.evaluate(pred_file.name, gt_file.name)

        return result

    def _tracks_to_jsonl(self, tracks: List[Track]) -> str:
        """Convert domain tracks to JSONL format"""
        lines = []
        for track in tracks:
            for detection in track.history:
                line = {
                    "frame": int(detection.timestamp.timestamp() * 10),  # Convert to frame number
                    "id": str(track.id),
                    "x": detection.position.x,
                    "y": detection.position.y,
                    "score": detection.confidence,
                }
                lines.append(json.dumps(line))
        return "\n".join(lines)
