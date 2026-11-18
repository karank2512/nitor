"""Direction proof for D1: one Chrome-rendered sheet (fresh profile), the
variable font embedded as a data URI, rows at wght 100 / 400 / 900.
Usage: python3.11 drift1/proof.py <tag>"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
VF = os.path.join(HERE, 'out', 'fonts', 'DriftD1-VF.ttf')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'dir1'
OUTP = os.path.join(HERE, 'out', 'proofs')
os.makedirs(OUTP, exist_ok=True)

ROWS = [  # (wght, px, text, ground)
    (100, 150, 'slow light', 'dark'), (400, 150, 'slow light', 'dark'), (900, 150, 'slow light', 'dark'),
    (900, 96, 'HOtel quiet zone', 'dark'),
    (100, 64, 'hours after midnight, the room is quiet.', 'dark'),
    (900, 64, 'hours after midnight, the room is quiet.', 'dark'),
    (400, 34, 'a slow drift of half-kept thoughts, by the window, past two.', 'dark'),
    (900, 120, 'drift', 'light'),
]


def chrome(args, profile):
    return subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                           '--no-default-browser-check', '--use-mock-keychain', '--password-store=basic',
                           '--disable-extensions', '--disk-cache-size=1', '--force-device-scale-factor=1',
                           f'--user-data-dir={profile}', '--virtual-time-budget=4000'] + args,
                          check=True, capture_output=True, timeout=120, text=True)


b64 = base64.b64encode(open(VF, 'rb').read()).decode()
y, html_rows = 30, []
for w, px, text, ground in ROWS:
    lh = round(px * 1.2)
    bg, fg = ('#050607', '#e9ecef') if ground == 'dark' else ('#efece6', '#111214')
    html_rows.append(f'<div style="position:absolute;left:0;right:0;top:{y}px;height:{lh + 30}px;background:{bg}"></div>')
    html_rows.append(f'<div class=lab style="top:{y + 4}px;color:{"#6b7178" if ground=="dark" else "#8a857c"}">wght {w} / {px}px</div>')
    html_rows.append(f'<div class=t style="top:{y + 20}px;font-size:{px}px;line-height:{lh}px;'
                     f'font-variation-settings:\'wght\' {w};color:{fg}">{text}</div>')
    y += lh + 30
js = """document.fonts.ready.then(()=>{const s=[];document.fonts.forEach(f=>s.push(f.status));
const c=document.createElement('canvas').getContext('2d');c.font="100px 'Probe'";const a=c.measureText('nnnn').width;
c.font='100px sans-serif';const b=c.measureText('nnnn').width;
document.getElementById('d').textContent='DIAG'+JSON.stringify({status:s,nnnn_probe:a,nnnn_fallback:b})+'END';});"""
html = f"""<!doctype html><meta charset=utf-8><title>D1 direction proof</title><style>
@font-face{{font-family:'Probe';src:url(data:font/ttf;base64,{b64}) format('truetype');font-weight:100 900;font-display:block}}
html,body{{margin:0;background:#050607}}
.lab{{position:absolute;left:40px;font:11px/14px Helvetica,sans-serif;letter-spacing:.04em;z-index:2}}
.t{{position:absolute;left:40px;font-family:'Probe';white-space:pre;z-index:2}}#d{{display:none}}
</style>{''.join(html_rows)}<div id=d></div><script>{js}</script>"""
page = os.path.join(OUTP, f'{TAG}.html')
open(page, 'w').write(html)
prof = os.path.join(LANE, '.chrome-diag-profiles', 'drift1', TAG)
dom = chrome(['--dump-dom', 'file://' + page], prof + '-dom').stdout
m = re.search(r'DIAG(.*?)END', dom)
png = os.path.join(OUTP, f'{TAG}.png')
chrome([f'--window-size=1500,{y + 20}', f'--screenshot={png}', 'file://' + page], prof + '-shot')
print(png, hashlib.sha256(open(png, 'rb').read()).hexdigest(), m.group(1).replace('&quot;', '"') if m else 'NO DIAG')
