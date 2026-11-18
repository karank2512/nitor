"""Build the r4 PRIVATE PROOF static fonts (existing fontTools 4.39.4, as-is).

  out/fonts/R4Clean.ttf  -> ink contours only (no construction contours at all)
  out/fonts/R4Trace.ttf  -> ink + per-glyph construction (display style)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fontTools.fontBuilder import FontBuilder  # noqa: E402
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates  # noqa: E402
from fontTools.ttLib.tables import ttProgram  # noqa: E402
from fontTools.ttLib.tables.O_S_2f_2 import Panose  # noqa: E402
from fontTools.cu2qu import curve_to_quadratic  # noqa: E402
import glyphs as G  # noqa: E402

OUT = os.path.join(HERE, 'out', 'fonts')
FAMILY = 'PRIVATE PROOF TraceMono R4'
NOTICE = ('PRIVATE PROOF - round 4 exploration. Not a release, not licensed for '
          'distribution. Original drawings; name and license TBD by Karan.')


def area(pts):
    s = 0.0
    for i in range(len(pts)):
        s += (pts[i][0] - pts[i - 1][0]) * (pts[i][1] + pts[i - 1][1])
    return s / 2  # > 0: clockwise (y-up)


def to_tt(items_list):
    res = []
    for c in items_list:
        role = 'outer'
        if isinstance(c, tuple) and c[0] == 'hole':
            role, c = 'hole', c[1]
        start, segs = G.segments(c)
        pts, cur = [(start[0], start[1], 1)], start
        for s in segs:
            if s[0] == 'L':
                pts.append((s[1][0], s[1][1], 1))
                cur = s[1]
            else:
                q = curve_to_quadratic([cur, s[1], s[2], s[3]], 0.6)
                pts += [(p[0], p[1], 0) for p in q[1:-1]] + [(s[3][0], s[3][1], 1)]
                cur = s[3]
        r = []
        for x, y, on in pts:
            p = (round(x), round(y), on)
            if r and p == r[-1]:
                continue
            r.append(p)
        while len(r) > 1 and r[-1][:2] == r[0][:2] and r[-1][2] == 1:
            r.pop()
        a = area(r)
        assert abs(a) > 50, ('degenerate contour', a)   # no zero-area contours, ever
        if (role == 'outer') != (a > 0):
            r = [r[0]] + r[1:][::-1]
        res.append(r)
    return res


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
    g.program = ttProgram.Program()
    g.program.fromBytecode(b'')
    return g


def panose():
    p = Panose()
    for k in ('bFamilyType', 'bSerifStyle', 'bWeight', 'bProportion', 'bContrast',
              'bStrokeVariation', 'bArmStyle', 'bLetterForm', 'bMidline', 'bXHeight'):
        setattr(p, k, 0)
    p.bFamilyType, p.bProportion = 2, 9
    return p


def build(style, with_trace):
    gm = {}
    for n in G.ORDER:
        items = G.ink(n) + (G.trace(n) if with_trace else [])
        gm[n] = make_glyph(to_tt(items))
    fb = FontBuilder(G.UPM, isTTF=True)
    fb.setupGlyphOrder(G.ORDER)
    fb.setupCharacterMap({u: n for n, u in G.CMAP.items()})
    fb.setupGlyf(gm)
    metrics = {}
    for n in G.ORDER:
        g = gm[n]
        if g.numberOfContours:
            g.recalcBounds(fb.font['glyf'])
        metrics[n] = (G.ADV, g.xMin if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-260, lineGap=0)
    fb.setupNameTable({
        'familyName': FAMILY, 'styleName': style,
        'uniqueFontIdentifier': f'{FAMILY} {style} r4',
        'fullName': f'{FAMILY} {style}',
        'psName': f'PrivateProofTraceMonoR4-{style}',
        'version': 'Version 0.004; PRIVATE PROOF',
        'copyright': 'PRIVATE PROOF. Original work; copyright holder TBD by Karan.',
        'description': NOTICE,
        'licenseDescription': 'No license granted. PRIVATE PROOF.',
    })
    fb.setupOS2(sTypoAscender=G.ASC, sTypoDescender=G.DESC, sTypoLineGap=230,
                usWinAscent=900, usWinDescent=260, sxHeight=G.XH, sCapHeight=G.CAP,
                achVendID='NONE', fsType=0x0002, fsSelection=0x00C0,
                xAvgCharWidth=G.ADV, version=4, panose=panose())
    fb.setupPost(isFixedPitch=1, underlinePosition=-120, underlineThickness=50)
    p = os.path.join(OUT, f'R4{style}.ttf')
    fb.save(p)
    return p


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    print(build('Clean', False))
    print(build('Trace', True))
