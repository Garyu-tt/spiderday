# MOD UI integration

The browser adapter is [spiderday-client.js](spiderday-client.js). It supports
the **stock Spider V 20 fixed-order DSP profile only**, and never writes MIDI,
effects or firmware.

```js
import { SpiderDayClient, boardToPreviewGraph } from "./spiderday-client.js";
const spider = new SpiderDayClient("/spiderday");
const health = await spider.health();
const graph = boardToPreviewGraph([{id:"gate"},{id:"delay"}]);
const preview = await spider.compilePreview(graph);
console.log(health, preview);
```

The adapter accepts an array of stock slot names, an array of `{id}` or
`{type}` slot objects, or `{effects:[...]}`. Unsupported plugin IDs and
duplicate slots **raise errors** rather than being silently omitted.
It does not translate arbitrary MOD UI plugin URIs into Line 6 effects.
A live MOD UI pedalboard graph requires a separate explicit mapping layer.

## Raspberry Pi local deployment

The Spider Day fork of MOD UI contains a standalone
`html/spiderday.html` panel and a link in `html/index.html`.
The Spider Day `dev_proxy.py` serves static assets at `/mod/` and proxies
allowlisted backend API endpoints at `/spiderday/api/`.
Default address on the Pi itself:
`http://127.0.0.1:8766/mod/spiderday.html`.

The static host **does not run the MOD UI application backend**.
Plugin discovery, audio graph processing and normal MOD UI runtime APIs
are not provided by the Spider Day proxy.

Both backend (8765) and proxy (8766) bind to loopback only.
Do not expose these or the legacy SysEx port 8081 to the network without
a separately authenticated and audited gateway.

## Tests

```sh
python3 -m unittest discover -v
node --test integrations/mod-ui/spiderday-client.test.mjs
```

CI runs both suites. Raspberry Pi deployment and hardware acceptance
must be verified separately.

## Limitations

- Preview compiles only a linear fixed-order chain, not arbitrary pedalboards.
- No DSP writes, firmware flashing, or effect parameter mapping.
- Legacy v0.3 SysEx bridge is not safe to start unchanged: it has write routes,
  defaults to listening on the LAN, and may initialize the MIDI device.
- No authenticated phone UI yet.
