#!/usr/bin/env python3
# dump_tree.py
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable

DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "node_modules",
    ".DS_Store",
}


def should_skip(p: Path, exclude: set[str]) -> bool:
    parts = set(p.parts)
    return bool(parts & exclude)


def iter_tree(root: Path, exclude: set[str]) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # prune excluded dirs in-place for speed
        dirnames[:] = sorted(
            [d for d in dirnames if not should_skip(Path(dirpath, d), exclude)]
        )
        for f in sorted(filenames):
            fp = Path(dirpath, f)
            if not should_skip(fp, exclude):
                yield fp


def render_tree(root: Path, exclude: set[str]) -> list[str]:
    lines: list[str] = [root.name + "/"]

    def walk(dir: Path, prefix: str):
        entries = sorted(
            [p for p in dir.iterdir() if not should_skip(p, exclude)],
            key=lambda p: (p.is_file(), p.name.lower()),
        )
        for i, p in enumerate(entries):
            last = i == len(entries) - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + (p.name + "/" if p.is_dir() else p.name))
            if p.is_dir():
                walk(p, prefix + ("    " if last else "│   "))

    walk(root, "")
    return lines


def to_json(root: Path, exclude: set[str]) -> dict:
    def build(d: Path) -> dict:
        children = []
        for p in sorted(
            [p for p in d.iterdir() if not should_skip(p, exclude)],
            key=lambda p: (p.is_file(), p.name.lower()),
        ):
            if p.is_dir():
                children.append(
                    {"type": "dir", "name": p.name, "children": build(p)["children"]}
                )
            else:
                children.append(
                    {"type": "file", "name": p.name, "size": p.stat().st_size}
                )
        return {"type": "dir", "name": d.name, "children": children}

    return build(root)


def main():
    ap = argparse.ArgumentParser(
        description="Dump project structure (tree + optional JSON)."
    )
    ap.add_argument("--root", default=".", help="Root folder (default: .)")
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Extra names to exclude (repeatable)",
    )
    ap.add_argument(
        "--json", dest="json_out", default=None, help="Write JSON to this path"
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    exclude = DEFAULT_EXCLUDES | set(args.exclude)

    # text tree
    for line in render_tree(root, exclude):
        print(line)

    # optional JSON
    if args.json_out:
        data = to_json(root, exclude)
        Path(args.json_out).write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
