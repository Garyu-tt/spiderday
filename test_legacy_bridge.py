import unittest
from unittest.mock import patch
from legacy_bridge import bridge_read, BridgeUnavailable

class FakeResponse:
    status=200
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n): return b'{"presets": []}'

class BridgeTests(unittest.TestCase):
    def test_read_presets(self):
        with patch("legacy_bridge.OPENER.open", return_value=FakeResponse()) as open_mock:
            self.assertEqual(bridge_read("/api/presets", "http://127.0.0.1:5000"),{"presets":[]})
            self.assertEqual(open_mock.call_args.args[0],"http://127.0.0.1:5000/api/presets")
    def test_read_only_routes(self):
        from legacy_bridge import ALLOWED_PATHS
        self.assertEqual(ALLOWED_PATHS, frozenset(("/api/presets", "/api/catalog", "/api/state", "/api/parameters", "/api/board")))
    def test_blocks_write_path(self):
        with self.assertRaises(ValueError): bridge_read("/api/presets/save")
    def test_blocks_remote_host(self):
        with self.assertRaises(ValueError): bridge_read("/api/presets","http://example.com")
    def test_bridge_unavailable(self):
        with patch("legacy_bridge.OPENER.open",side_effect=OSError("offline")):
            with self.assertRaises(BridgeUnavailable): bridge_read("/api/presets")

if __name__=="__main__": unittest.main()
