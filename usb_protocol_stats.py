"""Aggregate previously captured USB-MIDI traffic without dumping raw payloads."""
from collections import Counter
from usb_capture import parse_rows, decode_usb_midi
from sysex_decode import parse_stream

def summarize_usb(text):
    rows=parse_rows(text)
    streams={}
    invalid=Counter()
    for row in rows:
        endpoint=f"0x{row['endpoint']:02x}"
        stream=streams.setdefault(endpoint,bytearray())
        midi,errors=decode_usb_midi(row["data"])
        stream.extend(midi)
        invalid[endpoint]+=errors
    result={"packets":len(rows),"endpoints":{}}
    for endpoint,stream in sorted(streams.items()):
        frames=parse_stream(bytes(stream))
        line6=[f for f in frames if f.kind=="line6"]
        command_codes=Counter(f.payload[7:9].hex().upper() for f in line6 if len(f.payload)>=10)
        result["endpoints"][endpoint]={
            "midi_bytes":len(stream),
            "frames":len(frames),
            "line6_frames":len(line6),
            "other_frames":sum(f.kind=="other" for f in frames),
            "incomplete_frames":sum(f.kind=="incomplete" for f in frames),
            "invalid_events":invalid[endpoint],
            "line6_prefix_codes":dict(sorted(command_codes.items())),
            "line6_lengths":dict(sorted(Counter(len(f.payload) for f in line6).items())),
        }
    return result
