"""Offline, privacy-preserving comparison of Line 6 SysEx fields.

All offsets include F0. This is statistical evidence, not a parameter map.
No MIDI hardware access, device reads, writes, or replay.
"""
from collections import defaultdict
from sysex_layout import frames_from_capture

def field_profile(text, min_samples=3):
    if not isinstance(min_samples, int) or isinstance(min_samples, bool) or min_samples < 2:
        raise ValueError("min_samples must be an integer >= 2")
    groups=defaultdict(list)
    for endpoint, packet, stamp, payload in frames_from_capture(text):
        if len(payload) < 10:
            continue
        # The field at 7:9 is a candidate correlation identifier, not a known opcode.
        key=(endpoint, len(payload), payload[7:9])
        groups[key].append(payload)
    results=[]
    for (endpoint, length, key), payloads in sorted(groups.items()):
        if len(payloads)<min_samples:
            continue
        offsets=[]
        for offset in range(length):
            counts={}
            for payload in payloads:
                byte=payload[offset]
                counts[byte]=counts.get(byte,0)+1
            if len(counts)>1:
                offsets.append({
                    "offset":offset,
                    "distinct_values":len(counts),
                    "most_common_count":max(counts.values()),
                    "changed_fraction":round(1-max(counts.values())/len(payloads),4),
                })
        results.append({
            "endpoint":f"0x{endpoint:02x}",
            "length":length,
            "candidate_field_7_8":key.hex().upper(),
            "samples":len(payloads),
            "varying_fields":offsets,
            "identical_payloads":len(set(payloads))==1,
        })
    return {
        "groups":results,
        "grouping":"endpoint + length + candidate field 7:9",
        "interpretation":"observed byte variation only; no confirmed parameter semantics",
        "device_writes":False,
    }
