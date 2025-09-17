"""Lightweight, self-contained diagnostics for dashboard setup.

This module is **not** part of the test suite. It's a dev aid that:
  - verifies FastAPI import (if installed),
  - instantiates a tiny FastAPI app (isolated from project wiring),
  - demonstrates safe route introspection that satisfies type checkers.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple, Type

# We import APIRoute for typing and runtime. If FastAPI isn't present,
# we create a minimal fallback so the module still imports cleanly.
try:  # pragma: no cover - availability varies by environment
    from fastapi import FastAPI
    from fastapi.routing import APIRoute as FastAPIRoute

    FASTAPI_AVAILABLE = True
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
    FastAPIRoute = None  # type: ignore[assignment]
    FASTAPI_AVAILABLE = False


def _load_app() -> Tuple[Any, Optional[Type[Any]]]:
    """Return a tiny FastAPI app and the APIRoute type (if available)."""
    if FASTAPI_AVAILABLE and FastAPI is not None and FastAPIRoute is not None:
        app = FastAPI()

        @app.get("/health")
        def _health() -> dict[str, str]:  # noqa: ANN001 - tiny demo
            return {"status": "ok"}

        return app, FastAPIRoute

    # Fallback "app" with a `routes` attribute of an empty list.
    class _Dummy:
        routes: list[Any] = []

    return _Dummy(), None


def _list_paths() -> list[str]:
    """Introspect app routes in a Pylance-friendly way."""
    app, route_type = _load_app()
    routes: list[Any] = getattr(app, "routes", [])

    # Narrow by runtime check; avoid using a runtime variable as a type.
    if route_type is not None:
        typed: list[Any] = [r for r in routes if isinstance(r, route_type)]
        out: list[str] = []
        for r in typed:
            p = getattr(r, "path", None)
            if isinstance(p, str):
                out.append(p)
        return out

    # Fallback using getattr for unknown route objects.
    out: list[str] = []
    for r in routes:
        p = getattr(r, "path", None)
        if isinstance(p, str):
            out.append(p)
    return out


def main() -> None:
    # Print a tiny status line and discovered paths (if any).
    status = "available" if FASTAPI_AVAILABLE else "unavailable"
    try:
        paths = _list_paths()
    except Exception as exc:  # pragma: no cover
        paths = []
        status += f" (route introspection error: {exc})"
    print(f"FastAPI: {status}; routes: {paths}")


if __name__ == "__main__":  # pragma: no cover
    main()
