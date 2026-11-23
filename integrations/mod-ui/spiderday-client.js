/* Spider Day ↔ MOD UI adapter (browser ES module).
 * Import into a MOD UI fork integration. Never sends MIDI, firmware or effect writes.
 */
export class SpiderDayClient {
  constructor(baseUrl = "/spiderday") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }
  async get(path) {
    const response = await fetch(this.baseUrl + path, {credentials: "same-origin"});
    if (!response.ok) throw new Error("Spider Day HTTP " + response.status);
    return response.json();
  }
  async health() { return this.get("/api/health"); }
  async device() { return this.get("/api/device"); }
  async midi() { return this.get("/api/midi"); }
  async blocks() { return this.get("/api/blocks"); }
  async legacyState() { return this.get("/api/legacy/state"); }
  async legacyCatalog() { return this.get("/api/legacy/catalog"); }
  async legacyPresets() { return this.get("/api/legacy/presets"); }
  async legacyBoard() { return this.get("/api/legacy/board"); }
  async compilePreview(graph) {
    const response = await fetch(this.baseUrl + "/api/graph/compile", {
      method: "POST", credentials: "same-origin",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(graph)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Graph rejected");
    return data;
  }
}

// Accept a legacy slot list, or a board object containing an effects array.
// Reject unsupported structures instead of silently inventing a DSP chain.
export function boardToPreviewGraph(board) {
  const order = ["input","gate","comp","stomp","amp","mod","delay","reverb","wah","eq","volume","output"];
  const slots = Array.isArray(board) ? board : board?.effects;
  if (!Array.isArray(slots)) throw new TypeError("board must be an array or contain an effects array");
  const allowed = new Set(order.slice(1,-1));
  const selected = new Set(["input","output"]);
  for (const item of slots) {
    const type = typeof item === "string" ? item : item?.type ?? item?.id;
    if (typeof type !== "string" || !allowed.has(type)) {
      throw new TypeError("unsupported stock DSP slot: " + String(type));
    }
    if (selected.has(type)) throw new TypeError("duplicate stock DSP slot: " + type);
    selected.add(type);
  }
  const nodes = order.filter(type => selected.has(type)).map(type => ({id:type,type}));
  const edges = nodes.slice(1).map((node,i) => ({source:nodes[i].id,target:node.id}));
  return {nodes,edges};
}
