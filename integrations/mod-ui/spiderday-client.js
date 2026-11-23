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

// Convert a simple ordered MOD UI board to a preview-only stock DSP graph.
// A real graph editor should supply its explicit edges rather than using this.
export function boardToPreviewGraph(board) {
  if (!Array.isArray(board)) throw new TypeError("board must be an array");
  const order = ["input","gate","comp","stomp","amp","mod","delay","reverb","wah","eq","volume","output"];
  const selected = new Set(board.map(item => item.id));
  selected.add("input");
  selected.add("output");
  const nodes = order.filter(type => selected.has(type)).map(type => ({id: type, type}));
  const edges = nodes.slice(1).map((node, i) => ({source: nodes[i].id, target: node.id}));
  return {nodes, edges};
}
