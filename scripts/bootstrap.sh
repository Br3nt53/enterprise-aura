#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"; cd "$here"

# pin Python on macOS, avoid GPU extras
os="$(uname -s)"
if [[ "$os" == "Darwin" ]]; then
  : "${PY:=/opt/homebrew/opt/python@3.11/bin/python3.11}"
  command -v "$PY" >/dev/null || { echo "Python 3.11 missing. brew install python@3.11"; exit 1; }
  "$PY" -m venv .venv
  . .venv/bin/activate
  python -m ensurepip --upgrade
  python -m pip install -U pip setuptools wheel
  pip install -e '.[test,tracking,observability,messaging]'
else
  # Linux: allow GPU via uv group. Fallback to pip if uv absent.
  if command -v uv >/dev/null 2>&1; then
    uv python pin 3.11 || true
    uv venv
    uv sync || uv sync --group gpu || true
  else
    python3 -m venv .venv
    . .venv/bin/activate
    python -m ensurepip --upgrade
    python -m pip install -U pip setuptools wheel
    pip install -e '.[test,tracking,observability,messaging]'
  fi
fi

mkdir -p .vscode
cat > .vscode/settings.json <<'JSON'
{ "python.defaultInterpreterPath": ".venv/bin/python" }
JSON

echo "OK. Next:"
echo "  1) . .venv/bin/activate"
echo "  2) aura-cli dev-server"
echo "  3) aura-cli detections-send demo.jsonl  # use scripts/demo.jsonl"
echo "  4) aura-cli tracks-tail"
