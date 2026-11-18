"""Round 4 geometry for the PRIVATE PROOF mono (provisional internal name).

Original drawings, made in this lane. Nothing is traced or derived from any
existing font. Same 12-glyph set as Stage 0. Two separate static styles:

  ink(name)    -> Clean letters. The Clean font contains ONLY these contours.
  trace(name)  -> per-glyph construction for the separate Trace display
                  style: overshoot lines on the glyph's own edges, arcs of
                  its own curves, compass centres, short diagonals. No
                  full-width metric rules (r3 ones read as under/strike lines).

Identity moves in r4 (lettering level, Clean):
  * squarer rounds (superelliptic handles) on o 0 a g n s
  * a 45-degree chamfer "cut" on free stroke ends (spurs, flag, slabs,
    brace arms, l foot): the face's signature detail
  * braces rebuilt from straight segments with 45-degree pinches
  * arch springs from the stem with a narrow, high join
Units: UPM 1000, y-up, advance 600.
"""
from math import hypot, cos, sin, pi

UPM, ADV = 1000, 600
CAP, XH, ASC, DESC = 700, 540, 740, -230
OS, STEM, HOR, RSTEM = 10, 88, 74, 92
R = 10            # soft corner radius
CH = 26           # signature chamfer on free stroke ends
GW = 12           # Trace construction line weight

# ------------------------------------------------------------ path helpers
# item: ('V', p, r) line to vertex p; r>0 round, r<0 45-degree-ish chamfer of
# size |r|, 0 sharp. ('C', c1, c2, p) cubic to p. Item 0 must be a 'V'.


def V(x, y, r=R):
    return ('V', (x, y), r)


def Cv(c1, c2, p):
    return ('C', c1, c2, p)


def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = hypot(dx, dy)
    return (dx / d, dy / d), d


def segments(items):
    n = len(items)
    end = [it[1] if it[0] == 'V' else it[3] for it in items]
    entry, exit_, fil = list(end), list(end), [None] * n
    for i, it in enumerate(items):
        nxt = items[(i + 1) % n]
        if it[0] == 'V' and it[2] and nxt[0] == 'V':
            p, prev, nx = end[i], end[i - 1], end[(i + 1) % n]
            din, lin = _unit(prev, p)
            dout, lout = _unit(p, nx)
            if abs(din[0] * dout[1] - din[1] * dout[0]) < 1e-6:
                continue
            r = min(abs(it[2]), lin / 2.1, lout / 2.1)
            a = (p[0] - din[0] * r, p[1] - din[1] * r)
            b = (p[0] + dout[0] * r, p[1] + dout[1] * r)
            entry[i], exit_[i] = a, b
            if it[2] > 0:
                k = 0.552
                fil[i] = ('C', (a[0] + (p[0] - a[0]) * k, a[1] + (p[1] - a[1]) * k),
                          (b[0] + (p[0] - b[0]) * k, b[1] + (p[1] - b[1]) * k), b)
            else:
                fil[i] = ('L', b)
    start, segs = exit_[0], []
    for j in range(1, n + 1):
        i = j % n
        it = items[i]
        segs.append(('L', entry[i]) if it[0] == 'V' else ('C', it[1], it[2], it[3]))
        if fil[i]:
            segs.append(fil[i])
    return start, segs


def poly(*pts, r=R):
    return [V(p[0], p[1], p[2] if len(p) > 2 else r) for p in pts]


def oval(cx, cy, rx, ry, k=0.5523):
    return [
        V(cx, cy + ry, 0),
        Cv((cx + rx * k, cy + ry), (cx + rx, cy + ry * k), (cx + rx, cy)),
        Cv((cx + rx, cy - ry * k), (cx + rx * k, cy - ry), (cx, cy - ry)),
        Cv((cx - rx * k, cy - ry), (cx - rx, cy - ry * k), (cx - rx, cy)),
        Cv((cx - rx, cy + ry * k), (cx - rx * k, cy + ry), (cx, cy + ry)),
    ]


def mirror(items, axis=ADV / 2):
    def m(p):
        return (2 * axis - p[0], p[1])
    return [('V', m(it[1]), it[2]) if it[0] == 'V' else
            ('C', m(it[1]), m(it[2]), m(it[3])) for it in items]


