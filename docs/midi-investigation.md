# Passive MIDI / SysEx investigation

The Line 6 Spider V 20 was detected on Raspberry Pi as USB `0e41:506f`,
ALSA `card 1, device 0`, with `/dev/snd/midiC1D0`.

## Safety boundaries
- `midi_probe.py` inventories ALSA device nodes and never opens them.
- `tools/capture_midi.py` opens one selected raw MIDI node **read-only**.
  It has a hard 30-second and 64-KiB cap, never sends MIDI, and refuses to
  overwrite an existing output file.
- `sysex_decode.py` and `decode_capture.py` operate only on existing bytes.
- None of these tools starts the legacy bridge or enables effect writes.
- Capturing from ALSA raw MIDI can compete with other readers. Check the
  existing process users first; do not run simultaneous capture services.

## Verified Pi baseline (2026-11-24)
A three-second passive capture on `/dev/snd/midiC1D0` succeeded, but yielded
**zero bytes**. This does **not** mean the interface is defective or that
the amp never transmits MIDI. It means there was no incoming data during
that passive window. No SysEx handshake or request was sent.

## Repeat a capture, manually and deliberately
```sh
fuser /dev/snd/midiC1D0
cd ~/spiderday
python3 tools/capture_midi.py --device /dev/snd/midiC1D0 \
  --seconds 10 --max-bytes 8192 --output /tmp/spiderday-midi-session.bin
python3 decode_capture.py /tmp/spiderday-midi-session.bin
```

The raw capture may contain device or preset information. Keep it private.
Use a fresh filename for each session. Do not expose capture files through
the web API.

## What remains unverified
- Whether the amp sends unsolicited SysEx when physical knobs change.
- Whether the device requires a host-initiated, read-only handshake.
- Whether ALSA raw MIDI receives all proprietary USB traffic.
- Whether any observed message is a parameter read or a state change.

The decoder recognizes the manufacturer prefix `F0 00 01 0C`, but does
not claim to understand the proprietary payload. Any future active
protocol probing must be separately reviewed before sending bytes.
