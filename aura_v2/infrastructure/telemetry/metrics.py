from prometheus_client import Counter, Histogram

naive_ts_rejections = Counter(
    "aura_naive_ts_rejections_total", "Naive timestamps rejected by API"
)
ts_skew_seconds = Histogram(
    "aura_ts_skew_seconds",
    "Absolute timestamp skew vs server (seconds)",
    buckets=[1,5,10,30,60,120,300,600]
)