def hole(items):
    return ('hole', items)


# ------------------------------------------------------------ Clean letters
def _H():
    l0, l1, r0, r1 = 80, 80 + STEM, 520 - STEM, 520
    b0, b1 = 352, 352 + HOR
    return [poly((l0, 0), (l0, CAP), (l1, CAP), (l1, b1), (r0, b1), (r0, CAP),
                 (r1, CAP), (r1, 0), (r0, 0), (r0, b0), (l1, b0), (l1, 0))]


def _n():
    l0, l1, r0, r1 = 80, 80 + STEM, 520 - STEM, 520
    top = XH + 8
    itop = top - HOR
    return [[
        V(l0, 0), V(l0, XH), V(l1, XH, 0), V(l1, 474, 0),
        Cv((190, 524), (236, top), (316, top)),
        Cv((470, top), (r1, 506), (r1, 372)),
        V(r1, 0), V(r0, 0), V(r0, 360, 0),
        Cv((r0, 442), (410, itop), (310, itop)),
        Cv((250, itop), (200, 450), (l1, 404)),
        V(l1, 0, 0),
    ]]


def _o():
    rx, ry, cy = 232, (XH + 2 * OS) / 2, XH / 2
    return [oval(300, cy, rx, ry, 0.70),
            hole(oval(300, cy, rx - RSTEM, ry - HOR, 0.68))]


def _bowl(join_bottom):
    s0, s1 = 520 - STEM, 520
    top, bot = XH + OS, -OS
    outer = [
        V(s1, 0, R) if join_bottom else V(s1, -40, 0), V(s1, XH), V(s0, XH, 0), V(s0, 480, 0),
        Cv((400, 528), (350, top), (286, top)),
        Cv((128, top), (80, 470), (80, 270)),
        Cv((80, 70), (128, bot), (286, bot)),
        Cv((350, bot), (400, 12), (s0, 60)),
    ]
    inner = [
        V(s0, 410, 0),
        Cv((404, 456), (354, top - HOR), (292, top - HOR)),
        Cv((196, top - HOR), (172, 420), (172, 270)),
        Cv((172, 120), (196, bot + HOR), (292, bot + HOR)),
        Cv((354, bot + HOR), (404, 84), (s0, 130)),
    ]
    return outer, inner


def _a():
    outer, inner = _bowl(True)
    return [outer + [V(520 - STEM, 0, 0)], hole(inner)]


def _g():
    outer, inner = _bowl(False)
    s0, s1 = 520 - STEM, 520
    b = DESC - 4
    tail = [
        V(s0, -44, 0),
        Cv((s0, -128), (390, b + HOR), (296, b + HOR)),
        Cv((220, b + HOR), (170, -150), (128, -140)),
        V(128, -216, 0),
        Cv((180, -230), (226, b), (296, b)),
        Cv((460, b), (s1, -160), (s1, -40)),
    ]
    return [outer + tail, hole(inner)]


def _s():
    return [[
        V(500, 434, 0),
        Cv((500, 514), (430, 550), (302, 550)),
        Cv((168, 550), (102, 504), (102, 408)),
        Cv((102, 316), (170, 290), (290, 262)),
        Cv((390, 238), (424, 216), (424, 152)),
        Cv((424, 92), (382, 64), (300, 64)),
        Cv((222, 64), (180, 90), (178, 126)),
        V(84, 126, 0),
        Cv((86, 30), (166, -10), (300, -10)),
        Cv((450, -10), (516, 54), (516, 158)),
        Cv((516, 256), (450, 290), (330, 318)),
        Cv((230, 342), (194, 360), (194, 406)),
        Cv((194, 456), (240, 476), (302, 476)),
        Cv((372, 476), (404, 458), (406, 434)),
    ]]


def _zero():
    cy, rx, ry, d = CAP / 2, 206, CAP / 2 + OS, 48
    return [oval(300, cy, rx, ry, 0.74),
            hole(oval(300, cy, rx - RSTEM, ry - HOR, 0.72)),
            poly((300 - d, cy - d), (300 - d, cy + d), (300 + d, cy + d), (300 + d, cy - d))]


# brace: straight segments, 45-degree corners and pinch, chamfered arm tips
BR_TOP, BR_BOT, BR_MID = 760, -130, 315
BR_S0, BR_S1, BR_ARM, BR_END = 236, 316, 68, 470
BR_NOSE = 126


