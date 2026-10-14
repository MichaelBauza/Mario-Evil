#!/usr/bin/env python3
"""Procedural 32x32 textures + item icons for Mario EVIL. Output: PNGs in levels/bbh (named *.rgba16.png)."""
import random, os, sys
from PIL import Image, ImageDraw
OUT = sys.argv[1]
def noise(img, amt, seed):
    r = random.Random(seed); px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            p = px[x, y]; d = r.randint(-amt, amt)
            px[x, y] = (max(0, min(255, p[0]+d)), max(0, min(255, p[1]+d)), max(0, min(255, p[2]+d)), p[3])
def save(img, name): img.save(os.path.join(OUT, name + '.rgba16.png'))
T = {}
def new(c): return Image.new('RGBA', (32, 32), c)
# --- tiling surfaces -------------------------------------------------------
im = new((58, 36, 24, 255)); d = ImageDraw.Draw(im)           # parquet
for i in range(0, 32, 8):
    for j in range(0, 32, 8):
        shade = 10 if ((i + j) // 8) % 2 else -8
        d.rectangle([i, j, i+7, j+7], fill=(58+shade, 36+shade, 24+shade, 255), outline=(30, 18, 12, 255))
noise(im, 5, 1); save(im, 'mans_floor')
im = new((96, 18, 22, 255)); d = ImageDraw.Draw(im)           # red carpet
for i in range(0, 32, 8): d.line([i, 0, i, 31], fill=(80, 12, 16, 255))
d.rectangle([0, 0, 31, 3], fill=(150, 120, 40, 255)); d.rectangle([0, 28, 31, 31], fill=(150, 120, 40, 255))
noise(im, 6, 2); save(im, 'mans_carpet')
im = new((46, 52, 40, 255)); d = ImageDraw.Draw(im)           # wallpaper (damask)
for x in range(0, 32, 16):
    for y in range(0, 32, 16):
        d.ellipse([x+4, y+4, x+11, y+11], outline=(70, 80, 56, 255)); d.point([x+8, y+8], fill=(90, 100, 70, 255))
noise(im, 4, 3); save(im, 'mans_wall')
im = new((70, 44, 28, 255)); d = ImageDraw.Draw(im)           # wood panelling
for i in range(0, 32, 16):
    d.rectangle([i+1, 2, i+14, 29], outline=(40, 24, 14, 255)); d.rectangle([i+3, 4, i+12, 27], outline=(88, 58, 36, 255))
noise(im, 5, 4); save(im, 'mans_panel')
im = new((28, 22, 20, 255)); d = ImageDraw.Draw(im)           # ceiling
d.line([0, 15, 31, 15], fill=(48, 34, 26, 255)); d.line([15, 0, 15, 31], fill=(48, 34, 26, 255))
noise(im, 3, 5); save(im, 'mans_ceil')
im = new((92, 90, 84, 255)); d = ImageDraw.Draw(im)           # stone tile
for i in range(0, 32, 16):
    for j in range(0, 32, 16): d.rectangle([i, j, i+15, j+15], outline=(48, 48, 44, 255))
noise(im, 7, 6); save(im, 'mans_stone')
im = new((84, 52, 30, 255)); d = ImageDraw.Draw(im)           # door
d.rectangle([0, 0, 31, 31], outline=(34, 20, 10, 255)); d.rectangle([4, 3, 27, 14], outline=(52, 30, 16, 255))
d.rectangle([4, 17, 27, 28], outline=(52, 30, 16, 255)); d.ellipse([24, 15, 27, 18], fill=(190, 160, 60, 255))
noise(im, 4, 7); save(im, 'mans_door')
im = new((110, 70, 40, 255)); d = ImageDraw.Draw(im)          # table / furniture wood
for y in range(0, 32, 4): d.line([0, y, 31, y], fill=(90, 56, 30, 255))
noise(im, 6, 8); save(im, 'mans_wood')
im = new((150, 150, 140, 255)); d = ImageDraw.Draw(im)        # marble
for k in range(5): d.line([random.Random(k).randint(0, 31), 0, random.Random(k+9).randint(0, 31), 31], fill=(110, 110, 104, 255))
noise(im, 8, 9); save(im, 'mans_marble')
# --- v17 look: textures matching the concept art ------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
def user_floor(src, name, periods=2, tone=None, keep=1.0):
    """Crop `periods` repeats of the user's seamless 1024px floor texture (6 repeats per side) down to 32x32.
    tone: optional RGB multiplier; keep: 1.0 = original colour, lower = pulled toward grey."""
    im = Image.open(os.path.join(HERE, src)).convert('RGBA')
    n = int(round(1024.0 / 6 * periods))
    out = im.crop((0, 0, n, n)).resize((32, 32), Image.LANCZOS)
    if tone:
        px = out.load()
        for y in range(32):
            for x in range(32):
                r, g, b, a = px[x, y]; l = 0.3 * r + 0.59 * g + 0.11 * b
                c = [l + (v - l) * keep for v in (r, g, b)]
                px[x, y] = tuple(max(0, min(255, int(c[i] * tone[i]))) for i in range(3)) + (a,)
    save(out, name)
# indoor marble: the user's marble pulled toward grey and warmed, so rooms read as the mansion, not a green hall
user_floor('tex_floor_marble.jpg', 'mans_floor', tone=(1.0, 0.94, 0.84), keep=0.35)
user_floor('tex_floor_carpet.jpg', 'mans_carpet')

def seamless(img):
    """Make a 32x32 texture tile without seams (offset cross-fade)."""
    a = img.copy(); b = Image.new('RGBA', (32, 32)); b.paste(img, (16, 16)); b.paste(img, (-16, 16)); b.paste(img, (16, -16)); b.paste(img, (-16, -16))
    pa, pb, po = a.load(), b.load(), Image.new('RGBA', (32, 32)); out = po.load()
    for y in range(32):
        for x in range(32):
            wx = 1.0 - abs(x - 15.5) / 15.5; wy = 1.0 - abs(y - 15.5) / 15.5; w = max(0.0, min(1.0, min(wx, wy) * 2.0))
            out[x, y] = tuple(int(pa[x, y][k] * w + pb[x, y][k] * (1 - w)) for k in range(4))
    return po

# aged cream wallpaper with faded vertical stripes and grime (indoor walls, RE mansion style)
im = new((168, 150, 112, 255)); d = ImageDraw.Draw(im)
for x in range(0, 32, 8):
    d.line([x, 0, x, 31], fill=(146, 128, 92, 255)); d.line([x + 1, 0, x + 1, 31], fill=(186, 170, 130, 255))
for (sx, sy, ln) in ((6, 10, 12), (20, 2, 9), (13, 22, 8)):                       # grime streaks
    d.line([sx, sy, sx, sy + ln], fill=(112, 94, 66, 255)); d.line([sx + 1, sy + 1, sx + 1, sy + ln - 2], fill=(124, 106, 76, 255))
noise(im, 5, 13); save(seamless(im), 'mans_wall')
# dark wood wainscot
im = new((56, 36, 24, 255)); d = ImageDraw.Draw(im)
for i in range(0, 32, 16):
    d.rectangle([i+1, 2, i+14, 29], outline=(30, 18, 10, 255)); d.rectangle([i+3, 4, i+12, 27], outline=(78, 52, 32, 255))
    d.line([i+4, 6, i+4, 25], fill=(64, 42, 26, 255))
d.line([0, 31, 31, 31], fill=(26, 16, 10, 255)); d.line([0, 0, 31, 0], fill=(80, 56, 34, 255))
noise(im, 5, 14); save(im, 'mans_panel')
# mossy brick (courtyard walls) with a thorny vine
im = new((70, 50, 42, 255)); d = ImageDraw.Draw(im)
for row in range(8):
    y = row * 4; off = 0 if row % 2 == 0 else 8
    d.line([0, y, 31, y], fill=(34, 30, 28, 255))
    for bx in range(-8, 32, 16): d.line([bx + off, y, bx + off, y + 3], fill=(34, 30, 28, 255))
    for bx in range(-8, 32, 16):
        sh = random.Random(row * 9 + bx).randint(-10, 10)
        d.rectangle([bx + off + 1, y + 1, bx + off + 14, y + 3], fill=(70 + sh, 50 + sh // 2, 42 + sh // 2, 255))
for (px, py, w) in ((2, 26, 10), (18, 2, 9), (20, 28, 8)):                       # moss
    d.rectangle([px, py, px + w, py + 2], fill=(44, 78, 44, 255))
d.line([4, 31, 9, 22, 14, 16, 17, 8, 24, 3, 28, 0], fill=(30, 68, 36, 255))     # vine
for (tx, ty) in ((9, 22), (17, 8), (14, 16)): d.point([tx + 1, ty - 1], fill=(120, 150, 90, 255))
noise(im, 5, 15); save(seamless(im), 'mans_brick')
# cracked slime flagstones (courtyard floor)
im = new((74, 78, 72, 255)); d = ImageDraw.Draw(im)
for (x0, y0, x1, y1) in ((0, 0, 14, 10), (15, 0, 31, 13), (0, 11, 11, 31), (12, 14, 31, 22), (12, 23, 31, 31)):
    sh = random.Random(x0 * 7 + y0).randint(-8, 8)
    d.rectangle([x0, y0, x1, y1], fill=(74 + sh, 78 + sh, 72 + sh, 255), outline=(30, 34, 30, 255))
d.line([4, 3, 8, 8, 6, 12], fill=(24, 26, 24, 255)); d.line([22, 15, 26, 19, 24, 22], fill=(24, 26, 24, 255))
for (sx, sy, rx, ry) in ((16, 8, 5, 3), (4, 22, 6, 4), (24, 26, 5, 3)):          # toxic slime puddles
    d.ellipse([sx - rx, sy - ry, sx + rx, sy + ry], fill=(52, 120, 44, 255)); d.ellipse([sx - rx + 2, sy - ry + 1, sx + rx - 3, sy + ry - 2], fill=(90, 170, 70, 255))
noise(im, 5, 16); save(seamless(im), 'mans_cobble')
# slate (corridors, cellar, lab): dark with moss
im = new((60, 66, 62, 255)); d = ImageDraw.Draw(im)
for i in range(0, 32, 16):
    for j in range(0, 32, 16): d.rectangle([i, j, i+15, j+15], outline=(28, 32, 30, 255))
for (px, py) in ((3, 4), (20, 18), (9, 24)): d.rectangle([px, py, px + 6, py + 2], fill=(46, 84, 48, 255))
noise(im, 6, 17); save(im, 'mans_stone')
# dark grey-brown tile, no moss (indoor floors)
im = new((82, 76, 70, 255)); d = ImageDraw.Draw(im)
for i in range(0, 32, 16):
    for j in range(0, 32, 16):
        sh = random.Random(i * 3 + j).randint(-7, 7)
        d.rectangle([i, j, i + 15, j + 15], fill=(82 + sh, 76 + sh, 70 + sh, 255), outline=(40, 36, 34, 255))
d.line([5, 20, 9, 26, 7, 31], fill=(40, 36, 34, 255))
noise(im, 4, 19); save(im, 'mans_tile')
# iron railing band (courtyard balcony)
im = new((22, 24, 22, 255)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, 31, 3], fill=(80, 84, 76, 255)); d.rectangle([0, 28, 31, 31], fill=(80, 84, 76, 255))
for x in range(2, 32, 8):
    d.rectangle([x, 4, x + 1, 27], fill=(60, 66, 60, 255)); d.polygon([(x - 1, 4), (x + 2, 4), (x + 0.5, 0)], fill=(70, 76, 70, 255))
noise(im, 3, 18); save(im, 'mans_rail')
# arched iron gate in a mossy stone frame (drawn once on a wall)
im = Image.new('RGBA', (32, 32), (84, 92, 82, 255)); d = ImageDraw.Draw(im)
d.rectangle([4, 10, 27, 31], fill=(10, 12, 10, 255)); d.pieslice([4, 2, 27, 20], 180, 360, fill=(10, 12, 10, 255))
d.arc([3, 1, 28, 21], 180, 360, fill=(120, 130, 112, 255)); d.arc([2, 0, 29, 22], 180, 360, fill=(52, 58, 50, 255))
for x in range(7, 26, 3):
    d.line([x, 5 if 9 < x < 22 else 11, x, 31], fill=(54, 62, 54, 255)); d.point([x, 4 if 9 < x < 22 else 10], fill=(90, 98, 88, 255))
d.line([4, 18, 27, 18], fill=(44, 52, 44, 255)); d.line([4, 26, 27, 26], fill=(44, 52, 44, 255))
d.line([5, 31, 8, 22, 6, 14, 10, 8], fill=(40, 90, 44, 255))                      # vines over the gate
d.line([26, 31, 24, 24, 26, 15], fill=(40, 90, 44, 255))
noise(im, 4, 19); save(im, 'mans_gate')
# framed portraits (three faces)
def portrait(name, bg, skin, hair, seed):
    im = Image.new('RGBA', (32, 32), (46, 32, 18, 255)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 31, 31], outline=(150, 118, 52, 255)); d.rectangle([2, 2, 29, 29], outline=(80, 58, 26, 255))
    d.rectangle([3, 3, 28, 28], fill=bg)
    d.ellipse([10, 7, 21, 19], fill=skin); d.rectangle([13, 18, 18, 22], fill=skin)
    d.pieslice([9, 5, 22, 17], 180, 360, fill=hair); d.polygon([(5, 28), (9, 22), (22, 22), (27, 28)], fill=(26, 24, 30, 255))
    d.point([13, 12], fill=(10, 10, 10, 255)); d.point([18, 12], fill=(10, 10, 10, 255)); d.line([14, 16, 17, 16], fill=(90, 40, 40, 255))
    noise(im, 5, seed); save(im, name)
portrait('mans_portrait1', (36, 52, 44, 255), (170, 176, 150, 255), (30, 26, 22, 255), 21)
portrait('mans_portrait2', (52, 44, 34, 255), (190, 160, 130, 255), (120, 80, 36, 255), 22)
portrait('mans_portrait3', (30, 36, 52, 255), (176, 150, 140, 255), (60, 40, 50, 255), 23)

# --- item icons (billboards, alpha) ---------------------------------------
def icon(name, fn):
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0)); fn(ImageDraw.Draw(im)); save(im, name)
def herb(col, dark):
    def f(d):
        for ang in ((16, 28, 6, 8), (16, 28, 26, 8), (16, 28, 16, 3)):
            d.line(ang, fill=dark, width=1)
        for cx, cy in ((9, 10), (23, 10), (16, 6), (11, 17), (21, 17)):
            d.ellipse([cx-4, cy-3, cx+4, cy+3], fill=col, outline=dark)
        d.rectangle([14, 22, 17, 29], fill=(70, 50, 20, 255))
    return f
