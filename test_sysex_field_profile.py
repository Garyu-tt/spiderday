import unittest
from sysex_field_profile import field_profile
from test_sysex_layout import packet

class FieldProfileTests(unittest.TestCase):
    def test_repeated_identifier_tracks_changed_offsets(self):
        base=bytes.fromhex("f000010c22054d010201f7")
        changed=bytes.fromhex("f000010c22054d010202f7")
        capture=(packet(1,0x82,base)+packet(2,0x82,changed)+
                 packet(3,0x82,base))
        groups=field_profile(capture)["groups"]
        self.assertEqual(len(groups),1)
        group=groups[0]
        self.assertEqual(group["candidate_field_7_8"],"0102")
        self.assertEqual(group["varying_fields"],[{
            "offset":9,"distinct_values":2,"most_common_count":2,
            "changed_fraction":0.3333
        }])
        self.assertFalse(group["identical_payloads"])

    def test_separates_different_candidate_ids(self):
        a=bytes.fromhex("f000010c22054d010201f7")
        b=bytes.fromhex("f000010c22054d010301f7")
        capture=packet(1,0x82,a)+packet(2,0x82,b)
        self.assertEqual(field_profile(capture,min_samples=2)["groups"],[])

    def test_identical_frames_have_no_variation(self):
        a=bytes.fromhex("f000010c22054d010201f7")
        capture=packet(1,0x82,a)+packet(2,0x82,a)
        group=field_profile(capture,min_samples=2)["groups"][0]
        self.assertTrue(group["identical_payloads"])
        self.assertEqual(group["varying_fields"],[])

    def test_invalid_sample_threshold(self):
        for value in (1,True,2.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                field_profile("",min_samples=value)

if __name__=="__main__": unittest.main()
