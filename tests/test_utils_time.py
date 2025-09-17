from datetime import datetime
from zoneinfo import ZoneInfo

from aura_v2.utils.time import to_utc


def test_to_utc_with_offset():
    dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    assert to_utc(dt).tzinfo.key == "UTC"  # type: ignore[attr-defined, union-attr]


def test_to_utc_naive_rejected():
    from pytest import raises

    with raises(ValueError):
        to_utc(datetime(2025, 1, 1, 12, 0, 0))  # type: ignore
