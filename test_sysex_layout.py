import unittest
from sysex_layout import frames_from_capture, layout_report

def packet(num,endpoint,frame):
    chunks=[]
    for i in range(0,len(frame),3):
        group=frame[i:i+3]
        final=i+3>=len(frame)
        cin=(4+len(group)) if final else 4
        chunks.extend([cin,*group,*([0]*(3-len(group)))])
    return f"{num}\t1.0\t0x{endpoint:02x}\t{len(chunks)}\t{bytes(chunks).hex()}\n"

class LayoutTests(unittest.TestCase):
    def test_fixed_and_variable_offsets(self):
        a=bytes.fromhex("f000010c22054d010201f7")
        b=bytes.fromhex("f000010c22054d010202f7")
        c=bytes.fromhex("f000010c22054d010203f7")
        capture=packet(1,0x82,a)+packet(2,0x82,b)+packet(3,0x82,c)
        report=layout_report(capture)
        self.assertEqual(len(report["groups"]),1)
        group=report["groups"][0]
        self.assertEqual(group["varying_offsets"],[9])
        self.assertEqual(group["distinct_payloads"],3)
        self.assertEqual(group["unique_fields_7_8"],1)

    def test_group_threshold(self):
        capture=packet(1,0x82,bytes.fromhex("f000010c22054d010201f7"))
        self.assertEqual(layout_report(capture)["groups"],[])

    def test_reject_invalid_group(self):
        with self.assertRaises(ValueError): layout_report("",min_group=1)

if __name__=="__main__": unittest.main()
