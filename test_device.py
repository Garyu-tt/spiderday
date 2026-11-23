import tempfile
import unittest
from pathlib import Path
from device import probe_usb

class UsbProbeTests(unittest.TestCase):
    def test_detects_spider_v20(self):
        with tempfile.TemporaryDirectory() as tmp:
            dev = Path(tmp)/"1-1"
            dev.mkdir()
            (dev/"idVendor").write_text("0e41\n")
            (dev/"idProduct").write_text("506f\n")
            (dev/"product").write_text("Spider V 20\n")
            devices=probe_usb(tmp)
            self.assertEqual(len(devices),1)
            self.assertEqual(devices[0]["product"],"Spider V 20")
    def test_ignores_other_devices(self):
        with tempfile.TemporaryDirectory() as tmp:
            dev=Path(tmp)/"2-1"
            dev.mkdir()
            (dev/"idVendor").write_text("abcd")
            (dev/"idProduct").write_text("506f")
            self.assertEqual(probe_usb(tmp),[])

if __name__=="__main__":
    unittest.main()
