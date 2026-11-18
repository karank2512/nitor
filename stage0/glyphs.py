"""Stage 0 glyph geometry for the PRIVATE PROOF mono (working title only).

Original drawings: every coordinate here was chosen in this lane from the
metrics in the design brief. Nothing is traced, copied or derived from any
existing font.

Pure Python, no dependencies. Units: UPM 1000, y-up, advance 600.

Two layers per glyph:
  ink(name)      -> list of contours made of line / cubic segments
  ghost(name, w) -> list of TrueType-ready quadratic contours whose stroke
                    width is w. The point structure is independent of w, so
                    w=0 / w=2 / w=14 masters are point-compatible.
"""
from math import cos, sin, pi, hypot

UPM = 1000
ADV = 600
CAP = 700
XH = 540
ASC = 740
DESC = -230
OS = 10            # overshoot for rounds
STEM = 88          # wght 400 stem
HOR = 74           # horizontals ~0.84 x stem
RSTEM = 92         # round verticals ~1.05 x stem
R = 10             # corner softening radius
GHOST_MAX = 14     # ghost stroke at TRCE 100

# ---------------------------------------------------------------- helpers
# A contour is a list of items. ('V', (x, y), r) = line to a vertex, rounded
# with radius r if both adjacent segments are lines. ('C', c1, c2, p) = cubic
# to p. Item 0 must be a 'V' (the start point). The contour is closed.


def V(x, y, r=R):
    return ('V', (x, y), r)


def Cv(c1, c2, p):
    return ('C', c1, c2, p)


def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = hypot(dx, dy)
    return (dx / d, dy / d), d


def segments(items):
    """Expand items into (start, [segs]) with fillets. seg = ('L', p) or
    ('C', c1, c2, p)."""
    n = len(items)
    end = [it[1] if it[0] == 'V' else it[3] for it in items]
    entry, exit_ = list(end), list(end)
    fillet = [None] * n
    for i, it in enumerate(items):
        nxt = items[(i + 1) % n]
        if it[0] == 'V' and it[2] and nxt[0] == 'V':
            p, prev, nx = end[i], end[i - 1], end[(i + 1) % n]
            din, lin = _unit(prev, p)
            dout, lout = _unit(p, nx)
            if abs(din[0] * dout[1] - din[1] * dout[0]) < 1e-6:
                continue  # collinear, nothing to round
            r = min(it[2], lin / 2.1, lout / 2.1)
            a = (p[0] - din[0] * r, p[1] - din[1] * r)
            b = (p[0] + dout[0] * r, p[1] + dout[1] * r)
            k = 0.552
            c1 = (a[0] + (p[0] - a[0]) * k, a[1] + (p[1] - a[1]) * k)
            c2 = (b[0] + (p[0] - b[0]) * k, b[1] + (p[1] - b[1]) * k)
            entry[i], exit_[i] = a, b
            fillet[i] = (c1, c2, b)
    start = exit_[0]
    segs = []
    for j in range(1, n + 1):
        i = j % n
        it = items[i]
        if it[0] == 'V':
            segs.append(('L', entry[i]))
        else:
            segs.append(('C', it[1], it[2], it[3]))
        if fillet[i]:
            c1, c2, b = fillet[i]
            segs.append(('C', c1, c2, b))
    return start, segs


def poly(*pts, r=R):
    return [V(x, y, r) for x, y in pts]


def oval(cx, cy, rx, ry, k=0.5523):
    """Superellipse-ish oval from 4 cubics. k=0.5523 is a circle; larger
    values square it off."""
    return [
        V(cx, cy + ry, 0),
        Cv((cx + rx * k, cy + ry), (cx + rx, cy + ry * k), (cx + rx, cy)),
        Cv((cx + rx, cy - ry * k), (cx + rx * k, cy - ry), (cx, cy - ry)),
        Cv((cx - rx * k, cy - ry), (cx - rx, cy - ry * k), (cx - rx, cy)),
        Cv((cx - rx, cy + ry * k), (cx - rx * k, cy + ry), (cx, cy + ry)),
    ]


