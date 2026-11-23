"""Offline analysis of Line 6 payload layouts, without hardware access.

Offsets are measured in decoded SysEx bytes including F0. The fields
are observational and do not imply documented parameter semantics.
"""
from collections import Counter, defaultdict
from usb_capture import parse_rows, decode_usb_midi
from sysex_decode import LINE6_PREFIX

def frames_from_capture(text):
    active={}
    frames=[]
    for row in parse_rows(text):
        endpoint=row["endpoint"]
        midi,_=decode_usb_midi(row["data"])
        for byte in midi:
            if byte==0xF0:
                active[endpoint]=(row["number"],row["timestamp"],bytearray([byte]))
            elif endpoint in active:
                packet,stamp,buf=active[endpoint]
                if byte>=0xF8: continue
                buf.append(byte)
                if len(buf)>4096 or (byte>=0x80 and byte!=0xF7):
                    del active[endpoint]
                elif byte==0xF7:
                    payload=bytes(buf)
                    if payload.startswith(LINE6_PREFIX):
                        frames.append((endpoint,packet,stamp,payload))
                    del active[endpoint]
    return frames

def layout_report(text, min_group=3):
    if min_group<2: raise ValueError("min_group must be >=2")
    groups=defaultdict(list)
    for endpoint,packet,stamp,payload in frames_from_capture(text):
        # Group by endpoint and length, not by guessed effect type.
        groups[(endpoint,len(payload))].append(payload)
    result=[]
    for (endpoint,length),payloads in sorted(groups.items()):
        if len(payloads)<min_group: continue
        fixed=[]
        varying=[]
        for offset in range(length):
            distinct={payload[offset] for payload in payloads}
            (fixed if len(distinct)==1 else varying).append(offset)
        # Restrict output to offsets and counts, never dump raw preset bytes.
        result.append({
            "endpoint":f"0x{endpoint:02x}","length":length,
            "count":len(payloads),
            "fixed_offsets":fixed,
            "varying_offsets":varying,
            "unique_fields_7_8":len({p[7:9] for p in payloads if len(p)>=10}),
            "distinct_payloads":len(set(payloads)),
        })
    return {"groups":result,"grouping":"endpoint + decoded SysEx length",
            "semantics":"unknown; offsets only; no device writes"}
