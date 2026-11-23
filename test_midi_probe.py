import tempfile
import unittest
from pathlib import Path
from midi_probe import inventory

class MIDIProbeTests(unittest.TestCase):
    def test_card_inventory_without_opening_device(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            dev=root/"snd"
            dev.mkdir()
            (dev/"midiC1D0").touch()
            (dev/"midiC0D0").touch()
            cards=root/"cards"
            cards.write_text(" 0 [Headphones     ]: bcm2835 - Headphones\n 1 [S20            ]: USB-Audio - Spider V 20\n")
            result=inventory(dev,cards)
            self.assertEqual([d["card"] for d in result["midi_devices"]],[0,1])
            self.assertIn("Spider V 20",result["midi_devices"][1]["label"])
            self.assertFalse(result["monitoring"])
            self.assertFalse(result["writes_enabled"])

    def test_missing_cards_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"midiC2D0").touch()
            result=inventory(root,root/"missing")
            self.assertEqual(result["midi_devices"][0]["label"],"unknown")

if __name__=="__main__": unittest.main()
