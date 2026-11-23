#!/usr/bin/env python3
"""Decode an existing MIDI capture offline. No hardware access."""
import argparse
import json
from pathlib import Path
import sys

from sysex_decode import summarize

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture",type=Path)
    parser.add_argument("--max-bytes",type=int,default=65536)
    args=parser.parse_args(argv)
    if not 0 < args.max_bytes <= 65536:
        parser.error("max-bytes must be 1..65536")
    try:
        if args.capture.stat().st_size > args.max_bytes:
            parser.error("capture too large")
        raw=args.capture.read_bytes()
    except OSError as exc:
        print(f"Cannot read capture: {exc}",file=sys.stderr)
        return 1
    print(json.dumps(summarize(raw),indent=2))
    return 0

if __name__=="__main__":
    sys.exit(main())
