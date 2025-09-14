from __future__ import annotations
import os
import json
from typing import List, Dict, Any, Optional
import httpx
from .schemas import fused_track_payload, alert_payload

class WMSClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout_s: float = 5.0):
        self.base_url = base_url or os.getenv("WMS_BASE_URL", "")
        self.api_key = api_key or os.getenv("WMS_API_KEY", "")
        self.timeout_s = timeout_s

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def publish_tracks(self, fused_tracks: List[Dict[str, Any]]) -> int:
        if not self.base_url:
            return 0
        url = f"{self.base_url.rstrip('/')}/tracks"
        payload = [fused_track_payload(t) for t in fused_tracks]
        async with httpx.AsyncClient(timeout=self.timeout_s) as c:
            r = await c.post(url, headers=self._headers(), content=json.dumps(payload))
            r.raise_for_status()
        return len(payload)

    async def publish_alert(self, alert: Dict[str, Any]) -> None:
        if not self.base_url:
            return
        url = f"{self.base_url.rstrip('/')}/alerts"
        payload = alert_payload(alert)
        async with httpx.AsyncClient(timeout=self.timeout_s) as c:
            r = await c.post(url, headers=self._headers(), content=json.dumps(payload))
            r.raise_for_status()
