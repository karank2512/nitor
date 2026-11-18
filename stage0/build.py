"""Build Stage 0 PRIVATE PROOF fonts with the already-installed fontTools.

Outputs (stage0/out/fonts/):
  ProofClean.ttf      static, ink only (no ghost contours at all)
  ProofGhost.ttf      static, ink + ghost at full stroke (14 units)
  ProofTRCE-z0.ttf    variable, axis TRCE 0..100, ghost width 0 -> 14
                      (default master has zero-area ghost contours)
  ProofTRCE-h2.ttf    variable, axis TRCE 0..100, ghost width 2 -> 14
                      (hairline fallback)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fontTools.fontBuilder import FontBuilder  # noqa: E402
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates  # noqa: E402
from fontTools.ttLib.tables.TupleVariation import TupleVariation  # noqa: E402
from fontTools.cu2qu import curve_to_quadratic  # noqa: E402

import glyphs as G  # noqa: E402

OUT = os.path.join(HERE, 'out', 'fonts')
FAMILY = 'PRIVATE PROOF TraceMono S0'   # provisional internal name only
NOTICE = ('PRIVATE PROOF - Stage 0 exploration. Not a release, not licensed '
          'for distribution. Original drawings; name and license TBD by Karan.')


def area(pts):
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i][:2]
        x1, y1 = pts[i - 1][:2]
        s += (x0 - x1) * (y0 + y1)
    return s / 2  # >0 = clockwise in y-up with this formula


def ink_contours(name):
    """Return list of TT point contours (x, y, on) for the ink layer,
    outer clockwise, holes counter-clockwise."""
    res = []
    for c in G.ink(name):
        role = 'outer'
        if isinstance(c, tuple) and c[0] == 'hole':
            role, c = 'hole', c[1]
        start, segs = G.segments(c)
        pts = [(start[0], start[1], 1)]
        cur = start
        for s in segs:
            if s[0] == 'L':
                pts.append((s[1][0], s[1][1], 1))
                cur = s[1]
            else:
                q = curve_to_quadratic([cur, s[1], s[2], s[3]], 0.6)
                for p in q[1:-1]:
                    pts.append((p[0], p[1], 0))
                pts.append((s[3][0], s[3][1], 1))
                cur = s[3]
        # round + drop consecutive duplicates / closing duplicate
        r = []
        for x, y, on in pts:
            p = (round(x), round(y), on)
            if r and p[:2] == r[-1][:2] and p[2] == r[-1][2]:
                continue
            r.append(p)
        while len(r) > 1 and r[-1][:2] == r[0][:2] and r[-1][2] == 1:
            r.pop()
        cw = area(r) > 0
        if (role == 'outer') != cw:
            r = [r[0]] + r[1:][::-1]
        res.append(r)
    return res


def ghost_contours(name, w, ref_w=G.GHOST_MAX):
    """Ghost contours at width w. Orientation is decided on the ref_w master
    and applied identically to every master to keep point compatibility."""
    cur = G.ghost(name, w)
    ref = G.ghost(name, ref_w)
    out = []
    for c, rc in zip(cur, ref):
        c = [(round(x), round(y), on) for x, y, on in c]
        out.append(c)
    # verify orientation on the reference master: rings are (outer cw,
    # inner ccw) pairs, every other band is cw
    i = 0
    while i < len(ref):
        if len(ref[i]) == 16:
            assert area(ref[i]) > 0 and area(ref[i + 1]) < 0, (name, i)
            i += 2
        else:
            assert area(ref[i]) > 0, (name, i)
            i += 1
    return out
    return out


def make_glyph(contours):
    g = Glyph()
    if not contours:
        g.numberOfContours = 0
        return g
    coords, flags, ends = [], [], []
    for c in contours:
        for x, y, on in c:
            coords.append((x, y))
            flags.append(1 if on else 0)
        ends.append(len(coords) - 1)
    g.coordinates = GlyphCoordinates(coords)
    g.flags = bytearray(flags)
    g.endPtsOfContours = ends
    g.numberOfContours = len(ends)
    g.program = None
    from fontTools.ttLib.tables import ttProgram
    g.program = ttProgram.Program()
    g.program.fromBytecode(b'')
    return g


def notdef():
    o = G.poly((60, 0), (60, 700), (540, 700), (540, 0), r=0)
    i = G.poly((120, 60), (120, 640), (480, 640), (480, 60), r=0)
    return [o, ('hole', i)]


def glyph_points(name, w):
    if name == '.notdef':
        G.INK['.notdef'] = notdef
    ink = ink_contours(name)
    gh = [] if w is None else ghost_contours(name, w)
    return ink + gh


def _panose():
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    p = Panose()
    for k in ('bFamilyType', 'bSerifStyle', 'bWeight', 'bProportion',
              'bContrast', 'bStrokeVariation', 'bArmStyle', 'bLetterForm',
              'bMidline', 'bXHeight'):
        setattr(p, k, 0)
    p.bFamilyType, p.bProportion = 2, 9  # Latin text, monospaced
    return p


def base_font(style, glyph_map, variable_axes=None):
    fb = FontBuilder(G.UPM, isTTF=True)
    fb.setupGlyphOrder(G.ORDER)
    fb.setupCharacterMap({u: n for n, u in G.CMAP.items()})
    fb.setupGlyf(glyph_map)
    metrics = {}
    for n in G.ORDER:
        g = glyph_map[n]
        g.recalcBounds(fb.font['glyf'])
        metrics[n] = (G.ADV, getattr(g, 'xMin', 0) if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-260, lineGap=0)
    fb.setupNameTable({
        'familyName': FAMILY,
        'styleName': style,
        'uniqueFontIdentifier': f'{FAMILY} {style} stage0-r1',
        'fullName': f'{FAMILY} {style}',
        'psName': f'PrivateProofTraceMonoS0-{style.replace(" ", "")}',
        'version': 'Version 0.001; PRIVATE PROOF',
        'copyright': 'PRIVATE PROOF. Original work; copyright holder TBD by Karan.',
        'description': NOTICE,
        'licenseDescription': 'No license granted. PRIVATE PROOF.',
    })
    fb.setupOS2(sTypoAscender=G.ASC, sTypoDescender=G.DESC, sTypoLineGap=230,
                usWinAscent=900, usWinDescent=260, sxHeight=G.XH,
                sCapHeight=G.CAP, achVendID='NONE', fsType=0x0002,
                fsSelection=0x00C0, xAvgCharWidth=G.ADV,
                version=4, panose=_panose())
    fb.setupPost(isFixedPitch=1, underlinePosition=-120, underlineThickness=50)
    return fb


def build_static(style, w):
    gm = {n: G and make_glyph(glyph_points(n, w)) for n in G.ORDER}
    fb = base_font(style, gm)
    p = os.path.join(OUT, f'Proof{style}.ttf')
    fb.save(p)
    return p


def build_var(tag, w0, w1):
    m0 = {n: glyph_points(n, w0) for n in G.ORDER}
    m1 = {n: glyph_points(n, w1) for n in G.ORDER}
    gm = {n: make_glyph(m0[n]) for n in G.ORDER}
    fb = base_font(f'TRCE {tag}', gm)
    fb.setupFvar(axes=[('TRCE', 0, 0, 100, 'Trace')],
                 instances=[{'stylename': 'Clean', 'location': {'TRCE': 0}},
                            {'stylename': 'Trace', 'location': {'TRCE': 100}}])
    variations = {}
    for n in G.ORDER:
        a = [p for c in m0[n] for p in c]
        b = [p for c in m1[n] for p in c]
        assert len(a) == len(b), (n, len(a), len(b))
        assert all(x[2] == y[2] for x, y in zip(a, b)), n
        deltas = [(q[0] - p[0], q[1] - p[1]) for p, q in zip(a, b)]
        deltas += [(0, 0)] * 4  # phantom points: advance never varies
        if any(d != (0, 0) for d in deltas):
            variations[n] = [TupleVariation({'TRCE': (0, 1.0, 1.0)}, deltas)]
    fb.setupGvar(variations)
    p = os.path.join(OUT, f'ProofTRCE-{tag}.ttf')
    fb.save(p)
    return p


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for p in (build_static('Clean', None),
              build_static('Ghost', G.GHOST_MAX),
              build_var('z0', 0, G.GHOST_MAX),
              build_var('h2', 2, G.GHOST_MAX)):
        print(p)
