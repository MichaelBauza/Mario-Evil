"""Mario EVIL -- map: Tier 2 (mansion) + Tier 3 (fountain stairwell, cellar, Kamek's lab, escape tunnel, dock)."""

ITEM_IDS = {'herb_g': 1, 'herb_r': 2, 'herb_b': 3, 'ribbon': 4, 'key': 5, 'gun': 6, 'ammo': 10}
FILES = {1: "Peach's Letter", 2: "Toad Gardener's Diary", 3: "Researcher Toad's Letter",
         4: "Kamek's Orders", 5: "Specimen 42 Report", 6: "Spore Containment Memo", 7: "Luigi's Journal",
         8: "Kamek's Lab Log", 9: "Self-Destruct Notice"}


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
            boxes=[dict(x0=3550, z0=-2850, x1=3850, z1=-2650, y1=110, side='mans_wood', top='mans_wood'),
                   dict(x0=3192, z0=-3383, x1=3308, z1=-3317, y1=60, hidden=True)],
            lights=[(3500, 520, -3000, 0.85, 800)],
            objs=[dict(kind='typewriter', pos=(3700, -2750), y=110, yaw=0x8000), dict(kind='box', pos=(3250, -3350), yaw=0),
                  dict(kind='ribbon', pos=(3800, -3300)), dict(kind='key', pos=(3750, -3050), keyid=1),
                  dict(kind='gun', pos=(3350, -3250)), dict(kind='ammo', pos=(3500, -3350), amount=15)])
save['cams'] = [dict(pos=(3150, 600, -2650), look=(3550, 60, -3050), zone=(3000, -3500, 4000, -2500), fov=58)]
ROOMS.append(save)

# ---- West Corridor ---------------------------------------------------------
cw = room('corr_w', 'West Corridor', -7500, -250, -5800, 250, 700, floor='mans_stone', wainscot=300,
          lights=[(-6200, 520, 0, 0.45, 600), (-7100, 520, 0, 0.45, 600)],
          objs=[dict(kind='zombie', pos=(-6600, 0), yaw=0x4000), dict(kind='file', file=3, pos=(-6900, -150)),
                dict(kind='herb_b', pos=(-6900, 150))])
cw['cams'] = cams_along_x(cw, ya=0.9, inset=120, fov=60, front='N')
ROOMS.append(cw)

# ---- Kitchen (east wing) ----------------------------------------------------
kitchen = room('kitchen', 'Kitchen', 1600, -800, 3400, 800, 700, floor='mans_stone', wainscot=300,
               boxes=[dict(x0=2300, z0=-150, x1=2700, z1=150, y1=110, side='mans_wood', top='mans_wood')],
               lights=[(2500, 520, 0, 0.55, 800), (3000, 450, 500, 0.25, 500)],
               objs=[dict(kind='zombie', pos=(2900, 450), yaw=0x8000), dict(kind='zombie', pos=(2000, -450), yaw=0x4000),
                     dict(kind='herb_g', pos=(1850, 600)), dict(kind='ammo', pos=(3250, 600), amount=12),
                     dict(kind='file', file=6, pos=(2500, 0), y=110)])
kitchen['cams'] = cams_along_x(kitchen, front='N')
ROOMS.append(kitchen)

# ---- Courtyard (open sky) ---------------------------------------------------
court = room('court', 'Courtyard', 1500, -2300, 6500, -1000, 900, floor='mans_grass', wall='mans_stone', panel='mans_stone',
             wainscot=0, sky=True, ambient=0.50,
             boxes=[dict(x0=3800, z0=-1850, x1=4200, z1=-1450, y1=120, side='mans_marble', top='mans_marble'),
                   dict(x0=3880, z0=-1450, x1=4120, z1=-1370, y1=14, side='mans_wood', top='mans_door')],
             lights=[(2500, 400, -1650, 0.25, 900), (5500, 400, -1650, 0.25, 900)],
             objs=[dict(kind='zombie', pos=(3000, -1400), yaw=0xC000), dict(kind='zombie', pos=(4800, -1900), yaw=0x4000),
                   dict(kind='zombie', pos=(5600, -1300), yaw=0x8000),
                   dict(kind='herb_g', pos=(2200, -2050)), dict(kind='ammo', pos=(2250, -1700), amount=10),
                   dict(kind='file', file=5, pos=(6100, -2000))])
court['cams'] = cams_along_x(court, ya=0.8, inset=250, fov=55, front='N')
ROOMS.append(court)

