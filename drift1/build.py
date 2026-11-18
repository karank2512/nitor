# Copyright (c) 2026, Karan Kapur, with Reserved Font Name "Nitor".
# This file is part of the Nitor Font Software, licensed under the
# SIL Open Font License, Version 1.1 (see OFL.txt).
"""Build the D1 PRIVATE PROOF variable font (wght 100-900) + static instances,
with the existing fontTools 4.39.4 run as-is. Masters: thin (default, wght
100) and bold (wght 900); point structure is shared so they interpolate.
Advance widths vary through gvar phantom points. No kerning; unhinted;
overlapping contours (nonzero)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fontTools.fontBuilder import FontBuilder  # noqa: E402
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates  # noqa: E402
from fontTools.ttLib.tables import ttProgram  # noqa: E402
from fontTools.ttLib.tables.TupleVariation import TupleVariation  # noqa: E402
from fontTools.ttLib.tables.O_S_2f_2 import Panose  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402
import glyphs as K  # noqa: E402

OUT = os.path.join(HERE, 'out', 'fonts')
FAMILY = 'PRIVATE PROOF Drift D1'


def area(p):
    return sum((p[i][0] - p[i - 1][0]) * (p[i][1] + p[i - 1][1]) for i in range(len(p))) / 2


def master(name, P):
    raw = K.G[name](P)
    pts = [p for c in raw for p in (c[1] if isinstance(c, tuple) else c)]
    if not pts:
        return [], K.ADV_FIXED.get(name, 260), 0
    xmin, xmax = min(p[0] for p in pts), max(p[0] for p in pts)
    lsb, rsb = K.SB[name]
    dx = lsb - xmin
    res = []
    for c in raw:
        role = 'outer'
        if isinstance(c, tuple):
            role, c = 'hole', c[1]
        res.append((role, [(round(x + dx), round(y)) for x, y in c]))
    return res, round(xmax - xmin + lsb + rsb), lsb


def orient(thin, bold):
    """Decide each contour's direction on the bold master, apply to both."""
    t2, b2 = [], []
    for (role, tc), (_, bc) in zip(thin, bold):
        a = area(bc)
        assert abs(a) > 50, 'degenerate bold contour'
        if (role == 'outer') != (a > 0):
            tc, bc = [tc[0]] + tc[1:][::-1], [bc[0]] + bc[1:][::-1]
        t2.append(tc)
        b2.append(bc)
    return t2, b2


def make_glyph(cs):
    g = Glyph()
    if not cs:
        g.numberOfContours = 0
        return g
    coords, ends = [], []
    for c in cs:
        coords += c
        ends.append(len(coords) - 1)
    g.coordinates = GlyphCoordinates(coords)
    g.flags = bytearray([1] * len(coords))
    g.endPtsOfContours, g.numberOfContours = ends, len(ends)
    g.program = ttProgram.Program()
    g.program.fromBytecode(b'')
    return g


def main():
    os.makedirs(OUT, exist_ok=True)
    gm, mets, variations = {}, {}, {}
    for n in K.ORDER:
        tc, tadv, tlsb = master(n, K.MASTERS['thin'])
        bc, badv, _ = master(n, K.MASTERS['bold'])
        assert [len(c) for _, c in tc] == [len(c) for _, c in bc], (n, 'masters incompatible')
        tcs, bcs = orient(tc, bc)
        gm[n] = make_glyph(tcs)
        mets[n] = (tadv, tlsb)
        a = [p for c in tcs for p in c]
        b = [p for c in bcs for p in c]
        deltas = [(q[0] - p[0], q[1] - p[1]) for p, q in zip(a, b)]
        deltas += [(0, 0), (badv - tadv, 0), (0, 0), (0, 0)]   # phantom: advance grows
        if any(d != (0, 0) for d in deltas):
            variations[n] = [TupleVariation({'wght': (0, 1.0, 1.0)}, deltas)]
    fb = FontBuilder(K.UPM, isTTF=True)
    fb.setupGlyphOrder(K.ORDER)
    fb.setupCharacterMap({ord(K.CHAR[n]): n for n in K.ORDER if K.CHAR.get(n)})
    fb.setupGlyf(gm)
    fb.setupHorizontalMetrics(mets)
    fb.setupHorizontalHeader(ascent=950, descent=-280, lineGap=0)
    fb.setupNameTable({
        'familyName': FAMILY, 'styleName': 'Thin',
        'uniqueFontIdentifier': f'{FAMILY} variable proof', 'fullName': f'{FAMILY} Thin',
        'psName': 'PrivateProofDriftD1-Thin', 'version': 'Version 0.001; PRIVATE PROOF',
        'copyright': 'PRIVATE PROOF. Original work; copyright holder TBD by Karan.',
        'description': 'PRIVATE PROOF - exploratory display face, partial set, not a release.',
        'licenseDescription': 'No license granted. PRIVATE PROOF.'})
    p = Panose()
    for k in ('bFamilyType', 'bSerifStyle', 'bWeight', 'bProportion', 'bContrast',
              'bStrokeVariation', 'bArmStyle', 'bLetterForm', 'bMidline', 'bXHeight'):
        setattr(p, k, 0)
    fb.setupOS2(sTypoAscender=K.ASC, sTypoDescender=K.DESC, sTypoLineGap=200, usWinAscent=950,
                usWinDescent=280, sxHeight=K.XH, sCapHeight=K.CAP, achVendID='NONE',
                fsType=0x0002, fsSelection=0x00C0, version=4, panose=p, usWeightClass=100)
    fb.setupPost(underlinePosition=-120, underlineThickness=40)
    fb.setupFvar(axes=[('wght', 100, 100, 900, 'Weight')],
                 instances=[{'stylename': 'Thin', 'location': {'wght': 100}},
                            {'stylename': 'Regular', 'location': {'wght': 400}},
                            {'stylename': 'Bold', 'location': {'wght': 900}}])
    fb.setupGvar(variations)
    vpath = os.path.join(OUT, 'DriftD1-VF.ttf')
    fb.save(vpath)
    print(vpath, len(K.ORDER), 'glyphs; cmap', len([n for n in K.ORDER if K.CHAR.get(n)]))
    for w, nm in ((100, 'Thin'), (400, 'Regular'), (900, 'Bold')):
        inst = instancer.instantiateVariableFont(TTFont(vpath), {'wght': w})
        sp = os.path.join(OUT, f'DriftD1-{nm}.ttf')
        inst.save(sp)
        print(sp)


if __name__ == '__main__':
    main()