icon('item_herb_g', herb((60, 190, 70, 255), (20, 90, 30, 255)))
icon('item_herb_r', herb((210, 50, 50, 255), (110, 20, 20, 255)))
icon('item_herb_b', herb((70, 110, 220, 255), (30, 50, 120, 255)))
def key(d):
    d.ellipse([4, 4, 14, 14], outline=(235, 200, 70, 255), width=3); d.rectangle([12, 8, 28, 10], fill=(235, 200, 70, 255))
    d.rectangle([22, 10, 24, 15], fill=(235, 200, 70, 255)); d.rectangle([27, 10, 28, 14], fill=(235, 200, 70, 255))
    d.polygon([(9, 7), (10, 10), (13, 10), (11, 12), (12, 15), (9, 13), (6, 15), (7, 12), (5, 10), (8, 10)], fill=(255, 245, 160, 255))
icon('item_key', key)
def ribbon(d):
    d.ellipse([6, 8, 26, 26], fill=(30, 30, 34, 255), outline=(120, 120, 130, 255)); d.ellipse([12, 14, 20, 20], fill=(150, 150, 150, 255))
    d.rectangle([4, 4, 12, 7], fill=(180, 40, 40, 255))
icon('item_ribbon', ribbon)
def fileicon(d):
    d.rectangle([7, 3, 25, 28], fill=(230, 220, 190, 255), outline=(110, 90, 60, 255))
    for y in range(8, 25, 4): d.line([10, y, 22, y], fill=(120, 100, 80, 255))