def _brace():
    t, b, m, s0, s1, a, e = BR_TOP, BR_BOT, BR_MID, BR_S0, BR_S1, BR_ARM, BR_END
    return [poly(
        (e, t, -CH), (s0 + 70, t), (s0, t - 70), (s0, m + 125),
        (BR_NOSE, m + 15), (BR_NOSE, m - 15), (s0, m - 125), (s0, b + 70),
        (s0 + 70, b), (e, b, -CH), (e, b + a), (s1 + 18, b + a, 6), (s1, b + a + 18, 6),
        (s1, m - 100), (s1 - 100, m, 4), (s1, m + 100), (s1, t - a - 18, 6),
        (s1 + 18, t - a, 6), (e, t - a))]


def _i():
    s0, s1 = 256, 256 + STEM
    return [poly((110, 0), (110, HOR, -CH), (s0, HOR, 0), (s0, XH - HOR),
                 (136, XH - HOR), (136, XH, -CH), (s1, XH), (s1, HOR, 0),
                 (490, HOR, -CH), (490, 0)),
            poly((250, 616), (250, 716), (350, 716), (350, 616))]


def _l():
    s0, s1 = 212, 212 + STEM
    return [[
        V(100, ASC, -CH), V(s1, ASC), V(s1, 200, 0),
        Cv((s1, 112), (340, HOR - 4), (412, HOR - 4)),
        V(504, HOR - 4, -CH), V(504, -4),
        V(400, -4, 0),
        Cv((266, -4), (s0, 60), (s0, 200)),
        V(s0, ASC - HOR), V(100, ASC - HOR),
    ]]


def _one():
    s0, s1 = 262, 262 + STEM
    return [poly((112, 0), (112, HOR, -CH), (s0, HOR, 0), (s0, 598, 0), (122, 500),
                 (122, 592, -CH), (s0, 690), (s0 + 14, CAP), (s1, CAP), (s1, HOR, 0),
                 (488, HOR, -CH), (488, 0))]


INK = {
    'H': _H, 'n': _n, 'o': _o, 'a': _a, 'g': _g, 's': _s, 'zero': _zero,
    'braceleft': _brace, 'braceright': lambda: [mirror(_brace()[0])],
    'i': _i, 'l': _l, 'one': _one, 'space': lambda: [],
    '.notdef': lambda: [poly((60, 0), (60, 700), (540, 700), (540, 0), r=0),
                        hole(poly((120, 60), (120, 640), (480, 640), (480, 60), r=0))],
}
CMAP = {'H': 0x48, 'n': 0x6E, 'o': 0x6F, 'a': 0x61, 'g': 0x67, 's': 0x73,
        'zero': 0x30, 'braceleft': 0x7B, 'braceright': 0x7D, 'i': 0x69,
        'l': 0x6C, 'one': 0x31, 'space': 0x20}
ORDER = ['.notdef', 'space', 'H', 'n', 'o', 'a', 'g', 's', 'zero',
         'braceleft', 'braceright', 'i', 'l', 'one']


def ink(name):
    return INK[name]()


# ------------------------------------------------------------ Trace layer
def line(p, q, w=GW):
    (ux, uy), _ = _unit(p, q)
    nx, ny = -uy * w / 2, ux * w / 2
    return poly((p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny), r=0)


def vline(x, y0, y1):
    return line((x, y0), (x, y1))


def hline(y, x0, x1):
    return line((x0, y), (x1, y))


def cross(cx, cy, s=34):
    return [hline(cy, cx - s, cx + s), vline(cx, cy - s, cy + s)]


def ring(cx, cy, rx, ry, k, w=GW):
    return [oval(cx, cy, rx + w / 2, ry + w / 2, k),
            hole(oval(cx, cy, rx - w / 2, ry - w / 2, k))]


def arc(cx, cy, r, a0, a1, w=GW, n=10, ry=None):
    """Elliptical arc band (rx=r, ry) from angle a0 to a1 (degrees)."""
    ry = r if ry is None else ry
    out, inn = [], []
    for i in range(n + 1):
        a = (a0 + (a1 - a0) * i / n) * pi / 180
        out.append((cx + (r + w / 2) * cos(a), cy + (ry + w / 2) * sin(a), 0))
        inn.append((cx + (r - w / 2) * cos(a), cy + (ry - w / 2) * sin(a), 0))
    return poly(*(out + inn[::-1]), r=0)


