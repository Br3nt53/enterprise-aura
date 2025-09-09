from .demo import DemoSource
from .jsonl import JsonlSource
try:
    from .kafka import KafkaSource
except Exception:  # aiokafka not installed
    KafkaSource = None

def from_dsn(dsn: str):
    # demo://?fps=2
    # jsonl://<path>?loop=1&interval=1.0
    # kafka://<brokers>/<topic>?group_id=...
    import urllib.parse as u
    p = u.urlparse(dsn)
    q = dict(u.parse_qsl(p.query))
    if p.scheme == "demo":
        fps = float(q.get("fps", "2"))
        return DemoSource(fps=fps)
    if p.scheme == "jsonl":
        path = (p.netloc + p.path).lstrip("/")
        loop = q.get("loop", "1") not in ("0","false","False")
        interval = float(q.get("interval", "1.0"))
        return JsonlSource(path, loop=loop, interval=interval)
    if p.scheme == "kafka":
        assert KafkaSource, "aiokafka is not installed"
        brokers = p.netloc
        topic = p.path.lstrip("/")
        gid = q.get("group_id", "aura-dev")
        return KafkaSource(brokers, topic, gid)
    raise ValueError(f"Unsupported source DSN: {dsn}")
