"""Offline MIDI/SysEx framing analysis. Never accesses hardware."""
from dataclasses import dataclass

LINE6_PREFIX = bytes.fromhex("F0 00 01 0C")
MAX_FRAME = 4096

@dataclass(frozen=True)
class Frame:
    offset: int
    kind: str
    payload: bytes

def parse_stream(data: bytes, max_frame: int = MAX_FRAME):
    """Extract complete SysEx frames, preserving offsets and reporting truncation."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if not 2 <= max_frame <= MAX_FRAME:
        raise ValueError("invalid maximum frame size")
    frames = []
    start = None
    buf = bytearray()
    for offset, value in enumerate(data):
        if value == 0xF0:
            if start is not None:
                frames.append(Frame(start, "incomplete", bytes(buf)))
            start = offset
            buf = bytearray([value])
        elif start is not None:
            # MIDI real-time messages may appear inside a SysEx transfer.
            if value >= 0xF8:
                continue
            buf.append(value)
            if len(buf) > max_frame:
                frames.append(Frame(start, "oversize", bytes(buf[:max_frame])))
                start = None
                buf.clear()
            elif value == 0xF7:
                frames.append(Frame(start, "line6" if buf.startswith(LINE6_PREFIX) else "other", bytes(buf)))
                start = None
                buf.clear()
            elif value >= 0x80:
                frames.append(Frame(start, "invalid", bytes(buf)))
                start = None
                buf.clear()
    if start is not None:
        frames.append(Frame(start, "incomplete", bytes(buf)))
    return frames

def summarize(data: bytes):
    frames = parse_stream(data)
    return {
        "bytes": len(data),
        "frames": [
            {"offset": f.offset, "kind": f.kind, "length": len(f.payload),
             "hex": f.payload.hex(" ").upper()}
            for f in frames
        ],
        "device_writes": False,
    }
