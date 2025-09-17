# aura_v2/main.py
from __future__ import annotations

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from aura_v2.api.schemas import DetectionInput, TrackOutput, TrackRequest, TrackResponse
from aura_v2.domain import Confidence, Detection, Position3D, Track
from aura_v2.domain.services import BasicFusionService, FusionService, SensorCharacteristics
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker, TrackingResult
from aura_v2.utils.time import to_utc

# Optional telemetry guard (no-op if missing)
try:  # pragma: no cover - optional
    from aura_v2.infrastructure.telemetry.time_guard import (
        validate_and_record as _tg_validate,  # type: ignore
    )
except Exception:  # pragma: no cover - optional
    _tg_validate = None  # type: ignore[assignment]


class AURAApplication:
    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        self.app: Optional[FastAPI] = None
        self.tracker: Optional[ModernTracker] = None
        self.fusion_service: Optional[FusionService] = None
        self._frame_id: int = 0
        self._initialized: bool = False
        self._last_active_count: int = 0  # reported via /simple

    def _initialize_sync(self) -> None:
        if self._initialized:
            return
        self._build_app()
        self.tracker = ModernTracker()
        self.fusion_service = BasicFusionService(
            sensor_characteristics=[
                SensorCharacteristics(name="camera_1", accuracy=0.90, latency_ms=20),
                SensorCharacteristics(name="radar_1", accuracy=0.95, latency_ms=15),
                SensorCharacteristics(name="lidar_1", accuracy=0.97, latency_ms=10),
            ]
        )
        self._initialized = True

    def _lifespan(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # --- startup ---
            pump_task: Optional[asyncio.Task[Any]] = None
            if os.environ.get("AURA_PUMP_ENABLED", "0") == "1":
                dsn = os.environ.get("AURA_SOURCE_DSN", "")
                host = os.environ.get("AURA_PUMP_HOST", "127.0.0.1")
                try:
                    port = int(os.environ.get("AURA_PUMP_PORT", "8000"))
                except Exception:
                    port = 8000

                try:
                    from aura_v2.sources import from_dsn  # type: ignore

                    src = from_dsn(dsn)
                except Exception as e:  # pragma: no cover - optional
                    print(f"⚠️  Source disabled: {e}")
                    src = None

                if src is not None:

                    async def pump() -> None:
                        import httpx  # type: ignore

                        url = f"http://{host}:{port}/track"
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            # type: ignore for src.frames() if needed
                            async for frame in src.frames():  # type: ignore
                                try:
                                    await client.post(url, json=frame)
                                except Exception:
                                    pass

                    pump_task = asyncio.create_task(pump())

            app.state.pump_task = pump_task
            try:
                yield
            finally:
                task = getattr(app.state, "pump_task", None)
                if task is not None:
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task

        return lifespan

    def _build_app(self) -> None:
        app = FastAPI(title="AURA Enterprise", version="2.0.0", lifespan=self._lifespan())

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/", response_class=HTMLResponse, tags=["ui"])
        async def root() -> HTMLResponse:
            return HTMLResponse(
                """
            <html><head><title>AURA</title></head>
            <body>
              <h2>AURA Enterprise</h2>
              <p>OpenAPI: <a href="/docs">/docs</a></p>
              <button onclick="send()">Send sample detections</button>
              <pre id="out">Testing...</pre>
              <script>
                async function send() {
                    try {
                        const body = {
                          radar_detections: [],
                          camera_detections: [
                            {sensor_id: "camera_1", timestamp: new Date().toISOString(), position: {x: 10.1, y: 20.2}, confidence: 0.95}
                          ],
                          lidar_detections: [],
                          timestamp: new Date().toISOString()
                        };
                        const r = await fetch('/track', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
                        document.getElementById('out').textContent = 'Sending request...';
                        const result = await r.json();
                        document.getElementById('out').textContent = JSON.stringify(result,null,2);
                    } catch(error) {
                        document.getElementById('out').textContent = 'Error: ' + error.message;
                    }
                }
                </script>
            </body></html>"""
            )

        @app.get("/simple", tags=["system"])
        async def simple() -> Dict[str, int]:
            return {"frame_id": self._frame_id, "active": self._last_active_count}

        @app.get("/health", tags=["system"])
        async def health() -> Dict[str, str]:
            return {"status": "ok", "service": "aura", "version": "2.0.0"}

        @app.get("/ready", tags=["system"])
        async def ready() -> Dict[str, bool]:
            return {"ready": True}

        # Optional dashboard router if present
        try:
            from .web_dashboard.api import router as dashboard_router  # type: ignore

            if dashboard_router is not None:
                app.include_router(dashboard_router)
                print("✅ Dashboard API loaded successfully")
            else:  # pragma: no cover - optional
                print("⚠️  Dashboard API not available - dependencies missing")
                print("   Install FastAPI to enable dashboard: pip install fastapi")
        except ImportError as e:  # pragma: no cover - optional
            print(f"⚠️  Dashboard module not found: {e}")
            print("   Run: python -m aura_v2.setup_dashboard")
        except Exception as e:  # pragma: no cover - optional
            print(f"⚠️  Dashboard setup error: {e}")

        @app.post("/track", response_model=TrackResponse, tags=["tracking"])
        async def track(req: TrackRequest) -> TrackResponse:
            if self.tracker is None or self.fusion_service is None:
                raise HTTPException(status_code=503, detail="Service not initialized")

            # Normalize batch timestamp first (always UTC-aware)
            ts_raw = req.timestamp or datetime.now(timezone.utc)
            ts = to_utc(ts_raw)
            if _tg_validate is not None:  # pragma: no cover - optional
                try:
                    if _tg_validate is not None:
                        _tg_validate(ts, dev_ok=True, default_tz="UTC")  # type: ignore
                except Exception:
                    pass

            def to_det(d: DetectionInput) -> Detection:
                p = d.position or {}
                pos = Position3D(
                    x=float(p.get("x", 0.0)),
                    y=float(p.get("y", 0.0)),
                    z=float(p.get("z", 0.0)),
                )
                dts = to_utc(d.timestamp)
                if _tg_validate is not None:  # pragma: no cover - optional
                    try:
                        if _tg_validate is not None:
                            _tg_validate(dts, dev_ok=True, default_tz="UTC")  # type: ignore
                    except Exception:
                        pass
                return Detection(
                    timestamp=dts,
                    position=pos,
                    confidence=Confidence(value=float(d.confidence)),
                    sensor_id=d.sensor_id,
                    attributes=d.attributes or {},
                )

            detections: List[Detection] = []
            for d in req.radar_detections + req.camera_detections + req.lidar_detections:
                detections.append(to_det(d))

            result: TrackingResult = await self.tracker.update(detections, ts)

            threats: List[Dict[str, Any]] = [
                {
                    "track_id": tr.id,
                    "threat_level": int(tr.threat_level),
                    "confidence": float(tr.confidence),
                }
                for tr in result.active_tracks
            ]

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
            active = [out(t) for t in result.active_tracks]
            self._last_active_count = len(active)

            return TrackResponse(
                active_tracks=active,
                new_tracks=[out(t) for t in result.new_tracks],
                deleted_tracks=[t.id for t in result.deleted_tracks],
                threats=threats,
                processing_time_ms=result.processing_time_ms,
                frame_id=self._frame_id,
            )

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
    https: bool = False,
    source: Optional[str] = "demo://?fps=2",
    no_source: bool = False,
) -> None:
    """Start development server with optional HTTPS."""
    # Configure source pump env for the app factory
    if no_source or not source:
        os.environ["AURA_PUMP_ENABLED"] = "0"
    else:
        os.environ["AURA_PUMP_ENABLED"] = "1"
        os.environ["AURA_SOURCE_DSN"] = source or ""
        os.environ["AURA_PUMP_HOST"] = host
        os.environ["AURA_PUMP_PORT"] = str(port)

    if https:
        cert_file = Path("certs/localhost.crt")
        key_file = Path("certs/localhost.key")

        if not cert_file.exists() or not key_file.exists():
            print("HTTPS certificates not found. Run this first:")
            print("mkdir -p certs && cd certs")
            print("openssl genrsa -out localhost.key 2048")
            print(
                "openssl req -new -x509 -key localhost.key -out localhost.crt -days 365 -subj '/CN=localhost'",
            )
            return

        print(f"Starting HTTPS server on https://{host}:{port}")
        uvicorn.run(
            "aura_v2.main:get_app",
            host=host,
            port=port,
            reload=reload,
            factory=True,
            log_level=log_level,
            ssl_keyfile=str(key_file),
            ssl_certfile=str(cert_file),
        )
    else:
        print(f"Starting HTTP server on http://{host}:{port}")
        uvicorn.run(
            "aura_v2.main:get_app",
            host=host,
            port=port,
            reload=reload,
            factory=True,
            log_level=log_level,
        )


