import unittest
from usb_correlate import correlate, timeline

class USBCorrelateTests(unittest.TestCase):
    def test_pair_across_usb_packets(self):
        rows=("1\t1.000\t0x02\t8\t04f00001040c2200\n"
              "2\t1.001\t0x02\t8\t044d0102040000f7\n"
              "3\t1.015\t0x82\t12\t04f00001040c2200044d0102070000f7\n")
        events=timeline(rows)
        self.assertEqual(len(events),2)
        self.assertEqual(events[0]["field_7_8"],"0102")
        pairs=correlate(rows)
        self.assertEqual(pairs["candidate_pairs"],1)
        self.assertEqual(pairs["candidate_pairs_sample"][0]["delay_ms"],15)
        self.assertFalse(pairs["device_writes"])

    def test_mismatched_key_not_paired(self):
        rows=("1\t1.000\t0x02\t12\t04f00001040c2200044d0102070000f7\n"
              "2\t1.005\t0x82\t12\t04f00001040c2200044d0103070000f7\n")
        self.assertEqual(correlate(rows)["candidate_pairs"],0)

    def test_response_before_request_not_paired(self):
        rows=("1\t1.000\t0x82\t12\t04f00001040c2200044d0102070000f7\n"
              "2\t1.005\t0x02\t12\t04f00001040c2200044d0102070000f7\n")
        self.assertEqual(correlate(rows)["candidate_pairs"],0)

    def test_invalid_window(self):
        with self.assertRaises(ValueError): correlate("",max_delay=0)

if __name__=="__main__": unittest.main()
