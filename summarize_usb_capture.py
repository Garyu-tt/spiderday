#!/usr/bin/env python3
"""Show safe aggregate statistics for a USB capture, without raw payloads."""
import argparse
import json
from pathlib import Path
from usb_protocol_stats import summarize_usb

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture",type=Path)
    args=parser.parse_args()
    if args.capture.stat().st_size>2_000_000:
        parser.error("capture too large")
    print(json.dumps(summarize_usb(args.capture.read_text()),indent=2))

if __name__=="__main__": main()
