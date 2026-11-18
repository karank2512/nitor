"""Measure whether TRCE 0 is visually identical to the Clean font at 13px.

Renders the same text block once per (font, smoothing) pair in Chrome
headless with an identical layout, then diffs against Clean with Pillow.
Usage: python3.11 measure_trce0.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R  # noqa: E402
from PIL import Image, ImageChops  # noqa: E402

OUT = os.path.join(HERE, 'out', 'measure')
CASES = {
    'clean': ('Clean', ''),
    'z0': ('VZ', "font-variation-settings:'TRCE' 0;"),
    'h2': ('VH', "font-variation-settings:'TRCE' 0;"),
}
SMOOTH = {'default': '', 'antialiased': '-webkit-font-smoothing:antialiased;'}


def one(case, smooth):
    fam, var = CASES[case]
    faces = '\n'.join([R.font_face('Clean', 'ProofClean.ttf'),
                       R.font_face('VZ', 'ProofTRCE-z0.ttf'),
                       R.font_face('VH', 'ProofTRCE-h2.ttf')])
    html = (f"<!doctype html><meta charset=utf-8><style>{faces}"
            f"html,body{{margin:0;background:#f4f1ea;color:#16171a}}"
            f"div{{padding:20px;font-family:{fam};{var}{SMOOTH[smooth]}"
            f"font-size:13px;line-height:1.4;white-space:pre}}</style><div>"
            + '\n'.join(R.TEXT_LINES) + '</div>')
    hp = os.path.join(OUT, f'{case}-{smooth}.html')
    with open(hp, 'w') as f:
        f.write(html)
    png = os.path.join(OUT, f'{case}-{smooth}.png')
    R.shoot(hp, png, '420,160')
    return Image.open(png).convert('L')


def build_control():
    """Clean ink wrapped as a variable font (fvar + empty gvar, no ghost):
    isolates Chrome's static-vs-variable rasterisation difference."""
    from fontTools.ttLib import TTFont, newTable
    from fontTools.ttLib.tables._f_v_a_r import Axis
    f = TTFont(os.path.join(R.FONTS, 'ProofClean.ttf'))
    fvar = newTable('fvar')
    ax = Axis()
    ax.axisTag, ax.minValue, ax.defaultValue, ax.maxValue = 'TRCE', 0, 0, 100
    ax.axisNameID = f['name'].addMultilingualName({'en': 'Trace'}, f, minNameID=256)
    fvar.axes, fvar.instances = [ax], []
    f['fvar'] = fvar
    gvar = newTable('gvar')
    gvar.version, gvar.reserved, gvar.variations = 1, 0, {}
    f['gvar'] = gvar
    p = os.path.join(R.FONTS, 'ProofCtrlVar.ttf')
    f.save(p)


def diff(a, b, label):
    d = ImageChops.difference(a, b)
    hist = d.histogram()
    print(f'{label:34s} max diff {d.getextrema()[1]:3d}/255, '
          f'pixels changed {sum(hist[1:]):5d}, >15 levels {sum(hist[16:]):5d}')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build_control()
    CASES['ctrl'] = ('CV', "font-variation-settings:'TRCE' 0;")
    _ff = R.font_face

    def font_face(name, file):  # inject the control face into every page
        s = _ff(name, file)
        if name == 'Clean':
            s += '\n' + _ff('CV', 'ProofCtrlVar.ttf')
        return s
    R.font_face = font_face
    for smooth in SMOOTH:
        clean = one('clean', smooth)
        ctrl = one('ctrl', smooth)
        diff(clean, ctrl, f'{smooth}: ctrl-var vs clean-static')
        for case in ('z0', 'h2'):
            im = one(case, smooth)
            diff(clean, im, f'{smooth}: {case} vs clean-static')
            diff(ctrl, im, f'{smooth}: {case} vs ctrl-var')
