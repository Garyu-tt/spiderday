"""Spider Day preview control plane. No DSP writes or firmware flashing."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
from pathlib import Path
from device import probe_usb

BLOCKS = ('input','gate','comp','stomp','amp','mod','delay','reverb','wah','eq','volume','output')
CONTROLLED = {'gate','comp','stomp','mod','delay','reverb','wah','eq','volume'}
ORDER = {name:i for i,name in enumerate(BLOCKS)}
PRESETS = Path(os.getenv('SPIDERDAY_PRESETS',str(Path.home()/'.local/share/spiderday/presets.json')))

def compile_graph(graph):
    nodes, edges = graph.get('nodes'), graph.get('edges')
    if not isinstance(nodes,list) or not isinstance(edges,list):
        raise ValueError('nodes and edges must be arrays')
    if not nodes or len(nodes) > 32 or len(edges) > 64:
        raise ValueError('graph must contain 1..32 nodes and at most 64 edges')
    ids = {}
    for node in nodes:
        if not isinstance(node,dict) or not isinstance(node.get('id'),str) or node['id'] in ids:
            raise ValueError('invalid or duplicate node id')
        if not isinstance(node.get('parameters',{}),dict):
            raise ValueError('parameters must be an object')
        if node.get('type') not in BLOCKS:
            raise ValueError('unsupported block type')
        ids[node['id']] = node
    if len(set(n['type'] for n in nodes)) != len(nodes):
        raise ValueError('stock profile supports one slot per effect type')
    ordered = sorted(nodes,key=lambda n:ORDER[n['type']])
    expected = set(zip([n['id'] for n in ordered[:-1]],[n['id'] for n in ordered[1:]]))
    actual = set()
    for edge in edges:
        if not isinstance(edge,dict) or edge.get('source') not in ids or edge.get('target') not in ids:
            raise ValueError('unknown edge endpoint')
        actual.add((edge['source'],edge['target']))
    if len(edges)!=len(actual) or actual!=expected:
        raise ValueError('stock profile requires a linear fixed-order chain; no feedback or parallel branches')
    return {'target':'line6-spider-v20-stock','mode':'preview-only',
            'chain':[{'id':n['id'],'type':n['type'],'parameters':n.get('parameters',{}),
                      'controllable':n['type'] in CONTROLLED} for n in ordered],
            'warnings':['No device writes or DSP firmware compiler implemented']}

class Handler(BaseHTTPRequestHandler):
    def respond(self,status,obj):
        data=json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Access-Control-Allow-Origin',os.getenv('SPIDERDAY_UI_ORIGIN','http://localhost:8080'))
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
        self.end_headers()
        self.wfile.write(data)
    def do_OPTIONS(self): self.respond(200,{})
    def do_GET(self):
        if self.path=='/api/health':
            devices=probe_usb()
            self.respond(200,{'ok':True,'device':'Spider V 20','device_connected':bool(devices),'write_enabled':False})
        elif self.path=='/api/device':
            self.respond(200,{'devices':probe_usb(),'write_enabled':False})
        elif self.path=='/api/blocks':
            self.respond(200,{'blocks':[{'type':x,'controllable':x in CONTROLLED,'order':i} for i,x in enumerate(BLOCKS)]})
        elif self.path=='/api/presets':
            try: presets=json.loads(PRESETS.read_text()) if PRESETS.exists() else []
            except (ValueError,OSError): return self.respond(500,{'error':'preset store unreadable'})
            self.respond(200,{'presets':presets})
        else: self.respond(404,{'error':'not found'})
    def do_POST(self):
        if self.path!='/api/graph/compile': return self.respond(404,{'error':'not found'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=65536: raise ValueError('request size must be 1..65536 bytes')
            self.respond(200,compile_graph(json.loads(self.rfile.read(size))))
        except (ValueError,TypeError,KeyError) as e: self.respond(400,{'error':str(e)})

if __name__=='__main__':
    host=os.getenv('SPIDERDAY_HOST','127.0.0.1')
    port=int(os.getenv('SPIDERDAY_PORT','8765'))
    print(f'Spider Day preview API: http://{host}:{port}')
    ThreadingHTTPServer((host,port),Handler).serve_forever()
