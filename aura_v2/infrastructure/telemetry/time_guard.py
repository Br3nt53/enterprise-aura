from datetime import datetime, timezone

from aura_v2.utils.time import to_utc

from .metrics import naive_ts_rejections, ts_skew_seconds


def validate_and_record(
    dt: datetime, *, dev_ok: bool, default_tz: str, max_skew_sec: int = 300
) -> datetime:
    naive_before = dt.tzinfo is None
    utc_dt = to_utc(dt, dev_ok=dev_ok, default_tz=default_tz)
    if naive_before and not dev_ok:
        naive_ts_rejections.inc()
    now = datetime.now(timezone.utc)
    skew = abs((now - utc_dt).total_seconds())
    ts_skew_seconds.observe(skew)
    if skew > max_skew_sec:
        # Decide policy: reject or just record. Here we only record.
        pass
    return utc_dt