def mirror(items, axis=ADV / 2):
    """Mirror a contour across x = axis (direction is fixed later)."""
    def m(p):
        return (2 * axis - p[0], p[1])
    out = []
    for it in items:
        if it[0] == 'V':
            out.append(('V', m(it[1]), it[2]))
        else:
            out.append(('C', m(it[1]), m(it[2]), m(it[3])))
    return out


# ---------------------------------------------------------------- ink
def ink(name):
    g = INK[name]
    return g() if callable(g) else g


def _H():
    l0, l1 = 80, 80 + STEM
    r1, r0 = 520, 520 - STEM
    b0 = 352
    b1 = b0 + HOR
    return [poly((l0, 0), (l0, CAP), (l1, CAP), (l1, b1), (r0, b1), (r0, CAP),
                 (r1, CAP), (r1, 0), (r0, 0), (r0, b0), (l1, b0), (l1, 0))]


def _n():
    l0, l1 = 80, 80 + STEM
    r0, r1 = 520 - STEM, 520
    top = XH + 8
    itop = top - HOR
    return [[
        V(l0, 0), V(l0, XH), V(l1, XH, 0), V(l1, 468, 0),
        Cv((198, 520), (248, top), (322, top)),
        Cv((448, top), (r1, 486), (r1, 360)),
        V(r1, 0), V(r0, 0), V(r0, 352, 0),
        Cv((r0, 434), (392, itop), (306, itop)),
        Cv((244, itop), (196, 446), (l1, 392)),
        V(l1, 0, 0),
    ]]


def _o():
    rx, ry = 230, (XH + 2 * OS) / 2
    cy = XH / 2
    return [oval(300, cy, rx, ry, 0.58),
            ('hole', oval(300, cy, rx - RSTEM, ry - HOR, 0.56))]


def _bowl(stem_bottom):
    """Shared bowl for a / g: stem on the right, bowl joins it thinned."""
    s0, s1 = 520 - STEM, 520
    top, bot = XH + OS, -OS
    outer = [
        V(s1, stem_bottom), V(s1, XH), V(s0, XH, 0), V(s0, 474, 0),
        Cv((404, 520), (350, top), (282, top)),
        Cv((150, top), (80, 420), (80, 270)),
        Cv((80, 112), (150, bot), (282, bot)),
        Cv((350, bot), (404, 18), (s0, 68)),
    ]
    if stem_bottom == 0:
        outer.append(V(s0, 0, 0))
    hole = [
        V(s0, 404, 0),
        Cv((404, 452), (350, top - HOR), (290, top - HOR)),
        Cv((206, top - HOR), (172, 380), (172, 270)),
        Cv((172, 160), (206, bot + HOR), (290, bot + HOR)),
        Cv((350, bot + HOR), (404, 92), (s0, 140)),
    ]
    return outer, hole


def _a():
    outer, hole = _bowl(0)
    return [outer, ('hole', hole)]


def _g():
    outer, hole = _bowl(None)
    s0, s1 = 520 - STEM, 520
    # replace the open stem bottom with a descender tail (open arc, flat cut)
    bottom = DESC - 4
    tail = [
        V(s0, 60, 0),
        V(s0, -52, 0),
        Cv((s0, -120), (384, bottom + HOR), (292, bottom + HOR)),
        Cv((226, bottom + HOR), (170, -150), (124, -140)),
        V(124, -214, 0),
        Cv((176, -228), (230, bottom), (292, bottom)),
        Cv((436, bottom), (s1, -150), (s1, -40)),
    ]
    # outer currently: starts at (s1, None) -> build explicitly
    outer = [V(s1, -40, 0)] + outer[1:]
    # outer ends with the bowl's bottom join at (s0, 68); continue down tail
    outer = outer + tail[1:-1] + [tail[-1]]
    # the last cubic ends at (s1, -40) which is the start point
    return [outer, ('hole', hole)]


