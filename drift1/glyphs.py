"""D1 - reverse-contrast "scanline" display face (PRIVATE PROOF, working
internal name only, uncommitted, not a release).

A new original direction after S3 was judged too formal. These are original
drawings, made in this lane; they are not traced or derived from any existing
font.

Idea: invert the usual stress. Verticals are hairlines; every horizontal
(arch tops, bowl tops/bottoms, bars) carries the weight. One rule gives the
character: wherever strokes meet or bottom out, a horizontal band sits there
(bars overhang the letter, v/w bottom out on a flat band, x and k carry a
band through their junction). On a weight axis only the horizontals swell,
so the type "builds" like stacked scanlines.

Masters share point structure (fixed point counts per arc) so they
interpolate: P = {'V': vertical weight, 'Hh': horizontal weight}.
Units: UPM 1000, y-up.
"""
from math import cos, sin, asin, radians, degrees, hypot

UPM = 1000
XH, CAP, ASC, DESC, NUM = 560, 740, 800, -210, 740
OS = 14
NARC = 40
MASTERS = {'thin': {'V': 18, 'Hh': 22}, 'bold': {'V': 40, 'Hh': 132}}


# ------------------------------------------------------------------ kit
def ell(cx, cy, rx, ry):
    return (cx, cy, rx, ry)


def inset(e, TL, TR, TT, TB):
    cx, cy, rx, ry = e
    l, r, t, b = cx - rx + TL, cx + rx - TR, cy + ry - TT, cy - ry + TB
    return ((l + r) / 2, (t + b) / 2, (r - l) / 2, (t - b) / 2)


def pt(e, a):
    cx, cy, rx, ry = e
    return (cx + rx * cos(radians(a)), cy + ry * sin(radians(a)))


def ycut(e, y, side, near):
    cx, cy, rx, ry = e
    s = max(-1.0, min(1.0, (y - cy) / ry))
    a = degrees(asin(s))
    if side < 0:
        a = 180 - a
    while a - near > 180:
        a -= 360
    while near - a > 180:
        a += 360
    return a


