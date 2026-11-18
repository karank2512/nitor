# Copyright (c) 2026, Karan Kapur, with Reserved Font Name "Nitor".
# This file is part of the Nitor Font Software, licensed under the
# SIL Open Font License, Version 1.1 (see OFL.txt).
"""D1 RC1: final private-proof candidate + QA. Glyph OUTLINES ARE FROZEN (the
approved phone2 shapes); RC1 only adds collision kerning, the final internal
name, and runs QA. Existing fontTools 4.39.4 only.

QA performed (results -> out/rc1/qa.json):
  1. build: masters compatible (asserted in build.py), no degenerate contours
  2. coverage: cmap list, every non-space char has ink at wght 100/400/900
  3. outlines identical to the approved D1 build (per-glyph coordinate hash)
  4. vertical metrics: all glyph bounds inside usWinAscent/usWinDescent at 3 weights
  5. collisions: every ordered pair at wght 900 and 100; pairs whose ink
     would touch/overlap get a GPOS kern so the gap is >= MIN_GAP units
  6. round trip: saved font reloads, instancer cuts Thin/Regular/Bold
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402
from PIL import Image, ImageFont  # noqa: E402

SRC = os.path.join(HERE, 'out', 'fonts', 'DriftD1-VF.ttf')
OUT = os.path.join(HERE, 'out', 'rc1')
os.makedirs(OUT, exist_ok=True)
MIN_GAP = 28
# Naming hook (name NOT chosen yet): D1_FAMILY / D1_PS / D1_OUTTAG override the
# work-in-progress defaults. Defaults reproduce the existing RC1 files.
FAMILY = os.environ.get('D1_FAMILY', 'PRIVATE PROOF Drift D1 RC1')
PS = os.environ.get('D1_PS', 'PrivateProofDriftD1RC1')
OUTTAG = os.environ.get('D1_OUTTAG', 'DriftD1-RC1')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def glyph_hash(font):
    h = hashlib.sha256()
    for g in font.getGlyphOrder():
        gl = font['glyf'][g]
        if gl.numberOfContours > 0:
            c, e, f = gl.getCoordinates(font['glyf'])
            h.update(repr((g, list(c), list(e))).encode())
    return h.hexdigest()


def bounds_at(vf_path, w):
    inst = instancer.instantiateVariableFont(TTFont(vf_path), {'wght': w})
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


qa = {'source_font': os.path.relpath(SRC, os.path.dirname(HERE)), 'source_sha256': sha(SRC)}
src = TTFont(SRC)
cmap = src.getBestCmap()
qa['coverage'] = {'glyphs': src['maxp'].numGlyphs, 'mapped_chars': len(cmap),
                  'chars': ''.join(sorted(chr(c) for c in cmap))}
qa['outline_hash_approved'] = glyph_hash(src)

# 5. collision kerning (worst case of bold and thin)
names = [cmap[c] for c in sorted(cmap) if cmap[c] != 'space']
kerns = {}
for w in (900, 100):
    b = bounds_at(SRC, w)
    for L in names:
        advL, _, xmaxL, _, _ = b[L]
        for R in names:
            _, xminR, _, _, _ = b[R]
            gap = (advL - xmaxL) + xminR
            if gap < MIN_GAP:
                kerns[(L, R)] = max(kerns.get((L, R), 0), MIN_GAP - gap)
qa['collision_pairs_kerned'] = len(kerns)
qa['collision_pairs_sample'] = sorted(((f'{L}/{R}', v) for (L, R), v in kerns.items()),
                                      key=lambda x: -x[1])[:15]
fea = 'languagesystem DFLT dflt;\nfeature kern {\n' + ''.join(
    f'  pos {L} {R} {int(round(v))};\n' for (L, R), v in sorted(kerns.items())) + '} kern;\n'
open(os.path.join(OUT, 'kern.fea'), 'w').write(fea)

rc = TTFont(SRC)
if kerns:
    addOpenTypeFeaturesFromString(rc, fea)
name = rc['name']
for nid, val in ((1, FAMILY), (4, f'{FAMILY} Thin'), (6, f'{PS}-Thin'),
                 (3, f'{FAMILY} variable proof'), (5, 'Version 0.100; PRIVATE PROOF RC1')):
    name.setName(val, nid, 3, 1, 0x409)
    name.setName(val, nid, 1, 0, 0)
vf_out = os.path.join(OUT, f'{OUTTAG}-VF.ttf')
rc.save(vf_out)

# 3 + 6. reload, outlines unchanged, instances
re = TTFont(vf_out)
qa['outline_hash_rc1'] = glyph_hash(re)
qa['outlines_frozen'] = qa['outline_hash_rc1'] == qa['outline_hash_approved']
qa['tables'] = sorted(re.keys())
inst_files = {}
for w, nm in ((100, 'Thin'), (400, 'Regular'), (900, 'Bold')):
    inst = instancer.instantiateVariableFont(TTFont(vf_out), {'wght': w})
    p = os.path.join(OUT, f'{OUTTAG}-{nm}.ttf')
    inst.save(p)
    inst_files[nm] = [os.path.relpath(p, os.path.dirname(HERE)), sha(p)]
qa['instances'] = inst_files

# 2 + 4. ink per char per weight, vertical bounds
win_a, win_d = re['OS/2'].usWinAscent, re['OS/2'].usWinDescent
ink_missing, out_of_bounds = [], []
for w in (100, 400, 900):
    f = ImageFont.truetype(vf_out, 120)
    f.set_variation_by_axes([w])
    b = bounds_at(vf_out, w)
    for c, g in cmap.items():
        if g == 'space':
            continue
        im = Image.new('L', (260, 300), 0)
        from PIL import ImageDraw
        ImageDraw.Draw(im).text((40, 20), chr(c), font=f, fill=255)
        if im.getbbox() is None:
            ink_missing.append((chr(c), w))
        if b[g][3] is not None and (b[g][4] > win_a or b[g][3] < -win_d):
            out_of_bounds.append((chr(c), w, b[g][3], b[g][4]))
qa['ink_missing'] = ink_missing
qa['outside_win_metrics'] = out_of_bounds
qa['rc1_vf'] = [os.path.relpath(vf_out, os.path.dirname(HERE)), sha(vf_out)]
qa['license'] = re['name'].getDebugName(13)
json.dump(qa, open(os.path.join(OUT, 'qa.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in qa.items() if k not in ('collision_pairs_sample',)}, indent=1))
print('top collisions:', qa['collision_pairs_sample'][:8])
