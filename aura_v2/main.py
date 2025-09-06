from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# -----------------------------
# Domain-ish simple value objects
# -----------------------------

class Position(BaseModel):
    x: float
    y: float
    z: float = 0.0

class Velocity(BaseModel):
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

class Detection(BaseModel):
    timestamp: datetime
    position: Position
    confidence: float = Field(ge=0.0, le=1.0)
    sensor_id: str
    attributes: Dict[str, Any] | None = None

class Track(BaseModel):
    id: str
    position: Position
    velocity: Velocity = Field(default_factory=Velocity)
    confidence: float = 0.0
    status: str = "tentative"
    threat_level: str = "none"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# -----------------------------
# API schemas
# -----------------------------

class TrackRequest(BaseModel):
    radar_detections: List[Detection] = Field(default_factory=list)
    camera_detections: List[Detection] = Field(default_factory=list)
    lidar_detections: List[Detection] = Field(default_factory=list)
    timestamp: Optional[datetime] = None

class TrackResponse(BaseModel):
    active_tracks: List[Track]
    new_tracks: List[Track] = Field(default_factory=list)
    deleted_tracks: List[str] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_id: int = 0

class TracksListResponse(BaseModel):
    tracks: List[Track]
    total: int
    page: int = 1
    limit: int = 100

# -----------------------------
# Application core
# -----------------------------

class AURAApplication:
    """
    Minimal app container used by integration tests.
    Provides initialize() and shutdown() and holds the FastAPI app.
    """
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        self.app: Optional[FastAPI] = None
        self._tracks: Dict[str, Track] = {}
        self._frame_id: int = 0

    async def initialize(self) -> None:
        # Load config if present
        if self.config_path and self.config_path.exists():
            try:
                import yaml  # optional
                self.config = yaml.safe_load(self.config_path.read_text()) or {}
            except Exception:
                try:
                    self.config = json.loads(self.config_path.read_text())
                except Exception:
                    self.config = {}

        # Build FastAPI app
        self.app = FastAPI(title="AURA Enterprise v2 API", version="2.0.0")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/health")
        async def health():
            return {"status": "ok", "time": datetime.utcnow().isoformat()}

        @self.app.post("/api/v1/track", response_model=TrackResponse)
        async def process_track(req: TrackRequest):
            import time
            t0 = time.perf_counter()

            # naive fusion: pick first available detection as a stub
            det: Optional[Detection] = None
            for seq in (req.radar_detections, req.camera_detections, req.lidar_detections):
                if seq:
                    det = seq[0]
                    break

            self._frame_id += 1
            new_tracks: List[Track] = []
            if det:
                tid = f"track_{len(self._tracks) + 1:03d}"
                tr = Track(
                    id=tid,
                    position=Position(x=det.position.x, y=det.position.y, z=det.position.z),
                    velocity=Velocity(),
                    confidence=det.confidence,
                    status="tentative",
                    created_at=det.timestamp,
                    updated_at=datetime.utcnow(),
                )
                self._tracks[tid] = tr
                new_tracks = [tr]

            active_tracks = list(self._tracks.values())
            dt_ms = (time.perf_counter() - t0) * 1000.0
            return TrackResponse(
                active_tracks=active_tracks,
                new_tracks=new_tracks,
                deleted_tracks=[],
                threats=[],
                processing_time_ms=dt_ms,
                frame_id=self._frame_id,
            )

        @self.app.get("/api/v1/tracks", response_model=TracksListResponse)
        async def list_tracks(
            limit: int = 100,
            page: int = 1,
            threat_level: Optional[str] = None,
            status: Optional[str] = None,
        ):
            items = list(self._tracks.values())
            if threat_level:
                items = [t for t in items if t.threat_level == threat_level]
            if status:
                items = [t for t in items if t.status == status]
            start = (page - 1) * limit
            end = start + limit
            return TracksListResponse(tracks=items[start:end], total=len(items), page=page, limit=limit)

    async def shutdown(self) -> None:
        pass

# -----------------------------
# CLI
# -----------------------------

app_cli = typer.Typer(add_completion=False, help="AURA Enterprise v2 CLI")

@app_cli.command("version")
def version():
    typer.echo("AURA Enterprise v2 CLI 2.0.0")

@app_cli.command("dev-server")
def dev_server(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Port"),
    config: Optional[str] = typer.Option(None, help="Path to config YAML/JSON"),
    reload: bool = typer.Option(True, help="Enable autoreload"),
):
    """Run FastAPI dev server (uvicorn)."""
    app = AURAApplication(Path(config) if config else None)
    asyncio.run(app.initialize())
    uvicorn.run(app.app, host=host, port=port, reload=reload)

@app_cli.command("run")
def run(
    env: str = typer.Option("development", help="Environment name"),
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Port"),
    config: Optional[str] = typer.Option(None, help="Path to config YAML/JSON"),
):
    """Run production server."""
    os.environ["AURA_ENV"] = env
    app = AURAApplication(Path(config) if config else None)
    asyncio.run(app.initialize())
    uvicorn.run(app.app, host=host, port=port, reload=False, workers=1)

def get_app() -> FastAPI:
    """ASGI entrypoint for uvicorn: `uvicorn enterprise_aura.aura_v2.main:get_app`."""
    a = AURAApplication()
    asyncio.run(a.initialize())
    return a.app  # type: ignore[return-value]

if __name__ == "__main__":
    app_cli()
