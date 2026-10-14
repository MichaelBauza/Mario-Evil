"""Mario EVIL -- Tier 1 map definition (Main Hall, Dining Room, North Corridor, Save Room, West Corridor)."""

ITEM_IDS = {'herb_g': 1, 'herb_r': 2, 'herb_b': 3, 'ribbon': 4, 'key': 5, 'gun': 6}
FILES = {1: "Peach's Letter", 2: "Toad Gardener's Diary", 3: "Researcher Toad's Letter"}


def cams_along_x(r, ya=0.86, inset=200, fov=52, front='N'):
    x0, z0, x1, z1, h = r['x0'], r['z0'], r['x1'], r['z1'], r['h']
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    zA = z0 + inset if front == 'N' else z1 - inset
    zB = z1 - inset if front == 'N' else z0 + inset
    return [
        dict(pos=(x1 - inset, int(h * ya), zA), look=(x0 + int((x1 - x0) * 0.32), 90, cz), zone=(x0, z0, cx, z1), fov=fov),
        dict(pos=(x0 + inset, int(h * ya), zB), look=(x1 - int((x1 - x0) * 0.32), 90, cz), zone=(cx, z0, x1, z1), fov=fov),
    ]

def room(id, name, x0, z0, x1, z1, h, **kw):
    r = dict(id=id, name=name, x0=x0, z0=z0, x1=x1, z1=z1, h=h)
    r.update(kw)
    return r

ROOMS = []

# ---- Main Hall -------------------------------------------------------------
hall = room('hall', 'Main Hall', -4600, -900, -2400, 900, 850, floor='mans_floor',
            carpets=[(-4500, -190, -2500, 190)],
            boxes=[dict(x0=-3800, z0=-900, x1=-3200, z1=-560, y1=260, side='mans_marble', top='mans_carpet'),
                   dict(x0=-4000, z0=-850, x1=-3880, z1=-730, y1=800, side='mans_marble', top='mans_marble'),
                   dict(x0=-3000, z0=730, x1=-2880, z1=850, y1=800, side='mans_marble', top='mans_marble')],
            lights=[(-3500, 650, 0, 0.55, 1000), (-4350, 500, -650, 0.30, 600), (-2650, 500, 650, 0.30, 600)],
            objs=[dict(kind='herb_g', pos=(-2750, -650)), dict(kind='file', file=1, pos=(-4300, 650))])
hall['cams'] = cams_along_x(hall, front='N')
ROOMS.append(hall)

# ---- Dining Room -----------------------------------------------------------
dining = room('dining', 'Dining Room', -1000, -800, 1000, 800, 800, floor='mans_floor',
              carpets=[(-700, -350, 700, 350)],
              boxes=[dict(x0=-450, z0=-200, x1=450, z1=200, y1=150, side='mans_wood', top='mans_wood'),
                     dict(x0=-950, z0=-760, x1=-830, z1=-640, y1=760, side='mans_marble', top='mans_marble'),
                     dict(x0=830, z0=640, x1=950, z1=760, y1=760, side='mans_marble', top='mans_marble')],
              lights=[(0, 600, 0, 0.60, 900), (-800, 450, 600, 0.25, 500)],
              objs=[dict(kind='zombie', pos=(450, 450), yaw=0x8000), dict(kind='herb_r', pos=(-800, 600))])
dining['cams'] = cams_along_x(dining, front='N')
ROOMS.append(dining)

# ---- North Corridor --------------------------------------------------------
cn = room('corr_n', 'North Corridor', -1200, -3250, 1200, -2750, 700, floor='mans_stone', wainscot=300,
          lights=[(-700, 520, -3000, 0.45, 700), (700, 520, -3000, 0.45, 700)],
          objs=[dict(kind='zombie', pos=(500, -3000), yaw=0xC000), dict(kind='file', file=2, pos=(-1000, -3000))])
cn['cams'] = cams_along_x(cn, ya=0.9, inset=120, fov=60, front='S')
ROOMS.append(cn)

# ---- Save Room -------------------------------------------------------------
save = room('save', 'Save Room', 3000, -3500, 4000, -2500, 700, floor='mans_floor',
            boxes=[dict(x0=3550, z0=-2850, x1=3850, z1=-2650, y1=110, side='mans_wood', top='mans_wood')],
            lights=[(3500, 520, -3000, 0.85, 800)],
            objs=[dict(kind='typewriter', pos=(3700, -2750), y=110), dict(kind='box', pos=(3250, -3350)),
                  dict(kind='ribbon', pos=(3800, -3300)), dict(kind='key', pos=(3300, -2650), keyid=1)])
save['cams'] = [dict(pos=(3150, 600, -2650), look=(3550, 60, -3050), zone=(3000, -3500, 4000, -2500), fov=58)]
ROOMS.append(save)

# ---- West Corridor ---------------------------------------------------------
cw = room('corr_w', 'West Corridor', -7500, -250, -5800, 250, 700, floor='mans_stone', wainscot=300,
          lights=[(-6200, 520, 0, 0.45, 600), (-7100, 520, 0, 0.45, 600)],
          objs=[dict(kind='zombie', pos=(-6600, 0), yaw=0x4000), dict(kind='file', file=3, pos=(-7300, 0)),
                dict(kind='herb_b', pos=(-7300, 150))])
cw['cams'] = cams_along_x(cw, ya=0.9, inset=120, fov=60, front='N')
ROOMS.append(cw)

DOORS = [
    dict(id='hall_e',  room='hall',   wall='E', at=0,     to='dining_w'),
    dict(id='dining_w', room='dining', wall='W', at=0,     to='hall_e'),
    dict(id='dining_n', room='dining', wall='N', at=0,     to='corrn_s'),
    dict(id='corrn_s', room='corr_n', wall='S', at=0,     to='dining_n'),
    dict(id='corrn_e', room='corr_n', wall='E', at=-3000, to='save_w'),
    dict(id='save_w',  room='save',   wall='W', at=-3000, to='corrn_e'),
    dict(id='hall_w',  room='hall',   wall='W', at=0,     to='corrw_e', key=1),
    dict(id='corrw_e', room='corr_w', wall='E', at=0,     to='hall_w'),
]

START = (-2800, 0, 0xC000)   # (x, z, yaw): inside the hall facing west
