import unittest
from backend import compile_graph

class GraphTests(unittest.TestCase):
    def test_linear(self):
        graph={'nodes':[{'id':'a','type':'input'},{'id':'b','type':'gate'},{'id':'c','type':'output'}],
               'edges':[{'source':'a','target':'b'},{'source':'b','target':'c'}]}
        self.assertEqual([n['type'] for n in compile_graph(graph)['chain']],['input','gate','output'])
    def test_missing_terminals_rejected(self):
        with self.assertRaisesRegex(ValueError,'input and output'):
            compile_graph({'nodes':[{'id':'a','type':'gate'}],'edges':[]})
    def test_non_object_rejected(self):
        with self.assertRaisesRegex(ValueError,'object'):
            compile_graph([])
    def test_empty_node_id_rejected(self):
        with self.assertRaises(ValueError):
            compile_graph({'nodes':[{'id':'','type':'input'},{'id':'b','type':'output'}], 'edges':[{'source':'','target':'b'}]})
    def test_reverse_rejected(self):
        with self.assertRaises(ValueError):
            compile_graph({'nodes':[{'id':'a','type':'output'},{'id':'b','type':'input'}],
                           'edges':[{'source':'a','target':'b'}]})
    def test_parallel_rejected(self):
        with self.assertRaises(ValueError):
            compile_graph({'nodes':[{'id':'a','type':'input'},{'id':'b','type':'gate'},{'id':'c','type':'output'}],
                           'edges':[{'source':'a','target':'b'},{'source':'a','target':'c'}]})
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            compile_graph({'nodes':[{'id':'a','type':'gate'},{'id':'b','type':'gate'}],
                           'edges':[{'source':'a','target':'b'}]})

if __name__=='__main__': unittest.main()
