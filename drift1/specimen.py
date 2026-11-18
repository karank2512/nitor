"""Phone-size image specimen (1080 x 1920 PNG, Chrome-rendered, fresh profile)
for the D1 PRIVATE PROOF variable font. Usage: python3.11 drift1/specimen.py <tag>"""
import base64
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
VF = os.environ.get('D1_VF', os.path.join(HERE, 'out', 'fonts', 'DriftD1-VF.ttf'))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'phone1'
OUT = os.path.join(HERE, 'out', 'specimen')
os.makedirs(OUT, exist_ok=True)
b64 = base64.b64encode(open(VF, 'rb').read()).decode()


def w(n):
    return f"font-variation-settings:'wght' {n}"


html = f"""<!doctype html><meta charset=utf-8><title>D1 phone specimen</title><style>
@font-face{{font-family:'D';src:url(data:font/ttf;base64,{b64}) format('truetype');font-weight:100 900;font-display:block}}
html,body{{margin:0;width:1080px;height:1920px;background:#050607;color:#e9ecef;overflow:hidden}}
.p{{position:absolute;left:84px;right:84px;font-family:'D';white-space:pre;line-height:1}}
.lab{{position:absolute;left:84px;font:22px/1 'D';{w(500)};letter-spacing:.18em;color:#7d838a}}
.rule{{position:absolute;left:84px;right:84px;height:2px;background:#1c2024}}
#d{{display:none}}</style>
<div class=lab style="top:84px">PRIVATE PROOF  –  D1</div>
<div class=lab style="top:84px;left:auto;right:84px">WGHT 100–900</div>
<div class=p style="top:170px;font-size:250px;{w(100)}">slow</div>
<div class=p style="top:420px;font-size:250px;{w(500)};color:#c9ced3">slow</div>
<div class=p style="top:670px;font-size:250px;{w(900)}">slow</div>
<div class=rule style="top:950px"></div>
<div class=p style="top:990px;font-size:84px;{w(900)}">hours after</div>
<div class=p style="top:1080px;font-size:84px;{w(300)}">midnight, the</div>
<div class=p style="top:1170px;font-size:84px;{w(900)}">room is quiet.</div>
<div class=rule style="top:1300px"></div>
<div class=p style="top:1340px;font-size:54px;{w(700)};line-height:1.25">abcdefghijklm
nopqrstuvwxyz
ABCDEFGHIJKLM
NOPQRSTUVWXYZ
0123456789 .,:;!?&amp;()</div>
<div class=lab style="top:1800px">77 CHARACTERS  –  NOT A RELEASE</div>
<div id=d></div><script>document.fonts.ready.then(()=>{{const s=[];document.fonts.forEach(f=>s.push(f.status));
const c=document.createElement('canvas').getContext('2d');c.font="100px 'D'";const a=c.measureText('nnnn').width;
document.getElementById('d').textContent='DIAG'+JSON.stringify({{status:s,nnnn:a}})+'END';}});</script>"""
page = os.path.join(OUT, f'{TAG}.html')
open(page, 'w').write(html)
prof = os.path.join(LANE, '.chrome-diag-profiles', 'drift1', 'spec-' + TAG)
base = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
        '--no-default-browser-check', '--use-mock-keychain', '--password-store=basic', '--disable-extensions',
        '--disk-cache-size=1', '--force-device-scale-factor=1', '--virtual-time-budget=4000']
dom = subprocess.run(base + [f'--user-data-dir={prof}-dom', '--dump-dom', 'file://' + page],
                     check=True, capture_output=True, text=True, timeout=120).stdout
png = os.path.join(OUT, f'{TAG}.png')
subprocess.run(base + [f'--user-data-dir={prof}-shot', '--window-size=1080,1920', f'--screenshot={png}',
                       'file://' + page], check=True, capture_output=True, text=True, timeout=120)
m = re.search(r'DIAG(.*?)END', dom)
print(png, hashlib.sha256(open(png, 'rb').read()).hexdigest(), m.group(1).replace('&quot;', '"') if m else 'NO DIAG')
