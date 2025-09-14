# AURA v2.5 Bridge Validation Plan

This document defines the steps, acceptance criteria, and evidence to validate AURA v2.5 (bridge to v3). Record all artifacts under `artifacts/validation/<section>/`.

---

## 0) Environment

**Inputs**
- `.env` (local only; not committed)
- `docker-compose.mongo.yml`

**Actions**
1. Start Mongo locally (Docker or native).
2. Export environment variables from `.env` into the shell (do not commit).
3. Capture system info.

**Acceptance**
- Mongo reachable at `MONGO_URI`.
- Python 3.11.x available.
- Package set resolves.

**Evidence**
- `artifacts/validation/00_env/system.txt`
- `artifacts/validation/00_env/pip_freeze.txt`

**Commands**
```bash
mkdir -p artifacts/validation/00_env
mongosh --eval 'db.runCommand({ ping: 1 })' > artifacts/validation/00_env/mongo_ping.txt
python -c 'import platform,sys; print(platform.platform(), sys.version)' > artifacts/validation/00_env/system.txt
python -m pip freeze > artifacts/validation/00_env/pip_freeze.txt
