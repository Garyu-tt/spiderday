# Spider Day

Raspberry Pi control plane for the Line 6 Spider V 20, intended to connect to the owner's fork [MOD UI](https://github.com/Garyu-tt/mod-ui).

## Current status

This is an **experimental, read-only preview API**. It does not flash firmware, send SysEx commands or process audio. The native Spider V DSP remains the audio engine. The existing Raspberry Pi project `~/SpyderDay-MOD-v0.3/spider_bridge.py` is the intended hardware adapter, but has **not yet been migrated**.

## Run on Raspberry Pi

```bash
python3 backend.py
```

Defaults to `127.0.0.1:8765`. To expose to a trusted LAN, set `SPIDERDAY_HOST=0.0.0.0`; **do not expose this prototype publicly**. Set `SPIDERDAY_UI_ORIGIN` to the MOD UI origin. No authentication is implemented.

Endpoints: `GET /api/health`, `GET /api/device`, `GET /api/blocks`, `GET /api/presets`, `POST /api/graph/compile`.

`GET /api/device` reads Linux sysfs (`/sys/bus/usb/devices`) and detects the known Spider V 20 USB VID:PID `0e41:506f`. It does not open the MIDI port or transmit anything. `GET /api/health` now reports actual USB presence (not DSP readiness).

Example request:

```json
{"nodes":[{"id":"in","type":"input"},{"id":"amp","type":"amp"},{"id":"out","type":"output"}],"edges":[{"source":"in","target":"amp"},{"source":"amp","target":"out"}]}
```

The graph compiler **only validates** a linear chain in the stock effect order; it returns a preview, not a DSP binary.

## Firmware

Stock image: `a41_2.01.0.svu` (Spider V 20 firmware 2.01.0). Do not flash arbitrary builds. Before custom firmware: identify CPU/DSP, bootloader, integrity/signature checks, backup and verified recovery path. No firmware binary is redistributed here.

## Tests

```bash
python3 -m unittest -v test_backend.py
```
