# Copyright (c) 2026, Karan Kapur, with Reserved Font Name "Nitor".
# This file is part of the Nitor Font Software, licensed under the
# SIL Open Font License, Version 1.1 (see OFL.txt).
"""D1 RC2 proof: RC1 + ONE correctness fix (ampersand diagonal end tick).
Name NOT chosen; internal work-in-progress naming only. Writes ONLY to
drift1/out/rc2/ (RC1 and all originals untouched; glyphs.py untouched - the
fix is a single-glyph override applied here).

Fix: in RC1 the &'s diagonal began with a horizontal cut at (150, 450), which
sat in the upper loop's counter/edge and showed as a small tick. RC2 starts the
diagonal at the loop's BOTTOM centre, mid-way through the loop's bottom stroke
(per master), where the near-horizontal stroke fully covers the flat cut.

QA: per-glyph outline hashes vs RC1 (only 'ampersand' may differ), master
compatibility (build asserts), collisions recomputed at wght 100/900 and
kerned exactly like RC1, reload, instances, ink at 100/400/900, vertical bounds.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glyphs as K  # noqa: E402
import build as B  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

OUT = os.path.join(HERE, 'out', 'rc2')
BASE = os.path.join(OUT, 'base')
RC1 = os.path.join(HERE, 'out', 'rc1', 'DriftD1-RC1-VF.ttf')
MIN_GAP = 28
FAMILY = os.environ.get('D1_FAMILY', 'PRIVATE PROOF Drift D1 RC2')
PS = os.environ.get('D1_PS', 'PrivateProofDriftD1RC2')
OUTTAG = os.environ.get('D1_OUTTAG', 'DriftD1-RC2')
os.makedirs(BASE, exist_ok=True)


def _ampersand_rc2(P):
    V, Hh = P['V'], P['Hh']
    up = K.ell(230, 560, 130, K.CAP + K.OS - 560)
    lo = K.ell(250, 200, 220, 200 + K.OS)
    tb = Hh * 0.6                          # loop bottom stroke thickness (per master)
    top_y = (560 - (K.CAP + K.OS - 560)) + tb / 2   # middle of that stroke
    return K.ring(up, K.inset(up, V, V, Hh * 0.8, Hh * 0.6)) + \
        [K.band(lo, K.inset(lo, V, V, Hh * 0.6, Hh), 125, 380),
         K.diag((520, 0), (230, top_y), V * 1.3), K.rect(360, 300, 540 + K.OV, 300 + Hh * 0.9)]


K.G['ampersand'] = _ampersand_rc2       # the only geometry change
B.OUT = BASE                            # never write into out/fonts
B.main()
SRC = os.path.join(BASE, 'DriftD1-VF.ttf')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def per_glyph(font):
    out = {}
    for g in font.getGlyphOrder():
        gl = font['glyf'][g]
        c, e = ([], [])
        if gl.numberOfContours > 0:
            c, e, _ = gl.getCoordinates(font['glyf'])
        var = font['gvar'].variations.get(g, []) if 'gvar' in font else []
        vrep = [(sorted(v.axes.items()), list(v.coordinates)) for v in var]
        out[g] = hashlib.sha256(repr((list(c), list(e), vrep, font['hmtx'][g])).encode()).hexdigest()
    return out


def bounds_at(path, w):
    inst = instancer.instantiateVariableFont(TTFont(path), {'wght': w})
    gs, hm = inst['glyf'], inst['hmtx']
    b = {}
    for g in inst.getGlyphOrder():
        gl = gs[g]
        if gl.numberOfContours > 0:
            gl.recalcBounds(gs)
            b[g] = (hm[g][0], gl.xMin, gl.xMax, gl.yMin, gl.yMax)
        else:
            b[g] = (hm[g][0], None, None, None, None)
    return b


qa = {'rc1_source': os.path.relpath(RC1, os.path.dirname(HERE)), 'rc1_sha256': sha(RC1)}
rc1, src = TTFont(RC1), TTFont(SRC)
h1, h2 = per_glyph(rc1), per_glyph(src)
qa['glyphs_changed_vs_rc1'] = sorted(g for g in h1 if h1[g] != h2.get(g))
qa['glyph_sets_equal'] = sorted(h1) == sorted(h2)

cmap = src.getBestCmap()
names = [cmap[c] for c in sorted(cmap) if cmap[c] != 'space']
kerns = {}
for w in (900, 100):
    b = bounds_at(SRC, w)
    for L in names:
        for R in names:
            gap = (b[L][0] - b[L][2]) + b[R][1]
            if gap < MIN_GAP:
                kerns[(L, R)] = max(kerns.get((L, R), 0), MIN_GAP - gap)
rc1_fea = open(os.path.join(HERE, 'out', 'rc1', 'kern.fea')).read()
fea = 'languagesystem DFLT dflt;\nfeature kern {\n' + ''.join(
    f'  pos {L} {R} {int(round(v))};\n' for (L, R), v in sorted(kerns.items())) + '} kern;\n'
open(os.path.join(OUT, 'kern.fea'), 'w').write(fea)
qa['kern_pairs'] = len(kerns)
qa['kern_identical_to_rc1'] = fea == rc1_fea
rc = TTFont(SRC)
addOpenTypeFeaturesFromString(rc, fea)
for nid, val in ((1, FAMILY), (4, f'{FAMILY} Thin'), (6, f'{PS}-Thin'),
                 (3, f'{FAMILY} variable proof'), (5, 'Version 0.101; PRIVATE PROOF RC2')):
    rc['name'].setName(val, nid, 3, 1, 0x409)
    rc['name'].setName(val, nid, 1, 0, 0)
vf = os.path.join(OUT, f'{OUTTAG}-VF.ttf')
rc.save(vf)
re_ = TTFont(vf)
h3 = per_glyph(re_)
qa['reload_ok'] = sorted(h3) == sorted(h2) and all(h3[g] == h2[g] for g in h2)
qa['coverage'] = {'glyphs': re_['maxp'].numGlyphs, 'mapped_chars': len(re_.getBestCmap())}
inst = {}
for w, nm in ((100, 'Thin'), (400, 'Regular'), (900, 'Bold')):
    p = os.path.join(OUT, f'{OUTTAG}-{nm}.ttf')
    instancer.instantiateVariableFont(TTFont(vf), {'wght': w}).save(p)
    inst[nm] = [os.path.relpath(p, os.path.dirname(HERE)), sha(p)]
qa['instances'] = inst
win_a, win_d = re_['OS/2'].usWinAscent, re_['OS/2'].usWinDescent
missing, oob = [], []
for w in (100, 400, 900):
    f = ImageFont.truetype(vf, 120)
    f.set_variation_by_axes([w])
    b = bounds_at(vf, w)
    for c, g in re_.getBestCmap().items():
        if g == 'space':
            continue
        im = Image.new('L', (260, 300), 0)
        ImageDraw.Draw(im).text((40, 20), chr(c), font=f, fill=255)
        if im.getbbox() is None:
            missing.append((chr(c), w))
        if b[g][4] > win_a or b[g][3] < -win_d:
            oob.append((chr(c), w))
qa['ink_missing'], qa['outside_win_metrics'] = missing, oob
qa['rc2_vf'] = [os.path.relpath(vf, os.path.dirname(HERE)), sha(vf)]
qa['license'] = re_['name'].getDebugName(13)
json.dump(qa, open(os.path.join(OUT, 'qa.json'), 'w'), indent=1)
print(json.dumps(qa, indent=1))
