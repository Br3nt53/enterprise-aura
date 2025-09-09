from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from aura_v2.domain import Detection, Position3D, Confidence, Track
from aura_v2.domain.services import (
    BasicFusionService,
    FusionService,
    SensorCharacteristics,
)
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker, TrackingResult


class DetectionInput(BaseModel):
    timestamp: datetime
    position: Dict[str, float]
    confidence: float = Field(ge=0.0, le=1.0)
    sensor_id: str
    attributes: Optional[Dict[str, Any]] = None


class TrackOutput(BaseModel):
    id: str
    position: Dict[str, float]
    velocity: Dict[str, float]
    confidence: float
    status: str
    threat_level: int
    created_at: datetime
    updated_at: datetime


class TrackRequest(BaseModel):
    radar_detections: List[DetectionInput] = Field(default_factory=list)
    camera_detections: List[DetectionInput] = Field(default_factory=list)
    lidar_detections: List[DetectionInput] = Field(default_factory=list)
    timestamp: Optional[datetime] = None


class TrackResponse(BaseModel):
    active_tracks: List[TrackOutput]
    new_tracks: List[TrackOutput] = Field(default_factory=list)
    deleted_tracks: List[str] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_id: int = 0


class AURAApplication:
    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        self.app: Optional[FastAPI] = None
        self.tracker: Optional[ModernTracker] = None
        self.fusion_service: Optional[FusionService] = None
        self._frame_id: int = 0
        self._initialized: bool = False

    def _initialize_sync(self) -> None:
        if self._initialized:
            return
        self._build_app()
        self.tracker = ModernTracker()
        self.fusion_service = BasicFusionService(
            {
                "radar": SensorCharacteristics("radar", 2.0, 20.0, 0.95, 0.01, np.eye(3) * 4.0),
                "camera": SensorCharacteristics(
                    "camera", 5.0, 30.0, 0.90, 0.05, np.diag([25.0, 1.0, 25.0])
                ),
                "lidar": SensorCharacteristics("lidar", 0.2, 10.0, 0.85, 0.001, np.eye(3) * 0.04),
            }
        )
        self._initialized = True

    async def initialize(self) -> None:
        self._initialize_sync()

    def _build_app(self) -> None:  # 🔧 FIXED: Proper indentation
        app = FastAPI(title="AURA Enterprise", version="2.0.0")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 🔥 NEW: Add dashboard API routes with error handling
        try:
            from .web_dashboard.api import router as dashboard_router
            app.include_router(dashboard_router)
            print("✅ Dashboard API loaded successfully")
        except ImportError as e:
            print(f"⚠️  Dashboard not installed: {e}")
            print("   Run: python -m aura_v2.setup_dashboard")

        @app.get("/health", tags=["system"])
        async def health():
            return {"status": "ok", "service": "aura", "version": "2.0.0"}

        @app.get("/ready", tags=["system"])
        async def ready():
            has_services = self.tracker is not None and self.fusion_service is not None
            return {"ready": has_services}

        # 🔥 NEW: Serve the development dashboard at root
        @app.get("/", response_class=HTMLResponse, tags=["ui"])
        async def development_dashboard():
            """Serve the React development dashboard"""
            dashboard_path = Path(__file__).parent / "web_dashboard" / "dashboard.html"
            if dashboard_path.exists():
                return HTMLResponse(dashboard_path.read_text())
            else:
                # Fallback to simple dashboard if file doesn't exist
                return HTMLResponse("""
                <html><body style="font-family:ui-sans-serif;padding:20px;background:#1f2937;color:white">
                    <h1 style="color:#60a5fa">AURA v2 Enterprise</h1>
                    <div style="background:#374151;padding:20px;border-radius:8px;margin:20px 0">
                        <h3>🎛️ Development Dashboard</h3>
                        <p>Full dashboard not found. To install:</p>
                        <pre style="background:#111827;padding:10px;border-radius:4px">python -m aura_v2.setup_dashboard</pre>
                    </div>
                    <div style="background:#374151;padding:20px;border-radius:8px">
                        <h3>🚀 Quick Actions</h3>
                        <p><a href="/simple" style="color:#60a5fa">Simple Dashboard</a> | <a href="/track" style="color:#60a5fa">API Endpoint</a> | <a href="/docs" style="color:#60a5fa">API Documentation</a></p>
                        <button onclick="testTrack()" style="background:#3b82f6;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer">Test /track Endpoint</button>
                        <pre id="output" style="background:#111827;padding:10px;border-radius:4px;margin-top:10px;min-height:100px"></pre>
                    </div>
                    <script>
                    async function testTrack() {
                        document.getElementById('output').textContent = 'Testing...';
                        try {
                            const response = await fetch('/track', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    radar_detections: [],
                                    camera_detections: [{
                                        timestamp: new Date().toISOString(),
                                        position: {x: 10, y: 20, z: 0},
                                        confidence: 0.9,
                                        sensor_id: 'test_camera'
                                    }],
                                    lidar_detections: [],
                                    timestamp: new Date().toISOString()
                                })
                            });
                            const result = await response.json();
                            document.getElementById('output').textContent = JSON.stringify(result, null, 2);
                        } catch (error) {
                            document.getElementById('output').textContent = 'Error: ' + error.message;
                        }
                    }
                    </script>
                </body></html>
                """)

        # 🔥 NEW: Alternative simple dashboard route
        @app.get("/simple", response_class=HTMLResponse, tags=["ui"])
        async def simple_dashboard():
            return HTMLResponse("""
            <html><body style="font-family:ui-sans-serif;background:#1f2937;color:white;padding:20px">
                <h2 style="color:#60a5fa">AURA Simple Panel</h2>
                <div style="background:#374151;padding:20px;border-radius:8px;margin:20px 0">
                    <button onclick="send()" style="background:#3b82f6;color:white;padding:12px 24px;border:none;border-radius:6px;cursor:pointer;font-size:16px">🚀 Test /track Endpoint</button>
                    <pre id='out' style="border:1px solid #4b5563;padding:15px;margin-top:15px;background:#111827;border-radius:6px;min-height:200px;overflow:auto"></pre>
                </div>
                <script>
                async function send(){
                    document.getElementById('out').textContent = 'Sending request...';
                    try {
                        const r = await fetch('/track',{
                            method:'POST',
                            headers:{'Content-Type':'application/json'},
                            body: JSON.stringify({
                                radar_detections:[],
                                camera_detections:[{
                                    timestamp: new Date().toISOString(),
                                    position: {x: Math.random() * 100, y: Math.random() * 100, z: 0},
                                    confidence: 0.8 + Math.random() * 0.2,
                                    sensor_id: 'simple_test'
                                }],
                                lidar_detections:[],
                                timestamp:new Date().toISOString()
                            })
                        });
                        const result = await r.json();
                        document.getElementById('out').textContent = JSON.stringify(result,null,2);
                    } catch(error) {
                        document.getElementById('out').textContent = 'Error: ' + error.message;
                    }
                }
                </script>
            </body></html>""")

        @app.post("/track", response_model=TrackResponse, tags=["tracking"])
        async def track(req: TrackRequest) -> TrackResponse:
            if self.tracker is None or self.fusion_service is None:
                raise HTTPException(status_code=503, detail="Service not initialized")
            ts = req.timestamp or datetime.now(timezone.utc)

            def to_det(d: DetectionInput) -> Detection:
                pos = d.position
                return Detection(
                    timestamp=d.timestamp,
                    position=Position3D(pos.get("x", 0.0), pos.get("y", 0.0), pos.get("z", 0.0)),
                    confidence=Confidence(d.confidence),
                    sensor_id=d.sensor_id,
                    attributes=d.attributes or {},
                )

            detections: List[Detection] = []
            for d in req.radar_detections + req.camera_detections + req.lidar_detections:
                detections.append(to_det(d))

            result: TrackingResult = await self.tracker.update(detections, ts)

            threats: List[Dict[str, Any]] = []
            for tr in result.active_tracks:
                threats.append(
                    {
                        "track_id": tr.id,
                        "threat_level": int(tr.threat_level),
                        "confidence": float(tr.confidence),
                    }
                )

            def out(tr: Track) -> TrackOutput:
                return TrackOutput(
                    id=tr.id,
                    position={
                        "x": tr.state.position.x,
                        "y": tr.state.position.y,
                        "z": tr.state.position.z,
                    },
                    velocity={
                        "vx": tr.state.velocity.vx,
                        "vy": tr.state.velocity.vy,
                        "vz": tr.state.velocity.vz,
                    },
                    confidence=float(tr.confidence),
                    status=tr.status.value,
                    threat_level=int(tr.threat_level),
                    created_at=tr.created_at,
                    updated_at=tr.updated_at,
                )

            self._frame_id += 1
            return TrackResponse(
                active_tracks=[out(t) for t in result.active_tracks],
                new_tracks=[out(t) for t in result.new_tracks],
                deleted_tracks=[t.id for t in result.deleted_tracks],
                threats=threats,
                processing_time_ms=result.processing_time_ms,
                frame_id=self._frame_id,
            )

        # 🔧 REMOVED: The conflicting route that was causing issues
        # app.add_api_route("/", dashboard, tags=["ui"])  # DELETED THIS LINE

        self.app = app

    def get_app(self) -> FastAPI:
        if not self._initialized:
            self._initialize_sync()
        return self.app  # type: ignore[return-value]