def _s():
    return [[
        V(500, 432, 0),
        Cv((500, 512), (418, 550), (302, 550)),
        Cv((180, 550), (102, 496), (102, 404)),
        Cv((102, 318), (178, 288), (290, 258)),
        Cv((380, 234), (424, 212), (424, 150)),
        Cv((424, 96), (374, 64), (300, 64)),
        Cv((226, 64), (180, 92), (178, 124)),
        V(84, 124, 0),
        Cv((86, 34), (178, -10), (300, -10)),
        Cv((440, -10), (516, 56), (516, 154)),
        Cv((516, 250), (446, 288), (330, 318)),
        Cv((234, 344), (194, 360), (194, 404)),
        Cv((194, 450), (238, 476), (302, 476)),
        Cv((368, 476), (404, 456), (406, 432)),
    ]]


def _zero():
    cy = CAP / 2
    rx, ry = 205, CAP / 2 + OS
    d = 48  # square dot half-size (grid unit)
    return [oval(300, cy, rx, ry, 0.62),
            ('hole', oval(300, cy, rx - RSTEM, ry - HOR, 0.60)),
            poly((300 - d, cy - d), (300 - d, cy + d), (300 + d, cy + d), (300 + d, cy - d))]


def _brace():
    # left brace; } is its mirror
    top, bot = 760, -130
    mid = 315
    s0, s1 = 228, 228 + 80   # stem
    arm = 68
    return [[
        V(470, top), V(334, top, 0),
        Cv((268, top), (s0, 728), (s0, 660)),
        V(s0, 442, 0),
        Cv((s0, 380), (186, mid + 40), (118, mid + 36)),
        V(118, mid - 36, 0),
        Cv((186, mid - 40), (s0, 250), (s0, 188)),
        V(s0, -30, 0),
        Cv((s0, -98), (268, bot), (334, bot)),
        V(470, bot), V(470, bot + arm), V(350, bot + arm, 0),
        Cv((322, bot + arm), (s1, -50), (s1, -24)),
        V(s1, 196, 0),
        Cv((s1, 262), (276, 300), (226, mid)),
        Cv((276, 330), (s1, 368), (s1, 434)),
        V(s1, 654, 0),
        Cv((s1, 680), (322, top - arm), (350, top - arm)),
        V(470, top - arm),
    ]]


def _i():
    s0, s1 = 256, 256 + STEM
    d0, d1 = 250, 350  # square dot, 100 units
    return [poly((110, 0), (110, HOR), (s0, HOR), (s0, XH - HOR), (140, XH - HOR),
                 (140, XH), (s1, XH), (s1, HOR), (490, HOR), (490, 0)),
            poly((d0, 616), (d0, 716), (d1, 716), (d1, 616))]


def _l():
    s0, s1 = 212, 212 + STEM
    return [[
        V(104, ASC), V(s1, ASC), V(s1, 196, 0),
        Cv((s1, 118), (338, HOR - 4), (410, HOR - 4)),
        V(504, HOR - 4), V(504, -4),
        V(396, -4, 0),
        Cv((272, -4), (s0, 58), (s0, 196)),
        V(s0, ASC - HOR), V(104, ASC - HOR),
    ]]


def _one():
    s0, s1 = 262, 262 + STEM
    return [poly((112, 0), (112, HOR), (s0, HOR), (s0, 598), (122, 500),
                 (122, 588), (s0, 690), (s0 + 14, CAP), (s1, CAP), (s1, HOR),
                 (488, HOR), (488, 0))]


INK = {
    'H': _H, 'n': _n, 'o': _o, 'a': _a, 'g': _g, 's': _s, 'zero': _zero,
    'braceleft': _brace, 'braceright': lambda: [mirror(_brace()[0])],
    'i': _i, 'l': _l, 'one': _one, 'space': [],
}

CMAP = {
    'H': 0x48, 'n': 0x6E, 'o': 0x6F, 'a': 0x61, 'g': 0x67, 's': 0x73,
    'zero': 0x30, 'braceleft': 0x7B, 'braceright': 0x7D, 'i': 0x69,
    'l': 0x6C, 'one': 0x31, 'space': 0x20,
}
ORDER = ['.notdef', 'space', 'H', 'n', 'o', 'a', 'g', 's', 'zero',
         'braceleft', 'braceright', 'i', 'l', 'one']

