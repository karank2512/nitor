"""Crop the text-size bands out of a proof PNG and diff them pairwise.

Usage: python3.11 bands.py <proof.png> <outdir> <tag>
Bands are found by scanning rows for ink: groups taller than 40px are text
blocks (labels are ~10px). Crops are saved 1:1 and 4x (nearest), plus
amplified diff images vs band 0.
"""
import os
import sys
from PIL import Image, ImageChops, ImageOps

src, outdir, tag = sys.argv[1:4]
os.makedirs(outdir, exist_ok=True)
im = Image.open(src).convert('RGB')
W, H = im.size
bg = im.getpixel((5, 5))


def row_has_ink(y):
    for x in range(0, W):
        p = im.getpixel((x, y))
        if max(abs(p[i] - bg[i]) for i in range(3)) > 24:
            return True
    return False


rows = [row_has_ink(y) for y in range(H)]
groups, start, gap = [], None, 0
for y, ink in enumerate(rows + [False] * 9):
    if ink:
        if start is None:
            start = y
        gap = 0
        last = y
    elif start is not None:
        gap += 1
        if gap > 8:
            groups.append((start, last + 1))
            start = None
bands = [g for g in groups if g[1] - g[0] > 40]
print(f'{tag}: bands (y0, y1) = {bands}')
h = max(b[1] - b[0] for b in bands)
# align every band to band 0 by searching the vertical offset with the
# smallest mean difference (the ink-row detector shifts with top-edge ink)
ref = im.crop((0, bands[0][0] - 2, W, bands[0][0] - 2 + h + 4)).convert('L')
tops = [bands[0][0] - 2]
for (y0, _) in bands[1:]:
    best = None
    for dy in range(-24, 25):
        c = im.crop((0, y0 - 2 + dy, W, y0 - 2 + dy + h + 4)).convert('L')
        s = sum(i * n for i, n in enumerate(ImageChops.difference(ref, c).histogram()))
        if best is None or s < best[0]:
            best = (s, y0 - 2 + dy)
    tops.append(best[1])
print(f'{tag}: aligned crop tops = {tops}')
crops = []
for i, y0 in enumerate(tops):
    c = im.crop((0, y0, W, y0 + h + 4))
    crops.append(c)
    c.save(os.path.join(outdir, f'{tag}-band{i}.png'))
    c.resize((c.width * 4, c.height * 4), Image.NEAREST).save(
        os.path.join(outdir, f'{tag}-band{i}-x4.png'))
for i in range(len(crops)):
    for j in range(i + 1, len(crops)):
        d = ImageChops.difference(crops[i].convert('L'), crops[j].convert('L'))
        hist = d.histogram()
        print(f'{tag}: band{i} vs band{j}: max {d.getextrema()[1]:3d}/255, '
              f'changed px {sum(hist[1:]):5d}, >15 levels {sum(hist[16:]):5d}')
        if j == i + 1 or i == 0:
            amp = ImageOps.invert(ImageOps.autocontrast(d)) if d.getbbox() else ImageOps.invert(d)
            amp.save(os.path.join(outdir, f'{tag}-diff-band{i}-band{j}.png'))
