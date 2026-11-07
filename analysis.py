#!/usr/bin/env python3
"""Offline, reproducible Evidence Room entry point."""
import argparse
from src.evidence.pipeline import run
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    run()
