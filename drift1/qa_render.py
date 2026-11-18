"""Chrome render QA for the RC1 variable font (work in progress; name pending).

Sheets (fresh Chrome profile each, one @font-face, DOM font check):
  waterfall-<ground>-<dsf>x : full charset at 12/16/24/36/72 px, wght 100/400/700/900
  overlap-<ground>          : 300 px words at wght 100/350/550/750/900, to look for
                              seams or dark spots where overlapping contours meet
Usage: python3.11 drift1/qa_render.py
"""
import base64
import hashlib
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
VF = os.environ.get('D1_VF', os.path.join(HERE, 'out', 'rc1', 'DriftD1-RC1-VF.ttf'))
OUT = os.environ.get('D1_QA_OUT', os.path.join(HERE, 'out', 'qa-render'))   # separate dirs per candidate
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
os.makedirs(OUT, exist_ok=True)
B64 = base64.b64encode(open(VF, 'rb').read()).decode()
GROUNDS = {'dark': ('#050607', '#e9ecef'), 'light': ('#f2efe9', '#111214')}
CHARS = 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 !"&\'(),-./:;?–'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def page(body, bg, fg):
    return f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'P';src:url(data:font/ttf;base64,{B64}) format('truetype');font-weight:100 900;font-display:block}}
html,body{{margin:0;background:{bg};color:{fg}}}body{{padding:24px 30px}}
.r{{font-family:'P';white-space:nowrap;margin:0 0 6px}}.l{{font:10px/1.2 Helvetica;color:#888;margin-top:10px}}
#d{{display:none}}</style>{body}<div id=d></div><script>document.fonts.ready.then(()=>{{const s=[];
document.fonts.forEach(f=>s.push(f.status));const c=document.createElement('canvas').getContext('2d');
c.font="100px 'P'";document.getElementById('d').textContent='DIAG'+JSON.stringify({{status:s,nnnn:c.measureText('nnnn').width}})+'END';}});</script>"""


def shoot(name, html, size, dsf):
    p = os.path.join(OUT, name + '.html')
    open(p, 'w').write(html)
    prof = os.path.join(LANE, '.chrome-diag-profiles', 'drift1-qa-' + os.path.basename(OUT), name)
    base = [CH, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
            '--no-default-browser-check', '--use-mock-keychain', '--password-store=basic',
            '--disable-extensions', '--disk-cache-size=1', f'--force-device-scale-factor={dsf}',
            '--virtual-time-budget=4000']
    dom = subprocess.run(base + [f'--user-data-dir={prof}-dom', '--dump-dom', 'file://' + p],
                         capture_output=True, text=True, timeout=120, check=True).stdout
    png = os.path.join(OUT, name + '.png')
    subprocess.run(base + [f'--user-data-dir={prof}-shot', f'--window-size={size}', f'--screenshot={png}',
                           'file://' + p], capture_output=True, text=True, timeout=120, check=True)
    m = re.search(r'DIAG(.*?)END', dom)
    return {'png': os.path.relpath(png, LANE), 'sha256': sha(png),
            'dom_check': json.loads(m.group(1).replace('&quot;', '"')) if m else None}


man = {'font': os.path.relpath(VF, LANE), 'font_sha256': sha(VF), 'renders': {}}
for g, (bg, fg) in GROUNDS.items():
    body = ''
    for w in (100, 400, 700, 900):
        body += f'<div class=l>wght {w}</div>'
        for px in (12, 16, 24, 36, 72):
            body += (f"<div class=r style=\"font-size:{px}px;font-variation-settings:'wght' {w}\">"
                     f"{CHARS.replace('&', '&amp;')}</div>")
    for dsf in (1, 2):
        man['renders'][f'waterfall-{g}-{dsf}x'] = shoot(f'waterfall-{g}-{dsf}x', page(body, bg, fg), '1900,1500', dsf)
    body = ''.join(f"<div class=l>wght {w}</div><div class=r style=\"font-size:300px;line-height:1.05;"
                   f"font-variation-settings:'wght' {w}\">ehx&amp;4AK</div>" for w in (100, 350, 550, 750, 900))
    man['renders'][f'overlap-{g}'] = shoot(f'overlap-{g}', page(body, bg, fg), '1900,1800', 1)
json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
for k, v in man['renders'].items():
    print(k, v['png'], v['sha256'][:16], v['dom_check'])
