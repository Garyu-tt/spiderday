#!/usr/bin/env python3
"""Find candidate request/response pairs in a saved USB-MIDI capture offline."""
import argparse
import json
from pathlib import Path
from usb_correlate import correlate

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture",type=Path)
    parser.add_argument("--max-delay-ms",type=float,default=250)
    args=parser.parse_args()
    if args.capture.stat().st_size>2_000_000:
        parser.error("capture too large")
    print(json.dumps(correlate(args.capture.read_text(),max_delay=args.max_delay_ms/1000),indent=2))

if __name__=="__main__": main()
