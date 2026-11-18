"""Render r4 proofs + old-vs-new comparison, recording what Chrome loaded.

Every PNG comes from a page with exactly ONE @font-face ('Probe', data URI of
one named file), integer line-heights, and its own fresh Chrome profile. A
--dump-dom pass on the same page records FontFace.status and the canvas
width of 'HHHH' at 100px (240 = this 600-unit mono; system monospace = 240.82).
Results go to out/manifest.json (font sha256, rendered state, PNG sha256).
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PROFILES = os.path.join(LANE, '.chrome-diag-profiles', 'r4')
GROUNDS = {'light': ('#f4f1ea', '#16171a', '#8a8579'),
           'dark': ('#111317', '#e8e4da', '#7d8088')}
TEXT = ['nnonnoon  nnannsnngnn  HHnnHHoo',
        'il1  0o0  {lion}  {sign}  1001 0110',
        'a lagoon slang lion song gloss signs',
        'Hossain {aloss} snail1 log0 {nisga}',
        '{ sign{ son1 } 010 } iiillll1111']
DISPLAY = ['Hnoags', '0{}il1']
FONTS = {
    'r4-clean': os.path.join(HERE, 'out', 'fonts', 'R4Clean.ttf'),
    'r4-trace': os.path.join(HERE, 'out', 'fonts', 'R4Trace.ttf'),
    'r3-clean': os.path.join(LANE, 'stage0', 'out', 'fonts', 'ProofClean.ttf'),
    'r3-ghost': os.path.join(LANE, 'stage0', 'out', 'fonts', 'ProofGhost.ttf'),
}
manifest = {}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def page(key, kind, ground, path, label):
    bg, fg, mute = GROUNDS[ground]
    b64 = base64.b64encode(open(FONTS[key], 'rb').read()).decode()
    if kind == 'text':
        body = (f'<div class=t>{chr(10).join(TEXT)}</div>')
        size = 'font-size:13px;line-height:18px'
    elif kind == 'display':
        body = f'<div class=t>{chr(10).join(DISPLAY)}</div>'
        size = 'font-size:120px;line-height:150px'
    else:  # inspect
        body = '<div class=t>Hnoa\ngs0{\n}il1</div>'
        size = 'font-size:300px;line-height:360px'
    js = """document.fonts.ready.then(()=>{const f=[];document.fonts.forEach(x=>f.push(x.status));
    const c=document.createElement('canvas').getContext('2d');c.font="100px 'Probe'";
    const a=c.measureText('HHHH').width;c.font='100px monospace';const m=c.measureText('HHHH').width;
    document.getElementById('d').textContent='DIAG'+JSON.stringify({status:f,HHHH_probe:a,HHHH_monospace:m})+'END';});"""
    html = f"""<!doctype html><meta charset=utf-8><title>r4 proof</title><style>
@font-face{{font-family:'Probe';src:url(data:font/ttf;base64,{b64}) format('truetype');font-display:block}}
html,body{{margin:0;background:{bg};color:{fg}}}
.lab{{position:absolute;left:24px;top:14px;font:11px/14px Helvetica,sans-serif;color:{mute}}}
.t{{position:absolute;left:24px;top:40px;font-family:'Probe';{size};white-space:pre}}
#d{{display:none}}</style><div class=lab>{label}</div>{body}<div id=d></div><script>{js}</script>"""
    open(path, 'w').write(html)


def chrome(args, profile):
    return subprocess.run(
        [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
         '--no-default-browser-check', '--use-mock-keychain', '--password-store=basic',
         '--disable-extensions', '--disk-cache-size=1', '--force-device-scale-factor=1',
         f'--user-data-dir={profile}', '--virtual-time-budget=4000'] + args,
        check=True, capture_output=True, timeout=120, text=True)


def shoot(key, kind, ground, name, size, label):
    os.makedirs(os.path.join(OUT, 'pages'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'proofs'), exist_ok=True)
    h = os.path.join(OUT, 'pages', f'{name}.html')
    page(key, kind, ground, h, label)
    dom = chrome(['--dump-dom', 'file://' + h], os.path.join(PROFILES, name + '-dom')).stdout
    m = re.search(r'DIAG(.*?)END', dom)
    diag = json.loads(m.group(1).replace('&quot;', '"')) if m else None
    png = os.path.join(OUT, 'proofs', f'{name}.png')
    chrome([f'--window-size={size}', f'--screenshot={png}', 'file://' + h],
           os.path.join(PROFILES, name + '-shot'))
    manifest[name] = {'font_key': key, 'font_file': os.path.relpath(FONTS[key], LANE),
                      'font_sha256': sha(FONTS[key]), 'kind': kind, 'ground': ground,
                      'font_variation_settings': None, 'dom_check': diag,
                      'png': os.path.relpath(png, LANE), 'png_sha256': sha(png)}
    return png


def comparison():
    """Old (run-2 / r3 font files) vs new (r4), identical layouts."""
    pairs = []
    for kind, size in (('display', '820,370'), ('text', '420,150')):
        for old, new in (('r3-clean', 'r4-clean'), ('r3-ghost', 'r4-trace')):
            a = shoot(old, kind, 'light', f'cmp-{kind}-{old}', size, f'OLD {old} ({kind})')
            b = shoot(new, kind, 'light', f'cmp-{kind}-{new}', size, f'NEW {new} ({kind})')
            pairs.append((a, b))
    rows = []
    for a, b in pairs:
        ia, ib = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
        if ia.width < 600:  # 13px rows: upscale 2x for review
            ia, ib = (im.resize((im.width * 2, im.height * 2), Image.NEAREST) for im in (ia, ib))
        rows.append((ia, ib))
    W = max(a.width + b.width for a, b in rows) + 12
    H = sum(max(a.height, b.height) for a, b in rows) + 12 * len(rows)
    sheet = Image.new('RGB', (W, H), '#cfcac0')
    y = 0
    for a, b in rows:
        sheet.paste(a, (0, y))
        sheet.paste(b, (a.width + 12, y))
        y += max(a.height, b.height) + 12
    p = os.path.join(OUT, 'proofs', 'compare-old-r3-vs-new-r4.png')
    sheet.save(p)
    manifest['compare-sheet'] = {'png': os.path.relpath(p, LANE), 'png_sha256': sha(p),
                                 'note': 'left = run-2 (r3) font files, right = r4; '
                                         'rows: display clean, display ghost/trace, '
                                         'text clean (2x), text ghost/trace (2x)'}


if __name__ == '__main__':
    for style in ('clean', 'trace'):
        for ground in GROUNDS:
            shoot(f'r4-{style}', 'text', ground, f'{style}-13px-{ground}', '420,150',
                  f'R4 {style.title()} 13px / 18px - {ground}')
            shoot(f'r4-{style}', 'display', ground, f'{style}-120px-{ground}', '820,370',
                  f'R4 {style.title()} 120px - {ground}')
        shoot(f'r4-{style}', 'inspect', 'light', f'{style}-300px-inspect', '1200,1160',
              f'R4 {style.title()} 300px inspection')
    comparison()
    json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
    for k, v in manifest.items():
        print(k, v.get('png_sha256', '')[:12], (v.get('dom_check') or {}))
