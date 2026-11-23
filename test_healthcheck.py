"""Unit tests for the read-only deployment healthcheck."""
import io
import json
import unittest
from unittest.mock import patch
from deploy import healthcheck

class FakeResponse:
    status=200
    def __init__(self,body): self.body=body
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n): return self.body[:n]

class HealthcheckTests(unittest.TestCase):
    def test_connected_usb_and_disabled_writes(self):
        payload=json.dumps({"ok":True,"device_connected":True,"write_enabled":False}).encode()
        with patch.object(healthcheck,"urlopen",return_value=FakeResponse(payload)):
            ok,_=healthcheck.probe("http://127.0.0.1:8765/api/health")
        self.assertTrue(ok)

    def test_usb_missing_fails(self):
        payload=json.dumps({"ok":True,"device_connected":False,"write_enabled":False}).encode()
        with patch.object(healthcheck,"urlopen",return_value=FakeResponse(payload)):
            ok,_=healthcheck.probe("http://127.0.0.1:8765/api/health")
        self.assertFalse(ok)

    def test_writes_enabled_fails(self):
        payload=json.dumps({"ok":True,"device_connected":True,"write_enabled":True}).encode()
        with patch.object(healthcheck,"urlopen",return_value=FakeResponse(payload)):
            ok,_=healthcheck.probe("http://127.0.0.1:8765/api/health")
        self.assertFalse(ok)

    def test_panel_requires_html(self):
        with patch.object(healthcheck,"urlopen",return_value=FakeResponse(b"<!doctype html><html>")):
            ok,_=healthcheck.probe("http://127.0.0.1:8766/mod/spiderday.html")
        self.assertTrue(ok)
        with patch.object(healthcheck,"urlopen",return_value=FakeResponse(b"not a panel")):
            ok,_=healthcheck.probe("http://127.0.0.1:8766/mod/spiderday.html")
        self.assertFalse(ok)

if __name__=="__main__": unittest.main()
