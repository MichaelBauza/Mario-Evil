"""Rebuild cine_editor.html (the Cinematic Editor page) from the template, the map's rooms and cinematics.json.
Run:  python3 mario_evil/editor/gen_editor.py   -- then publish cine_editor.html as an Artifact."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import mansion_map as M
rooms = [dict(id=r['id'], name=r['name'], rect=[r['x0'], r['z0'], r['x1'], r['z1']]) for r in M.ROOMS]
actors = [dict(actor=1, model='toad', pos=[-3000, 330])]   # actors declared with kind='actor' in mansion_map.py
data = dict(rooms=rooms, actors=actors, cines=json.load(open(os.path.join(ROOT, 'cinematics.json'))))
src = open(os.path.join(HERE, 'cine_editor.template.html')).read().replace('/*DATA*/null', json.dumps(data))
open(os.path.join(HERE, 'cine_editor.html'), 'w').write(src)
print('wrote cine_editor.html', len(src))
