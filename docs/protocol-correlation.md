# Spider V 20 USB-MIDI protocol: offline correlation (2026-11-24)

Source: existing private capture `/home/sp/spider_usb_packets.txt` on the
Raspberry Pi. This is **not** a new device interaction. The source capture is
not committed to Git.

## Observations

- 461 USB packets, endpoint `0x02` has 149 packets and endpoint `0x82`
  has 312 packets.
- Reconstructed 148 Line 6 SysEx frames on `0x02` and 154 on `0x82`.
- In a 250-ms matching window, 140 candidate pairs share payload bytes
  at offsets 7 and 8.
- In a stricter 20-ms matching window, **135** candidate pairs remain,
  leaving 13 outgoing frames and 19 incoming frames unmatched.
- The 20-ms candidate-pair delays span **0.324 to 6.01 ms**.
- Several sequential `01xx` identifiers show approximately 4-ms delays
  and incoming payloads larger than their outgoing counterparts.

## Confidence levels

| Claim | Confidence | Evidence |
| --- | --- | --- |
| The capture contains USB-MIDI encoded SysEx | High | Decoded 4-byte USB-MIDI events with valid frame boundaries |
| Both endpoints contain Line 6 manufacturer-prefix frames | High | `F0 00 01 0C` and `F7` delimiters |
| Bytes 7:9 correlate between many directions | High | 135 matches in a 20-ms window |
| These bytes are request/response correlation IDs | Medium, hypothesis | Repeated short-latency matching, no protocol documentation |
| A particular `01xx` value is a named amp effect/parameter | Unknown | No independently validated semantic mapping |
| Sending an observed outgoing packet is read-only | **Not established** | A capture alone cannot prove absence of state changes |

## Reproduce without touching hardware

```sh
cd ~/spiderday
python3 -m unittest discover -q
python3 summarize_usb_capture.py ~/spider_usb_packets.txt
python3 correlate_usb_capture.py ~/spider_usb_packets.txt --max-delay-ms 20
```

No raw capture is exposed by the Spider Day web server. The tool's
`candidate_pairs_sample` reports offsets, packet numbers and lengths, not
complete SysEx payloads.

## Next research steps

1. Compare the old capture with `spider_after_init.txt` and
   `spider_protocol_code_map.txt` after validating their formats.
2. Separate startup negotiation, bulk preset retrieval and unsolicited
   device updates.
3. Establish parameter names only with independent evidence and confidence
   annotations.
4. Keep device writes disabled. Do not replay captured packets as probes
   without explicit review of their potential effects.
