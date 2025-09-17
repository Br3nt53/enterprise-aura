#!/usr/bin/env python3
import pathlib
import runpy

target = pathlib.Path(__file__).with_name("benchmarks").joinpath("fusion_benchmark.py")
runpy.run_path(str(target), run_name="__main__")
