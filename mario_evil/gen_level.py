#!/usr/bin/env python3
"""
Mario EVIL level generator.

Reads the room definitions in mansion_map.py and writes:
  levels/bbh/areas/1/mansion_model.inc.c   room display lists (vertex-lit, textured)
  levels/bbh/areas/1/collision.inc.c       collision for every room
  levels/bbh/areas/1/geo.inc.c             area geo layout + item billboard geos
  levels/bbh/script.c                      level script (objects, warps)
  levels/bbh/header.h                      externs
  levels/bbh/texture.inc.c (appended)      texture arrays (idempotent marker block)
  src/game/mansion_data.inc.c              rooms / cameras / doors / pickups tables for game code
Run from the repo root:  python3 mario_evil/gen_level.py
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from mansion_map import ROOMS, DOORS, ITEM_IDS, FILES, START, MAPRECTS
import cinematics as CIN
import models as MDL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LV = os.path.join(ROOT, 'levels', 'bbh')
TILE = 256.0          # world units per texture repeat
DOOR_W, DOOR_H = 300, 340
CELL = 520            # max vertex-lighting cell size

TEXTURES = ['mans_floor', 'mans_carpet', 'mans_wall', 'mans_panel', 'mans_ceil', 'mans_stone', 'mans_tile',
            'mans_door', 'mans_wood', 'mans_marble', 'mans_grass', 'mans_cement', 'mans_metal_plate', 'mans_metal_diamond',
            'mans_door_k1', 'mans_door_k2', 'mans_door_k3',
            'mans_brick', 'mans_cobble', 'mans_rail', 'mans_gate', 'mans_portrait1', 'mans_portrait2', 'mans_portrait3',
            'mans_paint_bowser', 'mans_paint_drybones', 'mans_paint_mushroom', 'mans_paint_goomba', 'mans_paint_peach',
            'mans_caution', 'mans_stairs_down']
ICONS = ['item_herb_g', 'item_herb_r', 'item_herb_b', 'item_key', 'item_ribbon', 'item_file',
         'item_box', 'item_typewriter', 'item_gun', 'item_key2', 'item_key3', 'item_ammo', 'held_gun', 'item_console', 'item_luigi',
         'prop_fountain', 'prop_chandelier', 'prop_lamp', 'prop_pot', 'prop_clock', 'prop_stairs', 'prop_vine', 'prop_table', 'prop_desk', 'prop_chair', 'prop_fireplace',
         'prop_fridge', 'prop_stove', 'prop_counter', 'prop_sink', 'prop_kpot', 'prop_cup', 'prop_mushroom', 'prop_mushroom_big',
         'prop_stair_flight', 'prop_balustrade', 'prop_hall_fountain']   # 3D models (models.py)

def door_emblem(d):
    """Key id whose emblem is painted on this door: its own key, or the key of the door it connects to."""
    if d.get('key'): return d['key'] if d['key'] < 8 else 0   # keys 8+ are story locks, no emblem
    for o in DOORS:
        if o['id'] == d['to'] and o.get('key'): return o['key'] if o['key'] < 8 else 0
    return 0

def door_tex(d):
    k = door_emblem(d)
    return 'mans_door_k%d' % k if k else 'mans_door'

def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def mul(a, k): return (a[0]*k, a[1]*k, a[2]*k)
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def length(a): return math.sqrt(dot(a, a))
def norm(a):
    l = length(a); return (a[0]/l, a[1]/l, a[2]/l)
def s16(v): return int(round(v))

class RoomGeo:
    def __init__(self, room):
        self.room = room
        self.faces = {}      # tex -> list of cells; cell = (verts[4], tris_idx_order)
        self.col = []        # collision quads: (p0,p1,p2,p3, desired normal)
        self.visible = True  # False while adding collision-only props

    # light --------------------------------------------------------------
    def shade(self, p):
        r = self.room
        p = (p[0], p[1] - r.get('yoff', 0), p[2])      # lights and falloff are in room-local height
        # Spooky grade: dim ambient, weaker candle pools, cold tint, deeper falloff toward the ceiling.
        # outdoor (open sky) rooms keep the sickly green cast; indoor rooms are warm, RE-mansion lamplight
        base = (0.76, 0.96, 0.82) if r.get('sky') else (1.0, 0.88, 0.70)
        amb = r.get('ambient', 0.40)
        v = [amb * base[0], amb * base[1], amb * base[2]]
        for lt in r.get('lights', []):
            (lx, ly, lz, inten, rad) = lt[:5]
            col = lt[5] if len(lt) > 5 else base
            d2 = (p[0]-lx)**2 + (p[1]-ly)**2 + (p[2]-lz)**2
            k = 0.75 * inten / (1.0 + d2 / (rad * rad))
            for i in range(3): v[i] += k * col[i]
        fall = 1.0 - 0.35 * max(0.0, min(1.0, p[1] / max(1, r['h'])))
        return tuple(int(255 * max(0.06, min(1.0, v[i] * fall))) for i in range(3))

    # faces --------------------------------------------------------------
    def face(self, tex, O, U, V, normal, collide=False, uvflip_v=False, cell=CELL, lit=True, uv_once=False):
        """Parallelogram O + s*U + t*V, s,t in [0,1].  `normal` = desired outward normal."""
        if self.room.get('yoff'): O = (O[0], O[1] + self.room['yoff'], O[2])      # raised room (balcony): everything shifts up
        lu, lv = length(U), length(V)
        nu = max(1, int(math.ceil(lu / cell))); nv = max(1, int(math.ceil(lv / cell)))
        uh, vh = norm(U), norm(V)
        u_off = (dot(O, uh) * 1024.0 / TILE) % 1024.0
        v_off = (dot(O, vh) * 1024.0 / TILE) % 1024.0
        def vert(i, j):
            p = add(O, add(mul(U, i / nu), mul(V, j / nv)))
            u = u_off + (lu * i / nu) * 1024.0 / TILE
            v = v_off + (lv * j / nv) * 1024.0 / TILE
            if uvflip_v: v = v_off + (lv * (nv - j) / nv) * 1024.0 / TILE
            if uv_once:   # map the whole texture exactly once across the face (doors)
                u = 1020.0 * i / nu
                v = 1020.0 * ((nv - j) / nv if uvflip_v else j / nv)
            col = self.shade(p) if lit else (255, 255, 255)
            return (p, (s16(u), s16(v)), col)
        # decide winding once for the whole face
        pa = O; pb = add(O, U); pc = add(add(O, U), V)
        flip = dot(cross(sub(pb, pa), sub(pc, pa)), normal) < 0
        if self.visible:
            lst = self.faces.setdefault(tex, [])
            for i in range(nu):
                for j in range(nv):
                    q = [vert(i, j), vert(i+1, j), vert(i+1, j+1), vert(i, j+1)]
                    lst.append((q, flip))
        if collide:
            self.col.append((pa, pb, pc, add(O, V), normal))

    def box(self, x0, z0, x1, z1, y0, y1, side, top, collide=True):
        # +y top
        self.face(top, (x0, y1, z0), (x1-x0, 0, 0), (0, 0, z1-z0), (0, 1, 0), collide)
        # -z side (north)
        self.face(side, (x0, y0, z0), (x1-x0, 0, 0), (0, y1-y0, 0), (0, 0, -1), collide, uvflip_v=True)
        self.face(side, (x0, y0, z1), (x1-x0, 0, 0), (0, y1-y0, 0), (0, 0, 1), collide, uvflip_v=True)
        self.face(side, (x0, y0, z0), (0, 0, z1-z0), (0, y1-y0, 0), (-1, 0, 0), collide, uvflip_v=True)
        self.face(side, (x1, y0, z0), (0, 0, z1-z0), (0, y1-y0, 0), (1, 0, 0), collide, uvflip_v=True)
        if y0 > 0: self.face(side, (x0, y0, z0), (x1-x0, 0, 0), (0, 0, z1-z0), (0, -1, 0), False)   # underside of a raised slab

def wall_of(room, side):
    """returns (origin, along-vector, inward-normal, coordinate along) for a wall."""
    x0, z0, x1, z1, h = room['x0'], room['z0'], room['x1'], room['z1'], room['h']
    if side == 'N': return ((x0, 0, z0), (x1-x0, 0, 0), (0, 0, 1))
    if side == 'S': return ((x0, 0, z1), (x1-x0, 0, 0), (0, 0, -1))
    if side == 'W': return ((x0, 0, z0), (0, 0, z1-z0), (1, 0, 0))
    if side == 'E': return ((x1, 0, z0), (0, 0, z1-z0), (-1, 0, 0))
    raise ValueError(side)

def build_room(room):
    g = RoomGeo(room)
    x0, z0, x1, z1, h = room['x0'], room['z0'], room['x1'], room['z1'], room['h']
    W, D = x1-x0, z1-z0
    floor = room.get('floor', 'mans_floor')
    # floor (collides), ceiling (collides), 4 walls (collide)
    g.face(floor, (x0, 0, z0), (W, 0, 0), (0, 0, D), (0, 1, 0), True)
    # carpet runner
    for (cx0, cz0, cx1, cz1) in room.get('carpets', []):
        g.face('mans_carpet', (cx0, 3, cz0), (cx1-cx0, 0, 0), (0, 0, cz1-cz0), (0, 1, 0), False)
    # texture pads over the floor (same overlay method as carpets): (x0, z0, x1, z1, texture)
    for pad in room.get('pads', []):
        (px0, pz0, px1, pz1, ptex) = pad[:5]
        g.face(ptex, (px0, 3, pz0), (px1-px0, 0, 0), (0, 0, pz1-pz0), (0, 1, 0), False, uv_once=(len(pad) > 5 and pad[5]))
    if not room.get('sky') and not room.get('noceil'):
        g.face(room.get('ceil', 'mans_ceil'), (x0, h, z0), (W, 0, 0), (0, 0, D), (0, -1, 0), True)
    wall = room.get('wall', 'mans_wall'); panel = room.get('panel', 'mans_panel')
    for side in 'NSEW':
        O, A, n = wall_of(room, side)
        g.visible = side not in room.get('open', '')      # 'open' walls keep their collision but are not drawn (balcony edge)
        # lower wainscot (panel) and upper wallpaper
        wh = room.get('wainscot', 330)
        if wh > 0:
            g.face(panel, O, A, (0, wh, 0), n, True, uvflip_v=True)
            g.face(wall, add(O, (0, wh, 0)), A, (0, h-wh, 0), n, True, uvflip_v=True)
        else:
            g.face(wall, O, A, (0, h, 0), n, True, uvflip_v=True)
        g.visible = True
    # decor quads painted on the walls (gates, portraits) and the balcony rail band
    for dc in room.get('decor', []):
        O, A, n = wall_of(room, dc['wall'])
        al = norm(A)
        cen = add(O, mul(al, dc['at'] - (O[0] if abs(al[0]) > .5 else O[2])))
        base = add(add(sub(cen, mul(al, dc['w'] / 2)), (0, dc['y0'], 0)), mul(n, 3))
        g.face(dc['tex'], base, mul(al, dc['w']), (0, dc['h'], 0), n, False, uvflip_v=True, lit=True, cell=140, uv_once=True)
    if room.get('rail'):
        ry0, ry1 = room['rail']
        for side in 'NSEW':
            O, A, n = wall_of(room, side)
            g.face('mans_rail', add(O, mul(n, 4)) if False else add(add(O, (0, ry0, 0)), mul(n, 3)), A, (0, ry1 - ry0, 0), n, False, uvflip_v=True, cell=300)
    # props
    for p in room.get('boxes', []):
        g.visible = not p.get('hidden', False)     # hidden = collision only (a 3D model object is drawn there)
        g.box(p['x0'], p['z0'], p['x1'], p['z1'], p.get('y0', 0), p['y1'], p.get('side', 'mans_wood'), p.get('top', 'mans_wood'), p.get('collide', True))
        g.visible = True
    # doors (drawn proud of the wall; wall collision already blocks)
    for d in DOORS:
        if d['room'] != room['id'] or 'virtual' in d: continue
        O, A, n = wall_of(room, d['wall'])
        al = norm(A)
        c = add(O, mul(al, d['at'] - (O[0] if abs(al[0]) > .5 else O[2])))
        base = add(sub(c, mul(al, DOOR_W/2)), mul(n, 4))
        g.face(door_tex(d), base, mul(al, DOOR_W), (0, DOOR_H, 0), n, False, uvflip_v=True, lit=True, cell=170, uv_once=True)
        # lintel
        lb = add(sub(c, mul(al, DOOR_W/2+30)), mul(n, 6))
        g.face('mans_wood', add(lb, (0, DOOR_H, 0)), mul(al, DOOR_W+60), (0, 40, 0), n, False, uvflip_v=True, cell=2000)
        for sgn in (-1, 1):
            pb = add(add(c, mul(al, sgn*(DOOR_W/2+15))), mul(n, 6))
            g.face('mans_wood', sub(pb, mul(al, 15)), mul(al, 30), (0, DOOR_H+40, 0), n, False, uvflip_v=True, cell=2000)
    return g

def validate():
    bad = 0
    for r in ROOMS:
        for i, c in enumerate(r['cams']):
            x, y, z = c['pos']
            if c.get('outside'): continue          # deliberate cameras beyond a wall (walls are one-sided, so they see through it)
            if not (r['x0'] < x < r['x1'] and r['z0'] < z < r['z1'] and 0 < y < r['h']):
                print('ERROR: camera %s/%d is outside the room' % (r['id'], i)); bad += 1
            for b in r.get('boxes', []):
                m = 150
                if b['x0'] - m < x < b['x1'] + m and b['z0'] - m < z < b['z1'] + m and y < b['y1'] + m:
                    print('ERROR: camera %s/%d is within %d units of a prop' % (r['id'], i, m)); bad += 1
            for o in r.get('objs', []):
                pass
    if bad: raise SystemExit(1)

def emit_all():
    validate()
    geos = [build_room(r) for r in ROOMS]
    # ---------------- model.inc.c ------------------------------------------------
    out = ['// Generated by mario_evil/gen_level.py -- do not edit by hand\n']
    tilesetup = (
        '    gsDPPipeSync(),\n'
        '    gsDPSetCombineMode(G_CC_MODULATERGBA, G_CC_MODULATERGBA),\n'
        '    gsSPClearGeometryMode(G_LIGHTING),\n'
        '    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0, 0, G_TX_LOADTILE, 0, G_TX_WRAP | G_TX_NOMIRROR, G_TX_NOMASK, G_TX_NOLOD, G_TX_WRAP | G_TX_NOMIRROR, G_TX_NOMASK, G_TX_NOLOD),\n'
        '    gsSPTexture(0xFFFF, 0xFFFF, 0, G_TX_RENDERTILE, G_ON),\n'
        '    gsDPTileSync(),\n'
        '    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 8, 0, G_TX_RENDERTILE, 0, G_TX_WRAP | G_TX_NOMIRROR, 5, G_TX_NOLOD, G_TX_WRAP | G_TX_NOMIRROR, 5, G_TX_NOLOD),\n'
        '    gsDPSetTileSize(0, 0, 0, (32 - 1) << G_TEXTURE_IMAGE_FRAC, (32 - 1) << G_TEXTURE_IMAGE_FRAC),\n')
    tileend = ('    gsSPTexture(0xFFFF, 0xFFFF, 0, G_TX_RENDERTILE, G_OFF),\n'
               '    gsDPPipeSync(),\n'
               '    gsDPSetCombineMode(G_CC_SHADE, G_CC_SHADE),\n'
               '    gsSPSetGeometryMode(G_LIGHTING),\n'
               '    gsSPEndDisplayList(),\n};\n\n')
    def vtx_line(v):
        (p, uv, col) = v
        return '    {{{%6d, %6d, %6d}, 0, {%6d, %6d}, {0x%02x, 0x%02x, 0x%02x, 0xff}}},\n' % (s16(p[0]), s16(p[1]), s16(p[2]), uv[0], uv[1], col[0], col[1], col[2])
    for r, g in zip(ROOMS, geos):
        body = []
        for tex, cells in g.faces.items():
            arr = 'mansion_vtx_%s_%s' % (r['id'], tex)
            out.append('static const Vtx %s[] = {\n' % arr)
            for (q, flip) in cells:
                for v in q: out.append(vtx_line(v))
            out.append('};\n\n')
            body.append('    gsDPSetTextureImage(G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, %s_tex),\n' % tex)
            body.append('    gsDPLoadSync(),\n')
            body.append('    gsDPLoadBlock(G_TX_LOADTILE, 0, 0, 32 * 32 - 1, CALC_DXT(32, G_IM_SIZ_16b_BYTES)),\n')
            n = len(cells); k = 0
            while k < n:
                m = min(7, n - k)  # 7 quads = 28 verts per load
                body.append('    gsSPVertex(&%s[%d], %d, 0),\n' % (arr, k*4, m*4))
                tris = []
                for c in range(m):
                    b = c*4; flip = cells[k+c][1]
                    t1, t2 = ((b, b+1, b+2), (b, b+2, b+3)) if not flip else ((b, b+2, b+1), (b, b+3, b+2))
                    tris += [t1, t2]
                for i in range(0, len(tris), 2):
                    if i+1 < len(tris):
                        a, b2 = tris[i], tris[i+1]
                        body.append('    gsSP2Triangles(%d, %d, %d, 0x0, %d, %d, %d, 0x0),\n' % (a + b2))
                    else:
                        body.append('    gsSP1Triangle(%d, %d, %d, 0x0),\n' % tris[i])
                k += m
        out.append('const Gfx mansion_dl_%s[] = {\n' % r['id'])
        out.append(tilesetup); out += body; out.append(tileend)
    # door-opening cinematic: textured, unlit, no z-test, no culling (drawn by geo_mansion_door_anim)
    door_texs = ['mans_door', 'mans_door_k1', 'mans_door_k2', 'mans_door_k3']
    for ei, dtex in enumerate(door_texs):
        out.append('const Gfx mansion_door_begin_dl%d[] = {\n' % ei)
        out.append(tilesetup)
        out.append('    gsDPSetTextureImage(G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, %s_tex),\n    gsDPLoadSync(),\n' % dtex)
        out.append('    gsDPLoadBlock(G_TX_LOADTILE, 0, 0, 32 * 32 - 1, CALC_DXT(32, G_IM_SIZ_16b_BYTES)),\n')
        out.append('    gsDPSetRenderMode(G_RM_OPA_SURF, G_RM_OPA_SURF2),\n')
        out.append('    gsSPClearGeometryMode(G_ZBUFFER | G_CULL_BACK),\n')
        out.append('    gsSPEndDisplayList(),\n};\n\n')
    # main-menu title screen: full-bleed 320x240 RGBA16 drawn as 40 texture-rectangle strips of 6 rows (TMEM is 4 KB)
    out.append('const Gfx mansion_title_dl[] = {\n')
    out.append('    gsDPPipeSync(),\n    gsDPSetCycleType(G_CYC_1CYCLE),\n    gsDPSetRenderMode(G_RM_OPA_SURF, G_RM_OPA_SURF2),\n')
    out.append('    gsDPSetCombineMode(G_CC_DECALRGB, G_CC_DECALRGB),\n    gsDPSetTexturePersp(G_TP_NONE),\n    gsDPSetTextureFilter(G_TF_POINT),\n    gsDPSetTextureLUT(G_TT_NONE),\n')
    out.append('    gsSPTexture(0xFFFF, 0xFFFF, 0, G_TX_RENDERTILE, G_ON),\n')
    for i in range(40):
        out.append('    gsDPLoadTextureBlock(mans_title_tex + %d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 320, 6, 0, G_TX_CLAMP | G_TX_NOMIRROR, G_TX_CLAMP | G_TX_NOMIRROR, G_TX_NOMASK, G_TX_NOMASK, G_TX_NOLOD, G_TX_NOLOD),\n' % (i * 320 * 6 * 2))
        out.append('    gsSPTextureRectangle(0 << 2, %d << 2, 320 << 2, %d << 2, G_TX_RENDERTILE, 0, 0, 1 << 10, 1 << 10),\n' % (i * 6, i * 6 + 6))
    out.append('    gsDPPipeSync(),\n    gsSPTexture(0xFFFF, 0xFFFF, 0, G_TX_RENDERTILE, G_OFF),\n    gsDPSetTexturePersp(G_TP_PERSP),\n    gsDPSetTextureFilter(G_TF_BILERP),\n    gsDPSetCombineMode(G_CC_SHADEFADEA, G_CC_SHADEFADEA),\n    gsSPEndDisplayList(),\n};\n\n')
    out.append('const Gfx mansion_door_end_dl[] = {\n    gsSPSetGeometryMode(G_ZBUFFER | G_CULL_BACK),\n')
    out.append(tileend)
    # 3D item / prop models (models.py)
    for ic in ICONS:
        out.append(MDL.emit_model(ic, MDL.MODELS[ic]()))
    open(os.path.join(LV, 'areas', '1', 'mansion_model.inc.c'), 'w').write(''.join(out))

    # ---------------- collision --------------------------------------------------
    verts = []; vidx = {}
    def vi(p):
        k = (s16(p[0]), s16(p[1]), s16(p[2]))
        if k not in vidx: vidx[k] = len(verts); verts.append(k)
        return vidx[k]
    tris = []
    for g in geos:
        for (p0, p1, p2, p3, n) in g.col:
            flip = dot(cross(sub(p1, p0), sub(p2, p0)), n) < 0
            a, b, c, d = vi(p0), vi(p1), vi(p2), vi(p3)
            tris += [(a, c, b), (a, d, c)] if flip else [(a, b, c), (a, c, d)]
    col = ['// Generated by mario_evil/gen_level.py -- do not edit by hand\n',
           'const Collision mansion_collision[] = {\n    COL_INIT(),\n    COL_VERTEX_INIT(%d),\n' % len(verts)]
    for v in verts: col.append('    COL_VERTEX(%d, %d, %d),\n' % v)
    col.append('    COL_TRI_INIT(SURFACE_DEFAULT, %d),\n' % len(tris))
    for t in tris: col.append('    COL_TRI(%d, %d, %d),\n' % t)
    col.append('    COL_TRI_STOP(),\n    COL_END(),\n};\n')
    open(os.path.join(LV, 'areas', '1', 'collision.inc.c'), 'w').write(''.join(col))
    print('rooms', len(ROOMS), 'collision verts', len(verts), 'tris', len(tris))

    # ---------------- geo ----------------------------------------------------------
    geo = ['// Generated by mario_evil/gen_level.py -- do not edit by hand\n']
    for ic in ICONS:
        geo.append('const GeoLayout mansion_geo_%s[] = {\n   GEO_NODE_START(),\n   GEO_OPEN_NODE(),\n' % ic)
        geo.append('      GEO_DISPLAY_LIST(LAYER_OPAQUE, mansion_dl_%s),\n' % ic)
        geo.append('   GEO_CLOSE_NODE(),\n   GEO_END(),\n};\n\n')
    geo.append('const GeoLayout mansion_geo_area[] = {\n')
    geo.append('   GEO_NODE_SCREEN_AREA(10, SCREEN_CENTER_X, SCREEN_CENTER_Y, SCREEN_CENTER_X, SCREEN_CENTER_Y),\n   GEO_OPEN_NODE(),\n')
    geo.append('      GEO_ZBUFFER(0),\n      GEO_OPEN_NODE(),\n         GEO_NODE_ORTHO(100),\n         GEO_OPEN_NODE(),\n')
    geo.append('            GEO_BACKGROUND_COLOR(0x0001),\n         GEO_CLOSE_NODE(),\n      GEO_CLOSE_NODE(),\n')
    geo.append('      GEO_ZBUFFER(1),\n      GEO_OPEN_NODE(),\n         GEO_CAMERA_FRUSTUM_WITH_FUNC(45, 100, 12800, geo_camera_fov),\n         GEO_OPEN_NODE(),\n')
    geo.append('            GEO_CAMERA(CAMERA_MODE_FIXED, 0, 600, 600, 0, 0, 0, geo_camera_main),\n            GEO_OPEN_NODE(),\n')
    geo.append('               GEO_SWITCH_CASE(%d, geo_switch_mansion_room),\n               GEO_OPEN_NODE(),\n' % len(ROOMS))
    for r in ROOMS:
        if r.get('see'):      # this room also draws another one (the balcony looks down into the hall)
            geo.append('                  GEO_NODE_START(),\n                  GEO_OPEN_NODE(),\n                     GEO_DISPLAY_LIST(LAYER_OPAQUE, mansion_dl_%s),\n                     GEO_DISPLAY_LIST(LAYER_OPAQUE, mansion_dl_%s),\n                  GEO_CLOSE_NODE(),\n' % (r['id'], r['see']))
        else:
            geo.append('                  GEO_DISPLAY_LIST(LAYER_OPAQUE, mansion_dl_%s),\n' % r['id'])
    geo.append('               GEO_CLOSE_NODE(),\n               GEO_RENDER_OBJ(),\n               GEO_ASM(0, geo_mansion_door_anim),\n')
    geo.append('            GEO_CLOSE_NODE(),\n         GEO_CLOSE_NODE(),\n      GEO_CLOSE_NODE(),\n   GEO_CLOSE_NODE(),\n   GEO_END(),\n};\n')
    open(os.path.join(LV, 'areas', '1', 'geo.inc.c'), 'w').write(''.join(geo))

    # ---------------- header.h ---------------------------------------------------
    hdr = open(os.path.join(LV, 'header.h')).read()
    start = hdr.find('// MANSION-BEGIN')
    if start != -1:
        hdr = hdr[:start] + hdr[hdr.find('// MANSION-END') + len('// MANSION-END\n'):]
    blk = ['// MANSION-BEGIN (generated)\n', 'extern const GeoLayout mansion_geo_area[];\n', 'extern const Collision mansion_collision[];\n']
    for ic in ICONS:
        blk.append('extern const GeoLayout mansion_geo_%s[];\nextern const Gfx mansion_dl_%s[];\n' % (ic, ic))
    blk.append(''.join('extern const Gfx mansion_door_begin_dl%d[];\n' % i for i in range(4)) + 'extern const Gfx mansion_door_end_dl[];\nextern const Gfx mansion_title_dl[];\n')
    for r in ROOMS: blk.append('extern const Gfx mansion_dl_%s[];\n' % r['id'])
    blk.append('// MANSION-END\n')
    endif = hdr.rfind('#endif')
    hdr = hdr[:endif] + ''.join(blk) + '\n' + hdr[endif:]
    open(os.path.join(LV, 'header.h'), 'w').write(hdr)

    # ---------------- texture.inc.c ------------------------------------------
    tx = open(os.path.join(LV, 'texture.inc.c')).read()
    m = tx.find('// MANSION-BEGIN')
    if m != -1: tx = tx[:m]
    tx += '// MANSION-BEGIN (generated)\n'
    for t in TEXTURES + ['mans_title']:
        tx += 'ALIGNED8 static const Texture %s_tex[] = {\n#include "levels/bbh/%s.rgba16.inc.c"\n};\n\n' % (t, t)
    open(os.path.join(LV, 'texture.inc.c'), 'w').write(tx)

    # ---------------- game data tables -----------------------------------------------
    roomidx = {r['id']: i for i, r in enumerate(ROOMS)}
    didx = {d['id']: i for i, d in enumerate(DOORS)}
    cams = []; rows = []
    for r in ROOMS:
        first = len(cams)
        for c in r['cams']:
            c = dict(c)
            yo = r.get('yoff', 0)
            if yo:
                c['pos'] = (c['pos'][0], c['pos'][1] + yo, c['pos'][2]); c['look'] = (c['look'][0], c['look'][1] + yo, c['look'][2])
            cams.append(c)
        rows.append((r, first, len(r['cams'])))
    dt = ['// Generated by mario_evil/gen_level.py -- do not edit by hand\n#define MANSION_NUM_ROOMS %d\n#define MANSION_NUM_DOORS %d\n#define MANSION_NUM_CAMS %d\n\n' % (len(ROOMS), len(DOORS), len(cams))]
    dt.append('const struct MansionRoom gMansionRooms[MANSION_NUM_ROOMS] = {\n')
    for (r, first, cnt) in rows:
        mr = [int(round(v * 10)) for v in MAPRECTS[r['id']]]
        dt.append('    { %d, %d, %d, %d, %d, %d, "%s", %d, %d, %d, %d },\n' % (r['x0'], r['z0'], r['x1'], r['z1'], first, cnt, r['name'], mr[0], mr[1], mr[2], mr[3]))
    dt.append('};\n\nconst struct MansionCam gMansionCams[MANSION_NUM_CAMS] = {\n')
    for c in cams:
        z = c['zone']; p = c['pos']; f = c['look']
        dt.append('    { %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d },\n' % (z[0], z[1], z[2], z[3], p[0], p[1], p[2], f[0], f[1], f[2], c.get('fov', 50)))
    dt.append('};\n\nconst struct MansionDoor gMansionDoors[MANSION_NUM_DOORS] = {\n')
    for d in DOORS:
        r = ROOMS[roomidx[d['room']]]
        if 'virtual' in d:
            cx, cz = d['virtual']; n = (d['n'][0], 0, d['n'][1])
        else:
            O, A, n = wall_of(r, d['wall'])
            al = norm(A)
            cx = O[0] + (al[0] * (d['at'] - O[0]) if abs(al[0]) > .5 else 0)
            cz = O[2] + (al[2] * (d['at'] - O[2]) if abs(al[2]) > .5 else 0)
        sx, sz = cx + n[0]*210, cz + n[2]*210
        yaw = int(round(math.atan2(n[0], n[2]) / (2*math.pi) * 65536)) & 0xFFFF
        dest = didx[d['to']]
        lc = geos[roomidx[d['room']]].shade((cx + n[0]*60, 170 + r.get('yoff', 0), cz + n[2]*60))
        dt.append('    { %d, %d, %d, %d, %d, %d, %d, %d, %d, 0x%04X, %d, %d, %d, %d, %d },  // %s\n' % (roomidx[d['room']], s16(cx), s16(cz), s16(n[0]), s16(n[2]), dest, d.get('key', 0), s16(sx), s16(sz), yaw, lc[0], lc[1], lc[2], door_emblem(d), d.get('stair', 0), d['id']))
    dt.append('};\n')
    # ---------------- room objects: loaded/unloaded at runtime, not by the level script -----
    # Every pickup, zombie, prop, cinematic actor, typewriter, console and Luigi is a row in
    # gMansionRoomObjs[] (src/game/mansion.c reads it). mansion_load_room()/mansion_unload_room()
    # spawn or delete a room's rows at the door transition, instead of the level script spawning
    # everything once at level load. See mario_evil-engine-hooks.md for the load/unload system.
    models = {k: ('MODEL_LEVEL_GEOMETRY_%02X' % (3 + i) if i < 20 else '0x%02X' % (0xE8 + i - 20)) for i, k in enumerate(ICONS)}
    room_objs = []
    uid = [0]
    def nuid():
        uid[0] += 1
        return uid[0]
    for r in ROOMS:
        ridx = roomidx[r['id']]
        for o in r.get('objs', []):
            kind = o['kind']; x, z = o['pos']; y = o.get('y', 0) + r.get('yoff', 0)
            yaw = o.get('yaw', 0)
            if kind in ITEM_IDS:
                iid = ITEM_IDS[kind]
                icon = {'herb_g': 'item_herb_g', 'herb_r': 'item_herb_r', 'herb_b': 'item_herb_b', 'ribbon': 'item_ribbon',
                        'key': {1: 'item_key', 2: 'item_key2', 3: 'item_key3'}.get(o.get('keyid', 1), 'item_key'),
                        'gun': 'item_gun', 'ammo': 'item_ammo'}[kind.split(':')[0]]
                par = (iid << 24) | (o.get('amount', 1) << 16) | (o.get('keyid', 0) << 8) | nuid()
                room_objs.append((ridx, models[icon], 'bhvMansionPickup', x, y + 10, z, yaw, par))
            elif kind == 'file':
                par = (o['file'] << 24)
                room_objs.append((ridx, models['item_file'], 'bhvMansionFile', x, y + 10, z, 0, par))
            elif kind == 'typewriter':
                room_objs.append((ridx, models['item_typewriter'], 'bhvMansionTypewriter', x, y + 10, z, yaw, 0))
            elif kind == 'box':
                room_objs.append((ridx, models['item_box'], 'bhvMansionItemBox', x, y + 10, z, yaw, 0))
            elif kind == 'zombie':
                mdl = 'MODEL_BOWSER' if o.get('boss') else 'MODEL_GOOMBA'
                room_objs.append((ridx, mdl, 'bhvMansionZombie', x, y, z, yaw, (o.get('hp', 3) << 24) | (o.get('boss', 0) << 8) | nuid()))
            elif kind == 'prop':
                room_objs.append((ridx, models['prop_' + o['model']], 'bhvMansionProp', x, y, z, yaw, 0))
            elif kind == 'actor':     # movable cinematic prop, addressed by its actor number
                mdl = 'MODEL_TOAD' if o['model'] == 'toad_rom' else models['prop_' + o['model']]
                room_objs.append((ridx, mdl, 'bhvMansionActor', x, y, z, yaw, o['actor']))
            elif kind in ('console', 'luigi'):
                beh = 'bhvMansionConsole' if kind == 'console' else 'bhvMansionLuigi'
                room_objs.append((ridx, models['item_' + kind], beh, x, y + 10, z, yaw, 0))
            else:
                raise SystemExit('unknown object kind ' + kind)
    dt.append('\nconst u8 gMansionViewOf[MANSION_NUM_ROOMS] = { %s };   // room whose scenery is also drawn (255 = none)\n' % ', '.join(str(roomidx[r['see']]) if r.get('see') else '255' for r in ROOMS))
    dt.append('\nconst struct MansionRoomObj gMansionRoomObjs[] = {\n')
    for (ridx, mdl, beh, x, y, z, yaw, par) in room_objs:
        dt.append('    { %d, %s, %s, %d, %d, %d, %d, 0x%08X },\n' % (ridx, mdl, beh, x, y, z, yaw & 0xFFFF, par))
    dt.append('};\nconst u16 gMansionRoomObjCount = %d;\n' % len(room_objs))
    open(os.path.join(ROOT, 'src', 'game', 'mansion_data.inc.c'), 'w').write(''.join(dt))

    # ---------------- script.c -----------------------------------------------------
    sc = open(os.path.join(os.path.dirname(__file__), 'script_template.c')).read()
    loads = ''.join('    LOAD_MODEL_FROM_GEO(%s, mansion_geo_%s),\n' % (models[k], k) for k in ICONS)
    sx, sz, syaw = START
    sc = (sc.replace('/*@@LOADS@@*/', loads).replace('/*@@OBJECTS@@*/', '')
            .replace('@@START_X@@', str(sx)).replace('@@START_Z@@', str(sz)).replace('@@START_YAW@@', str(syaw * 360 // 65536)))
    open(os.path.join(LV, 'script.c'), 'w').write(sc)

if __name__ == '__main__':
    emit_all()

# ---------------- cinematics (mario_evil/cinematics.py) ------------------------
def write_cinematics():
    OPS = {'cam': 'CINE_CAM', 'text': 'CINE_TEXT', 'move': 'CINE_MOVE', 'rot': 'CINE_ROT', 'wait': 'CINE_WAIT', 'sfx': 'CINE_SFX', 'walk': 'CINE_WALK'}
    def c_str(v):
        if v is None: return 'NULL'
        return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
    def flat(steps):
        for st in steps:
            if isinstance(st, list): yield from flat(st)
            elif st[0] == 'par': yield ('P',) + tuple(st[1])
            else: yield st
    out = ['/* generated by gen_level.py from mario_evil/cinematics.py -- do not edit */\n']
    tables = []
    for i, c in enumerate(CIN.CINES):
        rows = []
        for st in flat(c['steps']):
            par = 0
            if st[0] == 'P': par = 1; st = st[1:]
            op = st[0]
            v = [0] * 7; frames = 0; actor = 0; speaker = l0 = l1 = None; snd = 0; follow = 0
            if op == 'walk':
                v = [*st[1], 0, 0, 0, 0]; frames = st[2]
            elif op == 'cam':
                v = [*st[1], *st[2], int(st[3])]; frames = st[4]
                if len(st) > 5 and st[5] is not None:
                    follow = 1; v[3] = v[5] = 0; v[4] = int(st[5])   # follow: v[4] = look height above Mario's feet
            elif op == 'move':
                actor = st[1]; v = [*st[2], 0, 0, 0, 0]; frames = st[3]
            elif op == 'rot':
                actor = st[1]; v = [st[2], 0, 0, 0, 0, 0, 0]; frames = st[3]
            elif op == 'wait':
                frames = st[1]
            elif op == 'sfx':
                snd = st[1]
            elif op == 'text':
                speaker, l0, l1 = st[1], st[2], st[3]
            assert not (par and op == 'text'), 'text cannot run together with other steps'
            rows.append('    { .op = %s, .actor = %d, .par = %d, .follow = %d, .frames = %d, .v = {%s}, .speaker = %s, .line0 = %s, .line1 = %s, .sfx = %s },\n' % (
                OPS[op], actor, par, follow, frames, ', '.join(str(int(x)) for x in v), c_str(speaker), c_str(l0), c_str(l1), snd or 0))
        tables.append('static const struct CineStep gCineSteps%d[] = {\n%s};\n' % (i, ''.join(rows)))
    out.extend(tables)
    out.append('const struct CineScript gCines[] = {\n')
    for i, c in enumerate(CIN.CINES):
        x0, z0, x1, z1 = c.get('zone', (0, 0, 0, 0))
        talk = c.get('talk')
        ta, tr = (talk[0], talk[1]) if talk else (255, 0)
        once = 0 if talk else 1
        n = sum(1 for _ in flat(c['steps']))
        out.append('    { .zx0 = %d, .zz0 = %d, .zx1 = %d, .zz1 = %d, .talkRadius = %d, .talkActor = %d, .once = %d, .nSteps = %d, .steps = gCineSteps%d },   /* %s */\n' % (x0, z0, x1, z1, tr, ta, once, n, i, c['name']))
    out.append('};\n')
    out.append('const s32 gMansionCineCount = %d;\n' % len(CIN.CINES))
    assert len(CIN.CINES) <= 32, 'at most 32 cinematics'
    open(os.path.join(ROOT, 'src', 'game', 'mansion_cine_data.inc.h'), 'w').write(''.join(out))
    print('cinematics:', len(CIN.CINES))

write_cinematics()