def arc(e, a0, a1, n=NARC):
    return [pt(e, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def band(eo, ei, a0, a1, cut0=None, cut1=None):
    ao0, ao1, ai0, ai1 = a0, a1, a0, a1
    if cut0:
        ao0, ai0 = ycut(eo, cut0[0], cut0[1], a0), ycut(ei, cut0[0], cut0[1], a0)
    if cut1:
        ao1, ai1 = ycut(eo, cut1[0], cut1[1], a1), ycut(ei, cut1[0], cut1[1], a1)
    return arc(eo, ao0, ao1) + arc(ei, ai0, ai1)[::-1]


def ring(eo, ei):
    return [arc(eo, 0, 360)[:-1], ('hole', arc(ei, 0, 360)[:-1])]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]


def hband(xc, y, w, h):
    """Horizontal band centred at xc, bottom at y (the face's signature)."""
    return rect(xc - w / 2, y, xc + w / 2, y + h)


def diag(b, t, th):
    dx, dy = t[0] - b[0], t[1] - b[1]
    w = th * hypot(dx, dy) / abs(dy) / 2
    return [(b[0] - w, b[1]), (t[0] - w, t[1]), (t[0] + w, t[1]), (b[0] + w, b[1])]


def flip_y(cs, h):
    out = []
    for c in cs:
        if isinstance(c, tuple):
            out.append(('hole', [(x, h - y) for x, y in c[1]][::-1]))
        else:
            out.append([(x, h - y) for x, y in c][::-1])
    return out


def mirror(cs, axis):
    out = []
    for c in cs:
        if isinstance(c, tuple):
            out.append(('hole', [(2 * axis - x, y) for x, y in c[1]][::-1]))
        else:
            out.append([(2 * axis - x, y) for x, y in c][::-1])
    return out


def shift(cs, dx, dy=0):
    out = []
    for c in cs:
        if isinstance(c, tuple):
            out.append(('hole', [(x + dx, y + dy) for x, y in c[1]]))
        else:
            out.append([(x + dx, y + dy) for x, y in c])
    return out


# ------------------------------------------------------------------ registry
G, SB, CHAR = {}, {}, {}


def glyph(name, char, sb=(44, 44)):
    def deco(f):
        G[name], SB[name], CHAR[name] = f, sb, char
        return f
    return deco


OV = 34   # bar overhang past the letter: the "drifting band"


def arch(P, x0, x1, top=XH + OS, cy=290):
    """Reverse-contrast arch between stems at x0 (left edge) and x1 (right edge)."""
    V, Hh = P['V'], P['Hh']
    rx = (x1 - x0) / 2
    eo = ell(x0 + rx, cy, rx, top - cy)
    return band(eo, inset(eo, V, V, Hh, 0), 0, 180)


# ------------------------------------------------------------------ lowercase
@glyph('n', 'n')
def _n(P):
    V = P['V']
    return [rect(40, 0, 40 + V, XH), rect(460 - V, 0, 460, 290), arch(P, 40, 460)]


@glyph('m', 'm')
def _m(P):
    V = P['V']
    return [rect(40, 0, 40 + V, XH), rect(330 - V / 2, 0, 330 + V / 2, 290), rect(620 - V, 0, 620, 290),
            arch(P, 40, 330 + V / 2), arch(P, 330 - V / 2, 620)]


@glyph('h', 'h')
def _h(P):
    V = P['V']
    return [rect(40, 0, 40 + V, ASC), rect(460 - V, 0, 460, 290), arch(P, 40, 460)]


@glyph('u', 'u')
def _u(P):
    V = P['V']
    return [rect(460 - V, 0, 460, XH), rect(40, 270, 40 + V, XH)] + flip_y([arch(P, 40, 460)], XH)


@glyph('r', 'r', (44, 20))
def _r(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(220, 290, 180, XH + OS - 290)
    return [rect(40, 0, 40 + V, XH), band(eo, inset(eo, V, V, Hh, 0), 180, 62)]


@glyph('o', 'o', (36, 36))
def _o(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, XH / 2, 230, XH / 2 + OS)
    return ring(eo, inset(eo, V, V, Hh, Hh))


@glyph('c', 'c', (36, 30))
def _c(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, XH / 2, 230, XH / 2 + OS)
    return [band(eo, inset(eo, V, V, Hh, Hh), 38, 322)]


@glyph('e', 'e', (36, 10))
def _e(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, XH / 2, 230, XH / 2 + OS)
    ei = inset(eo, V, V, Hh, Hh)
    bar_h = Hh * 0.8 + 6
    y0 = XH / 2 - bar_h / 2 + 10
    return [band(eo, ei, 0, 326), rect(eo[0] - eo[2] + V / 2, y0, eo[0] + eo[2] + OV, y0 + bar_h)]


def _bowl_stem(P, stem_top, stem_bot, right=True):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, XH / 2, 230, XH / 2 + OS)
    x = 480 if right else 20
    st = rect(x - V, stem_bot, x, stem_top) if right else rect(x, stem_bot, x + V, stem_top)
    return ring(eo, inset(eo, V, V, Hh, Hh)) + [st]


@glyph('a', 'a', (36, 44))
def _a(P):
    return _bowl_stem(P, XH, 0)


@glyph('d', 'd', (36, 44))
def _d(P):
    return _bowl_stem(P, ASC, 0)


@glyph('b', 'b', (44, 36))
def _b(P):
    return _bowl_stem(P, ASC, 0, right=False)


@glyph('p', 'p', (44, 36))
def _p(P):
    return _bowl_stem(P, XH, DESC, right=False)


@glyph('q', 'q', (36, 44))
def _q(P):
    return _bowl_stem(P, XH, DESC)


@glyph('g', 'g', (36, 44))
def _g(P):
    V, Hh = P['V'], P['Hh']
    tail = ell(250, -30, 230, 180)
    return _bowl_stem(P, XH, -30) + [band(tail, inset(tail, V, V, 0, Hh), 0, -150)]


@glyph('l', 'l', (44, 20))
def _l(P):
    V, Hh = P['V'], P['Hh']
    # dir2: a square right foot made l read as capital L; now a curved tail
    # (thick bottom, hairline side), the same reverse-contrast logic as bowls
    return [rect(40, 150, 40 + V, ASC)] + [_tail(P, 40, 190)]


def _tail(P, x0, w):
    """Curved tail at a stem foot: quarter ellipse, thick bottom, hairline side."""
    V, Hh = P['V'], P['Hh']
    eo = ell(x0 + w / 2, 150, w / 2, 150 + OS)
    return band(eo, inset(eo, V, V, 0, Hh * 0.9 + 4), 180, 330)


@glyph('i', 'i', (44, 44))
def _i(P):
    V, Hh = P['V'], P['Hh']
    return [rect(80, 0, 80 + V, XH), hband(80 + V / 2, 650, 96, Hh * 0.8 + 10)]


@glyph('j', 'j', (20, 44))
def _j(P):
    V, Hh = P['V'], P['Hh']
    return [rect(150, DESC + Hh * 0.9, 150 + V, XH), rect(30, DESC, 150 + V, DESC + Hh * 0.9 + 4),
            hband(150 + V / 2, 650, 96, Hh * 0.8 + 10)]


@glyph('t', 't', (20, 20))
def _t(P):
    V, Hh = P['V'], P['Hh']
    return [rect(110, 150, 110 + V, 700), rect(110 - 80 - OV / 2, XH - Hh, 110 + V + 110 + OV / 2, XH),
            _tail(P, 110, 190)]


@glyph('f', 'f', (20, -10))
def _f(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(240, ASC - 150, 130, 150 + OS)
    return [rect(110, 0, 110 + V, ASC - 150), band(eo, inset(eo, V, V, Hh, 0), 180, 40),
            rect(110 - 80 - OV / 2, XH - Hh, 110 + V + 100 + OV / 2, XH)]


@glyph('s', 's', (36, 36))
def _s(P):
    V, Hh = P['V'], P['Hh']
    eu = ell(230, 420, 190, XH + OS - 420)
    el = ell(230, 140, 200, 140 + OS)
    # dir3: ONE spine. dir2 drew it twice (upper bowl's bottom + lower bowl's
    # top), leaving a bulge at the left middle. Bowls now stop short and a
    # single diagonal band joins them.
    eui, eli = inset(eu, V, V, Hh, Hh * 0.6), inset(el, V, V, Hh * 0.6, Hh)
    up = band(eu, eui, 20, 236)
    lo = band(el, eli, 64, -160)
    sp = [pt(eu, 236), pt(eli, 64), pt(el, 64), pt(eui, 236)]
    return [up, lo, sp]


@glyph('v', 'v', (16, 16))
def _v(P):
    V, Hh = P['V'], P['Hh']
    return [diag((240, Hh * 0.9), (40, XH), V * 1.2), diag((260, Hh * 0.9), (460, XH), V * 1.2),
            hband(250, 0, 120, Hh * 0.9 + 4)]


@glyph('w', 'w', (16, 16))
def _w(P):
    V, Hh = P['V'], P['Hh']
    out = []
    for dx in (0, 300):
        out += [diag((dx + 180, Hh * 0.9), (dx + 30, XH), V * 1.2),
                diag((dx + 200, Hh * 0.9), (dx + 350, XH), V * 1.2),
                hband(dx + 190, 0, 110, Hh * 0.9 + 4)]
    return out


@glyph('x', 'x', (20, 20))
def _x(P):
    V, Hh = P['V'], P['Hh']
    return [diag((40, 0), (440, XH), V * 1.2), diag((440, 0), (40, XH), V * 1.2),
            hband(240, XH / 2 - (Hh * 0.8 + 6) / 2, 260 + OV, Hh * 0.8 + 6)]


@glyph('y', 'y', (16, 16))
def _y(P):
    V, Hh = P['V'], P['Hh']
    return [diag((240, Hh * 0.9), (40, XH), V * 1.2), diag((110, DESC + Hh * 0.9), (460, XH), V * 1.2),
            hband(250, 0, 120, Hh * 0.9 + 4), rect(20, DESC, 150, DESC + Hh * 0.9 + 4)]


@glyph('k', 'k', (44, 16))
def _k(P):
    V, Hh = P['V'], P['Hh']
    jy = 200
    return [rect(40, 0, 40 + V, ASC), diag((40 + V, jy), (420, XH), V * 1.2),
            diag((440, 0), (200, jy + (Hh * 0.8 + 6) / 2), V * 1.2),
            rect(40, jy - (Hh * 0.8 + 6) / 2 + 40, 300 + OV, jy + (Hh * 0.8 + 6) / 2 + 40)]


@glyph('z', 'z', (30, 30))
def _z(P):
    V, Hh = P['V'], P['Hh']
    return [rect(30, XH - Hh, 420, XH), rect(30, 0, 440 + OV, Hh), diag((50, Hh), (410, XH - Hh), V * 1.3)]


# ------------------------------------------------------------------ capitals
@glyph('H', 'H', (50, 50))
def _H(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), rect(560 - V, 0, 560, CAP),
            rect(40 - OV, CAP / 2 - Hh / 2, 560 + OV, CAP / 2 + Hh / 2)]


@glyph('I', 'I', (40, 40))
def _I(P):
    V, Hh = P['V'], P['Hh']
    return [rect(120 - V / 2, 0, 120 + V / 2, CAP), rect(20, 0, 220, Hh), rect(20, CAP - Hh, 220, CAP)]


@glyph('O', 'O', (36, 36))
def _O(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(330, CAP / 2, 310, CAP / 2 + OS)
    return ring(eo, inset(eo, V, V, Hh, Hh))


@glyph('A', 'A', (16, 16))
def _A(P):
    V, Hh = P['V'], P['Hh']
    return [diag((40, 0), (290, CAP - Hh), V * 1.2), diag((560, 0), (310, CAP - Hh), V * 1.2),
            hband(300, CAP - Hh, 130, Hh), rect(120 - OV, 210, 480 + OV, 210 + Hh * 0.9)]



# ------------------------------------------------------------------ more capitals
def _cap_bowl(P, x0, y0, y1, w):
    """Right-facing reverse-contrast bowl from a stem at x0, spanning y0..y1."""
    V, Hh = P['V'], P['Hh']
    ry = (y1 - y0) / 2
    eo = ell(x0, y0 + ry, w, ry)
    ei = inset(eo, 0, V, Hh, Hh)
    return band(eo, ei, 90, -90)


@glyph('B', 'B', (50, 40))
def _B(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), _cap_bowl(P, 40 + 160, CAP / 2 - Hh / 2, CAP, 250),
            _cap_bowl(P, 40 + 180, 0, CAP / 2 + Hh / 2, 290),
            rect(40, CAP - Hh, 200, CAP), rect(40, 0, 220, Hh), rect(40, CAP / 2 - Hh / 2, 220, CAP / 2 + Hh / 2)]


@glyph('D', 'D', (50, 40))
def _D(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), _cap_bowl(P, 200, 0, CAP, 360),
            rect(40, CAP - Hh, 200, CAP), rect(40, 0, 200, Hh)]