icon('item_file', fileicon)
def chest(d):
    d.rectangle([3, 12, 28, 28], fill=(80, 55, 35, 255), outline=(30, 20, 10, 255)); d.rectangle([3, 8, 28, 14], fill=(100, 70, 45, 255), outline=(30, 20, 10, 255))
    d.rectangle([14, 13, 17, 18], fill=(210, 180, 60, 255))
icon('item_box', chest)
def typewriter(d):
    d.rectangle([4, 14, 28, 27], fill=(40, 40, 46, 255), outline=(150, 150, 160, 255)); d.rectangle([8, 6, 24, 14], fill=(220, 215, 195, 255), outline=(110, 100, 80, 255))
    for x in range(7, 27, 4):
        for y in (18, 22): d.rectangle([x, y, x+2, y+1], fill=(200, 200, 205, 255))
icon('item_typewriter', typewriter)
def pistol(d):
    d.rectangle([4, 8, 26, 14], fill=(60, 60, 66, 255), outline=(150, 150, 160, 255)); d.rectangle([5, 14, 12, 26], fill=(50, 40, 34, 255), outline=(150, 150, 160, 255))
icon('item_gun', pistol)
im = new((34, 52, 30, 255)); d = ImageDraw.Draw(im)           # dark overgrown grass (courtyard)
for k in range(40):
    r = random.Random(k); x = r.randint(0, 31); y = r.randint(0, 28)
    d.line([x, y, x + r.randint(-2, 2), y + 3], fill=(22 + r.randint(0, 24), 70 + r.randint(0, 30), 30, 255))
