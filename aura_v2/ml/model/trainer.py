from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

REGISTRY_DIR = Path("artifacts/models")


def train_quality_model(examples):
    # placeholder logic
    model = {"threshold": 0.85, "trained_at": datetime.utcnow().isoformat()}
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    path = REGISTRY_DIR / "quality_model.json"
    path.write_text(json.dumps(model))
    return path