@glyph('P', 'P', (50, 30))
def _P(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), _cap_bowl(P, 200, 300, CAP, 280),
            rect(40, CAP - Hh, 200, CAP), rect(40, 300, 200, 300 + Hh)]


@glyph('R', 'R', (50, 16))
def _R(P):
    V, Hh = P['V'], P['Hh']
    return _P(P) + [diag((500, Hh * 0.9), (300, 300), V * 1.2), hband(500, 0, 120, Hh * 0.9 + 4)]


@glyph('C', 'C', (36, 30))
def _C(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(330, CAP / 2, 310, CAP / 2 + OS)
    return [band(eo, inset(eo, V, V, Hh, Hh), 40, 320)]


@glyph('G', 'G', (36, 36))
def _G(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(330, CAP / 2, 310, CAP / 2 + OS)
    return [band(eo, inset(eo, V, V, Hh, Hh), 40, 345), rect(330, 300, 640 + OV, 300 + Hh),
            rect(640 - V, 60, 640, 300 + Hh)]


@glyph('E', 'E', (50, 20))
def _E(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), rect(40, CAP - Hh, 470, CAP),
            rect(40 - OV, CAP / 2 - Hh / 2, 420, CAP / 2 + Hh / 2), rect(40, 0, 490, Hh)]


@glyph('F', 'F', (50, 10))
def _F(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), rect(40, CAP - Hh, 470, CAP),
            rect(40 - OV, CAP / 2 - Hh / 2, 420, CAP / 2 + Hh / 2)]


