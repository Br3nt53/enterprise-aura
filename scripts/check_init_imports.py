#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import importlib
import os
import sys
import traceback
from pathlib import Path
from typing import Iterable, Tuple

ROOT = Path(__file__).resolve().parents[1]

# Only scan project trees (fast + avoids site-packages noise)
DEFAULT_SCAN_DIRS = ["aura_v2", "tests", "typings"]

# Optional external imports you don't want to fail the audit
OPTIONAL_PKGS = {"kafka", "ros2"}

def iter_init_files(dirs: Iterable[str]) -> Iterable[Path]:
    for d in dirs:
        base = (ROOT / d)
        if not base.exists():
            continue
        for p in base.rglob("__init__.py"):
            # skip compiled/venv/cache
            if any(seg in {"__pycache__", ".venv"} for seg in p.parts):
                continue
            yield p

def resolve_module_name(file: Path) -> str:
    rel = file.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)

def try_import(modname: str) -> Tuple[bool, str | None]:
    try:
        importlib.import_module(modname)
        return True, None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def validate_from(base_mod: str, names: Iterable[ast.alias]) -> list[str]:
    errs: list[str] = []
    ok, err = try_import(base_mod)
    if not ok:
        errs.append(f"from {base_mod} import ... -> {err}")
        return errs
    base = importlib.import_module(base_mod)
    for a in names:
        if a.name == "*":
            # cannot reliably validate; assume ok
            continue
        # First, prefer attribute presence (typical pattern)
        if hasattr(base, a.name):
            continue
        # Fallback: some packages re-expose subpackages; try import base.name
        subname = f"{base_mod}.{a.name}"
        ok2, err2 = try_import(subname)
        if not ok2:
            errs.append(f"from {base_mod} import {a.name} -> not found as attr; {err2}")
    return errs

def validate_import(names: Iterable[ast.alias]) -> list[str]:
    errs: list[str] = []
    for a in names:
        target = a.name  # 'import x.y as z' -> a.name == 'x.y'
        # If this is clearly optional, skip
        top = target.split(".", 1)[0]
        if top in OPTIONAL_PKGS:
            continue
        ok, err = try_import(target)
        if not ok:
            errs.append(f"import {target} -> {err}")
    return errs

def audit_init(init_file: Path) -> list[str]:
    modname = resolve_module_name(init_file)
    code = init_file.read_text(encoding="utf-8")
    tree = ast.parse(code, filename=str(init_file))
    errs: list[str] = []

    # ensure project root is importable
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            errs += validate_import(node.names)
        elif isinstance(node, ast.ImportFrom):
            # Build absolute base module
            if node.module is None:
                # 'from . import X' style
                base = modname.rsplit(".", node.level)[0]
            else:
                if node.level:
                    # relative like 'from ..sub import X'
                    prefix = modname.rsplit(".", node.level)[0]
                    base = f"{prefix}.{node.module}" if prefix else node.module
                else:
                    base = node.module
            top = base.split(".", 1)[0]
            if top in OPTIONAL_PKGS:
                continue
            errs += validate_from(base, node.names)
    return errs

def main():
    ap = argparse.ArgumentParser(description="Audit __init__.py imports (project only).")
    ap.add_argument("--dirs", nargs="*", default=DEFAULT_SCAN_DIRS,
                    help="Directories to scan (relative to repo root).")
    ap.add_argument("--fail-on", choices=["any", "project-only"], default="project-only",
                    help="Fail on any error or only errors whose top-level is within project.")
    args = ap.parse_args()

    all_errs: list[Tuple[str, str]] = []
    for init_file in iter_init_files(args.dirs):
        try:
            errs = audit_init(init_file)
        except Exception:
            tb = traceback.format_exc(limit=3)
            errs = [f"internal auditor error:\n{tb}"]
        modname = resolve_module_name(init_file)
        for e in errs:
            # Filter to project-only if requested
            if args.fail_on == "project-only":
                # consider project if error mentions a target starting with aura_v2 or tests or typings
                if not any(e.strip().startswith(prefix) or f" {prefix}" in e
                           for prefix in ("aura_v2", "tests", "typings")):
                    continue
            all_errs.append((modname, e))

    if not all_errs:
        print("[OK] No import issues found in project __init__.py files.")
        return 0

    print("Import issues:")
    for mod, e in all_errs:
        print(f"[FAIL] {mod}\n    - {e}")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
