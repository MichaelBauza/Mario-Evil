#!/usr/bin/env python3
"""Software preview of every room from each fixed camera (sanity check for geometry, winding, lighting, framing)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
import gen_level as G
from mansion_map import ROOMS, DOORS, START
LV = G.LV
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
avg = {}
for t in G.TEXTURES:
    im = Image.open(os.path.join(LV, t + '.rgba16.png')).convert('RGB').resize((1, 1), Image.BOX)
    avg[t] = im.getpixel((0, 0))
W, H = 640, 480

def render(room, g, cam, markers):
    pos = cam['pos']; look = cam['look']; fov = cam.get('fov', 50)
    fwd = G.norm(G.sub(look, pos)); right = G.norm(G.cross(fwd, (0, 1, 0))); up = G.cross(right, fwd)
    f = (H / 2) / math.tan(math.radians(fov) / 2)
    def proj(p):
        d = G.sub(p, pos); x = G.dot(d, right); y = G.dot(d, up); z = G.dot(d, fwd)
        return x, y, z
    polys = []
    for tex, cells in g.faces.items():
        base = avg[tex]
        for (q, flip) in cells:
            ps = [proj(v[0]) for v in q]
            if any(p[2] < 60 for p in ps): continue
            pts = [(W / 2 + f * p[0] / p[2], H / 2 - f * p[1] / p[2]) for p in ps]
            # backface cull using the winding the DL will use
            order = (0, 1, 2) if not flip else (0, 2, 1)
            a, b, c = [pts[i] for i in order]
            area = (b[0]-a[0]) * (c[1]-a[1]) - (b[1]-a[1]) * (c[0]-a[0])
            if area > 0: continue      # screen y is down, CCW front faces have negative area here
            sh = [v[2] for v in q]
            r = sum(s[0] for s in sh) / 4 / 255; gg = sum(s[1] for s in sh) / 4 / 255; bb = sum(s[2] for s in sh) / 4 / 255
            col = (int(base[0] * r), int(base[1] * gg), int(base[2] * bb))
            depth = sum(p[2] for p in ps) / 4
            polys.append((depth, pts, col))
    polys.sort(key=lambda t: -t[0])
    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    for _, pts, col in polys: d.polygon(pts, fill=col)
    for (p, col, label) in markers:
        x, y, z = proj(p)
        if z > 60:
            sx, sy = W / 2 + f * x / z, H / 2 - f * y / z; s = max(4, 90 * f / z / 2)
            d.rectangle([sx - s / 2, sy - s, sx + s / 2, sy], fill=col, outline=(255, 255, 255))
    return im

colors = {'zombie': (120, 200, 90), 'herb_g': (60, 190, 70), 'herb_r': (210, 50, 50), 'herb_b': (70, 110, 220), 'key': (235, 200, 70),
          'ribbon': (150, 150, 150), 'file': (230, 220, 190), 'typewriter': (255, 255, 255), 'box': (120, 80, 50)}
for r in ROOMS:
    g = G.build_room(r)
    marks = [((o['pos'][0], o.get('y', 0) + (170 if o['kind'] == 'zombie' else 20), o['pos'][1]), colors.get(o['kind'], (255, 0, 255)), o['kind']) for o in r.get('objs', [])]
    # Mario marker at the middle of the first zone
    for i, cam in enumerate(r['cams']):
        z = cam['zone']; mp = ((z[0] + z[2]) / 2, 80, (z[1] + z[3]) / 2)
        im = render(r, g, cam, marks + [(mp, (230, 40, 40), 'mario')])
        im.save(os.path.join(OUT, '%s_cam%d.png' % (r['id'], i)))
print('previews in', OUT)
