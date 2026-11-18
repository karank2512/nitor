"""Nitor specimen video frames (specimen media; not licensed). 1080 x 1350, 30 fps, 24.5 s, silent.

This file is complete on its own (standard library and Pillow only) and is the source
of video/Nitor-specimen.mp4. It was derived from an earlier specimen script that is not
part of this repository, with text-only changes: the weight-build word is "Nitor", a
cascade word is "glide", and the end card reads "Nitor". Only the virtual camera and
the real wght axis move.
Usage: python3.11 nitor/video/make_frames_nitor.py <Nitor-VF.ttf> <frames_dir> <qa.json>
"""
import json
import math
import os
import random
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

VF, OUTDIR, QA = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1350, 30
os.makedirs(OUTDIR, exist_ok=True)
random.seed(7)
_cache = {}


def font(px, wght):
    key = (int(px), int(round(wght)))
    if key not in _cache:
        f = ImageFont.truetype(VF, key[0])
        f.set_variation_by_axes([key[1]])
        _cache[key] = f
    return _cache[key]


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def text_layer(items):
    """items: [(text, px, wght, cx, cy, alpha, blur)] -> L image (white on black)."""
    out = Image.new('L', (W, H), 0)
    for text, px, wght, cx, cy, alpha, blur in items:
        f = font(px, wght)
        x0, y0, x1, y1 = f.getbbox(text)
        lay = Image.new('L', (W, H), 0)
        ImageDraw.Draw(lay).text((cx - (x0 + x1) / 2, cy - (y0 + y1) / 2), text, font=f,
                                 fill=int(255 * max(0.0, min(1.0, alpha))))
        if blur > 0.3:
            lay = lay.filter(ImageFilter.GaussianBlur(blur))
        out = ImageChops.lighter(out, lay)
    return out


# ---------------------------------------------------------------- CRT finish
SCAN = Image.new('L', (W, H), 255)
_d = ImageDraw.Draw(SCAN)
for y in range(0, H, 3):
    _d.line((0, y, W, y), fill=178)
GRAIN = [Image.effect_noise((W, H), 34) for _ in range(8)]
VIG = Image.radial_gradient('L').resize((int(W * 1.45), int(H * 1.45))).crop(
    (int(W * 0.225), int(H * 0.225), int(W * 0.225) + W, int(H * 0.225) + H)).point(
    lambda v: int(255 * max(0.0, 1 - (v / 255) ** 2 * 0.95)))
MASK = Image.new('L', (W, H), 0)
ImageDraw.Draw(MASK).rounded_rectangle((34, 34, W - 35, H - 35), radius=70, fill=255)
MASK = MASK.filter(ImageFilter.GaussianBlur(3))


def barrel_mesh(k=0.055, nx=18, ny=22):
    mesh = []
    for j in range(ny):
        for i in range(nx):
            x0, y0 = W * i / nx, H * j / ny
            x1, y1 = W * (i + 1) / nx, H * (j + 1) / ny

            def src(x, y):
                u, v = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)
                r2 = u * u + v * v
                s = 1 + k * r2
                return W / 2 + u * s * W / 2 * 0.965, H / 2 + v * s * H / 2 * 0.965
            q = src(x0, y0) + src(x0, y1) + src(x1, y1) + src(x1, y0)
            mesh.append(((int(x0), int(y0), int(x1), int(y1)), q))
    return mesh


MESH = barrel_mesh()


def crt(content, n):
    bloom = content.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.65))
    base = ImageChops.add(content, bloom)
    base = ImageChops.multiply(base, SCAN)
    g = GRAIN[n % len(GRAIN)].point(lambda v: int((v - 128) * 0.16 + 128))
    base = ImageChops.add(base, g, offset=-128)
    base = ImageChops.add(base, Image.new('L', (W, H), 7))          # black lift (phosphor)
    base = base.transform((W, H), Image.MESH, MESH, Image.BICUBIC)   # curved glass
    base = ImageChops.multiply(base, VIG)
    base = ImageChops.multiply(base, MASK)
    return base



# ---------------------------------------------------------------- scenes (v5)
def dip(i, n, k=8):
    return min(1.0, (i + 1) / k, (n - i) / k)


def feather_x(img, edge=110, ramp=170):
    """Fade content to nothing before the CRT side edges (no hard fragments)."""
    m = Image.new('L', (W, 1), 0)
    for x in range(W):
        d = min(x, W - 1 - x) - edge
        m.putpixel((x, 0), int(255 * ease(d / ramp)))
    return ImageChops.multiply(img, m.resize((W, H)))


def s_raster(i, n):
    """A beam sweeps down; everything above it is 'painted'."""
    a = dip(i, n, 6)
    t = i / n
    beam_y = 140 + (H - 280) * ease(t / 0.36)   # v6: paints the phrase sooner
    items = [('slow light', 168, 100 + 120 * ease((t - 0.55) / 0.45), W / 2, H / 2, a, 0)]
    for k, off in ((1, -215), (2, 215), (3, -410), (4, 410)):
        items.append(('slow light', 168 * (1 - 0.05 * k), 100 + 40 * k, W / 2, H / 2 + off,
                      a * (0.30 / (1 + (k > 2))), 2.5 * k))
    return items, beam_y


WALL = 'the horizontals carry the light'


