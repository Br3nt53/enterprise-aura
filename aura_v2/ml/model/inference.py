from __future__ import annotations

import json
from pathlib import Path


def load_quality_model():
    path = Path("artifacts/models/quality_model.json")
    return json.loads(path.read_text()) if path.exists() else {"threshold": 0.5}


def score_reading(reading, model):
    # placeholder scoring
    return 1.0