# ---- Guardhouse (second save point) -----------------------------------------
guard = room('guard', 'Guardhouse', 6900, -2100, 8000, -1000, 650, floor='mans_floor',
             boxes=[dict(x0=7450, z0=-2050, x1=7800, z1=-1850, y1=100, side='mans_wood', top='mans_wood'),
                    dict(x0=7067, z0=-1308, x1=7133, z1=-1192, y1=60, hidden=True)],
             lights=[(7450, 480, -1550, 0.80, 700)],
             objs=[dict(kind='typewriter', pos=(7700, -1950), y=100, yaw=0), dict(kind='box', pos=(7100, -1250), yaw=0x4000),
                   dict(kind='ribbon', pos=(7800, -1250)), dict(kind='herb_r', pos=(7500, -1200)),
                   dict(kind='ammo', pos=(7300, -1200), amount=15), dict(kind='file', file=7, pos=(7600, -1950), y=100)])
guard['cams'] = [dict(pos=(7850, 560, -1150), look=(7300, 60, -1700), zone=(6900, -2100, 8000, -1000), fov=58)]
ROOMS.append(guard)

# ---- Library (west wing) ----------------------------------------------------
lib = room('lib', 'Library', -7900, 1000, -6100, 2400, 750, floor='mans_floor', carpets=[(-7500, 1100, -6500, 2300)],
           boxes=[dict(x0=-7900, z0=1500, x1=-7700, z1=2000, y1=650, side='mans_wood', top='mans_wood'),
                  dict(x0=-6300, z0=1500, x1=-6100, z1=2000, y1=650, side='mans_wood', top='mans_wood'),
                  dict(x0=-7150, z0=1650, x1=-6850, z1=1850, y1=110, side='mans_wood', top='mans_wood')],
           lights=[(-7000, 560, 1700, 0.55, 800), (-6400, 450, 1200, 0.25, 500)],
           objs=[dict(kind='zombie', pos=(-6600, 2100), yaw=0x8000), dict(kind='zombie', pos=(-7500, 2100), yaw=0xC000),
                 dict(kind='herb_g', pos=(-7600, 1200)), dict(kind='herb_b', pos=(-6400, 1200)),
                 dict(kind='key', pos=(-7000, 2150), keyid=2), dict(kind='file', file=4, pos=(-7000, 1750), y=110)])
lib['cams'] = cams_along_x(lib, front='N')
ROOMS.append(lib)

# ---- Second floor landing -----------------------------------------------------
land = room('land', 'Second Floor Landing', -4600, 2000, -2400, 3200, 850, floor='mans_floor',
            carpets=[(-4500, 2500, -2500, 2700)],
            boxes=[dict(x0=-4200, z0=2800, x1=-4080, z1=2920, y1=800, side='mans_marble', top='mans_marble')],
            lights=[(-3500, 650, 2600, 0.55, 1000), (-4350, 500, 2300, 0.25, 600)],
            objs=[dict(kind='zombie', pos=(-3300, 2800), yaw=0x8000), dict(kind='herb_g', pos=(-4300, 2300)),
                  dict(kind='ammo', pos=(-2800, 2250), amount=10)])
land['cams'] = cams_along_x(land, front='S')
ROOMS.append(land)

# ---- Second floor corridor ----------------------------------------------------
c2 = room('corr2', 'Second Floor Corridor', -2000, 2450, 600, 2950, 700, floor='mans_floor', wainscot=300,
          lights=[(-1300, 520, 2700, 0.45, 700), (100, 520, 2700, 0.45, 700)],
          objs=[dict(kind='zombie', pos=(-300, 2700), yaw=0x4000), dict(kind='herb_g', pos=(-1000, 2550))])
c2['cams'] = cams_along_x(c2, ya=0.9, inset=120, fov=60, front='S')
ROOMS.append(c2)

# ---- Gallery (locked: Moon Key) -----------------------------------------------
gal = room('gal', 'Gallery', 1200, 2000, 3200, 3400, 800, floor='mans_floor', carpets=[(1300, 2550, 3100, 2850)],
           boxes=[dict(x0=2000, z0=2500, x1=2400, z1=2900, y1=140, side='mans_marble', top='mans_marble')],
           lights=[(2200, 600, 2700, 0.60, 900), (1500, 450, 3200, 0.25, 500)],
           objs=[dict(kind='zombie', pos=(1700, 3100), yaw=0xC000), dict(kind='zombie', pos=(2800, 2300), yaw=0x8000),
                 dict(kind='key', pos=(2200, 2700), keyid=3, y=140), dict(kind='herb_r', pos=(2900, 3100)),
                 dict(kind='ammo', pos=(1500, 2300), amount=12)])
gal['cams'] = cams_along_x(gal, front='N')
ROOMS.append(gal)

