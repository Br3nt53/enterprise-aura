# aura_v2/utils/time.py
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


_UTC = ZoneInfo("UTC")


def _coerce_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except Exception:
        return _UTC


def to_utc(
    value: datetime | None,
    *,
    dev_ok: bool = False,
    default_tz: str = "UTC",
) -> datetime:
    """
    Normalize to a TZ-aware UTC datetime using ZoneInfo('UTC') so tests
    can assert `dt.tzinfo.key == "UTC"`.

    - None  -> now() in UTC
    - Naive -> error unless `dev_ok`, in which case assume `default_tz`
    - Aware -> convert to UTC
    """
    if value is None:
        return datetime.now(_UTC)

    if value.tzinfo is None:
        if not dev_ok:
            raise ValueError(
                "Naive datetime not allowed; set AURA_ACCEPT_NAIVE_TS=1 for dev "
                "or provide an explicit timezone."
            )
        return value.replace(tzinfo=_coerce_tz(default_tz)).astimezone(_UTC)

    return value.astimezone(_UTC)
