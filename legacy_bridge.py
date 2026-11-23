"""Read-only adapter for existing SpyderDay MOD v0.3 HTTP bridge.

Keep the legacy bridge as an independent process. Do not call write endpoints.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

ALLOWED_PATHS = frozenset(("/api/presets", "/api/catalog", "/api/status"))

class BridgeUnavailable(RuntimeError):
    pass

def bridge_read(path, base_url=None, timeout=2):
    if path not in ALLOWED_PATHS:
        raise ValueError("legacy bridge path not on read-only allowlist")
    base = base_url or os.environ.get("SPIDERDAY_LEGACY_URL", "http://127.0.0.1:5000")
    parsed = urlsplit(base)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost") or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("legacy bridge must be an HTTP loopback service")
    url = base.rstrip("/") + path
    try:
        with urlopen(url, timeout=timeout) as response:
            if response.status != 200:
                raise BridgeUnavailable("legacy bridge returned non-200")
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise BridgeUnavailable("legacy response exceeds 1 MiB")
            return json.loads(data)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        raise BridgeUnavailable("legacy bridge unavailable or invalid response") from exc
