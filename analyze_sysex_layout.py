#!/usr/bin/env python3
"""Analyze variable SysEx offsets in a saved USB capture (offline only)."""
import argparse
import json
from pathlib import Path
from sysex_layout import layout_report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture",type=Path)
    parser.add_argument("--min-group",type=int,default=3)
    args=parser.parse_args()
    if args.capture.stat().st_size>2_000_000:
        parser.error("capture too large")
    print(json.dumps(layout_report(args.capture.read_text(),min_group=args.min_group),indent=2))

if __name__=="__main__": main()