# ---------------------------------------------------------------- ghost
# Ghost contours are emitted directly as TrueType points [(x, y, on)].
# Orientation: clockwise (y-up) for filled bands, the inner ring reversed.


def g_rect(x0, y0, x1, y1):
    # clockwise in y-up
    return [(x0, y0, 1), (x0, y1, 1), (x1, y1, 1), (x1, y0, 1)]


def g_hrule(y, w, x0=0, x1=ADV):
    return [g_rect(x0, y - w / 2, x1, y + w / 2)]


def g_vrule(x, w, y0=DESC, y1=ASC):
    return [g_rect(x - w / 2, y0, x + w / 2, y1)]


def _ellipse_pts(cx, cy, rx, ry, cw):
    n = 8
    pts = []
    k = 1 / cos(pi / n)
    for i in range(n):
        a = 2 * pi * i / n
        b = 2 * pi * (i + 0.5) / n
        pts.append((cx + rx * cos(a), cy + ry * sin(a), 1))
        pts.append((cx + rx * k * cos(b), cy + ry * k * sin(b), 0))
    if cw:
        pts = [pts[0]] + pts[1:][::-1]
    return pts


def g_ring(cx, cy, rx, ry, w):
    return [_ellipse_pts(cx, cy, rx + w / 2, ry + w / 2, True),
            _ellipse_pts(cx, cy, rx - w / 2, ry - w / 2, False)]


def g_line(p, q, w):
    """Straight guide from p to q as a w-wide band, clockwise."""
    (ux, uy), _ = _unit(p, q)
    nx, ny = -uy * w / 2, ux * w / 2
    pts = [(p[0] + nx, p[1] + ny, 1), (q[0] + nx, q[1] + ny, 1),
           (q[0] - nx, q[1] - ny, 1), (p[0] - nx, p[1] - ny, 1)]
    return [pts]


def ghost(name, w):
    if name == '.notdef':
        return []
    # Vocabulary (r2): metric rules run the full cell so they join into
    # continuous ruled lines in text; each glyph adds only the construction
    # it was actually drawn from (circles, tangent box, one guide).
    # No cell edges and no stem centrelines (r1 read as a cage).
    h = w / 2
    out = []
    out += g_hrule(0, w)
    if name == 'space':
        return out
    caplike = name in ('H', 'zero', 'one')
    top = CAP if caplike else XH
    out += g_hrule(top, w)
    if name == 'H':
        out += g_hrule(352 + HOR / 2, w)
    elif name == 'n':
        out += g_ring(300, 340, 176, 171, w)
    elif name in ('o', 'zero'):
        rx = 230 if name == 'o' else 205
        out += g_vrule(300 - rx, w, -40, top + 40)
        out += g_vrule(300 + rx, w, -40, top + 40)
    elif name == 'a':
        out += g_vrule(80, w, -40, top + 40)
    elif name == 'g':
        out += g_vrule(80, w, -40, top + 40) + g_hrule(DESC, w)
        out += g_ring(304, -60, 172, 133, w)
    elif name == 's':
        out += g_ring(300, 394, 152, 118, w)
        out += g_ring(300, 152, 170, 124, w)
    elif name in ('braceleft', 'braceright'):
        out += g_hrule(315, w)
    elif name == 'i':
        out += g_vrule(300, w, 0, 716)
    elif name == 'l':
        # r3: the foot circle read as a 'b' bowl; use the stem guide instead
        out += g_hrule(ASC - h, w)
        out += g_vrule(256, w, -40, ASC)
    elif name == 'one':
        # flag guide, extended across the cell (inset so the band stays inside)
        p, q = (114, 584), (262, 690)
        (ux, uy), _ = _unit(p, q)
        t0 = (w - p[0]) / ux
        t1 = (ADV - w - p[0]) / ux
        out += g_line((p[0] + ux * t0, p[1] + uy * t0),
                      (p[0] + ux * t1, p[1] + uy * t1), w)
    return out
