# AURA v2

## Dev quickstart
```bash
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .
pip install -e ".[tracking,observability,messaging,perf,test]"

python -m aura_v2.main dev-server --host 0.0.0.0 --port 8000
# visit http://localhost:8000/health

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=REPO_ID)
