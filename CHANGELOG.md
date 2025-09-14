[2025-09-14] — Mongo persistence, CI stability, typing & tooling
Added
Mongo repository
MongoTrackRepository.get_by_id(id: str) returning a fully reconstructed Track.
MongoTrackRepository.save(track: Track) with BSON-safe serialization (nested dataclasses supported).
MongoTrackRepository.delete_all() for test cleanup.
In-memory repository
API parity for tests/tracker: list(), save(track), delete(id), delete_all().
Track history (tests)
Minimal TrackHistoryRepository.update() and prune() used by coordinator tests.
Observability tests
tests/observability/test_metrics_validator.py uses pytest.importorskip("psutil") and a lightweight smoke check.
Changed
Mongo conversion layer
Robust dataclass ↔ BSON mapping:
Normalizes id ↔ _id.
Recreates TrackState, Position3D, Velocity3D, enums (TrackStatus, etc.).
tests/conftest.py
Rebuilt async fixture with AsyncIOMotorClient, ping-based readiness loop, and clean DB teardown.
Reads MONGO_URI/MONGO_DB for both local and CI runs.
modern_tracker.py
Kept full tracker implementation; only minimal, type-safe tweaks to match repo APIs (no logic regression).
Fixed
Tests failing due to:
Missing methods on Mongo/InMemory repositories.
Returning dicts instead of domain objects from Mongo reads.
Corrupted tests/conftest.py causing syntax/runtime errors.
Pylance type errors (optional subscripts, dataclass typing, missing imports).
Flaky “Mongo not reachable” in CI by:
Aligning MONGO_URI and adding an explicit wait-for-Mongo step.
CI/CD
GitHub Actions
smoke-v3.yml: Mongo service (mongo:6.0), env budgets, installs (including numpy/scipy), targeted suites, artifact upload.
ci.yml: uv-based pipeline (astral-sh/setup-uv), cached env, ruff lint, pymongo ping loop for Mongo readiness, full pytest -q.
Ensured tests stay green after ruff --fix and black.
Devcontainer
uv-based devcontainer with Python, Pylance, Ruff, Docker extension.
Forwarded ports limited to 27017 (Mongo) and optional 5015 (dashboard/dev endpoint).
Recommendation: remove 5015 if not needed.
Tooling & Editor
VS Code: interpreter pinned to .venv/bin/python, pytest enabled (-q).
Removed settings that conflict with pyrightconfig.json (e.g., python.analysis.extraPaths, venvPath).
Security / Housekeeping
.gitignore: ignore tmp/ to prevent accidental Mongo data commits.
Purged previously tracked tmp/mongo/** files from Git history on branch (local cleanup).
Port hygiene guidance and quick commands to audit listeners.
Rollback / Safety Tags
Created safety tag and branch prior to formatting:
Tag: pre-format-20250914-033826
Branch: checkpoint/green-<timestamp>
Rollback command:
git reset --hard pre-format-20250914-033826
uv run pytest -q
Developer Notes
Local run:
export MONGO_URI="mongodb://localhost:27017" MONGO_DB="aura_ci"
uv sync
uv run pytest -q
CI Mongo wait snippet (pymongo ping) included in workflows to avoid race with container health.
Branch: chore/gpt/mongo-repo-roundtrip
Status: All tests green locally and on CI after lint/format.
