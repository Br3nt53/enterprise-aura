import subprocess
import sys


def test_latency_budget_script():
    proc = subprocess.run(
        [sys.executable, "scripts/benchmark_fusion.py"], capture_output=True, text=True
    )
    print(proc.stdout)
    assert proc.returncode == 0, proc.stderr
