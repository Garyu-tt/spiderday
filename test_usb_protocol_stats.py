import unittest
from usb_protocol_stats import summarize_usb

class USBProtocolStatsTests(unittest.TestCase):
    def test_aggregates_line6_without_raw_hex(self):
        data=("1\t0.1\t0x02\t12\t04f00001040c2205074d00f7\n"
              "2\t0.2\t0x82\t4\t057ff700\n")
        stats=summarize_usb(data)
        self.assertEqual(stats["packets"],2)
        self.assertEqual(stats["endpoints"]["0x02"]["line6_frames"],1)
        self.assertEqual(stats["endpoints"]["0x02"]["line6_lengths"],{9:1})
        self.assertNotIn("hex",str(stats).lower())

if __name__=="__main__": unittest.main()