noise(im, 6, 11); save(im, 'mans_grass')
def keyc(col, hi):
    def f(d):
        d.ellipse([4, 4, 14, 14], outline=col, width=3); d.rectangle([12, 8, 28, 10], fill=col)
        d.rectangle([22, 10, 24, 15], fill=col); d.rectangle([27, 10, 28, 14], fill=col)
        d.ellipse([7, 7, 11, 11], fill=hi)
    return f
icon('item_key2', keyc((150, 170, 230, 255), (230, 240, 255, 255)))     # Moon Key: silver-blue
icon('item_key3', keyc((235, 130, 40, 255), (255, 220, 120, 255)))      # Sun Key: orange
def ammo(d):
    for i, x in enumerate((6, 12, 18, 24)):
        d.rectangle([x, 12, x + 4, 26], fill=(200, 160, 60, 255), outline=(110, 80, 20, 255))
        d.polygon([(x, 12), (x + 4, 12), (x + 2, 6)], fill=(170, 120, 50, 255), outline=(110, 80, 20, 255))
icon('item_ammo', ammo)

# --- doors marked with the emblem of the key that opens them ----------------------
import math
def door_emblem(name, col, kind):
    im = new((84, 52, 30, 255)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 31, 31], outline=(34, 20, 10, 255)); d.rectangle([4, 3, 27, 14], outline=(52, 30, 16, 255))
    d.rectangle([4, 17, 27, 28], outline=(52, 30, 16, 255)); d.ellipse([24, 19, 27, 22], fill=(190, 160, 60, 255))
    noise(im, 4, 7)
    # emblem drawn 8x oversized and box-filtered down so it stays readable at 32x32
    K = 8; cx, cy = 15.5 * K, 8.6 * K
    big = Image.new('RGBA', (32 * K, 32 * K), (0, 0, 0, 0)); g = ImageDraw.Draw(big)
    def circ(r, fill): g.ellipse([cx - r * K, cy - r * K, cx + r * K, cy + r * K], fill=fill)
    circ(6.6, (200, 168, 62, 255)); circ(5.6, (30, 22, 20, 255))                         # brass ring + dark plate
    if kind == 'star':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; r = (5.2 if i % 2 == 0 else 2.3) * K
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        g.polygon(pts, fill=col)
    elif kind == 'moon':
        circ(4.6, col)
        g.ellipse([cx - 1.2 * K, cy - 4.8 * K, cx + 5.0 * K, cy + 3.2 * K], fill=(30, 22, 20, 255))
    else:
        circ(2.4, col)
        for i in range(8):
            a = i * math.pi / 4
            g.line([cx + 3.2 * K * math.cos(a), cy + 3.2 * K * math.sin(a), cx + 5.2 * K * math.cos(a), cy + 5.2 * K * math.sin(a)], fill=col, width=int(1.5 * K))
    small = big.resize((32, 32), Image.BOX)
    im.alpha_composite(small)
    save(im, name)
