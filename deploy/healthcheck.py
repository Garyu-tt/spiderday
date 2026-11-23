#!/usr/bin/env python3
"""Read-only local Spider Day diagnostics; no device writes."""
import json
import sys
from urllib.error import URLError
from urllib.request import urlopen

ENDPOINTS = (
    ("api", "http://127.0.0.1:8765/api/health"),
    ("proxy", "http://127.0.0.1:8766/spiderday/api/health"),
    ("panel", "http://127.0.0.1:8766/mod/spiderday.html"),
)

def probe(url, timeout=2):
    try:
        with urlopen(url, timeout=timeout) as response:
            body = response.read(4096)
            if response.status != 200:
                return False, f"HTTP {response.status}"
            if url.endswith("/api/health"):
                data = json.loads(body)
                safe = data.get("write_enabled") is False
                connected = data.get("device_connected") is True
                return bool(data.get("ok")) and safe and connected, f"USB connected={connected}, writes={data.get('write_enabled')}"
            return body.lstrip().lower().startswith(b"<!doctype html>"), "HTML served"
    except (URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        return False, type(exc).__name__

def main():
    failed = False
    for name, url in ENDPOINTS:
        ok, detail = probe(url)
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        failed |= not ok
    return int(failed)

if __name__ == "__main__":
    sys.exit(main())