# ---- Bedroom ------------------------------------------------------------------
bed = room('bed', 'Bedroom', -1800, 3600, 0, 4800, 700, floor='mans_floor', carpets=[(-1500, 4000, -300, 4600)],
           boxes=[dict(x0=-1700, z0=3800, x1=-1300, z1=4200, y1=90, side='mans_wood', top='mans_wood')],
           lights=[(-900, 520, 4200, 0.50, 700)],
           objs=[dict(kind='zombie', pos=(-500, 4400), yaw=0x8000), dict(kind='herb_g', pos=(-300, 3900)),
                 dict(kind='herb_b', pos=(-1600, 4600)), dict(kind='ammo', pos=(-300, 4650), amount=10)])
bed['cams'] = cams_along_x(bed, front='N')
ROOMS.append(bed)

# ======================= TIER 3: below the courtyard fountain =======================
# ---- Fountain stairwell -------------------------------------------------------
stair = room('stair', 'Fountain Stairwell', 4400, 100, 6000, 600, 600, floor='mans_stone', wainscot=300,
             lights=[(4900, 450, 350, 0.40, 600), (5500, 450, 350, 0.40, 600)],
             objs=[dict(kind='zombie', pos=(5300, 330), yaw=0xC000), dict(kind='herb_b', pos=(5000, 180))])
stair['cams'] = cams_along_x(stair, ya=0.9, inset=120, fov=60, front='N')
ROOMS.append(stair)

# ---- Cellar (third save point) ----------------------------------------------------
cellar = room('cellar', 'Cellar', 6300, 0, 7700, 1000, 700, floor='mans_stone', wainscot=300,
              boxes=[dict(x0=7380, z0=40, x1=7660, z1=260, y1=100, side='mans_wood', top='mans_wood'),
                     dict(x0=6392, z0=892, x1=6508, z1=958, y1=60, hidden=True)],
              lights=[(7000, 520, 450, 0.80, 800)],
              objs=[dict(kind='typewriter', pos=(7520, 150), y=100, yaw=0x8000), dict(kind='box', pos=(6450, 925), yaw=0x4000),
                    dict(kind='ribbon', pos=(6500, 100)), dict(kind='ribbon', pos=(7600, 550)),
                    dict(kind='ammo', pos=(7550, 880), amount=15), dict(kind='herb_g', pos=(6700, 880)),
                    dict(kind='herb_r', pos=(7250, 880))])
cellar['cams'] = [dict(pos=(7650, 600, 950), look=(6900, 60, 350), zone=(6300, 0, 7700, 1000), fov=58)]
ROOMS.append(cellar)

# ---- Kamek's Laboratory (boss) ----------------------------------------------------
lab = room('lab', "Kamek's Laboratory", 5800, 1400, 7800, 3200, 900, floor='mans_stone', wall='mans_stone', panel='mans_marble',
           wainscot=350, ambient=0.30,
           boxes=[dict(x0=6000, z0=1800, x1=6400, z1=2000, y1=110, side='mans_marble', top='mans_marble'),
                  dict(x0=7350, z0=2100, x1=7650, z1=2300, y1=110, side='mans_marble', top='mans_marble'),
                  dict(x0=5880, z0=2300, x1=6080, z1=2600, y1=100, side='mans_marble', top='mans_marble'),
                  dict(x0=5850, z0=1450, x1=5970, z1=1570, y1=880, side='mans_marble', top='mans_marble'),
                  dict(x0=6560, z0=3040, x1=6680, z1=3160, y1=880, side='mans_marble', top='mans_marble'),
                  dict(x0=7320, z0=3040, x1=7440, z1=3160, y1=880, side='mans_marble', top='mans_marble')],
           lights=[(6800, 700, 2300, 0.55, 1500), (6000, 500, 2900, 0.30, 700), (7500, 500, 1700, 0.30, 700)],
           objs=[dict(kind='file', file=8, pos=(6200, 1900), y=110),
                 dict(kind='console', pos=(5980, 2450), y=100, yaw=0x4000),
                 dict(kind='zombie', pos=(7000, 2950), yaw=0x8000, hp=30, boss=1),
                 dict(kind='luigi', pos=(7560, 3000), yaw=0xA000),
                 dict(kind='ammo', pos=(6000, 2900), amount=15), dict(kind='ammo', pos=(7600, 2550), amount=15),
                 dict(kind='herb_r', pos=(6500, 2700)), dict(kind='herb_g', pos=(7300, 2700))])
lab['cams'] = cams_along_x(lab, ya=0.8, inset=150, fov=55, front='N')
ROOMS.append(lab)

