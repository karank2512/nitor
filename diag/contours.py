"""Dump every glyph's contours (points, signed area, bbox) per font file, flag
zero-area / degenerate contours, and check that Clean's contours are an
exact prefix of each ghost font's contours (ink identical, ghost appended).
Usage: python3.11 diag/contours.py <fontdir> <out.txt> [files...]
"""
import sys
from fontTools.ttLib import TTFont

fontdir, out = sys.argv[1:3]
files = sys.argv[3:] or ['ProofClean.ttf', 'ProofTRCE-z0.ttf', 'ProofTRCE-h2.ttf', 'ProofGhost.ttf']


def contours(font, name):
    g = font['glyf'][name]
    if g.numberOfContours <= 0:
        return []
    coords, ends, flags = g.getCoordinates(font['glyf'])  # fontTools order
    res, s = [], 0
    for e in ends:
        res.append([(coords[i][0], coords[i][1], flags[i] & 1) for i in range(s, e + 1)])
        s = e + 1
    return res


def area(c):
    a = 0.0
    for i in range(len(c)):
        a += (c[i][0] - c[i - 1][0]) * (c[i][1] + c[i - 1][1])
    return a / 2


lines = []
fonts = {f: TTFont(f'{fontdir}/{f}') for f in files}
clean = fonts[files[0]]
for f, font in fonts.items():
    lines.append(f'== {f}')
    for name in font.getGlyphOrder():
        cs = contours(font, name)
        n_clean = len(contours(clean, name))
        flags = []
        for k, c in enumerate(cs):
            a = area(c)
            xs, ys = [p[0] for p in c], [p[1] for p in c]
            tag = 'ink' if k < n_clean else 'ghost'
            deg = ' ZERO-AREA' if abs(a) < 1 else ''
            flags.append(f'    c{k} {tag:5s} pts={len(c):3d} area={a:10.0f} '
                         f'bbox=({min(xs)},{min(ys)})-({max(xs)},{max(ys)}){deg}')
        prefix_ok = cs[:n_clean] == contours(clean, name)
        zero = sum('ZERO-AREA' in x for x in flags)
        lines.append(f'  {name:11s} contours={len(cs):2d} (clean ink={n_clean}) '
                     f'ink-identical-to-clean={prefix_ok} zero-area={zero}')
        lines += flags
open(out, 'w').write('\n'.join(lines) + '\n')
for l in lines:
    if l.startswith('==') or ('contours=' in l):
        print(l)
