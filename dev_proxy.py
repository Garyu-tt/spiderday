"""Minimal reverse proxy serving MOD UI and Spider Day on one loopback origin.

Development/diagnostic use only; this is not an authentication gateway.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import mimetypes
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, unquote
from urllib.request import Request, build_opener, HTTPRedirectHandler
import os

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

OPENER = build_opener(NoRedirect())
TARGETS = {"/spiderday/": "http://127.0.0.1:8765/"}
MOD_HTML = Path(os.environ.get("SPIDERDAY_MOD_HTML", str(Path.home() / "mod-ui-spiderday" / "html"))).resolve()
ALLOWED_METHODS = {"GET", "HEAD", "POST", "OPTIONS"}
MAX_BODY = 65536
API_GET = frozenset(("health","device","blocks","presets","legacy/presets","legacy/catalog","legacy/state","legacy/parameters","legacy/board"))
API_POST = frozenset(("graph/compile",))

def resolve(path):
    parsed = urlsplit(path)
    if unquote(parsed.path) != parsed.path or "\\" in parsed.path:
        raise ValueError("encoded or backslash paths not supported")
    if parsed.query or parsed.fragment:
        raise ValueError("query strings not supported")
    for prefix, target in TARGETS.items():
        if parsed.path.startswith(prefix):
            suffix = parsed.path[len(prefix):]
            if ".." in suffix.split("/") or not suffix.startswith("api/"):
                raise ValueError("invalid API path")
            return target + suffix
    raise ValueError("unsupported path")

class Handler(BaseHTTPRequestHandler):
    def serve_mod(self):
        if self.command not in ("GET", "HEAD"):
            self.send_error(405); return
        try:
            parsed=urlsplit(self.path)
            if parsed.query or parsed.fragment: raise ValueError("query not allowed")
            if unquote(parsed.path) != parsed.path or "\\" in parsed.path:
                raise ValueError("encoded paths not supported")
            suffix=parsed.path.removeprefix("/mod/") or "index.html"
            target=(MOD_HTML / suffix).resolve()
            if not target.is_relative_to(MOD_HTML) or not target.is_file():
                self.send_error(404); return
            data=target.read_bytes()
            if len(data)>4*1024*1024:
                self.send_error(413); return
            self.send_response(200)
            self.send_header("Content-Type",mimetypes.guess_type(str(target))[0] or "application/octet-stream")
            self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            if self.command!="HEAD": self.wfile.write(data)
        except (ValueError,OSError): self.send_error(400)

    def forward(self):
        if self.path.startswith("/mod/"):
            return self.serve_mod()
        if self.command not in ALLOWED_METHODS:
            self.send_error(405); return
        api_path=self.path.removeprefix("/spiderday/api/")
        allowed = API_POST if self.command == "POST" else API_GET
        if not self.path.startswith("/spiderday/api/") or api_path not in allowed:
            self.send_error(404); return
        try:
            target = resolve(self.path)
            size = int(self.headers.get("Content-Length", "0"))
            if size < 0 or size > MAX_BODY:
                self.send_error(413); return
            body = self.rfile.read(size) if size else None
            request = Request(target, data=body, method=self.command)
            if body:
                request.add_header("Content-Type",self.headers.get("Content-Type","application/json"))
            try:
                response = OPENER.open(request,timeout=3)
            except HTTPError as e:
                response = e
            with response:
                data = response.read(2*1024*1024+1)
                if len(data)>2*1024*1024:
                    self.send_error(502,"upstream too large"); return
                self.send_response(response.status)
                self.send_header("Content-Type",response.headers.get("Content-Type","application/octet-stream"))
                self.send_header("Content-Length",str(len(data)))
                self.send_header("Cache-Control","no-store")
                self.end_headers()
                if self.command!="HEAD": self.wfile.write(data)
        except (ValueError,URLError,OSError,TimeoutError) as e:
            self.send_error(502,"upstream unavailable or invalid request")
    do_GET=forward
    do_POST=forward
    do_HEAD=forward
    do_OPTIONS=forward

if __name__=="__main__":
    host="127.0.0.1"
    port=int(os.environ.get("SPIDERDAY_PROXY_PORT","8766"))
    print(f"Spider Day local proxy http://{host}:{port}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()
