"""Mario EVIL cinematics: scripted camera angles, dialogue boxes and prop movement.

A cinematic plays once per session when Mario walks into its trigger zone (x0, z0, x1, z1 in world units).
Steps run in order; Mario's controls are locked while one plays.

  cam(pos, focus, fov=50, frames=0)   move the camera to a new angle (frames=0 is a hard cut)
  cam(pos, follow=100, fov, frames)   stationary camera at pos that keeps looking at Mario (100 = look height)
  text(speaker, body)                 dialogue box: typewriter text, A reveals / advances. Body is wrapped
                                      automatically into pages of two lines. speaker=None for narration.
  move(actor, pos, frames=60)         slide an actor (a prop placed with kind='actor') to (x, y, z)
  rot(actor, yaw, frames=0)           turn an actor (yaw 0x4000 = +x, 0x8000 = -z, 0xC000 = -x)
  walk(pos, frames=120)               Mario walks (scripted; the physics stay on)
  together(a, b, ...)                 run steps at the same time, e.g. a walk while the camera moves
  wait(frames)                        hold for a while
  sfx(name)                           play a sound macro, e.g. 'SOUND_GENERAL_OPEN_WOOD_DOOR'

Actors are declared in mansion_map.py like any other object:
  dict(kind='actor', actor=0, model='pot', pos=(x, z), y=0, yaw=0)
The cinematics themselves live in mario_evil/cinematics.json (edit them with the Cinematic Editor and
send the exported file back); this file turns that JSON into steps for the generator.
Build with `python3 mario_evil/gen_level.py` (writes src/game/mansion_cine_data.inc.h).
"""
import json, os, textwrap

WRAP = 46   # characters per dialogue line

def cam(pos, focus=(0, 0, 0), fov=50, frames=0, follow=None):
    # follow = look height above Mario's feet (None = look at the fixed focus point)
    return ('cam', tuple(pos), tuple(focus), fov, frames, follow)
def move(actor, pos, frames=60):        return ('move', actor, tuple(pos), frames)
def rot(actor, yaw, frames=0):          return ('rot', actor, yaw, frames)
def walk(pos, frames=120):              return ('walk', tuple(pos), frames)   # Mario walks to (x, y, z) at a steady pace
def together(*steps):
    """Run steps at the same time: the first starts now, the rest start with it. The group ends when all are done.
    Only camera, move, rot, walk, wait and sfx may be grouped (no text)."""
    return [steps[0]] + [('par', s) for s in steps[1:]]
def wait(frames):                       return ('wait', frames)
def sfx(name):                          return ('sfx', name)

def text(speaker, body):
    """One or more dialogue pages (a list; the caller's steps list is flattened)."""
    lines = textwrap.wrap(body, WRAP)
    pages = [lines[i:i + 2] for i in range(0, len(lines), 2)]
    return [('text', speaker, p[0], p[1] if len(p) > 1 else '') for p in pages]


def _step(d):
    op = d['op']
    if op == 'cam':
        if d.get('follow'):
            return cam(d['pos'], (0, d.get('height', 100), 0), d.get('fov', 50), d.get('frames', 0), follow=d.get('height', 100))
        return cam(d['pos'], d['focus'], d.get('fov', 50), d.get('frames', 0))
    if op == 'walk':     return walk(d['pos'], d.get('frames', 120))
    if op == 'wait':     return wait(d.get('frames', 20))
    if op == 'sfx':      return sfx(d['name'])
    if op == 'move':     return move(d['actor'], d['pos'], d.get('frames', 60))
    if op == 'rot':      return rot(d['actor'], d['yaw'], d.get('frames', 0))
    if op == 'text':     return text(d.get('speaker'), d['body'])
    if op == 'together': return together(*[_step(x) for x in d['steps']])
    raise ValueError('unknown cinematic step op: %r' % op)

def load(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cinematics.json')
    out = []
    for c in json.load(open(path)):
        t = c['trigger']
        e = dict(name=c['name'], steps=[_step(d) for d in c['steps']])
        if t['type'] == 'talk':
            e['talk'] = (t['actor'], t['radius']); e['once'] = False
        else:
            e['zone'] = tuple(t['rect'])
        out.append(e)
    return out

CINES = load()
