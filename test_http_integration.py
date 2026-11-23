"""HTTP-level regression tests for Spider Day API and proxy."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from backend import Handler as APIHandler
from dev_proxy import Handler as ProxyHandler

class HTTPTests(unittest.TestCase):
    def run_server(self, handler):
        server=ThreadingHTTPServer(("127.0.0.1",0),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(thread.join,2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server.server_address[1]

    def request(self,port,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
        try:
            conn.request(method,path,body,headers or {})
            response=conn.getresponse()
            return response.status,dict(response.getheaders()),response.read()
        finally:
            conn.close()

    def test_proxy_forbids_effect_writes(self):
        port=self.run_server(ProxyHandler)
        for method,path in (("POST","/spiderday/api/effect/gate"),
                            ("PUT","/spiderday/api/legacy/board"),
                            ("GET","/spiderday/api/graph/compile"),
                            ("OPTIONS","/spiderday/api/health")):
            status,_,_=self.request(port,method,path)
            self.assertIn(status,(404,405))

    def test_proxy_static_panel_and_head(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"spiderday.html").write_text("<!doctype html><title>Spider Day</title>")
            with patch("dev_proxy.MOD_HTML",root):
                port=self.run_server(ProxyHandler)
                status,headers,data=self.request(port,"GET","/mod/spiderday.html")
                self.assertEqual(status,200)
                self.assertIn(b"Spider Day",data)
                status,headers,data=self.request(port,"HEAD","/mod/spiderday.html")
                self.assertEqual(status,200)
                self.assertEqual(data,b"")
                status,_,_=self.request(port,"GET","/mod/%2e%2e/secret")
                self.assertNotEqual(status,200)

    def test_api_compile_and_origin(self):
        port=self.run_server(APIHandler)
        graph={"nodes":[{"id":"in","type":"input"},{"id":"out","type":"output"}],
               "edges":[{"source":"in","target":"out"}]}
        payload=json.dumps(graph)
        headers={"Content-Type":"application/json"}
        status,_,body=self.request(port,"POST","/api/graph/compile",payload,headers)
        self.assertEqual(status,200)
        self.assertEqual(json.loads(body)["mode"],"preview-only")
        status,_,_=self.request(port,"POST","/api/graph/compile",payload,
                               {**headers,"Origin":"https://untrusted.example"})
        self.assertEqual(status,403)
        status,_,_=self.request(port,"POST","/api/graph/compile",payload,
                               {**headers,"Transfer-Encoding":"chunked"})
        self.assertEqual(status,400)
        status,_,_=self.request(port,"OPTIONS","/api/graph/compile",None,
                               {"Origin":"https://untrusted.example"})
        self.assertEqual(status,403)
        malformed=payload.replace('"edges":', '"extra": NaN, "edges":')
        status,_,_=self.request(port,"POST","/api/graph/compile",malformed,headers)
        self.assertEqual(status,400)

if __name__=="__main__":
    unittest.main()
