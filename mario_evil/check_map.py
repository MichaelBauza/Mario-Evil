#!/usr/bin/env python3
"""Sanity checks for mansion_map.py: bounds, room overlap, items in props, door placement/pairing."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mansion_map import ROOMS, DOORS, MAPRECTS
R = {r['id']: r for r in ROOMS}
bad = 0
for i, a in enumerate(ROOMS):
    for k in ('x0', 'x1', 'z0', 'z1'):
        if abs(a[k]) > 8000: print('BOUNDS', a['id'], k, a[k]); bad += 1
    for b in ROOMS[i+1:]:
        if a['x0'] < b['x1'] and b['x0'] < a['x1'] and a['z0'] < b['z1'] and b['z0'] < a['z1']:
            print('OVERLAP', a['id'], b['id']); bad += 1
def in_box(r, x, z, m):
    return any(p['x0']-m < x < p['x1']+m and p['z0']-m < z < p['z1']+m for p in r.get('boxes', []))
for r in ROOMS:
    for o in r.get('objs', []):
        if o['kind'] == 'prop': continue
        x, z = o['pos']
        if not (r['x0']+60 < x < r['x1']-60 and r['z0']+60 < z < r['z1']-60): print('OBJ OUT', r['id'], o); bad += 1
        if o['kind'] == 'prop': continue
        if o.get('y', 0) == 0 and o['kind'] != 'box' and in_box(r, x, z, 60): print('OBJ IN PROP', r['id'], o); bad += 1
by = {d['id']: d for d in DOORS}
for d in DOORS:
    if 'virtual' in d:
        r = R[d['room']]; cx, cz = d['virtual']; n = d['n']
        sx, sz = cx+n[0]*210, cz+n[1]*210
        if in_box(r, sx, sz, 90): print('ARRIVAL IN PROP', d['id']); bad += 1
        if d['to'] not in by or by[d['to']]['to'] != d['id']: print('UNPAIRED', d['id']); bad += 1
        continue
    r = R[d['room']]; w = d['wall']; at = d['at']
    if w in 'NS':
        lo, hi = r['x0'], r['x1']; n = (0, 1 if w == 'N' else -1); cx, cz = at, (r['z0'] if w == 'N' else r['z1'])
    else:
        lo, hi = r['z0'], r['z1']; n = (1 if w == 'W' else -1, 0); cx, cz = (r['x0'] if w == 'W' else r['x1']), at
    if not (lo+220 < at < hi-220): print('DOOR NEAR CORNER', d['id']); bad += 1
    sx, sz = cx+n[0]*210, cz+n[1]*210
    if in_box(r, sx, sz, 90): print('ARRIVAL IN PROP', d['id']); bad += 1
    for o in r.get('objs', []):
        if o['kind'] == 'prop': continue
        ox, oz = o['pos']
        if (ox-sx)**2 + (oz-sz)**2 < 200**2: print('ITEM NEAR ARRIVAL', d['id'], o['kind']); bad += 1
    if d['to'] not in by or by[d['to']]['to'] != d['id']: print('UNPAIRED', d['id']); bad += 1
    for e in DOORS:
        if e is not d and 'wall' in e and e['room'] == d['room'] and e['wall'] == w and abs(e['at']-at) < 500: print('DOORS CLOSE', d['id'], e['id']); bad += 1
ids = [r['id'] for r in ROOMS]
for i in ids:
    if i not in MAPRECTS: print('NO MAPRECT', i); bad += 1
for i, a in enumerate(ids):
    for b in ids[i+1:]:
        if a in MAPRECTS and b in MAPRECTS:
            A, B = MAPRECTS[a], MAPRECTS[b]
            if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]: print('MAPRECT OVERLAP', a, b); bad += 1
print('map problems:', bad)
sys.exit(1 if bad else 0)
