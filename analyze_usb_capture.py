#!/usr/bin/env python3
"""Analyze existing USB-MIDI TSV captures offline; no USB hardware access."""
import argparse
import json
from pathlib import Path
from usb_capture import report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture",type=Path)
    parser.add_argument("--max-bytes",type=int,default=2_000_000)
    args=parser.parse_args()
    if not 0 < args.max_bytes <= 10_000_000:
        parser.error("max-bytes must be 1..10000000")
    if args.capture.stat().st_size>args.max_bytes:
        parser.error("capture exceeds maximum size")
    print(json.dumps(report(args.capture.read_text(errors="replace")),indent=2))

if __name__=="__main__": main()