# ===== BEGIN-CLI-CMDS =====


@app_cli.command("scenario-run")
def scenario_run(outdir: Optional[str] = None) -> None:
    """
    Minimal offline scenario executor that runs a canned set of frames
    through the tracking pipeline, then writes metrics.
    """
    outp = (
        Path(outdir)
        if outdir
        else Path("runs") / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    )
    outp.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex[:8]

    async def _run() -> None:
        # Replace this with real scenario loading as needed
        scenario = {
            "name": "demo",
            "frames": [
                {
                    "detections": [
                        {
                            "sensor_id": "camera_1",
                            "timestamp": datetime.now(timezone.utc),
                            "position": {"x": 10.0, "y": 20.0},
                            "confidence": 0.9,
                        }
                    ]
                }
                for _ in range(10)
            ],
        }

        tracker = ModernTracker()

        async def process(dets: List[Dict[str, Any]], ts: datetime) -> None:
            def td(d: Dict[str, Any]) -> Detection:
                p = d.get("position") or {}
                pos = Position3D(
                    x=float(p.get("x", 0.0)),
                    y=float(p.get("y", 0.0)),
                    z=float(p.get("z", 0.0)),
                )
                dts = to_utc(d["timestamp"])
                return Detection(
                    timestamp=dts,
                    position=pos,
                    confidence=Confidence(value=float(d["confidence"])),
                    sensor_id=str(d["sensor_id"]),
                    attributes=d.get("attributes", {}),
                )

            dd = [td(x) for x in dets]
            await tracker.update(dd, ts)

        ts0 = datetime.now(timezone.utc)
        frames = scenario.get("frames") or []
        total = 0
        for frame in frames:
            detections = frame.get("detections", [])
            await process(detections, ts=ts0)
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
def detections_send(
    jsonl_path: str,
    host: str = "127.0.0.1",
    port: int = 8000,
    repeat: int = 1,
    interval: float = 1.0,
) -> None:
    # Local imports keep CLI startup snappy
    import time  # type: ignore

    import httpx  # type: ignore

    rows: List[Dict[str, Any]] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                rows.append(json.loads(s))

    url = f"http://{host}:{port}/track"
    for _ in range(max(1, repeat)):
        req = {
            "radar_detections": [],
            "camera_detections": rows,
            "lidar_detections": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        r = httpx.post(url, json=req, timeout=10.0)
        if r.status_code >= 400:
            print("ERROR", r.status_code, r.text)
            raise SystemExit(1)
        print(r.json())
        if repeat > 1:
            time.sleep(max(0.0, interval))


@app_cli.command("tracks-tail")
def tracks_tail(host: str = "127.0.0.1", port: int = 8000, interval: float = 1.0) -> None:
    # Local imports keep CLI startup snappy
    import time  # type: ignore

    import httpx  # type: ignore

    url = f"http://{host}:{port}/simple"
    while True:
        try:
            r = httpx.get(url, timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                print({"frame_id": data.get("frame_id"), "active": data.get("active", 0)})
        except Exception:
            pass
        time.sleep(interval)


def main() -> None:
    app_cli()


if __name__ == "__main__":
    main()
