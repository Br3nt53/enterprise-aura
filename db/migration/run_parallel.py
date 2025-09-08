"""Utility to compare migration results and run legacy/new pipelines."""

import subprocess
from typing import Any


def compare_results(left: Any, right: Any) -> None:
    """Placeholder comparison (kept for API parity)."""
    pass


def run_existing() -> None:
    """Run the existing system."""
    _ = subprocess.run(["python", "legacy_main.py"], check=False)


def run_new() -> None:
    """Run the new system."""
    _ = subprocess.run(["python", "-m", "aura_v2.main"], check=False)


if __name__ == "__main__":
    run_existing()
    run_new()
