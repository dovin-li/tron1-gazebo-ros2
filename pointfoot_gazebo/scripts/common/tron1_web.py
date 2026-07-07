#!/usr/bin/env python3
"""
TRON1 Web 遥控面板 — Flask
适配: yhlee@192.168.1.34
访问: http://192.168.1.34:8080
"""

import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return HTML

@app.route('/cmd/<action>', methods=['POST'])
def cmd(action):
    speeds = {
        'fw':   [0.3,  0.0,  0.0],
        'bw':   [-0.3,  0.0,  0.0],
        'left':  [0.0,  0.2,  0.0],
        'right': [0.0, -0.2,  0.0],
        'tl':   [0.0,  0.0,  0.5],
        'tr':   [0.0,  0.0, -0.5],
        'stop':  [0.0,  0.0,  0.0],
    }
    if action in speeds:
        with open('/tmp/tron1_cmd.json', 'w') as f:
            json.dump(speeds[action], f)
        return jsonify(ok=action)
    return jsonify(error=action)

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TRON1 Walk</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui;background:#1a1a2e;color:#eee;display:flex;justify-content:center;padding:10px}
.w{max-width:400px;width:100%}
h1{text-align:center;margin:10px 0;color:#00B08A;font-size:20px}
.c{background:#16213e;border-radius:10px;padding:12px;margin:6px 0}
button{padding:22px 15px;border:none;border-radius:8px;font-size:16px;cursor:pointer;font-weight:700;min-width:60px}
button:active{transform:scale(0.95)}
.r{display:flex;gap:6px;justify-content:center;flex-wrap:wrap}
.fw{background:#00B08A;color:#000}
.bw{background:#c0392b;color:#fff}
.lr{background:#533483;color:#fff}
.turn{background:#f39c12;color:#000}
.stop{background:#c0392b;color:#fff;width:100%}
.st{text-align:center;font-size:12px;color:#888;padding:4px}
</style></head><body><div class="w">
<h1>TRON1 Walk</h1>
<div class="c">
<div class="r"><button class="fw" onclick="S('fw')">前进</button></div>
<div class="r" style="margin-top:6px">
<button class="lr" onclick="S('left')">左移</button>
<button class="stop" style="width:80px" onclick="S('stop')">停</button>
<button class="lr" onclick="S('right')">右移</button>
</div>
<div class="r" style="margin-top:6px"><button class="bw" onclick="S('bw')">后退</button></div>
<div class="r" style="margin-top:10px">
<button class="turn" onclick="S('tl')">左转</button>
<button class="turn" onclick="S('tr')">右转</button>
</div>
</div>
<div class="st" id="s">就绪</div>
</div>
<script>
async function S(cmd){document.getElementById('s').textContent=cmd;try{let r=await fetch('/cmd/'+cmd,{method:'POST'});let d=await r.json();document.getElementById('s').textContent=d.ok}catch(e){document.getElementById('s').textContent='ERR'}}
</script></body></html>"""

if __name__ == '__main__':
    import os
    ip = os.popen('hostname -I').read().strip().split()[0]
    print(f"Web遥控: http://{ip}:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
