# Stock firmware analysis: Spider V 20, 2.01.0

Source: owner-supplied `a41_2.01.0.svu`. Analysis is offline, no hardware flashing.

- File size: 2,244,744 bytes
- SHA-256: `0d513d8df7ab1e5c6c768892ca1ebcd5182d725d37f6049479c36b3861b56464`
- FORM type: `L6FF`
- Chunks: `HEAD` (52 bytes), `dinf` (16 bytes), `data` (2,244,639 bytes)
- `data` is zlib-decodable to 2,243,948 bytes
- Decoded SHA-256: `617cea79cca06e91b34003323e1998cb72577cb284b3b139ac84b2f42c6d1eae`

## Usage

```sh
python3 firmware/inspect_svu.py /path/to/a41_2.01.0.svu
python3 -m unittest discover -v
```

## Next research gates

1. Reverse-engineer `HEAD` and `dinf` semantics, firmware target identification.
2. Establish whether decompressed `data` is encrypted, encoded or compressed again. High entropy alone is not proof of encryption.
3. Identify DSP CPU, bootloader and firmware update protocol from independent evidence.
4. Establish read-back backup and tested recovery procedure **before** any experimental flash.
5. Separate host-side graph validation from actual DSP code generation.

No firmware binaries or secret device data are committed. This document does not claim custom firmware is available.
