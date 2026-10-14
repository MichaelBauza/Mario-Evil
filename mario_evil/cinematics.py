"""Mario EVIL cinematics: scripted camera angles, dialogue boxes and prop movement.

A cinematic plays once per session when Mario walks into its trigger zone (x0, z0, x1, z1 in world units).
Steps run in order; Mario's controls are locked while one plays.

  cam(pos, focus, fov=50, frames=0)   move the camera to a new angle (frames=0 is a hard cut)
  text(speaker, body)                 dialogue box: typewriter text, A reveals / advances. Body is wrapped
                                      automatically into pages of two lines. speaker=None for narration.
  move(actor, pos, frames=60)         slide an actor (a prop placed with kind='actor') to (x, y, z)
  rot(actor, yaw, frames=0)           turn an actor (yaw 0x4000 = +x, 0x8000 = -z, 0xC000 = -x)
  wait(frames)                        hold for a while
  sfx(name)                           play a sound macro, e.g. 'SOUND_GENERAL_OPEN_WOOD_DOOR'

Actors are declared in mansion_map.py like any other object:
  dict(kind='actor', actor=0, model='pot', pos=(x, z), y=0, yaw=0)
Build with `python3 mario_evil/gen_level.py` (writes src/game/mansion_cine_data.inc.h).
"""
import textwrap

WRAP = 36   # characters per dialogue line

def cam(pos, focus, fov=50, frames=0):  return ('cam', tuple(pos), tuple(focus), fov, frames)
def move(actor, pos, frames=60):        return ('move', actor, tuple(pos), frames)
def rot(actor, yaw, frames=0):          return ('rot', actor, yaw, frames)
def wait(frames):                       return ('wait', frames)
def sfx(name):                          return ('sfx', name)

def text(speaker, body):
    """One or more dialogue pages (a list; the caller's steps list is flattened)."""
    lines = textwrap.wrap(body, WRAP)
    pages = [lines[i:i + 2] for i in range(0, len(lines), 2)]
    return [('text', speaker, p[0], p[1] if len(p) > 1 else '') for p in pages]

CINES = [
    # Intro: plays once, as soon as the title screen is dismissed and Mario is in the hall.
    dict(name='intro_hall', zone=(-3000, -300, -2600, 300), steps=[
        cam((-4000, 320, 500), (-2800, 80, 0), fov=50),
        wait(30),
        text('MARIO', "Let's-a go!"),
        cam((-3300, 220, 380), (-2800, 80, 0), fov=45, frames=120),
        wait(30),
    ]),
    dict(name='dining_fire', zone=(-300, 560, 300, 720), steps=[
        cam((0, 330, -120), (0, 200, 740), fov=50),
        text('MARIO', 'The fire is still warm. Someone was dining here not long ago.'),
        wait(20),
        move(0, (-600, 0, -420), frames=120),
        rot(0, 0x2000, frames=40),
        text(None, 'Something knocked that pot across the floor.'),
        cam((-500, 300, -700), (0, 150, 640), fov=50, frames=150),
        text(None, 'Somewhere above you, a door creaks open.'),
    ]),
]
