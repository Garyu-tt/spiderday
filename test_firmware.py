import struct
import unittest
import zlib
from firmware.inspect_svu import inspect

def chunk(name, payload):
    return name + struct.pack(">I",len(payload)) + payload + (b"\0" if len(payload)%2 else b"")

def form(*parts):
    body=b"L6FF"+b"".join(parts)
    return b"FORM"+struct.pack(">I",len(body))+body

class FirmwareTests(unittest.TestCase):
    def test_valid_zlib(self):
        data=form(chunk(b"HEAD",b"test"),chunk(b"data",zlib.compress(b"payload")))
        info=inspect(data)
        self.assertEqual(info["chunks"][1]["decoded_size"],7)
        self.assertEqual(info["chunks"][1]["zlib"],"decoded")
    def test_invalid_length(self):
        data=form(chunk(b"HEAD",b"ok"))
        with self.assertRaises(ValueError):
            inspect(data[:-1])
    def test_truncated_chunk(self):
        data=form(b"HEAD")
        with self.assertRaises(ValueError):
            inspect(data)

if __name__=="__main__":
    unittest.main()
