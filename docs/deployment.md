# Spider Day: deployment and acceptance

## Current scope
The Raspberry Pi is the control-plane host. Audio stays in the Line 6 Spider V 20.
The compiler validates a **fixed-order preview graph**, not executable DSP code.
No firmware flashing, effect writes, or preset writes are implemented here.

## Components
- `backend.py`: loopback-only preview API on port 8765.
- `dev_proxy.py`: loopback-only static MOD UI + allowlisted API proxy on port 8766.
- `~/mod-ui-spiderday/html/spiderday.html`: standalone preview panel.
- `legacy_bridge.py`: read-only HTTP adapter to a separately managed legacy service.
- `deploy/systemd/`: user services with restart-on-failure.
- `deploy/healthcheck.py`: verifies API, USB, disabled writes, proxy, panel.
- `deploy/update-pi.sh`: fast-forward updates, tests, service restart and healthcheck.

## Install / update on Pi
Do not run the script until the device is reachable and the existing checkouts and user
services have been verified. The script is intended to run as `sp`, not root.

```sh
cd ~/spiderday
git pull --ff-only
bash deploy/update-pi.sh
systemctl --user status spiderday-api.service spiderday-proxy.service
```

The services require `loginctl show-user sp -p Linger` to report `yes` for
startup without an interactive login.

## Loopback smoke checks
```sh
python3 -m unittest discover -v
python3 deploy/healthcheck.py
curl -fsS http://127.0.0.1:8766/spiderday/api/health
curl -fsS http://127.0.0.1:8766/mod/spiderday.html >/dev/null
```

Expected: `write_enabled: false`, `device_connected: true` with the USB amp
attached. If USB is absent, the diagnostic intentionally fails.

## Security boundary
Neither the proxy nor the backend is an authentication service.
Both must remain bound to `127.0.0.1`. Do not forward ports 8765, 8766 or
8081 directly to the LAN or Internet. To provide remote access, add a separate
authenticated gateway and audit it before enabling writes.

The legacy SysEx service may have unauthenticated write routes and may send
MIDI during initialization. **Do not start it unchanged**. Read-only API
endpoints alone do not prove the legacy process is free of hardware side effects.

## Known limitations
- MOD UI static files are served, but the full MOD UI application server,
  its plugin discovery and live pedalboard functionality are not provided by
  this static host.
- No device-state SysEx handshake is verified end to end.
- No authenticated phone access yet.
- No native DSP firmware compiler or safe flash/rollback procedure.
- Changes made while the Pi is unreachable are not considered deployed or
  device-tested.
