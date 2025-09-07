"""
AURA v2 package initialization.

This module provides a lightweight package initializer and exposes a minimal
public API without importing heavy dependencies at import time. Avoiding
eager imports ensures that simply importing the ``aura_v2`` package does not
pull in frameworks like FastAPI, Typer or third‑party trackers unless they
are explicitly used by the caller.

This file also declares the package version for easy access.
"""

from importlib import metadata as _metadata

__all__ = ["__version__", "get_app", "get_cli"]

try:
    # Attempt to read the version from package metadata.  When running
    # from a source checkout the version may not be available; in that
    # case ``__version__`` will fall back to "unknown".
    __version__ = _metadata.version("aura-v2")  # type: ignore[assignment]
except Exception:
    __version__ = "unknown"


def get_app():
    """Return a new FastAPI application instance.

    This function defers import of the API implementation until called,
    preventing side effects at module import time.
    """
    from .main import get_app as _get_app  # local import
    return _get_app()


def get_cli():
    """Return a Typer CLI application for use by aura‑v2 scripts."""
    from .main import app_cli as _cli  # local import
    return _cli
