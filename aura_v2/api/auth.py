from __future__ import annotations

import os
from typing import Optional

from fastapi import HTTPException

API_KEY_HEADER = "X-AURA-API-KEY"


def get_valid_keys() -> set[str]:
    keys = os.getenv("AURA_API_KEYS", "")
    return {k.strip() for k in keys.split(",") if k.strip()}


def api_key_guard(x_api_key: Optional[str] = None):
    if not x_api_key or x_api_key not in get_valid_keys():
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