# ---- Escape tunnel ------------------------------------------------------------------
tunnel = room('tunnel', 'Service Tunnel', 5400, 3600, 7000, 4100, 600, floor='mans_stone', wainscot=300, ambient=0.30,
              lights=[(5800, 450, 3850, 0.45, 700), (6600, 450, 3850, 0.45, 700)],
              objs=[dict(kind='zombie', pos=(6000, 3800), yaw=0x4000), dict(kind='zombie', pos=(6500, 3900), yaw=0xC000)])
tunnel['cams'] = cams_along_x(tunnel, ya=0.9, inset=120, fov=60, front='S')
ROOMS.append(tunnel)

# ---- Escape dock (open sky) ---------------------------------------------------------
dock = room('dock', 'Escape Dock', 3800, 3300, 5000, 4400, 900, floor='mans_stone', wall='mans_stone', panel='mans_stone',
            wainscot=0, sky=True, ambient=0.55,
            boxes=[dict(x0=3900, z0=3650, x1=4300, z1=4050, y1=60, side='mans_wood', top='mans_wood')],
            lights=[(4300, 400, 3850, 0.35, 900)],
            objs=[])
dock['cams'] = [dict(pos=(4900, 700, 3400), look=(4100, 60, 3900), zone=(3800, 3300, 5000, 4400), fov=55)]
ROOMS.append(dock)

DOORS = [
    dict(id='hall_e',  room='hall',   wall='E', at=0,     to='dining_w'),
    dict(id='dining_w', room='dining', wall='W', at=0,     to='hall_e'),
    dict(id='dining_n', room='dining', wall='N', at=0,     to='corrn_s'),
    dict(id='corrn_s', room='corr_n', wall='S', at=0,     to='dining_n'),
    dict(id='corrn_e', room='corr_n', wall='E', at=-3000, to='save_w'),
    dict(id='save_w',  room='save',   wall='W', at=-3000, to='corrn_e'),
    dict(id='hall_w',  room='hall',   wall='W', at=0,     to='corrw_e', key=1),
    dict(id='corrw_e', room='corr_w', wall='E', at=0,     to='hall_w'),
    dict(id='dining_e', room='dining', wall='E', at=0,     to='kitchen_w'),
    dict(id='kitchen_w', room='kitchen', wall='W', at=0,   to='dining_e'),
    dict(id='kitchen_n', room='kitchen', wall='N', at=2500, to='court_s'),
    dict(id='court_s', room='court', wall='S', at=2500,    to='kitchen_n'),
    dict(id='court_n', room='court', wall='N', at=3350,    to='save_s'),
    dict(id='save_s',  room='save',  wall='S', at=3350,    to='court_n'),
    dict(id='court_e', room='court', wall='E', at=-1650,   to='guard_w', key=3),
    dict(id='guard_w', room='guard', wall='W', at=-1550,   to='court_e'),
    dict(id='corrw_w', room='corr_w', wall='W', at=0,      to='lib_n'),
    dict(id='lib_n',   room='lib',   wall='N', at=-7000,   to='corrw_w'),
    dict(id='hall_s',  room='hall',  wall='S', at=-3500,   to='land_n'),
    dict(id='land_n',  room='land',  wall='N', at=-3500,   to='hall_s'),
    dict(id='land_e',  room='land',  wall='E', at=2600,    to='corr2_w'),
    dict(id='corr2_w', room='corr2', wall='W', at=2700,    to='land_e'),
    dict(id='corr2_e', room='corr2', wall='E', at=2700,    to='gal_w', key=2),
    dict(id='gal_w',   room='gal',   wall='W', at=2700,    to='corr2_e'),
    dict(id='corr2_s', room='corr2', wall='S', at=-800,    to='bed_n'),
    dict(id='bed_n',   room='bed',   wall='N', at=-800,    to='corr2_s'),
    dict(id='court_hatch', room='court', virtual=(4000, -1440), n=(0, 1), to='stair_w'),
    dict(id='stair_w', room='stair', wall='W', at=350,     to='court_hatch'),
    dict(id='stair_e', room='stair', wall='E', at=350,     to='cellar_w'),
    dict(id='cellar_w', room='cellar', wall='W', at=350,   to='stair_e'),
    dict(id='cellar_s', room='cellar', wall='S', at=7000,  to='lab_n'),
    dict(id='lab_n',   room='lab',   wall='N', at=7000,    to='cellar_s'),
    dict(id='lab_s',   room='lab',   wall='S', at=6300,    to='tun_n', key=9),
    dict(id='tun_n',   room='tunnel', wall='N', at=6300,   to='lab_s'),
    dict(id='tun_w',   room='tunnel', wall='W', at=3850,   to='dock_e'),
    dict(id='dock_e',  room='dock',  wall='E', at=3850,    to='tun_w'),
]

START = (-2800, 0, 0xC000)   # (x, z, yaw): inside the hall facing west
