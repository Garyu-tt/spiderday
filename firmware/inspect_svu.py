"""Read-only parser for Line 6 L6FF/SVU containers. Never flashes devices."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

def inspect(data: bytes) -> dict:
    if len(data) < 12 or data[:4] != b"FORM" or data[8:12] != b"L6FF":
        raise ValueError("not a FORM/L6FF container")
    form_size = struct.unpack_from(">I", data, 4)[0]
    if form_size + 8 != len(data):
        raise ValueError("FORM length mismatch")
    offset, chunks = 12, []
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError("truncated chunk header")
        tag = data[offset:offset+4]
        size = struct.unpack_from(">I", data, offset+4)[0]
        begin, end = offset+8, offset+8+size
        if end > len(data):
            raise ValueError("chunk exceeds container")
        payload = data[begin:end]
        item = {"tag":tag.decode("ascii", errors="replace"), "size":size,
                "offset":offset, "sha256":hashlib.sha256(payload).hexdigest()}
        if tag == b"data":
            try:
                decoded = zlib.decompress(payload)
            except zlib.error:
                item["zlib"] = "not-decodable"
            else:
                item["zlib"] = "decoded"
                item["decoded_size"] = len(decoded)
                item["decoded_sha256"] = hashlib.sha256(decoded).hexdigest()
        chunks.append(item)
        offset = end + (size & 1)
    if offset != len(data):
        raise ValueError("invalid IFF alignment")
    return {"format":"FORM/L6FF", "size":len(data),
            "sha256":hashlib.sha256(data).hexdigest(), "chunks":chunks}

def main():
    parser = argparse.ArgumentParser(description="Inspect stock Spider V SVU without device access")
    parser.add_argument("firmware", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.firmware.read_bytes()), indent=2))

if __name__ == "__main__":
    main()
