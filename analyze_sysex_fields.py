#!/usr/bin/env python3
"""Analyze repeated Line 6 SysEx fields in a saved USB capture, offline."""
import argparse
import json
from pathlib import Path
from sysex_field_profile import field_profile

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture",type=Path)
    parser.add_argument("--min-samples",type=int,default=3)
    args=parser.parse_args()
    if args.capture.stat().st_size>2_000_000:
        parser.error("capture too large")
    print(json.dumps(field_profile(args.capture.read_text(),
                                   min_samples=args.min_samples),indent=2))

if __name__=="__main__": main()
