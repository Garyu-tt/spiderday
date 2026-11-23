import unittest
from dev_proxy import resolve, MOD_HTML, api_allowed

class ProxyTests(unittest.TestCase):
    def test_api_allowlist(self):
        self.assertTrue(api_allowed("GET","/spiderday/api/health"))
        self.assertTrue(api_allowed("HEAD","/spiderday/api/device"))
        self.assertTrue(api_allowed("POST","/spiderday/api/graph/compile"))
        self.assertFalse(api_allowed("POST","/spiderday/api/health"))
        self.assertFalse(api_allowed("GET","/spiderday/api/graph/compile"))
        self.assertFalse(api_allowed("PUT","/spiderday/api/legacy/board"))
        self.assertFalse(api_allowed("OPTIONS","/spiderday/api/health"))
        self.assertFalse(api_allowed("POST","/spiderday/api/effect/gate"))
    def test_api(self):
        self.assertEqual(resolve("/spiderday/api/health"),"http://127.0.0.1:8765/api/health")
    def test_mod_static_root(self):
        self.assertEqual(MOD_HTML.name, "html")
    def test_duplicate_slash_rejected(self):
        with self.assertRaises(ValueError): resolve("/spiderday/api//health")
    def test_encoded_path_rejected(self):
        with self.assertRaises(ValueError): resolve("/spiderday/api/%2e%2e/health")
    def test_non_api_upstream_rejected(self):
        with self.assertRaises(ValueError): resolve("/spiderday/private")
    def test_unknown_path(self):
        with self.assertRaises(ValueError): resolve("/api/effect/gate")
    def test_path_traversal(self):
        with self.assertRaises(ValueError): resolve("/mod/../private")
    def test_query_not_allowed(self):
        with self.assertRaises(ValueError): resolve("/spiderday/api/health?secret=x")

if __name__=="__main__": unittest.main()