def get_app() -> FastAPI:
    return AURAApplication().get_app()


app_cli = typer.Typer(help="AURA Enterprise CLI")


@app_cli.command("dev-server")
def dev_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
):
    uvicorn.run(
        "aura_v2.main:get_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
        log_level=log_level,
    )


# ===== BEGIN-CLI-CMDS =====
import json
import uuid
import asyncio
from datetime import timezone
import yaml  # type: ignore


@app_cli.command("scenario-run")
def scenario_run(file: str, out_dir: str = "out"):
    run_id = str(uuid.uuid4())[:8]
    outp = Path(out_dir) / run_id
    outp.mkdir(parents=True, exist_ok=True)
    with open(file, "r", encoding="utf-8") as f:
        scenario = yaml.safe_load(f) or {}
    from aura_v2.infrastructure.container import Container

    c = Container()
    pipeline = c.tracking_pipeline()

    async def _run():
        ts0 = datetime.now(timezone.utc)
        frames = scenario.get("frames") or []
        total = 0
        for frame in frames:
            detections = frame.get("detections", [])
            await pipeline.process(detections, ts=ts0)
            total += 1
        metrics = {
            "run_id": run_id,
            "scenario": scenario.get("name", "unknown"),
            "summary": {"frames": total},
            "meta": {"versions": {"app": "2.0.0"}},
        }
        (outp / "metrics.json").write_text(json.dumps(metrics, indent=2))

    asyncio.run(_run())
    print(str(outp))