def tick(p, d, ln_out=44, ln_in=20):
    """Short tick across the outline at p, along unit direction d (outward)."""
    return line((p[0] - d[0] * ln_in, p[1] - d[1] * ln_in),
                (p[0] + d[0] * ln_out, p[1] + d[1] * ln_out))


OV = 46  # how far construction lines overshoot past a corner


def trace(name):
    t = []
    if name in ('.notdef', 'space'):
        return t
    if name == 'H':
        for x in (80, 168, 432, 520):           # stem edges overshoot
            t += [vline(x, -OV, 0 + 4), vline(x, CAP - 4, CAP + OV)]
        for y in (352, 426):                     # bar edges run into the counters' sides
            t += [hline(y, 80 - OV, 80 + 4), hline(y, 520 - 4, 520 + OV)]
    elif name == 'n':
        t += ring(300, 360, 176, 152, 0.62)      # the arch's own construction oval
        for x in (80, 168, 432, 520):
            t += [vline(x, -OV, 4)]
        t += [vline(80, XH - 4, XH + OV)]
    elif name in ('o', 'zero'):
        cy = XH / 2 if name == 'o' else CAP / 2
        rx = 232 if name == 'o' else 206
        ry = (XH + 2 * OS) / 2 if name == 'o' else CAP / 2 + OS
        if name == 'o':
            t += cross(300, cy)
        # r4c: no side ticks - at mid-height they chained into a dashed
        # strike line across 'oag' in running text
        for p, d in (((300, cy + ry), (0, 1)), ((300, cy - ry), (0, -1))):
            t += [tick(p, d)]
    elif name == 'a':
        t += cross(286, 270)
        t += [vline(520, -OV, 4), vline(520, XH - 4, XH + OV), vline(432, XH - 4, XH + OV)]
        t += [tick((286, XH + OS), (0, 1)), tick((286, -OS), (0, -1))]
    elif name == 'g':
        t += cross(286, 270)
        t += [vline(520, XH - 4, XH + OV), vline(432, XH - 4, XH + OV)]
        t += [tick((286, XH + OS), (0, 1))]
        t += [arc(296, -48, 140, 180, 250)]       # tail circle, continued up-left
    elif name == 's':
        # r4b: open arcs continuing each bowl past its terminal (full rings
        # closed the s into an '8')
        t += [arc(300, 398, 154, 14, -62, ry=116)]
        t += [arc(300, 154, 170, 190, 128, ry=127)]
    elif name in ('braceleft', 'braceright'):
        # pinch diagonals continued until they cross (an X left of the nose),
        # and the uncut corners the 45-degree chamfers were taken from
        ax, ay = BR_S0 - (BR_MID + 125 - BR_MID), BR_MID   # virtual apex
        ax = BR_NOSE - 15
        g = [line((BR_S0 - 6, BR_MID + 131), (ax - 40, ay - 40)),
             line((BR_S0 - 6, BR_MID - 131), (ax - 40, ay + 40))]
        for y, s in ((BR_TOP, 1), (BR_BOT, -1)):
            g += [hline(y, BR_S0 - 40, BR_S0 + 74), vline(BR_S0, y - s * 74, y + s * 40)]
        if name == 'braceright':
            g = [mirror(c) for c in g]
        t += g
    elif name == 'i':
        for x in (256, 344):
            t += [vline(x, -OV, 4)]
    elif name == 'l':
        # no closed shapes here (r3: a foot circle made l read as b)
        for x in (212, 300):
            t += [vline(x, ASC - 4, ASC + OV)]
        t += [hline(HOR - 4, 504 - 30, 504 + OV)]
    elif name == 'one':
        p, q = (122, 592), (262, 690)
        (ux, uy), _ = _unit(p, q)
        t += [line((p[0] - ux * 70, p[1] - uy * 70), (q[0] + ux * 90, q[1] + uy * 90))]
        for x in (262, 350):
            t += [vline(x, -OV, 4)]
        t += [vline(350, CAP - 4, CAP + OV)]
    return t
