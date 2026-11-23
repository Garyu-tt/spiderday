#!/usr/bin/env python3
"""Explicit, bounded, read-only ALSA raw MIDI capture.

Not run by the server. Does not send MIDI or initialize the legacy bridge.
Opening an ALSA MIDI input can affect other readers; run only with permission
and after checking whether the device is already in use.
"""
import argparse
import os
from pathlib import Path
import select
import stat
import sys
import time

MAX_BYTES = 65536
MAX_SECONDS = 30

def capture(path: Path, seconds: float, limit: int) -> bytes:
    if not (0 < seconds <= MAX_SECONDS and 0 < limit <= MAX_BYTES):
        raise ValueError("capture bounds exceeded")
    if not path.name.startswith("midiC") or path.parent != Path("/dev/snd"):
        raise ValueError("only /dev/snd/midiC*D* is supported")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY)
    try:
        if not stat.S_ISCHR(os.fstat(fd).st_mode):
            raise ValueError("expected a character device")
        deadline = time.monotonic() + seconds
        data = bytearray()
        while len(data) < limit:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            readable, _, _ = select.select([fd], [], [], remaining)
            if not readable:
                break
            try:
                chunk = os.read(fd, min(4096, limit - len(data)))
            except BlockingIOError:
                continue
            if not chunk:
                break
            data.extend(chunk)
        return bytes(data)
    finally:
        os.close(fd)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device",type=Path,required=True)
    parser.add_argument("--seconds",type=float,default=5)
    parser.add_argument("--max-bytes",type=int,default=8192)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; refusing overwrite")
    try:
        data=capture(args.device,args.seconds,args.max_bytes)
        fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        try:
            with os.fdopen(fd,"wb") as file:
                file.write(data)
        except BaseException:
            args.output.unlink(missing_ok=True)
            raise
    except (OSError,ValueError) as error:
        print(f"Capture failed: {error}",file=sys.stderr)
        return 1
    print(f"Captured {len(data)} bytes into {args.output} (read-only; no MIDI writes)")
    return 0

if __name__=="__main__":
    sys.exit(main())
