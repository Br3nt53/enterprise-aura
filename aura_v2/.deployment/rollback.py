#!/usr/bin/env python3
# deployment/rollback.py
"""
Rollback to previous version if metrics degrade
"""

import subprocess
from typing import Dict


def check_metrics_health(new_metrics: Dict, baseline_metrics: Dict) -> bool:
    """Check if new metrics are acceptable"""
    degradation_threshold = 0.05  # Allow 5% degradation

    for key in ["mota", "precision", "recall"]:
        if key in new_metrics and key in baseline_metrics:
            degradation = (baseline_metrics[key] - new_metrics[key]) / baseline_metrics[
                key
            ]
            if degradation > degradation_threshold:
                return False
    return True


def rollback_deployment():
    """Rollback to previous version"""
    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["docker-compose", "down"])
    subprocess.run(["docker-compose", "up", "-d"])
