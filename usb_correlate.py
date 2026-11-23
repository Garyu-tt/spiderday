"""Offline USB-MIDI SysEx frame reconstruction with timestamps and endpoint directions.

This is a heuristic timeline: pairing by a two-byte payload field is not
proof of a request/response relationship.
"""
from collections import Counter
from usb_capture import parse_rows, decode_usb_midi
from sysex_decode import LINE6_PREFIX

def timeline(text):
    rows=parse_rows(text)
    active={}
    events=[]
    for row in rows:
        endpoint=row["endpoint"]
        midi,invalid=decode_usb_midi(row["data"])
        if invalid:
            events.append({"packet":row["number"],"endpoint":f"0x{endpoint:02x}","kind":"invalid_usb_event"})
        for byte in midi:
            if byte==0xF0:
                active[endpoint]={"start":row["timestamp"],"packet":row["number"],"data":bytearray([byte])}
            elif endpoint in active:
                frame=active[endpoint]
                if byte>=0xF8:
                    continue
                frame["data"].append(byte)
                if len(frame["data"])>4096:
                    events.append({"packet":frame["packet"],"endpoint":f"0x{endpoint:02x}","kind":"oversize"})
                    del active[endpoint]
                elif byte==0xF7:
                    payload=bytes(frame["data"])
                    line6=payload.startswith(LINE6_PREFIX)
                    events.append({
                        "packet":frame["packet"],"time":frame["start"],
                        "endpoint":f"0x{endpoint:02x}",
                        "kind":"line6" if line6 else "other",
                        "length":len(payload),
                        "field_7_8":payload[7:9].hex().upper() if line6 and len(payload)>=10 else None,
                    })
                    del active[endpoint]
                elif byte>=0x80:
                    events.append({"packet":frame["packet"],"endpoint":f"0x{endpoint:02x}","kind":"invalid_status"})
                    del active[endpoint]
    return sorted(events,key=lambda e:e["packet"])

def correlate(text, request_endpoint=0x02, response_endpoint=0x82, max_delay=0.25):
    if not 0<max_delay<=10:
        raise ValueError("max_delay must be within (0,10] seconds")
    events=timeline(text)
    requests=[e for e in events if e["kind"]=="line6" and e["endpoint"]==f"0x{request_endpoint:02x}"]
    responses=[e for e in events if e["kind"]=="line6" and e["endpoint"]==f"0x{response_endpoint:02x}"]
    matched=[]
    used=set()
    for request in requests:
        candidates=[(index,response) for index,response in enumerate(responses)
                    if index not in used
                    and response["field_7_8"]==request["field_7_8"]
                    and 0 <= response["time"]-request["time"] <= max_delay]
        if candidates:
            index,response=min(candidates,key=lambda pair:pair[1]["time"]-request["time"])
            used.add(index)
            matched.append({
                "field_7_8":request["field_7_8"],
                "request_packet":request["packet"],
                "response_packet":response["packet"],
                "delay_ms":round((response["time"]-request["time"])*1000,3),
                "request_length":request["length"],
                "response_length":response["length"],
            })
    return {
        "heuristic":"same payload bytes 7:9 and response within window; NOT confirmed protocol semantics",
        "request_frames":len(requests),
        "response_frames":len(responses),
        "candidate_pairs":len(matched),
        "unmatched_requests":len(requests)-len(matched),
        "unmatched_responses":len(responses)-len(matched),
        "candidate_pairs_sample":matched[:25],
        "candidate_delay_ms": {
            "min":min((m["delay_ms"] for m in matched),default=None),
            "max":max((m["delay_ms"] for m in matched),default=None),
        },
        "device_writes":False,
    }