door_emblem('mans_door_k1', (240, 205, 70, 255), 'star')
door_emblem('mans_door_k2', (160, 185, 240, 255), 'moon')
door_emblem('mans_door_k3', (245, 140, 40, 255), 'sun')

# --- main-menu title image (320x240, RGBA16, Floyd-Steinberg dithered to 5 bits/channel) --------------
def title_image():
    import numpy as np
    src = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'title_logo.jpg')).convert('RGB')
    h = 240; w = round(src.width * h / src.height)
    src = src.resize((w, h), Image.LANCZOS)
    x0 = (w - 320) // 2
    a = np.asarray(src.crop((x0, 0, x0 + 320, 240)), dtype=np.float64)
    # darken the bottom strip so the PRESS START prompt reads cleanly
    ramp = np.clip((np.arange(240) - 196) / 44.0, 0, 1)[:, None, None]
    a = a * (1.0 - 0.72 * ramp)
    out = np.zeros_like(a)
    H, W, _ = a.shape
    for y in range(H):
        for x in range(W):
            old = a[y, x].copy()
            q = np.clip(np.round(old / 255.0 * 31.0), 0, 31)
            new = q * 255.0 / 31.0
            out[y, x] = q
            err = old - new
            if x + 1 < W: a[y, x + 1] += err * (7 / 16)
            if y + 1 < H:
                if x > 0: a[y + 1, x - 1] += err * (3 / 16)
                a[y + 1, x] += err * (5 / 16)
                if x + 1 < W: a[y + 1, x + 1] += err * (1 / 16)
    q = out.astype(np.uint8)
    rgb = ((q << 3) | (q >> 2)).astype(np.uint8)
    im = Image.fromarray(rgb, 'RGB').convert('RGBA')
    save(im, 'mans_title')
