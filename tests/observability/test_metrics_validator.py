# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

import pytest

psutil = pytest.importorskip(
    "psutil", reason="psutil not installed; metrics smoke skipped"
)


def test_metrics_psutil_smoke() -> None:
    cpu = psutil.cpu_percent(interval=0.0)
    mem = psutil.virtual_memory().percent
    assert isinstance(cpu, (int, float))
    assert 0 <= cpu <= 100
    assert 0 <= mem <= 100
