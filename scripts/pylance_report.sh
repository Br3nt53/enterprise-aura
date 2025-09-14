#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts/pylance

# Ensure pyright installed in venv
if ! command -v pyright >/dev/null 2>&1; then
  python -m pip install pyright >/dev/null
fi

echo "Running pyright static analysis..."
pyright --outputjson > artifacts/pylance/pyright_output.json || true
pyright > artifacts/pylance/pyright_output.txt || true

echo "Summarizing diagnostics..."
python - <<'PY'
import json, pathlib, collections
p = pathlib.Path("artifacts/pylance/pyright_output.json")
if not p.exists():
    print("no_json_output"); raise SystemExit(0)
j = json.loads(p.read_text())
counts = collections.Counter()
files = collections.defaultdict(list)
for d in j.get("generalDiagnostics", []):
    sev = d.get("severity")
    rule = d.get("rule")
    path = d.get("file")
    counts[(sev, rule)] += 1
    files[path].append((sev, rule, d.get("message")))
summary = {
  "totals_by_severity_rule": {f"{k[0]}:{k[1]}": v for k,v in counts.items()},
  "top_files": sorted([(len(v), k) for k,v in files.items()], reverse=True)[:20]
}
pathlib.Path("artifacts/pylance/summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY

echo "Done. See artifacts/pylance/{pyright_output.txt,pyright_output.json,summary.json}"
