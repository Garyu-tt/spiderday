# Offline SysEx field research

Spider Day can now analyze saved USB-MIDI captures without opening the
amplifier's MIDI device or sending any commands.

## Commands

```sh
cd ~/spiderday
python3 -m unittest discover -q
python3 analyze_sysex_layout.py ~/spider_usb_packets.txt
python3 analyze_sysex_fields.py ~/spider_usb_packets.txt --min-samples 3
python3 correlate_usb_capture.py ~/spider_usb_packets.txt --max-delay-ms 20
```

The layout report groups by endpoint and frame length, and marks fixed and
varying byte offsets. The field profile is narrower: it groups by endpoint,
length, and the **observed** two-byte value at offsets 7:9. It reports
sample count, changed byte positions, distinct value counts, and the fraction
that differs from the modal byte. It does not dump preset content.

Do not interpret the two-byte grouping field as a verified parameter or
opcode. Repeated frames can reflect retries, initialization, preset reads,
or unrelated notifications. Variation at a byte offset does not prove it
represents an effect control. Cross-capture validation and independent
evidence are required before naming a field.

The parser now rejects nonfinite timestamps, malformed endpoint metadata,
and declared packet lengths that differ from actual bytes. The analyzers
have no live USB access, and the backend continues to prohibit DSP writes.

## Validation status

The changes in this research phase have been committed to GitHub. A fresh
Raspberry Pi test/deployment is **not confirmed** until the Pi is reachable
again. The prior confirmed baseline was 53 passing Python tests.
