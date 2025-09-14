import math


def log_sum_exp(log_weights):
    m = max(log_weights)
    accum = 0.0
    for lw in log_weights:
        accum += math.exp(lw - m)
    return m + math.log(accum + 1e-15)
