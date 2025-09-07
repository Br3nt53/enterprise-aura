"""
Lightweight package init. No heavy imports at module import time.
"""
from importlib import metadata as _md

try:
    __version__ = _md.version("aura-v2")
except Exception:
    __version__ = "unknown"

def get_app():
    from .main import get_app as _get
    return _get()

def get_cli():
    from .main import app_cli as _cli
    return _cli
