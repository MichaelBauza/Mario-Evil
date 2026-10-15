"""Bakes the game's own Mario model (actors/mario) into a static, flat-grey statue mesh: reads the display lists
and vertex data from the repo, poses the joints with frame 0 of Mario's idle animation and emits Mesh triangles."""
import math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def _sin(a): return math.sin(a * math.pi / 32768.0)
def _cos(a): return math.cos(a * math.pi / 32768.0)

def _mat(trans, rot):
    sx, cx, sy, cy, sz, cz = _sin(rot[0]), _cos(rot[0]), _sin(rot[1]), _cos(rot[1]), _sin(rot[2]), _cos(rot[2])
    return [[cy*cz, cy*sz, -sy, 0],
            [sx*cz*sy - cx*sz, sx*sz*sy + cx*cz, sx*cy, 0],
            [cx*cz*sy + sx*sz, cx*sz*sy - sx*cz, cx*cy, 0],
            [trans[0], trans[1], trans[2], 1]]

def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def _xf(p, M): return tuple(sum(p[i] * M[i][j] for i in range(3)) + M[3][j] for j in range(3))
def _xn(n, M):
    v = tuple(sum(n[i] * M[i][j] for i in range(3)) for j in range(3))
    l = math.sqrt(sum(c * c for c in v)) or 1.0
    return (v[0] / l, v[1] / l, v[2] / l)

class _Model:
    def __init__(self):
        src = open(os.path.join(ROOT, 'actors/mario/model.inc.c')).read()
        self.vtx = {}
        for m in re.finditer(r'static const Vtx (\w+)\[\] = \{(.*?)\n\};', src, re.S):
            vs = []
            for v in re.finditer(r'\{\{\{\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\},\s*\d+,\s*\{\s*-?\d+,\s*-?\d+\},\s*\{0x(\w\w), 0x(\w\w), 0x(\w\w), 0x\w\w\}', m.group(2)):
                sb = lambda h: (int(h, 16) ^ 0x80) - 0x80
                vs.append(((int(v.group(1)), int(v.group(2)), int(v.group(3))), (sb(v.group(4)) / 127.0, sb(v.group(5)) / 127.0, sb(v.group(6)) / 127.0)))
            self.vtx[m.group(1)] = vs
        self.dl = {}
        for m in re.finditer(r'\nconst Gfx (\w+)\[\] = \{(.*?)\n\};', src, re.S):
            self.dl[m.group(1)] = m.group(2)

    def draw(self, name, M, out, st):
        cur = []
        for line in self.dl[name].split('\n'):
            line = line.strip()
            m = re.match(r'gsSPLightColor\(LIGHT_1, 0x(\w{6})ff\)', line)
            if m:
                c = int(m.group(1), 16); st['col'] = ((c >> 16) & 255, (c >> 8) & 255, c & 255); continue
            m = re.match(r'gsSPDisplayList\((\w+)\)', line)
            if m: self.draw(m.group(1), M, out, st); continue
            m = re.match(r'gsSPVertex\((\w+), (\d+), (\d+)\)', line)
            if m:
                cur = self.vtx[m.group(1)][:int(m.group(2))]; continue
            tris = []
            m = re.match(r'gsSP2Triangles\(\s*(\d+),\s*(\d+),\s*(\d+),\s*\w+,\s*(\d+),\s*(\d+),\s*(\d+),', line)
            if m: tris = [tuple(map(int, m.groups()[:3])), tuple(map(int, m.groups()[3:]))]
            m = re.match(r'gsSP1Triangle\(\s*(\d+),\s*(\d+),\s*(\d+),', line)
            if m: tris = [tuple(map(int, m.groups()))]
            for t in tris:
                out.append(([(_xf(cur[i][0], M), _xn(cur[i][1], M)) for i in t], st['col']))

def _anim_frame0(name='anim_C5'):
    src = open(os.path.join(ROOT, 'assets/anims/%s.inc.c' % name)).read()
    idx = [int(x, 16) for x in re.findall(r'0x[0-9A-Fa-f]+', re.search(r'%s_indices\[\] = \{(.*?)\};' % name, src, re.S).group(1))]
    vals = [int(x, 16) for x in re.findall(r'0x[0-9A-Fa-f]+', re.search(r'%s_values\[\] = \{(.*?)\};' % name, src, re.S).group(1))]
    s16 = lambda v: v - 65536 if v >= 32768 else v
    pairs = [(idx[i], idx[i + 1]) for i in range(0, len(idx), 2)]
    return [s16(vals[off]) for (mx, off) in pairs]

# (offset, draw list names) tree in joint order; see actors/mario/geo.inc.c mario_geo_body
def build(rot_over=None, scale=3.0):
    md = _Model(); a = _anim_frame0()
    rot_over = rot_over or {}
    def R(j):
        r = [a[6 + 3 * (j - 1) + k] if j > 0 else a[3 + k] for k in range(3)]
        for k, v in rot_over.get(j, {}).items(): r[k] += v
        return r
    # joint -> (offset, parent, [dls])
    J = {
        0: ((0, 0, 0), None, []),
        1: ((0, 0, 0), 0, ['mario_butt']),
        2: ((68, 0, 0), 1, ['mario_torso']),
        3: ((87, 0, 0), 2, ['mario_cap_on_eyes_front']),
        4: ((67, -10, 79), 2, []),
        5: ((0, 0, 0), 4, ['mario_left_arm']),
        6: ((65, 0, 0), 5, ['mario_left_forearm_shared_dl']),
        7: ((60, 0, 0), 6, ['mario_left_hand_closed']),
        8: ((68, -10, -79), 2, []),
        9: ((0, 0, 0), 8, ['mario_right_arm']),
        10: ((65, 0, 0), 9, ['mario_right_forearm_shared_dl']),
        11: ((60, 0, 0), 10, ['mario_right_hand_closed']),
        12: ((13, -8, 42), 1, []),
        13: ((0, 0, 0), 12, ['mario_left_thigh']),
        14: ((89, 0, 0), 13, ['mario_left_leg_shared_dl']),
        15: ((67, 0, 0), 14, ['mario_left_foot']),
        16: ((13, -8, -42), 1, []),
        17: ((0, 0, 0), 16, ['mario_right_thigh']),
        18: ((89, 0, 0), 17, ['mario_right_leg_shared_dl']),
        19: ((67, 0, 0), 18, ['mario_right_foot']),
    }
    mats = {}
    out = []; st = {'col': (120, 120, 120)}
    for j in range(20):
        off, par, dls = J[j]
        tr = (a[0], a[1], a[2]) if j == 0 else off
        L = _mat(tr, R(j))
        mats[j] = _mul(L, mats[par]) if par is not None else L
        for d in dls: md.draw(d, mats[j], out, st)
    return out

if __name__ == '__main__':
    t = build()
    print(len(t), 'tris')
    xs = [p[0][0] for tri in t for p in tri[0]]; ys = [p[0][1] for tri in t for p in tri[0]]; zs = [p[0][2] for tri in t for p in tri[0]]
    print(min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