@glyph('L', 'L', (50, 20))
def _L(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), rect(40, 0, 470, Hh)]


@glyph('T', 'T', (20, 20))
def _T(P):
    V, Hh = P['V'], P['Hh']
    return [rect(20, CAP - Hh, 560, CAP), rect(290 - V / 2, 0, 290 + V / 2, CAP)]


@glyph('J', 'J', (20, 50))
def _J(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, 200, 210, 200 + OS)
    return [rect(460 - V, 200, 460, CAP), band(eo, inset(eo, V, V, 0, Hh), 0, -170)]


@glyph('U', 'U', (50, 50))
def _U(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(300, 300, 260, 300 + OS)
    return [rect(40, 300, 40 + V, CAP), rect(560 - V, 300, 560, CAP),
            band(eo, inset(eo, V, V, 0, Hh), 180, 360)]


@glyph('K', 'K', (50, 16))
def _K(P):
    V, Hh = P['V'], P['Hh']
    jy = 290
    bh = Hh * 0.9 + 6
    return [rect(40, 0, 40 + V, CAP), diag((40 + V, jy), (520, CAP), V * 1.2),
            diag((540, 0), (240, jy + bh / 2), V * 1.2), rect(40, jy, 330 + OV, jy + bh)]


@glyph('M', 'M', (50, 50))
def _M(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), rect(700 - V, 0, 700, CAP),
            diag((360, Hh), (50, CAP), V * 1.2), diag((380, Hh), (690, CAP), V * 1.2),
            hband(370, 0, 140, Hh)]


