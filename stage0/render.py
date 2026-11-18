"""Render Stage 0 proof sheets with the installed Google Chrome (headless).

Fonts are embedded as data: URIs so no file:// font loading is involved.
Chrome uses a throwaway profile inside the lane folder.
Usage: python3.11 render.py [round-label]
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'out', 'fonts')
PROOFS = os.path.join(HERE, 'out', 'proofs')
PAGES = os.path.join(HERE, 'out', 'pages')
PROFILE = os.path.join(HERE, '..', '.chrome-proof-profile')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

GROUNDS = {
    'light': ('#f4f1ea', '#16171a', '#8a8579'),
    'dark': ('#111317', '#e8e4da', '#7d8088'),
}

TEXT_LINES = [
    'nnonnoon  nnannsnngnn  HHnnHHoo',
    'il1  0o0  {lion}  {sign}  1001 0110',
    'a lagoon slang lion song gloss signs',
    'Hossain {aloss} snail1 log0 {nisga}',
    '{ sign{ son1 } 010 } iiillll1111',
]
DISPLAY_LINES = ['Hnoags', '0{}il1']


def font_face(name, file):
    with open(os.path.join(FONTS, file), 'rb') as f:
        b = base64.b64encode(f.read()).decode()
    return (f"@font-face{{font-family:'{name}';src:url(data:font/ttf;base64,{b})"
            f" format('truetype');font-display:block}}")


def page(kind, ground):
    bg, fg, mute = GROUNDS[ground]
    faces = '\n'.join([
        font_face('Clean', 'ProofClean.ttf'),
        font_face('Ghost', 'ProofGhost.ttf'),
        font_face('VZ', 'ProofTRCE-z0.ttf'),
        font_face('VH', 'ProofTRCE-h2.ttf'),
    ])
    css = f"""{faces}
    html,body{{margin:0;background:{bg};color:{fg}}}
    body{{padding:24px 28px;font:12px/1.4 -apple-system,Helvetica,sans-serif}}
    .lab{{color:{mute};font-size:11px;margin:14px 0 4px;letter-spacing:.02em}}
    .t{{font-size:13px;line-height:1.4;white-space:pre}}
    .d{{font-size:120px;line-height:1.25;white-space:pre}}
    """
    rows = []
    if kind == 'text':
        variants = [
            ('Clean static (ink only) - 13px', "font-family:Clean"),
            ('Variable TRCE 0, zero-width ghost default - 13px',
             "font-family:VZ;font-variation-settings:'TRCE' 0"),
            ('Variable TRCE 0, 2-unit hairline fallback - 13px',
             "font-family:VH;font-variation-settings:'TRCE' 0"),
            ('Variable TRCE 100 (ghost 14 units) - 13px',
             "font-family:VZ;font-variation-settings:'TRCE' 100"),
        ]
        for lab, st in variants:
            rows.append(f'<div class="lab">{lab}</div>')
            rows.append(f'<div class="t" style="{st}">' + '\n'.join(TEXT_LINES) + '</div>')
    elif kind == 'smoothing':
        aa = '-webkit-font-smoothing:antialiased;'
        variants = [
            ('Clean, antialiased (no macOS dilation)', aa + "font-family:Clean"),
            ('TRCE 0 zero-width, antialiased', aa + "font-family:VZ;font-variation-settings:'TRCE' 0"),
            ('TRCE 0 zero-width, default smoothing', "font-family:VZ;font-variation-settings:'TRCE' 0"),
            ('TRCE 0 hairline, antialiased', aa + "font-family:VH;font-variation-settings:'TRCE' 0"),
        ]
        for lab, st in variants:
            rows.append(f'<div class="lab">{lab}</div>')
            rows.append(f'<div class="t" style="{st}">' + '\n'.join(TEXT_LINES[:3]) + '</div>')
    elif kind == 'inspect':
        rows.append('<div class="lab">Clean - 300px inspection</div>')
        rows.append('<div style="font-family:Clean;font-size:300px;line-height:1.15;white-space:pre">'
                    'Hnoa\ngs0{\n}il1</div>')
    else:
        variants = [
            ('Clean - 120px', "font-family:Clean"),
            ('Variable TRCE 50 - 120px', "font-family:VZ;font-variation-settings:'TRCE' 50"),
            ('Variable TRCE 100 - 120px', "font-family:VZ;font-variation-settings:'TRCE' 100"),
        ]
        for lab, st in variants:
            rows.append(f'<div class="lab">{lab}</div>')
            rows.append(f'<div class="d" style="{st}">' + '\n'.join(DISPLAY_LINES) + '</div>')
    html = (f'<!doctype html><meta charset="utf-8"><title>Stage 0 proof</title>'
            f'<style>{css}</style>' + '\n'.join(rows))
    p = os.path.join(PAGES, f'{kind}-{ground}.html')
    with open(p, 'w') as f:
        f.write(html)
    return p


def shoot(html, png, size):
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
           '--no-first-run', '--no-default-browser-check', '--use-mock-keychain',
           '--password-store=basic', '--disable-extensions',
           f'--user-data-dir={os.path.abspath(PROFILE)}',
           '--force-device-scale-factor=1', f'--window-size={size}',
           '--virtual-time-budget=4000', f'--screenshot={png}',
           'file://' + html]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)


if __name__ == '__main__':
    os.makedirs(PROOFS, exist_ok=True)
    os.makedirs(PAGES, exist_ok=True)
    for kind, size in (('text', '760,620'), ('display', '1180,1060')):
        for ground in GROUNDS:
            h = page(kind, ground)
            png = os.path.join(PROOFS, f'{kind}-{ground}.png')
            shoot(h, png, size)
            print(png)
    for kind, size in (('smoothing', '760,420'), ('inspect', '1300,1150')):
        h = page(kind, 'light')
        png = os.path.join(PROOFS, f'{kind}-light.png')
        shoot(h, png, size)
        print(png)