def s_wall(i, n):
    a = dip(i, n, 8)
    t = i / n
    rows = []
    pitch, px = 104, 60
    for r in range(-5, 6):
        y = H / 2 + r * pitch
        if r == 0:
            continue
        w = 100 + 800 * ((0.37 * (r + 5) + 0.9 * t) % 1.0)
        speed = (60 + 22 * abs(r)) * (1 if r % 2 else -1)
        line = (WALL + '   ') * 3
        f = font(px, w)
        lw = f.getlength(WALL + '   ')
        x = W / 2 + ((speed * t * 6) % lw) - lw / 2
        d = abs(r)
        rows.append((line, px, w, x, y, a * (0.85 / (1 + 0.18 * d)), 1.2 * d))   # v6: brighter rows
    focus_w = 100 + 800 * ease((t - 0.15) / 0.6)
    rows.append(('the horizontals', 96, focus_w, W / 2, H / 2 - 6, a, 0))
    return rows


CASCADE = ['after', 'hours', 'the', 'room', 'is', 'quiet', 'half', 'kept', 'thoughts', 'glide',
           'by', 'the', 'window', 'past', 'two', 'slow']


def s_cascade(i, n):
    a = dip(i, n, 8)
    step = 176
    scroll = (i / n) * step * 6.0
    items = []
    for k, word in enumerate(CASCADE):
        y = H / 2 + (k - 3) * step - scroll
        d = abs(y - H / 2) / step
        if -step < y < H + step:
            focus = max(0.0, 1 - d)
            edge = ease((min(y, H - y) - 150) / 220)
            if edge > 0:
                items.append((word, 128 + 30 * focus, 200 + 700 * focus, W / 2, y,
                              a * edge * (0.28 + 0.72 * focus), 7 * min(1.0, d)))
    return items


def s_build(i, n):
    a = dip(i, n, 8)
    t = i / n
    w = 100 + 800 * ease((t - 0.08) / 0.62)
    px = 290 * (1.0 + 0.10 * ease((t - 0.7) / 0.3))
    items = [('Nitor', px, w, W / 2, H / 2 - 30, a, 0)]
    for k, off in ((1, -270), (2, 270), (3, -430), (4, 430)):
        lag = ease((t - 0.08 - 0.06 * k) / 0.62)
        items.append(('Nitor', px, 100 + 800 * lag, W / 2, H / 2 - 30 + off, a * 0.24 / (1 + (k > 2)), 2 + 2 * k))
    return items, w


CHARSET = ['abcdefghijklm', 'nopqrstuvwxyz', 'ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789 .,:;!?&']


def s_charset(i, n):
    a = dip(i, n, 8)
    items = []
    for k, line in enumerate(CHARSET):
        la = a * ease((i - 4 - 8 * k) / 10)
        items.append((line, 70, 640, W / 2, H / 2 + (k - 2) * 108, la, 4 * (1 - la) if la < 1 else 0))
    return items


def s_end(i, n):
    f = min(1.0, (i + 1) / 10)
    return [('Nitor', 82, 100 + 400 * ease(i / (n * 0.6)), W / 2, H / 2 - 64, f, 0),
            ('the horizontals carry the light', 44, 340, W / 2, H / 2 + 30, f * 0.9, 0),
            ('not a release', 38, 340, W / 2, H / 2 + 104, f * 0.7, 0)]   # v6: larger


def meter(img, w, alpha):
    """Small bottom weight meter: hairline track, thick fill band, readout."""
    d = ImageDraw.Draw(img)
    x0, x1, y = 220, W - 220, H - 230
    v = int(110 * alpha)
    d.rectangle((x0, y, x1, y + 2), fill=v)
    d.rectangle((x0, y - 8, x0 + (x1 - x0) * (w - 100) / 800, y + 10), fill=int(235 * alpha))
    f = font(42, 500)   # v6: larger readout
    s = f'wght {int(round(w))}'
    d.text((W / 2 - f.getlength(s) / 2, y + 30), s, font=f, fill=int(200 * alpha))
    return img


def beam(img, y, alpha):
    lay = Image.new('L', (W, H), 0)
    ImageDraw.Draw(lay).rectangle((90, y - 3, W - 90, y + 3), fill=int(255 * alpha))
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).rectangle((90, y - 26, W - 90, y + 26), fill=int(60 * alpha))
    return ImageChops.lighter(img, ImageChops.lighter(lay, glow.filter(ImageFilter.GaussianBlur(18))))


SCENES = [('raster', 120), ('wall', 180), ('cascade', 135), ('build', 150), ('charset', 75), ('end', 75)]
qa, n_out = {'scenes': []}, 0
inner = Image.new('L', (W, H), 255)
ImageDraw.Draw(inner).rectangle((72, 72, W - 73, H - 73), fill=0)
for name, n in SCENES:
    worst = 0
    for i in range(n):
        if name == 'raster':
            items, by = s_raster(i, n)
            content = text_layer(items)
            mask = Image.new('L', (W, H), 0)
            ImageDraw.Draw(mask).rectangle((0, 0, W, int(by)), fill=255)
            content = ImageChops.multiply(content, mask.filter(ImageFilter.GaussianBlur(10)))
            if i / n < 0.39:
                content = beam(content, by, dip(i, n, 6))
        elif name == 'wall':
            content = feather_x(text_layer(s_wall(i, n)))
        elif name == 'build':
            items, w = s_build(i, n)
            content = meter(text_layer(items), w, dip(i, n, 8))
        else:
            content = text_layer({'cascade': s_cascade, 'charset': s_charset, 'end': s_end}[name](i, n))
        hard = content.point(lambda v: 255 if v > 60 else 0)
        worst = max(worst, ImageChops.multiply(hard, inner).histogram()[255])
        crt(content, n_out).convert('RGB').save(os.path.join(OUTDIR, f'f{n_out:04d}.png'))
        n_out += 1
    qa['scenes'].append({'scene': name, 'frames': n, 'max_content_px_outside_safe_72': worst})
qa['total_frames'], qa['seconds'] = n_out, n_out / FPS
json.dump(qa, open(QA, 'w'), indent=1)
print(json.dumps(qa))