@glyph('N', 'N', (50, 50))
def _N(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, 0, 40 + V, CAP), rect(560 - V, 0, 560, CAP),
            diag((540, Hh), (60, CAP - Hh), V * 1.2), rect(40, CAP - Hh, 160, CAP), rect(440, 0, 560, Hh)]


@glyph('Q', 'Q', (36, 20))
def _Q(P):
    V, Hh = P['V'], P['Hh']
    return _O(P) + [rect(420, -10, 660, -10 + Hh * 0.9 + 8)]  # crosses the bowl


@glyph('S', 'S', (36, 36))
def _S(P):
    V, Hh = P['V'], P['Hh']
    eu = ell(290, 545, 240, CAP + OS - 545)
    el = ell(290, 180, 260, 180 + OS)
    eui, eli = inset(eu, V, V, Hh, Hh * 0.6), inset(el, V, V, Hh * 0.6, Hh)
    return [band(eu, eui, 20, 236), band(el, eli, 64, -160),
            [pt(eu, 236), pt(eli, 64), pt(el, 64), pt(eui, 236)]]


@glyph('V', 'V', (16, 16))
def _V(P):
    V, Hh = P['V'], P['Hh']
    return [diag((290, Hh), (30, CAP), V * 1.2), diag((310, Hh), (570, CAP), V * 1.2), hband(300, 0, 140, Hh)]


@glyph('W', 'W', (16, 16))
def _W(P):
    V, Hh = P['V'], P['Hh']
    out = []
    for dx in (0, 380):
        out += [diag((dx + 220, Hh), (dx + 30, CAP), V * 1.2), diag((dx + 240, Hh), (dx + 430, CAP), V * 1.2),
                hband(dx + 230, 0, 120, Hh)]
    return out