@app_cli.command("detections-send")
def detections_send(jsonl_path: str, host: str = "127.0.0.1", port: int = 8000):
    import httpx  # type: ignore

    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    req = {
        "radar_detections": [],
        "camera_detections": rows,
        "lidar_detections": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    url = f"http://{host}:{port}/track"
    r = httpx.post(url, json=req, timeout=30.0)
    r.raise_for_status()
    print(r.json())


@app_cli.command("tracks-tail")
def tracks_tail(host: str = "127.0.0.1", port: int = 8000, interval: float = 1.0):
    import httpx
    import time  # type: ignore

    url = f"http://{host}:{port}/track"
    while True:
        req = {
            "radar_detections": [],
            "camera_detections": [],
            "lidar_detections": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            r = httpx.post(url, json=req, timeout=10.0)
            if r.status_code == 200:
                data = r.json()
                print(
                    {"frame_id": data.get("frame_id"), "active": len(data.get("active_tracks", []))}
                )
        except Exception:
            pass
        time.sleep(interval)


# 🔧 MOVED: Dashboard function (no longer used as main route, but kept for compatibility)
async def dashboard():
    """Legacy dashboard function - now replaced by development_dashboard"""
    html = """<html><body style="font-family:ui-sans-serif">
    <h2>AURA Operator Panel (Legacy)</h2>
    <p>This is the legacy dashboard. <a href="/">Go to new dashboard</a></p>
    <button onclick="send()">Tick /track</button>
    <pre id='out' style="border:1px solid #ccc;padding:8px"></pre>
    <script>
    async function send(){
      const r = await fetch('/track',{method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({radar_detections:[],camera_detections:[],lidar_detections:[],
          timestamp:new Date().toISOString()})});
      document.getElementById('out').textContent = JSON.stringify(await r.json(),null,2);
    }
    </script></body></html>"""
    return HTMLResponse(html)


# ===== END-CLI-CMDS =====


def main():
    app_cli()


if __name__ == "__main__":
    main()    threat_level: int
    created_at: datetime
    updated_at: datetime


class TrackRequest(BaseModel):
    radar_detections: List[DetectionInput] = Field(default_factory=list)
    camera_detections: List[DetectionInput] = Field(default_factory=list)
    lidar_detections: List[DetectionInput] = Field(default_factory=list)
    timestamp: Optional[datetime] = None


class TrackResponse(BaseModel):
    active_tracks: List[TrackOutput]
    new_tracks: List[TrackOutput] = Field(default_factory=list)
    deleted_tracks: List[str] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_id: int = 0


class AURAApplication:
    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        self.app: Optional[FastAPI] = None
        self.tracker: Optional[ModernTracker] = None
        self.fusion_service: Optional[FusionService] = None
        self._frame_id: int = 0
        self._initialized: bool = False  # NEW

    # NEW: pure sync initializer used by server and tests
    def _initialize_sync(self) -> None:
        if self._initialized:
            return
        self._build_app()
        self.tracker = ModernTracker()
        self.fusion_service = BasicFusionService(
            {
                "radar": SensorCharacteristics("radar", 2.0, 20.0, 0.95, 0.01, np.eye(3) * 4.0),
                "camera": SensorCharacteristics(
                    "camera", 5.0, 30.0, 0.90, 0.05, np.diag([25.0, 1.0, 25.0])
                ),
                "lidar": SensorCharacteristics("lidar", 0.2, 10.0, 0.85, 0.001, np.eye(3) * 0.04),
            }
        )
        self._initialized = True

    # CHANGED: async shim so tests can await it
    async def initialize(self) -> None:
        self._initialize_sync()

   def _build_app(self) -> None:
    app = FastAPI(title="AURA Enterprise", version="2.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 🔥 NEW: Add dashboard API routes
    from .web_dashboard.api import router as dashboard_router
    app.include_router(dashboard_router)

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok", "service": "aura", "version": "2.0.0"}

    @app.get("/ready", tags=["system"])
    async def ready():
        has_services = self.tracker is not None and self.fusion_service is not None
        return {"ready": has_services}

    # 🔥 NEW: Serve the development dashboard at root
    @app.get("/", response_class=HTMLResponse, tags=["ui"])
    async def development_dashboard():
        """Serve the React development dashboard"""
        dashboard_path = Path(__file__).parent / "web_dashboard" / "dashboard.html"
        if dashboard_path.exists():
            return HTMLResponse(dashboard_path.read_text())
        else:
            # Fallback to simple dashboard if file doesn't exist
            return HTMLResponse("""
            <html><body style="font-family:ui-sans-serif;padding:20px">
                <h1>AURA v2 Enterprise</h1>
                <p>Development dashboard not found. Please run:</p>
                <pre>python -m aura_v2.setup_dashboard</pre>
                <p><a href="/track">Go to API endpoint</a></p>
            </body></html>
            """)

    # 🔥 NEW: Alternative simple dashboard route
    @app.get("/simple", response_class=HTMLResponse, tags=["ui"])
    async def simple_dashboard():
        return HTMLResponse("""<html><body style="font-family:ui-sans-serif">
        <h2>AURA Simple Panel</h2>
        <button onclick="send()">Test /track</button>
        <pre id='out' style="border:1px solid #ccc;padding:8px"></pre>
        <script>
        async function send(){
          const r = await fetch('/track',{method:'POST',headers:{'Content-Type':'application/json'},
            body: JSON.stringify({radar_detections:[],camera_detections:[],lidar_detections:[],
              timestamp:new Date().toISOString()})});
          document.getElementById('out').textContent = JSON.stringify(await r.json(),null,2);
        }
        </script></body></html>""")

    @app.post("/track", response_model=TrackResponse, tags=["tracking"])
    async def track(req: TrackRequest) -> TrackResponse:
            if self.tracker is None or self.fusion_service is None:
                raise HTTPException(status_code=503, detail="Service not initialized")
            ts = req.timestamp or datetime.now(timezone.utc)

            def to_det(d: DetectionInput) -> Detection:
                pos = d.position
                return Detection(
                    timestamp=d.timestamp,
                    position=Position3D(pos.get("x", 0.0), pos.get("y", 0.0), pos.get("z", 0.0)),
                    confidence=Confidence(d.confidence),
                    sensor_id=d.sensor_id,
                    attributes=d.attributes or {},
                )

            detections: List[Detection] = []
            for d in req.radar_detections + req.camera_detections + req.lidar_detections:
                detections.append(to_det(d))

            result: TrackingResult = await self.tracker.update(detections, ts)

            threats: List[Dict[str, Any]] = []
            for tr in result.active_tracks:
                threats.append(
                    {
                        "track_id": tr.id,
                        "threat_level": int(tr.threat_level),
                        "confidence": float(tr.confidence),
                    }
                )

            def out(tr: Track) -> TrackOutput:
                return TrackOutput(
                    id=tr.id,
                    position={
                        "x": tr.state.position.x,
                        "y": tr.state.position.y,
                        "z": tr.state.position.z,
                    },
                    velocity={
                        "vx": tr.state.velocity.vx,
                        "vy": tr.state.velocity.vy,
                        "vz": tr.state.velocity.vz,
                    },
                    confidence=float(tr.confidence),
                    status=tr.status.value,
                    threat_level=int(tr.threat_level),
                    created_at=tr.created_at,
                    updated_at=tr.updated_at,
                )

            self._frame_id += 1
            return TrackResponse(
                active_tracks=[out(t) for t in result.active_tracks],
                new_tracks=[out(t) for t in result.new_tracks],
                deleted_tracks=[t.id for t in result.deleted_tracks],
                threats=threats,
                processing_time_ms=result.processing_time_ms,
                frame_id=self._frame_id,
            )

        app.add_api_route("/", dashboard, tags=["ui"])
        self.app = app

    def get_app(self) -> FastAPI:
        if not self._initialized:
            self._initialize_sync()
        # self.app is set in _initialize_sync
        return self.app  # type: ignore[return-value]


def get_app() -> FastAPI:
    return AURAApplication().get_app()


app_cli = typer.Typer(help="AURA Enterprise CLI")


@app_cli.command("dev-server")
def dev_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
):
    uvicorn.run(
        "aura_v2.main:get_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
        log_level=log_level,
    )


# ===== BEGIN-CLI-CMDS =====
import json
import uuid
import asyncio
from datetime import timezone
import yaml  # type: ignore


@app_cli.command("scenario-run")
def scenario_run(file: str, out_dir: str = "out"):
    run_id = str(uuid.uuid4())[:8]
    outp = Path(out_dir) / run_id
    outp.mkdir(parents=True, exist_ok=True)
    with open(file, "r", encoding="utf-8") as f:
        scenario = yaml.safe_load(f) or {}
    from aura_v2.infrastructure.container import Container

    c = Container()
    pipeline = c.tracking_pipeline()

    async def _run():
        ts0 = datetime.now(timezone.utc)
        frames = scenario.get("frames") or []
        total = 0
        for frame in frames:
            detections = frame.get("detections", [])
            await pipeline.process(detections, ts=ts0)
            total += 1
        metrics = {
            "run_id": run_id,
            "scenario": scenario.get("name", "unknown"),
            "summary": {"frames": total},
            "meta": {"versions": {"app": "2.0.0"}},
        }
        (outp / "metrics.json").write_text(json.dumps(metrics, indent=2))

    asyncio.run(_run())
    print(str(outp))


@app_cli.command("detections-send")
def detections_send(jsonl_path: str, host: str = "127.0.0.1", port: int = 8000):
    import httpx  # type: ignore

    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    req = {
        "radar_detections": [],
        "camera_detections": rows,
        "lidar_detections": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    url = f"http://{host}:{port}/track"
    r = httpx.post(url, json=req, timeout=30.0)
    r.raise_for_status()
    print(r.json())


@app_cli.command("tracks-tail")
def tracks_tail(host: str = "127.0.0.1", port: int = 8000, interval: float = 1.0):
    import httpx
    import time  # type: ignore

    url = f"http://{host}:{port}/track"
    while True:
        req = {
            "radar_detections": [],
            "camera_detections": [],
            "lidar_detections": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            r = httpx.post(url, json=req, timeout=10.0)
            if r.status_code == 200:
                data = r.json()
                print(
                    {"frame_id": data.get("frame_id"), "active": len(data.get("active_tracks", []))}
                )
        except Exception:
            pass
        time.sleep(interval)


# Minimal operator dashboard at "/"
from fastapi.responses import HTMLResponse


async def dashboard():
    html = """<html><body style="font-family:ui-sans-serif">
    <h2>AURA Operator Panel</h2>
    <button onclick="send()">Tick /track</button>
    <pre id='out' style="border:1px solid #ccc;padding:8px"></pre>
    <script>
    async function send(){
      const r = await fetch('/track',{method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({radar_detections:[],camera_detections:[],lidar_detections:[],
          timestamp:new Date().toISOString()})});
      document.getElementById('out').textContent = JSON.stringify(await r.json(),null,2);
    }
    </script></body></html>"""
    return HTMLResponse(html)


# ===== END-CLI-CMDS =====


def main():
    app_cli()


if __name__ == "__main__":
    main()
