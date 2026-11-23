import unittest
from dev_proxy import resolve

class ProxyTests(unittest.TestCase):
    def test_api(self):
        self.assertEqual(resolve("/spiderday/api/health"),"http://127.0.0.1:8765/api/health")
    def test_mod(self):
        self.assertEqual(resolve("/mod/spiderday.html"),"http://127.0.0.1:8888/spiderday.html")
    def test_unknown_path(self):
        with self.assertRaises(ValueError): resolve("/api/effect/gate")
    def test_path_traversal(self):
        with self.assertRaises(ValueError): resolve("/mod/../private")
    def test_query_not_allowed(self):
        with self.assertRaises(ValueError): resolve("/spiderday/api/health?secret=x")

if __name__=="__main__": unittest.main()
