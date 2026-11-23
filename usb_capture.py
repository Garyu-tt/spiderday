"""Offline analysis of tab-separated USB capture exports.

Rows: packet_number, timestamp, endpoint, reported_length, hex_bytes.
USB-MIDI event packets have a 1-byte CIN/cable header per four-byte event.
This module never accesses a USB or MIDI device.
"""
import re
from collections import Counter
from sysex_decode import summarize

HEX = re.compile(r"^[0-9a-fA-F]*$")
CIN_LENGTH = {0x2:2,0x3:3,0x4:3,0x5:1,0x6:2,0x7:3,
              0x8:3,0x9:3,0xA:3,0xB:3,0xC:2,0xD:2,0xE:3,0xF:1}

def parse_rows(text, max_rows=20000):
    rows=[]
    for line_no,line in enumerate(text.splitlines(),1):
        if not line.strip(): continue
        if len(rows)>=max_rows: raise ValueError("too many capture rows")
        parts=line.split("\t")
        if len(parts)!=5: raise ValueError(f"line {line_no}: expected 5 columns")
        number,timestamp,endpoint,length,hexdata=parts
        if not HEX.fullmatch(hexdata) or len(hexdata)%2:
            raise ValueError(f"line {line_no}: invalid hex")
        data=bytes.fromhex(hexdata)
        if len(data)>65536: raise ValueError(f"line {line_no}: packet too large")
        rows.append({"number":int(number),"timestamp":float(timestamp),
                     "endpoint":int(endpoint,16),"reported_length":int(length),
                     "data":data})
    return rows

def decode_usb_midi(data):
    """Return (MIDI bytes, invalid event count). Assumes 4-byte USB-MIDI packets."""
    out=bytearray()
    invalid=0
    if len(data)%4: invalid+=1
    for offset in range(0,len(data)-len(data)%4,4):
        header,b1,b2,b3=data[offset:offset+4]
        count=CIN_LENGTH.get(header&0x0f)
        if count is None:
            invalid+=1
            continue
        out.extend((b1,b2,b3)[:count])
    return bytes(out),invalid

def report(text):
    rows=parse_rows(text)
    endpoints=Counter()
    midi_by_endpoint={}
    invalid=Counter()
    for row in rows:
        key=f"0x{row['endpoint']:02x}"
        endpoints[key]+=1
        midi,errors=decode_usb_midi(row["data"])
        midi_by_endpoint.setdefault(key,bytearray()).extend(midi)
        invalid[key]+=errors
    return {
        "rows":len(rows),
        "endpoints":dict(sorted(endpoints.items())),
        "streams":{key:{"invalid_events":invalid[key],**summarize(bytes(value))}
                   for key,value in sorted(midi_by_endpoint.items())},
        "device_writes":False
    }