@glyph('X', 'X', (20, 20))
def _X(P):
    V, Hh = P['V'], P['Hh']
    return [diag((40, 0), (560, CAP), V * 1.2), diag((560, 0), (40, CAP), V * 1.2),
            hband(300, CAP / 2 - Hh / 2, 320 + OV, Hh)]


@glyph('Y', 'Y', (16, 16))
def _Y(P):
    V, Hh = P['V'], P['Hh']
    jy = 300
    return [diag((290, jy + Hh), (30, CAP), V * 1.2), diag((310, jy + Hh), (570, CAP), V * 1.2),
            rect(300 - V / 2, 0, 300 + V / 2, jy), hband(300, jy, 200 + OV, Hh)]


@glyph('Z', 'Z', (30, 30))
def _Z(P):
    V, Hh = P['V'], P['Hh']
    return [rect(40, CAP - Hh, 540, CAP), rect(40, 0, 560 + OV, Hh), diag((70, Hh), (520, CAP - Hh), V * 1.3)]


# ------------------------------------------------------------------ figures
@glyph('zero', '0', (40, 40))
def _zero(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, NUM / 2, 230, NUM / 2 + OS)
    return ring(eo, inset(eo, V, V, Hh, Hh))


@glyph('one', '1', (40, 40))
def _one(P):
    V, Hh = P['V'], P['Hh']
    return [rect(220 - V / 2, 0, 220 + V / 2, NUM), rect(60, NUM - Hh, 220 + V / 2, NUM),
            rect(60, 0, 380, Hh)]


