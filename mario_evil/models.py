#!/usr/bin/env python3
"""
Mini 3D mesh kit + the item/prop models for Mario EVIL (pistol, chest, typewriter, herbs, keys, ...).

Everything is flat-coloured, hardware-lit (normals + gsSPSetLights1, so spinning items stay lit
consistently), no textures.  Model origin = centre of the base; +y is up.  Sizes are world units
(Mario is ~160 tall).
"""
import math

# ---- tiny vector / matrix helpers --------------------------------------------------------
def v_sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def v_add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def v_dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def v_cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def v_norm(a):
    l = math.sqrt(v_dot(a, a))
    return (a[0]/l, a[1]/l, a[2]/l) if l > 1e-9 else (0.0, 1.0, 0.0)

def rot(yaw=0.0, pitch=0.0, roll=0.0):
    """3x3 rotation, degrees: roll about z, then pitch about x, then yaw about y."""
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    cr, sr = math.cos(math.radians(roll)), math.sin(math.radians(roll))
    Rz = ((cr, -sr, 0), (sr, cr, 0), (0, 0, 1))
    Rx = ((1, 0, 0), (0, cp, -sp), (0, sp, cp))
    Ry = ((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))
    def mm(A, B): return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    return mm(Ry, mm(Rx, Rz))

IDENT = rot()
def apply(R, p): return (R[0][0]*p[0]+R[0][1]*p[1]+R[0][2]*p[2],
                         R[1][0]*p[0]+R[1][1]*p[1]+R[1][2]*p[2],
                         R[2][0]*p[0]+R[2][1]*p[1]+R[2][2]*p[2])

