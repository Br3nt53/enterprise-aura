AURA v2
FastAPI service for multi-sensor detection ingestion, tracking, and simple fusion.

Strict UTC timestamp normalization (schema-level & server-side)

Lifespan startup for optional source pump

Typer-based CLI (aura-cli) for dev ergonomics

Modern tracking pipeline with a basic fusion service

Uses uv for env and package management

Quickstart (with uv)
Bash
# 1) Create & activate venv
uv venv
source .venv/bin/activate

# 2) Install package + extras
uv pip install -e .
uv pip install -e ".[tracking,observability,messaging,perf,test]"

# 3) Run server (demo source pump enabled by default)
uv run aura-cli dev-server --host 0.0.0.0 --port 8000 --source "demo://?fps=2"

# 4) Verify
curl -sS http://127.0.0.1:8000/health
OpenAPI UI: http://127.0.0.1:8000/docs

Repo layout
aura_v2/
  api/
    schemas.py            # Pydantic models: DetectionInput, TrackRequest/Response, TrackOutput (UTC-validated)
  domain/                 # Core entities & services (Detection, Track, FusionService, etc.)
  infrastructure/
    tracking/modern_tracker.py  # Tracker + TrackingResult
    telemetry/            # optional (e.g., time_guard)
  sources/                # demo/jsonl/kafka (optional; gated by extras)
  utils/
    time.py               # to_utc() and helpers used across app & schemas
  web_dashboard/          # optional dashboard router
  main.py                 # FastAPI app factory + Typer CLI (aura-cli)
tests/
scripts/                  # samples/onboarding (optional)
Configuration
Env var	Default	Purpose
AURA_PUMP_ENABLED	0	Lifespan source pump toggle (CLI sets to 1 when --source used).
AURA_SOURCE_DSN	—	DSN describing the source (see Source pump (DSN)).
AURA_PUMP_HOST	127.0.0.1	Where frames are POSTed (/track).
AURA_PUMP_PORT	8000	Target port for POSTs to /track.
AURA_ACCEPT_NAIVE_TS	unset	Dev-only: if 1, accept naïve datetimes using AURA_DEFAULT_TZ.
AURA_DEFAULT_TZ	UTC	TZ assumed when AURA_ACCEPT_NAIVE_TS=1 and timestamps are naïve.
The dev-server command sets the pump envs for you when --source is provided.

API
GET /health

JSON
{"status":"ok","service":"aura","version":"2.0.0"}
GET /ready

JSON
{"ready": true}
GET /simple

Lightweight poll endpoint for dev:

JSON
{"frame_id": 42, "active": 3}
POST /track

Ingest detections and return tracking state.

DetectionInput

JSON
{
  "sensor_id": "camera_1",
  "timestamp": "2025-09-09T11:00:01Z",
  "position": {"x": 10.1, "y": 20.2, "z": 0.0},
  "confidence": 0.93,
  "attributes": {"any": "json"}
}
Request

JSON
{
  "radar_detections":  [],
  "camera_detections": [/* DetectionInput */],
  "lidar_detections":  [],
  "timestamp": "2025-09-09T11:00:00Z"
}
timestamp is an optional batch timestamp; it will be normalized to UTC if present.

Response (example)

JSON
{
  "active_tracks": [
    {
      "id": "track_00000",
      "position": {"x": 10.1, "y": 20.2, "z": 0.0},
      "velocity": {"vx": 0.0, "vy": 0.0, "vz": 0.0},
      "confidence": 1.0,
      "status": "active",
      "threat_level": 0,
      "created_at": "2025-09-09T13:24:28.688304Z",
      "updated_at": "2025-09-09T13:24:28.688304Z"
    }
  ],
  "new_tracks": [],
  "deleted_tracks": [],
  "threats": [{"track_id":"track_00000","threat_level":0,"confidence":1.0}],
  "processing_time_ms": 0.12,
  "frame_id": 25
}
Smoke test
Bash
uv run python - <<'PY'
import json, urllib.request
spec = json.load(urllib.request.urlopen("http://127.0.0.1:8000/openapi.json"))
print("track endpoints:", [p for p in spec["paths"] if "track" in p.lower()])
PY

curl -sS -H 'Content-Type: application/json' \
  -d '{"camera_detections":[{"sensor_id":"camera_1","timestamp":"2025-09-09T11:00:01Z","position":{"x":10.1,"y":20.2},"confidence":0.95}]}' \
  http://127.0.0.1:8000/track