@glyph('two', '2', (40, 40))
def _two(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(250, 520, 220, NUM + OS - 520)
    ei = inset(eo, V, V, Hh, 0)
    top = pt(inset(eo, V / 2, V / 2, 0, 0), -20)
    return [band(eo, ei, 170, -20), diag((60 + V, Hh), top, V * 1.3), rect(40, 0, 480 + OV, Hh)]


@glyph('three', '3', (40, 40))
def _three(P):
    V, Hh = P['V'], P['Hh']
    eu = ell(240, 545, 210, NUM + OS - 545)
    el = ell(240, 190, 230, 190 + OS)
    return [band(eu, inset(eu, V, V, Hh, Hh * 0.6), 160, -90), band(el, inset(el, V, V, Hh * 0.6, Hh), 90, -160)]


@glyph('four', '4', (30, 30))
def _four(P):
    V, Hh = P['V'], P['Hh']
    return [rect(360 - V, 0, 360, NUM), diag((50, 230 + Hh), (360 - V, NUM), V * 1.2),
            rect(30 - OV / 2, 230, 480 + OV / 2, 230 + Hh)]


@glyph('five', '5', (40, 40))
def _five(P):
    V, Hh = P['V'], P['Hh']
    el = ell(250, 230, 230, 230 + OS)
    return [rect(60, NUM - Hh, 460, NUM), rect(60, 380, 60 + V, NUM),
            band(el, inset(el, V, V, Hh, Hh), 140, -160)]


@glyph('six', '6', (40, 40))
def _six(P):
    V, Hh = P['V'], P['Hh']
    lo = ell(250, 230, 230, 230 + OS)
    up = ell(330, 300, 310, NUM + OS - 300)
    return ring(lo, inset(lo, V, V, Hh, Hh)) + [band(up, inset(up, V, V, Hh, 0), 180, 70)]


@glyph('nine', '9', (40, 40))
def _nine(P):
    return [[(500 - x, NUM - y) for x, y in c] if not isinstance(c, tuple)
            else ('hole', [(500 - x, NUM - y) for x, y in c[1]]) for c in _six(P)]


@glyph('seven', '7', (30, 30))
def _seven(P):
    V, Hh = P['V'], P['Hh']
    return [rect(30, NUM - Hh, 470, NUM), diag((160, 0), (460, NUM - Hh), V * 1.4)]


@glyph('eight', '8', (40, 40))
def _eight(P):
    V, Hh = P['V'], P['Hh']
    up = ell(250, 545, 190, NUM + OS - 545)
    lo = ell(250, 190, 230, 190 + OS)
    return ring(up, inset(up, V, V, Hh, Hh * 0.6)) + ring(lo, inset(lo, V, V, Hh * 0.6, Hh))


# ------------------------------------------------------------------ punctuation
@glyph('colon', ':', (50, 50))
def _colon(P):
    Hh = P['Hh']
    return [_dot(P, 0, 0), _dot(P, 0, XH - (50 + Hh * 0.6))]


@glyph('semicolon', ';', (50, 50))
def _semicolon(P):
    Hh = P['Hh']
    return _comma(P) + [_dot(P, 0, XH - (50 + Hh * 0.6))]


@glyph('exclam', '!', (60, 60))
def _exclam(P):
    V, Hh = P['V'], P['Hh']
    return [rect(45 - V / 2, 240, 45 + V / 2, CAP), _dot(P, 0, 0)]


@glyph('question', '?', (40, 40))
def _question(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(220, 520, 200, CAP + OS - 520)
    ei = inset(eo, V, V, Hh, Hh * 0.6)
    return [band(eo, ei, 160, -90), rect(220 - V / 2, 240, 220 + V / 2, 330), _dot(P, 175, 0)]


@glyph('quotesingle', "'", (50, 50))
def _quotesingle(P):
    V = P['V']
    return [rect(0, 520, V * 1.6 + 6, ASC)]


@glyph('quotedbl', '"', (50, 50))
def _quotedbl(P):
    V = P['V']
    return [rect(0, 520, V * 1.6 + 6, ASC), rect(110, 520, 110 + V * 1.6 + 6, ASC)]


@glyph('hyphen', '-', (40, 40))
def _hyphen(P):
    Hh = P['Hh']
    return [rect(0, 260 - Hh / 2, 240, 260 + Hh / 2)]


@glyph('endash', '–', (20, 20))
def _endash(P):
    Hh = P['Hh']
    return [rect(0, 260 - Hh / 2, 500, 260 + Hh / 2)]


@glyph('parenleft', '(', (40, 10))
def _parenleft(P):
    V, Hh = P['V'], P['Hh']
    eo = ell(300, 280, 260, 520)
    return [band(eo, inset(eo, V, 0, Hh, Hh), 100, 260)]


@glyph('parenright', ')', (10, 40))
def _parenright(P):
    return mirror(_parenleft(P), 160)


@glyph('slash', '/', (10, 10))
def _slash(P):
    V = P['V']
    return [diag((0, -120), (340, ASC), V * 1.3)]


@glyph('ampersand', '&', (36, 20))
def _ampersand(P):
    # D1b: closed upper loop, lower bowl open toward the arm, thin diagonal leg,
    # thick arm band overhanging right (D1a read as "8-")
    V, Hh = P['V'], P['Hh']
    up = ell(230, 560, 130, CAP + OS - 560)
    lo = ell(250, 200, 220, 200 + OS)
    return ring(up, inset(up, V, V, Hh * 0.8, Hh * 0.6)) + \
        [band(lo, inset(lo, V, V, Hh * 0.6, Hh), 125, 380),
         diag((520, 0), (150, 450), V * 1.3), rect(360, 300, 540 + OV, 300 + Hh * 0.9)]


@glyph('space', ' ', (0, 0))
def _space(P):
    return []


def _dot(P, x, y):
    """Dot: near-square at every weight (thin-master dots read as dashes)."""
    d = 50 + P['Hh'] * 0.6
    return rect(x, y, x + d, y + d)


@glyph('period', '.', (50, 50))
def _period(P):
    V, Hh = P['V'], P['Hh']
    return [_dot(P, 0, 0)]


@glyph('comma', ',', (50, 50))
def _comma(P):
    V, Hh = P['V'], P['Hh']
    return [_dot(P, 0, 0), diag((10, -130), (60, 6), V * 1.6)]


@glyph('.notdef', None, (50, 50))
def _notdef(P):
    return [rect(0, 0, 400, 700), ('hole', rect(40, 40, 360, 660))]


ADV_FIXED = {'space': 260}
ORDER = ['.notdef', 'space'] + [n for n in G if n not in ('.notdef', 'space')]
