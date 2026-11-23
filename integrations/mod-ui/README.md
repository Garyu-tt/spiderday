# MOD UI integration

The browser adapter lives in [spiderday-client.js](spiderday-client.js). It has no write operations.

```js
import { SpiderDayClient, boardToPreviewGraph } from "./spiderday-client.js";

const spider = new SpiderDayClient("/spiderday");
const health = await spider.health();
const board = await spider.legacyBoard(); // requires running legacy bridge
const preview = await spider.compilePreview(boardToPreviewGraph(board));
console.log(health, preview);
```

**Reverse proxy required:** MOD UI must proxy `/spiderday/*` to `http://127.0.0.1:8765/*` from the **same host** as the Python backend. For example, with Caddy running on the Raspberry Pi:

```caddyfile
handle_path /spiderday/* {
    reverse_proxy 127.0.0.1:8765
}
```

Keep the existing MOD UI handlers and any authentication intact. Do not expose `8765` to the public network or configure wildcard CORS.

## Limitations

- The source MOD UI fork is not yet modified. This is an integration module, not an installed MOD UI plugin.
- The legacy v0.3 bridge listens on `8081` **when running**, but was not running when checked. It contains effect-write routes and defaults to binding `0.0.0.0`; do **not** start it unchanged on an untrusted network.
- The graph conversion preserves known effect slot types but not custom parallel connections, MIDI values, or DSP code. It is strictly a preview.
- Firmware flashing is not implemented.
