import unittest
from sysex_decode import parse_stream, summarize

class SysExDecodeTests(unittest.TestCase):
    def test_line6_and_other(self):
        raw=bytes.fromhex("90 40 7F F0 00 01 0C 22 05 4D F7 F0 7D 01 F7")
        frames=parse_stream(raw)
        self.assertEqual([(f.offset,f.kind) for f in frames],[(3,"line6"),(11,"other")])
        self.assertEqual(summarize(raw)["device_writes"],False)

    def test_truncated(self):
        frames=parse_stream(bytes.fromhex("F0 00 01 0C 22"))
        self.assertEqual(frames[0].kind,"incomplete")

    def test_restart_discards_partial(self):
        frames=parse_stream(bytes.fromhex("F0 01 F0 7D F7"))
        self.assertEqual([f.kind for f in frames],["incomplete","other"])

    def test_realtime_interleaving(self):
        frames=parse_stream(bytes.fromhex("F0 7D F8 01 FE F7"))
        self.assertEqual(frames[0].payload,bytes.fromhex("F0 7D 01 F7"))

    def test_invalid_status(self):
        self.assertEqual(parse_stream(bytes.fromhex("F0 7D 90"))[0].kind,"invalid")

    def test_bounded(self):
        self.assertEqual(parse_stream(bytes([0xF0]+[1]*15),max_frame=8)[0].kind,"oversize")

    def test_input_contract(self):
        with self.assertRaises(TypeError): parse_stream("F0 7D F7")
        with self.assertRaises(ValueError): parse_stream(b"",max_frame=1)

if __name__=="__main__": unittest.main()
