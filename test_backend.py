import unittest
import math
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
    def test_nonfinite_parameter_rejected(self):
        for value in (math.nan,math.inf,-math.inf):
            graph={'nodes':[{'id':'a','type':'input','parameters':{'gain':value}},
                            {'id':'b','type':'output'}],
                   'edges':[{'source':'a','target':'b'}]}
            with self.assertRaisesRegex(ValueError,'finite'):
                compile_graph(graph)
    def test_deep_parameters_rejected(self):
        nested={'value':1}
        for _ in range(10): nested={'next':nested}
        graph={'nodes':[{'id':'a','type':'input','parameters':nested},
                        {'id':'b','type':'output'}],
               'edges':[{'source':'a','target':'b'}]}
        with self.assertRaisesRegex(ValueError,'deeply'):
            compile_graph(graph)
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
