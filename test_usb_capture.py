import unittest
from usb_capture import decode_usb_midi, parse_rows, report

class USBMidiCaptureTests(unittest.TestCase):
    def test_usb_midi_sysex(self):
        midi,errors=decode_usb_midi(bytes.fromhex("04f00001 040c2205 074d00f7"))
        self.assertEqual(midi,bytes.fromhex("f000010c22054d00f7"))
        self.assertEqual(errors,0)

    def test_report_separates_direction(self):
        data=("1\t0.1\t0x02\t12\t04f00001040c2205074d00f7\n"
              "2\t0.2\t0x82\t4\t057ff700\n")
        result=report(data)
        self.assertEqual(result["rows"],2)
        self.assertEqual(result["endpoints"],{"0x02":1,"0x82":1})
        self.assertEqual(result["streams"]["0x02"]["frames"][0]["kind"],"line6")
        self.assertFalse(result["device_writes"])

    def test_invalid_hex(self):
        with self.assertRaises(ValueError): parse_rows("1\t0\t0x02\t4\tZZ")

    def test_invalid_cin(self):
        midi,errors=decode_usb_midi(bytes.fromhex("00f00001"))
        self.assertEqual(midi,b"")
        self.assertEqual(errors,1)

if __name__=="__main__": unittest.main()
