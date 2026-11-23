import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";

const source = await readFile(new URL("./spiderday-client.js",import.meta.url),"utf8");
const {boardToPreviewGraph} = await import("data:text/javascript;base64,"+Buffer.from(source).toString("base64"));

test("empty board compiles to input -> output",()=>{
  assert.deepEqual(boardToPreviewGraph([]),{
    nodes:[{id:"input",type:"input"},{id:"output",type:"output"}],
    edges:[{source:"input",target:"output"}]
  });
});

test("slot order is fixed, independent of board order",()=>{
  const graph=boardToPreviewGraph([{id:"delay"},{type:"gate"}]);
  assert.deepEqual(graph.nodes.map(n=>n.type),["input","gate","delay","output"]);
  assert.deepEqual(graph.edges.map(e=>[e.source,e.target]),
    [["input","gate"],["gate","delay"],["delay","output"]]);
});

test("board object with effects array is supported",()=>{
  assert.deepEqual(boardToPreviewGraph({effects:["amp","reverb"]}).nodes.map(n=>n.type),
    ["input","amp","reverb","output"]);
});

test("unknown slots are rejected",()=>{
  assert.throws(()=>boardToPreviewGraph([{id:"unknown-plugin"}]),/unsupported/);
});

test("duplicate slots are rejected",()=>{
  assert.throws(()=>boardToPreviewGraph(["gate","gate"]),/duplicate/);
});

test("invalid board shapes are rejected",()=>{
  for (const value of [null,{},42,"gate",{effects:{gate:true}}]) {
    assert.throws(()=>boardToPreviewGraph(value),TypeError);
  }
});
