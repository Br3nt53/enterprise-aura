#!/usr/bin/env python3
# migration/run_parallel.py
"""
Run both old and new systems in parallel for validation
"""
import asyncio
import argparse
from pathlib import Path

async def run_parallel_validation(scenario_path: str, config_path: str):
    """Run both systems and compare results"""
    
    # 1. Run legacy system
    legacy_result = run_legacy_system(scenario_path, config_path)
    
    # 2. Run new system
    from aura_v2.infrastructure.config.container import Container
    container = Container()
    container.config.from_yaml(config_path)
    container.wire(modules=[
        'aura_v2.application.use_cases',
        'aura_v2.infrastructure.adapters'
    ])
    
    pipeline = container.tracking_pipeline()
    new_result = await pipeline.run(PipelineContext(
        config=container.config(),
        telemetry=container.telemetry(),
        cancellation_token=asyncio.Event()
    ))
    
    # 3. Compare results
    comparison = compare_results(legacy_result, new_result)
    
    # 4. Generate report
    generate_migration_report(comparison)
    
    return comparison

def run_legacy_system(scenario_path: str, config_path: str) -> dict:
    """Run the existing system"""
    import subprocess
    result = subprocess.run([
        'python', 'tools/run_single.py',
        '--scenario', scenario_path,
        '--params', config_path,
        '--out-dir', 'out/legacy'
    ], capture_output=True)
    
    # Load results
    with open('out/legacy/metrics.json') as f:
        return json.load(f)