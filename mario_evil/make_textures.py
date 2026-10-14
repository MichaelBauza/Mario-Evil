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
print('textures written')