title_image()

# --- user-supplied photo textures: carpet, table/box wood, courtyard cement + grass ---------------
user_floor('tex_floor_carpet_rug.jpg', 'mans_carpet', periods=6)    # whole rug (border + medallion), not a sub-tile crop
user_floor('tex_wood_table.jpg', 'mans_wood', periods=2)            # tables, desks, crates, shelves
user_floor('tex_courtyard_grass.jpg', 'mans_grass', periods=2)      # courtyard floor
user_floor('tex_courtyard_cement.jpg', 'mans_cement', periods=4)    # courtyard walls/panels
user_floor('tex_metal_plate.jpg', 'mans_metal_plate', periods=2)    # riveted rusted plates: lab walls, tunnel walls
user_floor('tex_metal_diamond.jpg', 'mans_metal_diamond', periods=2) # diamond plate + vents: tunnel and dock floors
user_floor('tex_courtyard_brick.jpg', 'mans_brick', periods=3)      # courtyard walls; replaces the procedural mossy brick above
# framed oil paintings hung on room walls: the whole square canvas, squashed to 32x32 like the other textures
for _pname in ('bowser', 'drybones', 'mushroom', 'goomba', 'peach'):
    user_floor('tex_paint_%s.jpg' % _pname, 'mans_paint_%s' % _pname, periods=6)

print('textures written')