class Mesh:
    def __init__(self):
        self.tris = []      # (p0, p1, p2, n0, n1, n2, color)

    def tri(self, p0, p1, p2, color, normals=None, inside=None):
        """Add a triangle wound counter-clockwise seen from outside.  `inside` = a point inside the
        solid (used to pick the winding); with None the winding is kept as given."""
        gn = v_norm(v_cross(v_sub(p1, p0), v_sub(p2, p0)))
        if inside is not None:
            cen = ((p0[0]+p1[0]+p2[0])/3, (p0[1]+p1[1]+p2[1])/3, (p0[2]+p1[2]+p2[2])/3)
            if v_dot(gn, v_sub(cen, inside)) < 0:
                p1, p2 = p2, p1
                gn = (-gn[0], -gn[1], -gn[2])
                if normals: normals = (normals[0], normals[2], normals[1])
        if normals is None: normals = (gn, gn, gn)
        self.tris.append((p0, p1, p2, normals[0], normals[1], normals[2], color))

    def quad(self, a, b, c, d, color, inside=None, double=False):
        self.tri(a, b, c, color, None, inside); self.tri(a, c, d, color, None, inside)
        if double:   # leaves: visible from both sides
            self.tri(a, c, b, color, None, None); self.tri(a, d, c, color, None, None)

    # ---- solids ---------------------------------------------------------------------
    def box(self, c, size, color, R=IDENT):
        hx, hy, hz = size[0]/2, size[1]/2, size[2]/2
        pts = [(sx*hx, sy*hy, sz*hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        P = [v_add(apply(R, p), c) for p in pts]
        idx = {(sx, sy, sz): P[i] for i, (sx, sy, sz) in enumerate([(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])}
        for axis in range(3):
            for sgn in (-1, 1):
                def key(u, v):
                    k = [0, 0, 0]; k[axis] = sgn
                    o = [i for i in range(3) if i != axis]
                    k[o[0]] = u; k[o[1]] = v
                    return idx[tuple(k)]
                self.quad(key(-1, -1), key(1, -1), key(1, 1), key(-1, 1), color, inside=c)

    def cyl(self, c, r, h, color, n=10, r_top=None, R=IDENT, smooth=True):
        """Upright cylinder / cone frustum centred on c (c = middle of the axis), height h."""
        rt = r if r_top is None else r_top
        W = lambda p: v_add(apply(R, p), c)
        for i in range(n):
            j = (i+1) % n
            a0 = 2*math.pi*i/n; a1 = 2*math.pi*j/n
            n0 = apply(R, (math.cos(a0), 0, math.sin(a0))); n1 = apply(R, (math.cos(a1), 0, math.sin(a1)))
            b0 = W((r*math.cos(a0), -h/2, r*math.sin(a0))); b1 = W((r*math.cos(a1), -h/2, r*math.sin(a1)))
            t0 = W((rt*math.cos(a0), h/2, rt*math.sin(a0))); t1 = W((rt*math.cos(a1), h/2, rt*math.sin(a1)))
            self._side(b0, b1, t1, t0, n0, n1, color, c, smooth)
            if rt > 0.01: self.tri(W((0, h/2, 0)), t0, t1, color, None, c)
            self.tri(W((0, -h/2, 0)), b0, b1, color, None, c)

    def _side(self, b0, b1, t1, t0, n0, n1, color, inside, smooth):
        gn = v_norm(v_cross(v_sub(b1, b0), v_sub(t1, b0)))
        cen = ((b0[0]+t1[0])/2, (b0[1]+t1[1])/2, (b0[2]+t1[2])/2)
        flip = v_dot(gn, v_sub(cen, inside)) < 0
        if not smooth:
            n0 = n1 = v_norm(((n0[0]+n1[0])/2, (n0[1]+n1[1])/2, (n0[2]+n1[2])/2))
        if not flip:
            self.tris.append((b0, b1, t1, n0, n1, n1, color)); self.tris.append((b0, t1, t0, n0, n1, n0, color))
        else:
            self.tris.append((b0, t1, b1, n0, n1, n1, color)); self.tris.append((b0, t0, t1, n0, n0, n1, color))

    def sphere(self, c, r, color, nlat=6, nlon=10, squash=(1.0, 1.0, 1.0)):
        """Smooth-shaded ellipsoid (poles on +/-y)."""
        def P(i, j):
            th = math.pi * i / nlat; ph = 2 * math.pi * (j % nlon) / nlon
            n = (math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph))
            return (c[0] + r * squash[0] * n[0], c[1] + r * squash[1] * n[1], c[2] + r * squash[2] * n[2]), n
        for i in range(nlat):
            for j in range(nlon):
                (a, na), (b, nb), (cc, nc), (d, nd) = P(i, j), P(i, j + 1), P(i + 1, j + 1), P(i + 1, j)
                for (p0, p1, p2, n0, n1, n2) in ((a, d, cc, na, nd, nc), (a, cc, b, na, nc, nb)):
                    if p0 == p2 or p0 == p1 or p1 == p2: continue
                    gn = v_cross(v_sub(p1, p0), v_sub(p2, p0))
                    if v_dot(gn, v_sub(p0, c)) < 0: p1, p2, n1, n2 = p2, p1, n2, n1
                    self.tris.append((p0, p1, p2, n0, n1, n2, color))

    def prism(self, pts2, thick, color, c=(0, 0, 0), R=IDENT):
        """Extrude a star-shaped polygon (list of (x,y) around the origin) along z by `thick`."""
        n = len(pts2); z = thick/2
        W = lambda x, y, zz: v_add(apply(R, (x, y, zz)), c)
        for i in range(n):
            j = (i+1) % n
            a, b = pts2[i], pts2[j]
            self.tri(W(0, 0, z), W(a[0], a[1], z), W(b[0], b[1], z), color, None, c)
            self.tri(W(0, 0, -z), W(a[0], a[1], -z), W(b[0], b[1], -z), color, None, c)
            self.quad(W(a[0], a[1], -z), W(b[0], b[1], -z), W(b[0], b[1], z), W(a[0], a[1], z), color, c)

    def band(self, outer, inner, thick, color, c=(0, 0, 0), R=IDENT, closed=True):
        """Flat strip between two matching point lists (rings, crescents), extruded along z."""
        n = len(outer); z = thick/2
        W = lambda p, zz: v_add(apply(R, (p[0], p[1], zz)), c)
        last = n if closed else n-1
        for i in range(last):
            j = (i+1) % n
            o0, o1, i0, i1 = outer[i], outer[j], inner[i], inner[j]
            ins = v_add(apply(R, ((o0[0]+o1[0]+i0[0]+i1[0])/4, (o0[1]+o1[1]+i0[1]+i1[1])/4, 0)), c)
            self.quad(W(o0, z), W(o1, z), W(i1, z), W(i0, z), color, inside=ins)      # front
            self.quad(W(o0, -z), W(o1, -z), W(i1, -z), W(i0, -z), color, inside=ins)  # back
            self.quad(W(o0, -z), W(o1, -z), W(o1, z), W(o0, z), color, inside=ins)    # outer wall
            self.quad(W(i0, -z), W(i1, -z), W(i1, z), W(i0, z), color, inside=ins)    # inner wall
        if not closed:
            for idx in (0, n-1):
                o, q = outer[idx], inner[idx]
                ins = v_add(apply(R, ((o[0]+q[0])/2, (o[1]+q[1])/2, 0)), c)
                self.quad(W(o, -z), W(q, -z), W(q, z), W(o, z), color, inside=None, double=True)

    def leaf(self, base, length, width, yaw, pitch, color, c=(0, 0, 0)):
        """Double-sided diamond leaf growing from `base`, tilted `pitch` degrees from vertical."""
        R = rot(yaw=yaw, pitch=pitch)
        b = v_add(c, base)
        p0 = b
        p1 = v_add(b, apply(R, (-width/2, length*0.4, 0)))
        p2 = v_add(b, apply(R, (0, length, 0)))
        p3 = v_add(b, apply(R, (width/2, length*0.4, 0)))
        self.quad(p0, p3, p2, p1, color, inside=None, double=True)

def ring_pts(r, n, a0=0.0, a1=2*math.pi, closed=True):
    cnt = n if closed else n+1
    return [(r*math.cos(a0 + (a1-a0)*i/n), r*math.sin(a0 + (a1-a0)*i/n)) for i in range(cnt)]

# ---- colours -------------------------------------------------------------------------
GREEN = (60, 160, 60); GREEN_D = (36, 100, 40); RED = (200, 40, 40); BLUE = (70, 110, 225)
STEM = (50, 120, 40); POT = (120, 70, 48); SOIL = (40, 28, 20); YELLOW = (230, 200, 70)
WOOD = (92, 58, 34); WOOD_D = (60, 38, 22); METAL = (150, 150, 158); METAL_D = (62, 64, 72)
GUN = (52, 54, 62); GUN_L = (92, 94, 104); BRASS = (205, 165, 60); LEATHER = (70, 44, 30)

# ---- models ----------------------------------------------------------------------------
def herb(flower):
    m = Mesh()
    m.cyl((0, 11, 0), 20, 22, POT, n=10, r_top=26)
    m.cyl((0, 22.5, 0), 24, 2, SOIL, n=10)
    for k in range(6):
        m.leaf((0, 22, 0), 52 + (k % 2) * 10, 22, k * 60 + 10, 38 + (k % 3) * 8, GREEN if k % 2 == 0 else GREEN_D)
    m.cyl((0, 40, 0), 2.5, 36, STEM, n=5)
    if flower is not None:
        col = RED if flower == 'r' else BLUE
        for k in range(5):
            m.leaf((0, 56, 0), 24, 14, k * 72, 55, col)
        m.cyl((0, 58, 0), 5, 5, YELLOW, n=6)
    return m

def key_model(kind):
    m = Mesh()
    col = {'star': (232, 190, 55), 'moon': (150, 175, 225), 'sun': (240, 130, 40)}[kind]
    dark = tuple(int(c * 0.65) for c in col)
    # key stands upright: bow on top, shaft down, bit on the lower right; flat in the xy plane
    BOWY = 74
    if kind == 'star':
        pts = []
        for i in range(10):
            a = math.pi/2 + i*math.pi/5; r = 24 if i % 2 == 0 else 10.5
            pts.append((r*math.cos(a), r*math.sin(a)))
        m.prism(pts, 8, col, c=(0, BOWY, 0))
    elif kind == 'moon':
        outer = ring_pts(24, 10, math.radians(60), math.radians(60+300), closed=False)
        # inner arc is the same circle shifted: gives a crescent
        inner = [(x + 11, y - 2) for (x, y) in ring_pts(20, 10, math.radians(60), math.radians(60+300), closed=False)]
        # clamp so strip ends meet the outer arc
        inner[0] = outer[0]; inner[-1] = outer[-1]
        m.band(outer, inner, 8, col, c=(0, BOWY, 0), closed=False)
    else:
        m.band(ring_pts(15, 10), ring_pts(8, 10), 8, col, c=(0, BOWY, 0))
        for i in range(8):
            a = i*math.pi/4
            rr = 25
            m.box((rr*math.cos(a), BOWY + rr*math.sin(a), 0), (9, 9, 7), col, rot(roll=math.degrees(a)))
    m.box((0, 36, 0), (7, 46, 7), col)                    # shaft
    m.box((0, BOWY - 28, 0), (12, 6, 10), dark)           # collar
    m.box((8, 14, 0), (13, 6, 6), col); m.box((9, 26, 0), (11, 6, 6), col); m.box((7, 5, 0), (8, 8, 6), col)  # bit teeth
    m.box((0, 44, 0), (3, 3, 9), dark)
    return m

def pistol():
    m = Mesh()
    # barrel along +x, grip down; floats with its centre ~ 40 above the base
    y = 44
    m.box((4, y + 8, 0), (74, 14, 14), GUN)                       # slide
    m.box((-31, y + 8, 0), (6, 14, 10), GUN_L)                    # rear sight block
    m.box((38, y + 8, 0), (8, 8, 8), GUN_L)                       # muzzle
    m.box((-2, y - 3, 0), (56, 8, 12), GUN_L)                     # frame
    m.box((-22, y - 24, 0), (18, 38, 12), LEATHER, rot(roll=-14)) # grip
    m.box((-22, y - 24, 6.2), (14, 32, 1.5), (30, 22, 18), rot(roll=-14))
    m.box((8, y - 14, 0), (3, 12, 7), GUN)                        # trigger guard front
    m.box((-6, y - 20, 0), (3, 12, 7), GUN)                       # (rear)
    m.box((1, y - 21, 0), (14, 3, 7), GUN)                        # (bottom)
    m.box((0, y - 10, 0), (2, 6, 3), METAL)                       # trigger
    m.box((-31, y + 17, 0), (5, 4, 5), METAL_D)                   # hammer
    return m

def ammo_box():
    m = Mesh()
    m.box((0, 14, 0), (44, 26, 28), (66, 78, 50))
    m.box((0, 20, 14.3), (36, 10, 1.5), (210, 205, 170))
    for k in range(3):
        x = -12 + k*12
        m.cyl((x, 33, 0), 3.5, 14, BRASS, n=6)
        m.cyl((x, 42, 0), 3.5, 6, (150, 110, 70), n=6, r_top=0.8)
    return m

def ribbon():
    m = Mesh()
    m.box((0, 11, 0), (62, 20, 38), (36, 36, 42))                 # cassette
    m.box((0, 21.5, 0), (50, 2, 24), (190, 190, 196))             # label
    m.box((0, 21.8, 0), (20, 2.2, 24), (210, 40, 40))
    for sx in (-1, 1):
        m.cyl((sx*17, 12, 0), 9, 22, (120, 120, 130), n=8)
    m.box((0, 5, 20), (40, 3, 3), (20, 20, 22))                   # ribbon run
    return m

def file_model():
    m = Mesh()
    m.box((0, 30, 0), (46, 60, 6), (214, 198, 150))
    m.box((-22, 30, 0), (4, 60, 8), (130, 40, 36))                # spine
    m.box((2, 40, 3.5), (26, 3, 1.5), (110, 96, 76)); m.box((2, 31, 3.5), (26, 3, 1.5), (110, 96, 76))
    m.box((2, 22, 3.5), (18, 3, 1.5), (110, 96, 76))
    m.cyl((10, 12, 3.8), 6, 2, (160, 30, 30), n=8, R=rot(pitch=90))   # wax seal
    return m

def chest():
    m = Mesh()
    m.box((0, 24, 0), (116, 48, 66), WOOD)                        # body
    m.box((0, 52, 0), (118, 12, 68), WOOD_D)                      # lid
    for sx in (-44, 0, 44):
        m.box((sx, 28, 0), (8, 62, 70), METAL_D)                  # iron bands
    m.box((0, 40, 34.5), (14, 16, 4), BRASS)                      # lock plate
    m.box((0, 38, 36.8), (4, 6, 2), METAL_D)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((sx*56, 4, sz*30), (8, 8, 8), METAL_D)          # feet / corners
    return m

def typewriter():
    """Just the machine (the desk is a separate prop in the room); keys face +z."""
    m = Mesh()
    D = -40   # base of the machine at y=0
    m.box((0, 49+D, 4), (58, 18, 34), (34, 36, 42))                  # body
    m.box((0, 60+D, -4), (50, 6, 20), (44, 46, 54))                  # upper deck
    m.box((0, 46+D, 24), (50, 6, 12), (30, 32, 38))                  # key bank slope
    for r in range(3):
        for k in range(7):
            m.box((-18 + k*6, 51+D - r*1.5, 17 + r*4.2), (4, 3, 3), (205, 205, 210))
    m.cyl((0, 64+D, -4), 4, 52, (20, 20, 22), n=8, R=rot(roll=90))   # platen roller
    m.box((0, 78+D, -8), (34, 26, 1.5), (232, 228, 210))             # paper sheet
    for ln in range(4):
        m.box((0, 70+D + ln*5, -7), (26, 1.2, 0.6), (80, 78, 70))
    m.box((-30, 66+D, -4), (4, 8, 4), METAL); m.box((30, 66+D, -4), (4, 8, 4), METAL)
    m.box((0, 40+D+0.5, 4), (60, 1, 36), (20, 20, 24))                # base plate
    return m

def pistol_held():
    """Pistol for Mario's fist: origin = grip centre, barrel along +z (Mario's forward), up = +y."""
    m = pistol()
    R = rot(yaw=-90)                 # barrel +x -> +z
    out = Mesh()
    S = 0.8
    def tx(q):
        q = apply(R, ((q[0] + 22) * S, (q[1] - 22) * S, q[2] * S))
        return q
    for (p0, p1, p2, n0, n1, n2, c) in m.tris:
        out.tris.append((tx(p0), tx(p1), tx(p2), apply(R, n0), apply(R, n1), apply(R, n2), c))
    return out


def console():
    """Wall-less lab console: slanted screen with a red warning display; keys face +z."""
    m = Mesh()
    m.box((0, 40, 0), (110, 80, 60), (70, 74, 84))
    m.box((0, 85, -6), (104, 14, 40), (50, 54, 64), rot(pitch=-25))
    m.box((0, 108, -14), (96, 52, 8), (24, 26, 32), rot(pitch=-12))
    m.box((0, 108, -9.5), (80, 38, 2), (200, 40, 40), rot(pitch=-12))
    for k in range(5):
        m.box((-36 + k*18, 78, 14), (8, 4, 8), (230, 200, 70) if k % 2 else (200, 60, 60))
    return m

def luigi():
    m = Mesh()
    SK = (236, 190, 150); GRN = (50, 160, 60); OVR = (60, 90, 200)
    for sx in (-1, 1):
        m.box((sx*20, 32, 0), (28, 64, 30), OVR)                     # legs
        m.box((sx*20, 4, 10), (30, 10, 46), (90, 54, 34))            # shoes
        m.box((sx*47, 90, 0), (20, 56, 22), GRN)                      # arms
        m.box((sx*47, 56, 0), (20, 14, 22), (240, 240, 240))          # gloves
    m.box((0, 70, 0), (68, 40, 40), OVR)
    m.box((0, 104, 0), (70, 36, 40), GRN)
    m.box((0, 78, 21), (24, 24, 3), (232, 200, 70))                  # buttons plate
    m.box((0, 142, 0), (52, 46, 48), SK)                             # head
    m.box((0, 136, 28), (16, 14, 14), SK)                            # nose
    m.box((0, 126, 25), (40, 8, 8), (70, 44, 28))                    # moustache
    m.box((-12, 148, 25), (8, 8, 3), (30, 30, 40)); m.box((12, 148, 25), (8, 8, 3), (30, 30, 40))
    m.box((0, 168, -2), (58, 14, 54), GRN)                            # cap
    m.box((0, 162, 30), (56, 6, 26), GRN)                             # brim
    m.box((-6, 108, 21), (30, 14, 3), (120, 30, 30))                  # bandage
    return m

def tyrant():
    """Tyrant Bowser: hulking spore-mutated Bowser, facing +z.  ~520 tall."""
    m = Mesh()
    SK = (92, 70, 120); SKD = (60, 44, 84); BELLY = (170, 150, 110); SHELL = (40, 36, 42)
    SPIKE = (200, 190, 170); RED = (230, 30, 30); PURP = (150, 60, 190)
    for sx in (-1, 1):
        m.box((sx*85, 22, 25), (96, 44, 130), SKD)                    # feet
        for k in (-1, 0, 1):
            m.cyl((sx*85 + k*30, 22, 98), 9, 36, SPIKE, n=5, r_top=0.5, R=rot(pitch=90))   # claws
        m.box((sx*85, 125, 0), (84, 160, 84), SK)                     # legs
    m.box((0, 255, 0), (260, 110, 170), SK)                           # hips / waist
    m.box((0, 250, 88), (190, 90, 14), BELLY)                         # belly
    m.box((0, 385, 0), (330, 170, 190), SK)                           # chest
    m.box((0, 380, 98), (230, 110, 12), BELLY)
    for sx in (-1, 1):
        m.box((sx*215, 380, 25), (84, 200, 90), SK, rot(roll=sx*10))  # arms
        m.box((sx*232, 270, 55), (84, 70, 84), SKD, rot(roll=sx*6))   # forearm
        for k in (-1, 0, 1):
            m.cyl((sx*232 + k*26, 235, 100), 10, 50, SPIKE, n=5, r_top=0.5, R=rot(pitch=90))
        for k in range(2):
            m.cyl((sx*(165 + k*32), 475 + k*8, 0), 24, 80, SPIKE, n=6, r_top=0.5, R=rot(roll=-sx*20))  # shoulder spikes
    # head
    m.box((0, 520, 50), (170, 120, 170), SK)
    m.box((0, 492, 150), (130, 56, 90), SKD)                          # snout
    for k in range(-2, 3):
        m.cyl((k*24, 462, 190), 7, 26, SPIKE, n=4, r_top=0.5, R=rot(pitch=180))   # lower teeth point up
    for sx in (-1, 1):
        m.box((sx*42, 545, 132), (32, 18, 12), RED)                   # glowing eyes
        m.cyl((sx*70, 600, 20), 20, 130, SPIKE, n=6, r_top=0.5, R=rot(roll=-sx*18))   # horns
    m.cyl((0, 620, 10), 40, 20, (200, 40, 40), n=8, r_top=8)           # hair crest
    # spore growth on the shoulder / back
    m.cyl((120, 520, -40), 12, 60, (190, 180, 150), n=6)
    m.cyl((120, 560, -40), 60, 34, PURP, n=10, r_top=14)
    m.cyl((-100, 420, -110), 10, 40, (190, 180, 150), n=6)
    m.cyl((-100, 448, -110), 40, 24, PURP, n=10, r_top=10)
    # shell
    m.box((0, 395, -125), (300, 220, 70), SHELL)
    for ix in (-1, 0, 1):
        for iy in (0, 1):
            m.cyl((ix*95, 345 + iy*105, -190), 34, 85, SPIKE, n=6, r_top=0.5, R=rot(pitch=-90))
    return m

# ---- v17 set dressing (courtyard / hall concept art) ----------------------------------------------------
STONE = (118, 124, 112); STONE_D = (84, 90, 80); MOSS = (52, 92, 50); VINE = (36, 72, 40); WATER = (30, 64, 52)
GHOST = (206, 210, 198); CRACK = (120, 124, 112); FLAME = (140, 255, 150); IRON = (40, 42, 44)

def vine_strand(m, pts, r=6, color=VINE, thorn=True):
    """Chain of thin cylinders through 3D points, with little thorns."""
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        d = v_sub(b, a); L = math.sqrt(v_dot(d, d))
        if L < 1: continue
        mid = ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2)
        # rotate the cylinder's y axis onto d
        yaw = math.degrees(math.atan2(d[0], d[2])); pitch = math.degrees(math.atan2(math.sqrt(d[0]**2 + d[2]**2), d[1]))
        R = rot(yaw=yaw, pitch=pitch)
        m.cyl(mid, r, L, color, n=5, R=R)
        if thorn and k % 2 == 0:
            side = apply(R, (1, 0, 0))
            m.cyl(v_add(mid, (side[0]*r, side[1]*r, side[2]*r)), 3.5, 14, (150, 170, 110), n=4, r_top=0.4, R=rot(yaw=yaw, pitch=pitch, roll=-90))

def fountain():
    """Courtyard fountain: wide basin, column, bowl and a ghost statue (white Boo-like head, one red eye)."""
    m = Mesh()
    m.cyl((0, 55, 0), 205, 110, STONE, n=14)                               # basin wall
    m.cyl((0, 112, 0), 214, 12, STONE_D, n=14)                              # rim
    m.cyl((0, 104, 0), 188, 4, WATER, n=14)                                 # water
    m.cyl((0, 175, 0), 46, 150, STONE, n=10, r_top=36)                      # column
    m.cyl((0, 262, 0), 120, 36, STONE, n=12, r_top=70)                      # lower bowl
    m.cyl((0, 262 + 20, 0), 104, 4, WATER, n=12)                            # upper water
    m.cyl((0, 300, 0), 30, 70, STONE_D, n=8)                                # statue pedestal
    m.sphere((0, 395, 0), 82, GHOST, nlat=6, nlon=10, squash=(1.0, 0.95, 0.95))       # head
    m.box((0, 410, 76), (30, 30, 12), (230, 30, 30))                        # red eye
    m.box((0, 410, 83), (14, 14, 6), (255, 190, 190))
    m.box((0, 350, 70), (84, 26, 20), (30, 8, 8))                           # mouth
    for k in range(-3, 4):
        m.cyl((k*11, 358, 80), 4, 20, (240, 240, 230), n=4, r_top=0.4, R=rot(pitch=180))
        m.cyl((k*11, 340, 80), 4, 16, (240, 240, 230), n=4, r_top=0.4)
    for sx in (-1, 1):
        m.sphere((sx*95, 330, 20), 24, GHOST, nlat=4, nlon=8)               # stubby arms
    # thorny vines climbing the basin and the column
    for (ph, hmax) in ((0.0, 330), (2.1, 250), (4.2, 300)):
        pts = []
        for t in range(9):
            a = ph + t * 0.55; rr = 208 - t * 15 if t < 3 else 50
            pts.append((rr * math.cos(a), 110 + t * hmax / 9, rr * math.sin(a)))
        vine_strand(m, pts, r=6)
    for k in range(6):
        a = k * 1.05
        m.sphere((205 * math.cos(a), 118, 205 * math.sin(a)), 14, MOSS, nlat=3, nlon=6)
    return m

def chandelier():
    """Hangs from the ceiling: origin at the bottom of the ring, chain rises 250 up."""
    m = Mesh()
    m.cyl((0, 150, 0), 4, 200, IRON, n=5)
    m.cyl((0, 45, 0), 26, 20, IRON, n=8, r_top=10)
    ring = ring_pts(104, 14); inner = ring_pts(96, 14)
    m.band(ring, inner, 8, IRON, c=(0, 30, 0), R=rot(pitch=90))
    m.band(ring_pts(60, 12), ring_pts(54, 12), 6, IRON, c=(0, 50, 0), R=rot(pitch=90))
    for k in range(6):
        a = k * math.pi / 3
        x, z = 100 * math.cos(a), 100 * math.sin(a)
        m.cyl((x, 46, z), 8, 32, (220, 220, 200), n=6)
        m.cyl((x, 70, z), 5, 16, FLAME, n=5, r_top=0.4)
        m.cyl((x, 40 - 14, z), 3, 40, (110, 190, 90), n=4, r_top=1.2)       # slime dripping from the candles
    m.sphere((0, 10, 0), 14, IRON, nlat=3, nlon=6)
    return m

def lamp():
    """Wall lantern with green glass; origin = wall mount, sticks out along +z."""
    m = Mesh()
    m.box((0, 0, 4), (24, 60, 8), IRON)
    m.box((0, 14, 28), (8, 8, 44), IRON)
    m.cyl((0, 20, 52), 17, 38, (150, 255, 170), n=8, r_top=14)
    m.cyl((0, 44, 52), 21, 10, IRON, n=8, r_top=7)
    m.cyl((0, -2, 52), 18, 6, IRON, n=8)
    return m

def pot():
    """Broken terracotta pot on its side."""
    m = Mesh()
    T = (160, 82, 52); TD = (108, 54, 36)
    m.cyl((0, 26, 0), 26, 46, T, n=8, r_top=36, R=rot(roll=70))
    m.cyl((22, 20, 6), 20, 8, TD, n=6, R=rot(roll=70))
    for k in range(4):
        a = k * 1.6
        m.box((60 * math.cos(a) + 30, 3, 60 * math.sin(a)), (16, 5, 10), T, rot(yaw=k * 50))
    m.sphere((-40, 8, 12), 14, (54, 40, 28), nlat=3, nlon=6)
    return m

def clock():
    m = Mesh()
    W = (62, 40, 26); WD = (40, 26, 16)
    m.box((0, 14, 0), (64, 28, 44), WD)
    m.box((0, 110, 0), (54, 164, 36), W)
    m.box((0, 215, 0), (66, 50, 42), WD)
    m.box((0, 218, 22), (40, 40, 3), (210, 214, 190))
    m.box((0, 224, 24), (2, 16, 2), (20, 20, 20)); m.box((6, 218, 24), (14, 2, 2), (20, 20, 20))
    m.box((0, 100, 19), (34, 90, 3), (22, 18, 14))
    m.cyl((0, 80, 21), 9, 3, BRASS, n=8, R=rot(pitch=90))
    return m

def stairs():
    """Grand staircase block, 600 wide (x) x 340 deep (z), rising toward -z (back wall) to 260; vine railings."""
    m = Mesh()
    N = 6
    for i in range(N):
        y1 = 260 * (i + 1) / N; zf = -170 + 340 * (N - 1 - i) / N + 340 / N     # front edge of this step
        zb = -170
        m.box((0, y1 / 2, (zf + zb) / 2), (600, y1, zf - zb), (96, 100, 90) if i % 2 == 0 else (82, 86, 78))
        m.box((0, y1 - 2, zf - 3), (606, 6, 8), (60, 64, 58))
    for sx in (-1, 1):
        for k in range(8):
            z = 160 - k * 40; y = 28 + (160 - z) / 340 * 260 + 40
            m.box((sx * 292, y + 20, z), (6, 80, 6), IRON)
        m.box((sx * 292, 140, -10), (10, 8, 360), IRON, rot(pitch=-37))
        m.box((sx * 292, 286, -110), (14, 80, 14), (150, 150, 140))
    for sx in (-1, 1):
        pts = [(sx * 292, 300 - 15 * math.sin(t), 160 - t * 40) for t in range(9)]
        vine_strand(m, [(p[0], 40 + t * 28 + 18 * math.sin(t * 1.3), p[2]) for t, p in enumerate(pts)], r=5)
    return m

# ---- v0.2.6 grand hall: two-storey atrium pieces ---------------------------------------------------------
MARB = (176, 172, 162); MARB_D = (140, 136, 128); CARPET_R = (128, 22, 26); BLOODW = (104, 12, 16)

def stair_flight():
    """Straight flight, 500 wide, climbing 500 over 750 toward -z. Origin = centre of the foot. 14 steps,
    red runner, stone balustrades (handrail tilted along the slope)."""
    m = Mesh()
    N, W, RUN, RISE = 14, 500, 750.0, 500.0
    d = RUN / N; r = RISE / N
    for i in range(N):
        top = r * (i + 1); zc = -(i + 0.5) * d
        m.box((0, top / 2, zc), (W, top, d), MARB if i % 2 == 0 else MARB_D)
        zf = -i * d; zb = -(i + 1) * d
        m.quad((-180, top + 1.5, zf), (180, top + 1.5, zf), (180, top + 1.5, zb), (-180, top + 1.5, zb), CARPET_R, inside=(0, top / 2, zc))
        m.quad((-180, r * i, zf + 1.5), (180, r * i, zf + 1.5), (180, top, zf + 1.5), (-180, top, zf + 1.5), CARPET_R, inside=(0, top / 2, zc))
    ang = math.degrees(math.atan2(RISE, RUN)); L = math.hypot(RISE, RUN)
    for sx in (-1, 1):
        x = sx * 238
        m.box((x, RISE / 2 + 98, -RUN / 2), (16, 14, L), MARB, rot(pitch=-ang))
        m.box((x, RISE / 2 + 10, -RUN / 2), (16, 10, L), MARB_D, rot(pitch=-ang))
        for k in range(0, N + 1, 2):
            zk = -k * d; yk = r * k + 55
            m.box((x, yk + 18, zk - d * 0.5), (14, 90, 14), MARB)
        m.box((x, 30, 18), (30, 100, 30), MARB)                                 # newel post at the foot
        m.box((x, RISE + 60, -RUN + 12), (30, 110, 30), MARB)                  # newel post at the top
    return m

def balustrade():
    """250-long stone balcony rail along x, 100 high. Origin = centre of the base."""
    m = Mesh()
    m.box((0, 7, 0), (250, 14, 26), MARB_D)
    m.box((0, 97, 0), (250, 14, 30), MARB)
    for k in range(-5, 6):
        m.cyl((k * 21, 52, 0), 7, 76, MARB, n=6, r_top=5)
    for sx in (-1, 1):
        m.box((sx * 122, 52, 0), (12, 90, 24), MARB)
    return m

def hall_fountain():
    """Atrium fountain: octagonal basin of blood-red water, moss, a tall stone figure holding up a golden star."""
    m = Mesh()
    m.cyl((0, 50, 0), 300, 100, MARB, n=8, smooth=False)
    m.cyl((0, 108, 0), 312, 16, MARB_D, n=8, smooth=False)
    m.cyl((0, 98, 0), 276, 4, BLOODW, n=8, smooth=False)
    m.cyl((0, 170, 0), 52, 140, MARB, n=8, r_top=40)
    m.cyl((0, 250, 0), 150, 30, MARB_D, n=8, r_top=110, smooth=False)
    m.cyl((0, 268, 0), 130, 4, BLOODW, n=8, smooth=False)
    m.cyl((0, 310, 0), 46, 80, MARB_D, n=8)                                   # plinth
    # the statue: the game's own Mario model (actors/mario, idle pose) baked in flat stone grey, standing on the plinth
    import mario_statue
    sc = 0.62
    for (tri, col) in mario_statue.build():
        lum = 0.30 * col[0] + 0.59 * col[1] + 0.11 * col[2]
        g = int(min(232, 90 + 0.9 * lum)); gc = (g, g, g)
        P = [(p[0][0] * sc, p[0][1] * sc + 350, (p[0][2] - 40) * sc) for p in tri]
        m.tri(P[0], P[1], P[2], gc, normals=(tri[0][1], tri[1][1], tri[2][1]))
    pts = []
    for i in range(10):
        rr = 36 if i % 2 == 0 else 15; a = math.pi / 2 + i * math.pi / 5
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    m.prism(pts, 14, (240, 200, 40), c=(0, 790, 60))                                    # a golden star floating above his head
    for k in range(8):                                                                   # blood drips and moss
        a = k * math.pi / 4 + 0.2
        m.cyl((312 * math.cos(a), 78, 312 * math.sin(a)), 4, 50 + 14 * (k % 3), BLOODW, n=4)
        m.sphere((290 * math.cos(a + 0.4), 116, 290 * math.sin(a + 0.4)), 16, MOSS, nlat=3, nlon=6)
    return m


def table():
    """Dining table, 900 long (x) x 400 deep (z), top at y=160, with a candelabra and a cloth runner."""
    m = Mesh()
    CLOTH = (150, 140, 120)
    m.box((0, 150, 0), (900, 20, 400), WOOD)                       # top
    m.box((0, 141, 0), (860, 4, 360), WOOD_D)                      # apron shadow
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((sx * 410, 70, sz * 170), (34, 140, 34), WOOD_D)  # legs
    m.box((0, 162, 0), (300, 2, 220), CLOTH)                       # runner
    m.cyl((0, 170, 0), 16, 10, BRASS, n=8)                         # candelabra base
    m.cyl((0, 240, 0), 4, 130, BRASS, n=6)                         # stem
    for k in range(3):
        x = (k - 1) * 46
        m.cyl((x, 290, 0), 7, 40, (230, 220, 190), n=6)           # candles
        m.sphere((x, 316, 0), 6, (255, 170, 70), nlat=2, nlon=4)   # flames
    return m

def chair():
    """High-back dining chair. Origin at floor centre; sits facing +z, back rail on the -z side."""
    m = Mesh()
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((sx * 52, 42, sz * 50), (16, 84, 16), WOOD_D)  # legs
    m.box((0, 92, 0), (130, 14, 120), WOOD)                        # seat
    m.box((0, 160, -55), (130, 12, 12), WOOD_D)                    # back rails
    m.box((0, 210, -55), (130, 12, 12), WOOD_D)
    for sx in (-1, 1):
        m.box((sx * 52, 150, -55), (14, 130, 14), WOOD_D)           # back posts
    m.box((0, 260, -55), (140, 14, 16), WOOD)                      # crest rail
    return m

def desk():
    """Plain writing desk / side table, 340 long (x) x 220 deep (z), top at y=110, with one drawer.
    Used for the typewriter desk in every safe room plus the kitchen counter and library reading table."""
    m = Mesh()
    m.box((0, 100, 0), (340, 20, 220), WOOD)                        # top
    m.box((0, 91, 0), (300, 4, 180), WOOD_D)                        # apron shadow
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((sx * 150, 45, sz * 90), (22, 90, 22), WOOD_D)    # legs
    m.box((70, 68, 94), (90, 46, 18), WOOD_D)                       # drawer front
    m.box((70, 68, 104), (24, 10, 4), BRASS)                        # drawer pull
    return m

# ---- kitchen set (origin = floor centre of the BACK face; each piece projects +z, like the fireplace) ----
ENAMEL = (190, 182, 156); ENAMEL_D = (118, 112, 96); SLAB = (176, 166, 138); POTRUST = (112, 66, 40)
SHROOM_CAP = (166, 38, 38); SHROOM_STEM = (214, 200, 164); SHROOM_SPOT = (232, 226, 210)

def fridge():
    """Grimy two-door fridge, 150 wide x 130 deep x 330 tall."""
    m = Mesh()
    m.box((0, 165, 65), (150, 330, 130), ENAMEL)
    m.box((0, 215, 131), (150, 4, 4), ENAMEL_D)                    # door seam
    m.box((-56, 262, 137), (6, 62, 8), METAL_D); m.box((-56, 168, 137), (6, 72, 8), METAL_D)   # handles
    m.box((10, 36, 131), (96, 56, 2), ENAMEL_D)                    # grime smear
    m.box((0, 332, 65), (150, 4, 130), ENAMEL_D)
    return m

def stove():
    """Four-burner stove with oven, 190 wide x 130 deep x 90 tall (+ raised back)."""
    m = Mesh()
    m.box((0, 45, 65), (190, 90, 130), ENAMEL)
    m.box((0, 92, 65), (194, 6, 134), ENAMEL_D)                    # cooktop
    m.box((0, 130, 6), (190, 80, 12), ENAMEL)                      # back panel
    for (x, z) in ((-46, 42), (46, 42), (-46, 96), (46, 96)):
        m.cyl((x, 97, z), 24, 4, METAL_D, n=10)                    # burners
    for x in (-60, -20, 20, 60):
        m.cyl((x, 74, 132), 6, 8, METAL_D, n=6, R=rot(pitch=90))   # knobs
    m.box((0, 36, 132), (150, 46, 4), ENAMEL_D)                    # oven door
    m.box((0, 38, 135), (100, 26, 3), (24, 22, 20))                # oven window
    m.box((0, 62, 138), (120, 5, 6), METAL_D)                      # oven handle
    return m

def counter(sink=False):
    """Kitchen counter run, 500 wide x 130 deep x 100 tall; the sink variant has a basin and tap."""
    m = Mesh()
    m.box((0, 45, 65), (500, 90, 130), ENAMEL)
    m.box((0, 95, 65), (510, 10, 138), SLAB)                       # worktop
    for x in (-190, -65, 65, 190):
        m.box((x, 44, 131), (112, 74, 3), ENAMEL_D)                # cabinet doors
        m.box((x + 40, 62, 134), (6, 18, 4), METAL_D)
    if sink:
        m.box((0, 100, 78), (170, 4, 92), (40, 38, 34))            # basin
        m.cyl((0, 126, 22), 5, 52, METAL, n=6)                     # tap stem
        m.box((0, 150, 38), (6, 6, 40), METAL)                     # spout
    return m

def kpot():
    """Rusty cooking pot, ~44 tall. Origin = base centre."""
    m = Mesh()
    m.cyl((0, 22, 0), 26, 44, POTRUST, n=10)
    m.cyl((0, 44, 0), 22, 3, (30, 24, 20), n=10)                   # dark contents
    for sx in (-1, 1):
        m.box((sx * 29, 34, 0), (8, 5, 8), METAL_D)                # handles
    return m

def cup():
    """Stained mug, 18 tall."""
    m = Mesh()
    m.cyl((0, 9, 0), 7, 18, (210, 204, 188), n=8)
    m.box((9, 10, 0), (4, 9, 3), (210, 204, 188))
    return m

def mushroom():
    """Little Super-Mushroom-style fungus, ~60 tall."""
    m = Mesh()
    m.cyl((0, 14, 0), 10, 28, SHROOM_STEM, n=8)
    m.sphere((0, 34, 0), 30, SHROOM_CAP, nlat=4, nlon=8, squash=(1, 0.7, 1))
    for (x, y, z) in ((12, 52, 8), (-14, 48, 6), (0, 50, -16)):
        m.sphere((x, y, z), 7, SHROOM_SPOT, nlat=2, nlon=4)
    return m

def mushroom_big():
    """Giant spotted mushroom growing out of the floor, ~390 tall, with two small ones at its base."""
    m = Mesh()
    m.cyl((0, 160, 0), 24, 320, SHROOM_STEM, n=8, r_top=15)
    m.sphere((0, 330, 0), 120, SHROOM_CAP, nlat=5, nlon=10, squash=(1, 0.5, 1))
    for (x, y, z) in ((48, 378, 30), (-62, 366, -22), (8, 388, -62), (-8, 390, 46), (70, 352, -36)):
        m.sphere((x, y, z), 20, SHROOM_SPOT, nlat=2, nlon=5, squash=(1, 0.5, 1))
    for (x, z, h) in ((78, 44, 44), (-70, 52, 34)):
        m.cyl((x, h / 2, z), 8, h, SHROOM_STEM, n=6)
        m.sphere((x, h + 6, z), 24, SHROOM_CAP, nlat=3, nlon=6, squash=(1, 0.6, 1))
    return m

def fireplace():
    """Stone fireplace against a wall. Origin at floor centre of the back; projects +z (150 deep), 420 wide, mantel ~300."""
    m = Mesh()
    FIRE = (255, 140, 40); EMBER = (200, 70, 20); SOOT = (22, 16, 14)
    m.box((0, 140, 75), (420, 280, 150), STONE_D)                  # body
    m.box((0, 150, 152), (300, 300, 4), STONE)                     # front face
    for sx in (-1, 1):
        m.box((sx * 165, 150, 158), (70, 300, 16), STONE)          # pillars
    m.box((0, 303, 176), (460, 16, 60), STONE)                     # mantel shelf
    m.box((0, 6, 90), (460, 12, 180), STONE_D)                     # hearth
    m.box((0, 104, 156), (230, 170, 6), SOOT)                      # firebox opening
    m.box((0, 30, 142), (150, 22, 22), WOOD_D); m.box((0, 30, 118), (130, 20, 20), WOOD)   # logs
    m.cyl((0, 80, 130), 38, 90, FIRE, n=6, r_top=12)               # flames
    m.cyl((-30, 70, 130), 22, 60, EMBER, n=6, r_top=6)
    for sx in (-1, 1):
        m.cyl((sx * 120, 330, 176), 9, 44, (230, 220, 190), n=6)   # mantel candles
        m.sphere((sx * 120, 356, 176), 6, (255, 170, 70), nlat=2, nlon=4)
    return m

def toad():
    """Toad, hurt: pale skin smeared with blood, a ragged dark-red cap, blood running from the mouth. ~240 tall."""
    import random
    rnd = random.Random(7)
    m = Mesh()
    SKIN = (168, 150, 128); SKIN_D = (120, 100, 88); BLOOD = (120, 10, 12); BLOOD_D = (62, 6, 8)
    CAP = (150, 22, 24); CAP_D = (88, 12, 14); EYE = (18, 10, 10); SHOE = (60, 30, 26)
    for sx in (-1, 1):                                              # legs and shoes
        m.cyl((sx * 26, 30, 0), 24, 60, SKIN_D, n=8)
        m.box((sx * 26, 6, 6), (46, 12, 60), SHOE)
    m.cyl((0, 118, 0), 50, 116, SKIN, n=9)                          # torso
    m.cyl((0, 62, 0), 52, 20, (60, 34, 30), n=9)                    # waistband
    for sx in (-1, 1):                                              # arms and hands
        m.cyl((sx * 70, 128, 0), 15, 90, SKIN, n=6, R=rot(roll=-sx * 18))
        m.sphere((sx * 84, 78, 0), 17, SKIN_D, nlat=3, nlon=5)
    for (x, y, z, s) in [(30, 150, 46, 20), (-38, 110, 42, 14), (8, 90, 50, 16), (-70, 80, 4, 12), (62, 140, 8, 12)]:
        m.sphere((x, y, z), s, BLOOD, nlat=3, nlon=5, squash=(1, 1.4, 0.3))   # blood smears
    m.sphere((0, 190, 0), 58, SKIN, nlat=5, nlon=8)                 # head
    m.sphere((0, 232, 0), 84, CAP, nlat=5, nlon=8, squash=(1, 0.5, 1))   # cap
    for k in range(14):                                             # ragged, torn rim of the cap
        a = k * 2 * math.pi / 14 + rnd.uniform(-0.1, 0.1)
        r = 78 + rnd.uniform(-6, 10)
        m.box((r * math.cos(a), 204 + rnd.uniform(-6, 6), r * math.sin(a)),
              (rnd.uniform(14, 26), rnd.uniform(14, 30), rnd.uniform(10, 18)), CAP_D if k % 3 else BLOOD_D)
    for (x, y, z, s) in [(-40, 250, 30, 12), (30, 262, 46, 9), (-10, 220, 74, 10)]:
        m.sphere((x, y, z), s, BLOOD_D, nlat=3, nlon=5)              # dark blood spots on the cap
    for sx in (-1, 1):                                              # eyes and cheeks
        m.sphere((sx * 22, 200, 54), 9, EYE, nlat=3, nlon=5)
        m.sphere((sx * 34, 180, 50), 10, BLOOD, nlat=3, nlon=5)
    m.box((0, 176, 56), (34, 8, 4), EYE)                            # mouth
    m.box((0, 158, 58), (6, 34, 3), BLOOD)                          # blood from the mouth
    return m

def vine():
    """Hanging thorn vine for walls: ~420 tall, origin at the bottom centre, wanders in x with a little z."""
    m = Mesh()
    pts = [(40 * math.sin(t * 0.8) + 12 * math.sin(t * 2.1), t * 52, 6 + 4 * math.sin(t * 1.7)) for t in range(9)]
    vine_strand(m, pts, r=6)
    pts2 = [(-30 + 36 * math.sin(t * 0.7 + 1), 60 + t * 44, 8) for t in range(7)]
    vine_strand(m, pts2, r=4)
    for (x, y) in ((pts[3][0], pts[3][1]), (pts[6][0], pts[6][1])):
        m.sphere((x, y, 10), 16, MOSS, nlat=3, nlon=6, squash=(1, 0.5, 0.6))
    return m


MODELS = {
    'item_herb_g': lambda: herb(None),
    'item_herb_r': lambda: herb('r'),
    'item_herb_b': lambda: herb('b'),
    'item_key': lambda: key_model('star'),
    'item_key2': lambda: key_model('moon'),
    'item_key3': lambda: key_model('sun'),
    'item_ribbon': ribbon,
    'item_file': file_model,
    'item_box': chest,
    'item_typewriter': typewriter,
    'item_gun': pistol,
    'item_ammo': ammo_box,
    'held_gun': pistol_held,
    'item_console': console,
    'item_luigi': luigi,
    'prop_fountain': fountain,
    'prop_chandelier': chandelier,
    'prop_lamp': lamp,
    'prop_pot': pot,
    'prop_clock': clock,
    'prop_stairs': stairs,
    'prop_stair_flight': stair_flight,
    'prop_balustrade': balustrade,
    'prop_hall_fountain': hall_fountain,
    'prop_toad': toad,
    'prop_vine': vine,
    'prop_table': table,
    'prop_desk': desk,
    'prop_fridge': fridge,
    'prop_stove': stove,
    'prop_counter': counter,
    'prop_sink': lambda: counter(sink=True),
    'prop_kpot': kpot,
    'prop_cup': cup,
    'prop_mushroom': mushroom,
    'prop_mushroom_big': mushroom_big,
    'prop_chair': chair,
    'prop_fireplace': fireplace,
}

def _sb(v):
    return int(round(max(-127.0, min(127.0, v * 127.0)))) & 0xFF

def emit_model(name, mesh):
    """Returns C source (Vtx arrays and a Gfx list `mansion_dl_<name>`)."""
    groups = {}
    for t in mesh.tris:
        groups.setdefault(t[6], []).append(t)
    out = []; body = []
    for gi, (col, tris) in enumerate(groups.items()):
        arr = 'mansion_vtx_%s_%d' % (name, gi)
        out.append('static const Vtx %s[] = {\n' % arr)
        for (p0, p1, p2, n0, n1, n2, _) in tris:
            for (p, n) in ((p0, n0), (p1, n1), (p2, n2)):
                out.append('    {{{%6d, %6d, %6d}, 0, {0, 0}, {0x%02x, 0x%02x, 0x%02x, 0xff}}},\n'
                           % (round(p[0]), round(p[1]), round(p[2]), _sb(n[0]), _sb(n[1]), _sb(n[2])))
        out.append('};\n\n')
        r, g, b = col
        # same format tools/fixlights.py produces for converted assets: LIGHT_1 = diffuse, LIGHT_2 = ambient
        dif = (min(255, int(r*0.80)) << 24) | (min(255, int(g*0.80)) << 16) | (min(255, int(b*0.80)) << 8) | 0xFF
        amb = (int(r*0.42) << 24) | (int(g*0.42) << 16) | (int(b*0.42) << 8) | 0xFF
        body.append('    gsSPLightColor(LIGHT_1, 0x%08x),\n    gsSPLightColor(LIGHT_2, 0x%08x),\n' % (dif, amb))
        n = len(tris); k = 0
        while k < n:
            m = min(10, n - k)
            body.append('    gsSPVertex(&%s[%d], %d, 0),\n' % (arr, k*3, m*3))
            for c in range(0, m - 1, 2):
                body.append('    gsSP2Triangles(%d, %d, %d, 0x0, %d, %d, %d, 0x0),\n' % (c*3, c*3+1, c*3+2, c*3+3, c*3+4, c*3+5))
            if m % 2: body.append('    gsSP1Triangle(%d, %d, %d, 0x0),\n' % ((m-1)*3, (m-1)*3+1, (m-1)*3+2))
            k += m
    out.append('const Gfx mansion_dl_%s[] = {\n' % name)
    out.append('    gsDPPipeSync(),\n    gsDPSetCombineMode(G_CC_SHADE, G_CC_SHADE),\n'
               '    gsSPTexture(0xFFFF, 0xFFFF, 0, G_TX_RENDERTILE, G_OFF),\n    gsSPSetGeometryMode(G_LIGHTING),\n')
    out += body
    out.append('    gsSPEndDisplayList(),\n};\n\n')
    return ''.join(out)

def bounds(mesh):
    xs = [p[i] for t in mesh.tris for p in t[:3] for i in (0,)]
    ys = [p[1] for t in mesh.tris for p in t[:3]]
    zs = [p[2] for t in mesh.tris for p in t[:3]]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

if __name__ == '__main__':
    for k, f in MODELS.items():
        m = f(); print(k, len(m.tris), 'tris', ['%.0f' % v for v in bounds(m)])