CLI (via uv run)
All commands also work as python -m aura_v2.main <cmd>.

dev-server

Start API; optionally HTTPS and/or a source pump.

Bash
uv run aura-cli dev-server --host 0.0.0.0 --port 8000 --source "demo://?fps=2"

# HTTPS (requires certs in ./certs)
uv run aura-cli dev-server --https

# If missing:
#   mkdir -p certs && cd certs
#   openssl genrsa -out localhost.key 2048
#   openssl req -new -x509 -key localhost.key -out localhost.crt -days 365 -subj '/CN=localhost'
detections-send

Post a JSONL batch as camera detections:

Bash
mkdir -p scripts
cat > scripts/demo.jsonl <<'EOF'
{"sensor_id":"camera_1","timestamp":"2025-09-09T11:00:01Z","position":{"x":10.1,"y":20.2},"confidence":0.93}
{"sensor_id":"radar_1","timestamp":"2025-09-09T11:00:00Z","position":{"x":10.0,"y":20.0},"confidence":0.88}
{"sensor_id":"lidar_1","timestamp":"2025-09-09T11:00:02Z","position":{"x":9.9,"y":19.8},"confidence":0.91}
EOF

# Send once
uv run aura-cli detections-send scripts/demo.jsonl

# Replay to keep tracks warm
uv run aura-cli detections-send scripts/demo.jsonl --repeat 999999 --interval 1.0
tracks-tail

A tiny poller for /simple:

Bash
uv run aura-cli tracks-tail --host 127.0.0.1 --port 8000 --interval 1.0
scenario-run

Run a canned scenario and write metrics:

Bash
uv run aura-cli scenario-run --outdir runs/my-run
cat runs/my-run/metrics.json
Source pump (DSN)
When --source is provided, a lifespan task starts and POSTs frames to /track. Supported DSNs (if the corresponding source exists):

Demo (built-in):
demo://?fps=2

JSONL (loop a file, interval in seconds):
jsonl://?path=scripts/demo.jsonl&loop=1&interval=1.0

Kafka (experimental; requires messaging extras):
kafka://?topic=aura.detections&brokers=localhost:9092

See aura_v2/sources/*.py for parameters. If a source isn’t available, the app logs a warning and continues.

UTC & timezone policy
Everything is stored and processed in UTC.

Schema validators in aura_v2/api/schemas.py call utils.time.to_utc():

DetectionInput.timestamp → required, normalized to UTC.

TrackRequest.timestamp → optional, normalized to UTC if provided.

Dev-only escape hatch:

Set AURA_ACCEPT_NAIVE_TS=1 to accept naïve datetimes.

They are interpreted using AURA_DEFAULT_TZ (default UTC).

In CI/prod, don’t set this—naïve timestamps will result in a 422 error.

Dev tasks
Bash
# Lint
uv run ruff check .
uv run ruff check --fix .

# Tests
uv run pytest -q
If you added a Makefile:

Bash
make help
make dev         # typically -> runs server
make test        # -> pytest
make lint        # -> ruff check .
make fmt         # -> ruff --fix .
make clean
Troubleshooting
422 on /track
Each detection needs sensor_id, timestamp (TZ-aware ISO-8601), position (x,y, optional z), and confidence ∈ [0.0, 1.0]. For naïve timestamps in dev: AURA_ACCEPT_NAIVE_TS=1.

“address already in use”
Port 8000 is busy. Stop the other process or pass --port 8001.

“unexpected keyword argument 'state'”
The new domain model uses position: Position3D (not state/covariance). Send a position{} object in requests.

Dashboard not loading
This is optional. Install extras and ensure aura_v2/web_dashboard/api.py exists; otherwise, you’ll just see a warning.

Recommended Startup Flow
Start MongoDB

If using devcontainer: it starts automatically.
Else: docker-compose -f [docker-compose.devcontainer.yml] up -d mongo
Bootstrap environment

make setup (runs bootstrap.sh)
Start dev server

make dev or . .venv/bin/activate && python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000
Send demo detections

make demo or . .venv/bin/activate && aura-cli detections-send scripts/demo.jsonl
View dashboard

Open http://localhost:8000 in your browser.
Run tests

make test or . .venv/bin/activate && python -m pytest -q
