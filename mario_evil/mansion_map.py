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
hall = room('hall', 'Main Hall', -5200, -1400, -2400, 1800, 1100, floor='mans_floor', wall='mans_brick', panel='mans_brick', wainscot=0,
            carpets=[(-5100, 440, -2450, 800), (-4050, -1050, -3750, 1800)],     # cross-shaped runners, the east-west one in front of the fountain
            boxes=[dict(x0=-5200, z0=-1400, x1=-2400, z1=-1050, y0=450, y1=500, side='mans_marble', top='mans_carpet', collide=False),   # the gallery (upper floor), seen from below and above
                   dict(x0=-4900, z0=-1050, x1=-4400, z1=-300, y1=500, hidden=True),      # west flight (collision only; the model is drawn)
                   dict(x0=-3400, z0=-1050, x1=-2900, z1=-300, y1=500, hidden=True),      # east flight
                   dict(x0=-4160, z0=360, x1=-3640, z1=880, y1=300, hidden=True),         # fountain
                   dict(x0=-5190, z0=-720, x1=-5050, z1=-580, y1=1100, side='mans_marble', top='mans_marble'),   # west wall pillars
                   dict(x0=-5190, z0=1620, x1=-5050, z1=1760, y1=1100, side='mans_marble', top='mans_marble'),   # front corner pillars
                   dict(x0=-2550, z0=-720, x1=-2410, z1=-580, y1=1100, side='mans_marble', top='mans_marble'),   # east wall pillars
                   dict(x0=-2550, z0=1620, x1=-2410, z1=1760, y1=1100, side='mans_marble', top='mans_marble')],
            lights=[(-3900, 330, 620, 0.55, 1500), (-4400, 650, 350, 0.40, 900), (-3400, 650, 350, 0.40, 900), (-3900, 320, -1200, 0.35, 800),
                    (-4650, 700, -700, 0.30, 700), (-3150, 700, -700, 0.30, 700)],
            objs=[dict(kind='herb_g', pos=(-2750, -650)), dict(kind='file', file=1, pos=(-4300, 650))])
hall['cams'] = [      # the one and only hall camera: high, just outside the (one-sided, so see-through) south wall, looking north and down; close enough that the frame holds only room
    dict(pos=(-3900, 1500, 2000), look=(-3900, 100, 900), zone=(-5200, -1400, -2400, 1800), fov=60, outside=True),   # checked numerically: the frame stays inside the room's silhouette (no black void) at widescreen
]
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
cn = room('corr_n', 'North Corridor', -1200, -3250, 1200, -2750, 700, floor='mans_tile', wainscot=300,
          lights=[(-700, 520, -3000, 0.45, 700), (700, 520, -3000, 0.45, 700)],
          objs=[dict(kind='zombie', pos=(500, -3000), yaw=0xC000), dict(kind='file', file=2, pos=(-1000, -3000))])
cn['cams'] = cams_along_x(cn, ya=0.9, inset=120, fov=60, front='S')
ROOMS.append(cn)

# ---- Save Room -------------------------------------------------------------
save = room('save', 'Save Room', 3000, -7200, 4000, -6200, 700, floor='mans_floor',
            boxes=[dict(x0=3550, z0=-6550, x1=3850, z1=-6350, y1=110, side='mans_wood', top='mans_wood'),
                   dict(x0=3192, z0=-7083, x1=3308, z1=-7017, y1=60, hidden=True)],
            lights=[(3500, 520, -6700, 0.85, 800)],
            objs=[dict(kind='typewriter', pos=(3700, -6532), y=110, yaw=0x8000), dict(kind='box', pos=(3250, -7050), yaw=0),
                  dict(kind='ribbon', pos=(3800, -7000)), dict(kind='key', pos=(3750, -6750), keyid=1),
                  dict(kind='gun', pos=(3350, -6950)), dict(kind='ammo', pos=(3500, -7050), amount=15)])
save['cams'] = [dict(pos=(3850, 600, -7050), look=(3550, 60, -6750), zone=(3000, -7200, 4000, -6200), fov=58)]
ROOMS.append(save)

# ---- West Corridor ---------------------------------------------------------
cw = room('corr_w', 'West Corridor', -7500, -250, -5800, 250, 700, floor='mans_tile', wainscot=300,
          lights=[(-6200, 520, 0, 0.45, 600), (-7100, 520, 0, 0.45, 600)],
          objs=[dict(kind='zombie', pos=(-6600, 0), yaw=0x4000), dict(kind='file', file=3, pos=(-6900, -150)),
                dict(kind='herb_b', pos=(-6900, 150))])
cw['cams'] = cams_along_x(cw, ya=0.9, inset=120, fov=60, front='N')
ROOMS.append(cw)

# ---- Kitchen (east wing) ----------------------------------------------------
kitchen = room('kitchen', 'Kitchen', 1600, -800, 3400, 800, 700, floor='mans_tile', wainscot=300,
               boxes=[dict(x0=2300, z0=-150, x1=2700, z1=150, y1=110, side='mans_wood', top='mans_wood')],
               lights=[(2500, 520, 0, 0.55, 800), (3000, 450, 500, 0.25, 500)],
               objs=[dict(kind='zombie', pos=(2900, 450), yaw=0x8000), dict(kind='zombie', pos=(2000, -450), yaw=0x4000),
                     dict(kind='herb_g', pos=(1850, 600)), dict(kind='ammo', pos=(3250, 600), amount=12),
                     dict(kind='file', file=6, pos=(2500, 0), y=110)])
kitchen['cams'] = cams_along_x(kitchen, front='N')
ROOMS.append(kitchen)

# ---- Courtyard (open sky) ---------------------------------------------------
court = room('court', 'Courtyard', 1500, -6000, 6500, -1000, 900, floor='mans_grass', wall='mans_stone', panel='mans_stone',
             wainscot=0, sky=True, ambient=0.50,
             boxes=[dict(x0=3800, z0=-3700, x1=4200, z1=-3300, y1=120, side='mans_marble', top='mans_marble'),
                   dict(x0=3880, z0=-3300, x1=4120, z1=-3220, y1=14, side='mans_wood', top='mans_door')],
             lights=[(2500, 400, -3500, 0.25, 900), (5500, 400, -3500, 0.25, 900), (4000, 400, -3500, 0.20, 900)],
             objs=[dict(kind='zombie', pos=(3000, -2000), yaw=0xC000), dict(kind='zombie', pos=(5200, -4800), yaw=0x4000),
                   dict(kind='zombie', pos=(5800, -2000), yaw=0x8000),
                   dict(kind='herb_g', pos=(2200, -2300)), dict(kind='ammo', pos=(2300, -4800), amount=10),
                   dict(kind='file', file=5, pos=(6100, -1400))])
# camera on the south wall centre (x=4000), looking north at Mario: it keeps x=4000 as its pivot (half-way pull towards Mario's x),
# stays 1000 south of him and 750 up, so he is always in view.  follow=2 -> pos.x = pivot (px) + 0.5*(Mario x - px)
court['cams'] = [dict(pos=(4000, 750, 1000), look=(0, 0, 0), zone=(1500, -6000, 6500, -1000), fov=55, outside=True, follow=2)]
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
           boxes=[dict(x0=-7900, z0=1500, x1=-7700, z1=2000, y1=650, side='mans_wood', top='mans_wood', hidden=True),   # bookcase (model drawn)
                  dict(x0=-6300, z0=1500, x1=-6100, z1=2000, y1=650, side='mans_wood', top='mans_wood', hidden=True),   # bookcase (model drawn)
                  dict(x0=-7150, z0=1650, x1=-6850, z1=1850, y1=110, side='mans_wood', top='mans_wood')],
           lights=[(-7000, 560, 1700, 0.55, 800), (-6400, 450, 1200, 0.25, 500)],
           objs=[dict(kind='prop', model='bookshelf', pos=(-7900, 1750), y=0, yaw=0x4000),    # west bookcase (back on the wall)
                 dict(kind='prop', model='bookshelf', pos=(-6100, 1750), y=0, yaw=0xC000),    # east bookcase
                 dict(kind='zombie', pos=(-6600, 2100), yaw=0x8000), dict(kind='zombie', pos=(-7500, 2100), yaw=0xC000),
                 dict(kind='herb_g', pos=(-7600, 1200)), dict(kind='herb_b', pos=(-6400, 1200)),
                 dict(kind='key', pos=(-7000, 2150), keyid=2), dict(kind='file', file=4, pos=(-7000, 1750), y=110)])
lib['cams'] = cams_along_x(lib, front='N')
ROOMS.append(lib)

# ---- Second floor landing -----------------------------------------------------
land = room('land', 'Second Floor Balcony', -5200, 1810, -2400, 2710, 800, floor='mans_floor', wall='mans_brick', panel='mans_brick', wainscot=0,
            yoff=500, noceil=True, open='N', see='hall',     # raised to the gallery height; the north edge is open onto the hall below
            carpets=[(-5100, 2250, -2450, 2550)],
            pads=[(-4900, 1820, -4400, 2150, 'mans_stairs_down', True), (-3400, 1820, -2900, 2150, 'mans_stairs_down', True)],   # the two stairwells down to the hall
            boxes=[],
            lights=[(-4300, 450, 2300, 0.50, 1200), (-3200, 450, 2300, 0.50, 1200), (-4650, 350, 2050, 0.30, 600), (-3150, 350, 2050, 0.30, 600)],
            objs=[dict(kind='zombie', pos=(-3300, 2450), yaw=0x8000), dict(kind='herb_g', pos=(-4300, 2350)),
                  dict(kind='ammo', pos=(-2900, 2350), amount=10)])
land['cams'] = [      # outside the end walls (one-sided, so see-through), north side so the south wall's doors are in view; each half is seen from the opposite end
    dict(pos=(-2100, 650, 1950), look=(-4400, -250, 2450), zone=(-5200, 1810, -3800, 2710), fov=44, outside=True),   # west half: camera at the east end
    dict(pos=(-5500, 650, 1950), look=(-3300, -250, 2450), zone=(-3800, 1810, -2400, 2710), fov=44, outside=True),   # east half: camera at the west end
]
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
stair = room('stair', 'Fountain Stairwell', 4400, 100, 6000, 600, 600, floor='mans_tile', wainscot=300,
             lights=[(4900, 450, 350, 0.40, 600), (5500, 450, 350, 0.40, 600)],
             objs=[dict(kind='zombie', pos=(5300, 330), yaw=0xC000), dict(kind='herb_b', pos=(5000, 180))])
stair['cams'] = cams_along_x(stair, ya=0.9, inset=120, fov=60, front='N')
ROOMS.append(stair)

# ---- Cellar (third save point) ----------------------------------------------------
cellar = room('cellar', 'Cellar', 6300, 0, 7700, 1000, 700, floor='mans_tile', wainscot=300,
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
lab = room('lab', "Kamek's Laboratory", 5800, 1100, 8000, 3500, 1500, floor='mans_tile', wall='mans_metal_plate', panel='mans_metal_plate',
           wainscot=350, ambient=0.30,
           boxes=[dict(x0=7280, z0=1330, x1=7620, z1=1670, y1=480, hidden=True),          # specimen tank (north-east)
                  dict(x0=6430, z0=1330, x1=6770, z1=1670, y1=480, hidden=True),          # specimen tank (north-west)
                  dict(x0=7480, z0=2580, x1=7820, z1=2920, y1=480, hidden=True),          # specimen tank (east)
                  dict(x0=6280, z0=2280, x1=6520, z1=2520, y1=170, hidden=True),          # cauldron (by the console)
                  dict(x0=6880, z0=3180, x1=7120, z1=3420, y1=170, hidden=True),          # cauldron (south)
                  dict(x0=7480, z0=3396, x1=7920, z1=3500, y1=280, hidden=True),          # control bank (south wall)
                  dict(x0=5800, z0=1730, x1=5900, z1=2170, y1=260, hidden=True),          # control bank (west wall)
                  dict(x0=7910, z0=1810, x1=8000, z1=2190, y1=300, hidden=True),          # vial rack (east wall)
                  dict(x0=6110, z0=1100, x1=6490, z1=1190, y1=300, hidden=True),          # vial rack (north wall)
                  dict(x0=5950, z0=1100, x1=6900, z1=1340, y0=900, y1=940, side='mans_metal_plate', top='mans_metal_plate'),   # north catwalk (above the floor)
                  dict(x0=5950, z0=1100, x1=5990, z1=1140, y1=900, side='mans_metal_plate', top='mans_metal_plate'),           # catwalk posts
                  dict(x0=6860, z0=1100, x1=6900, z1=1140, y1=900, side='mans_metal_plate', top='mans_metal_plate'),
                  dict(x0=6560, z0=3040, x1=6680, z1=3160, y1=880, side='mans_marble', top='mans_marble'),
                  dict(x0=7320, z0=3040, x1=7440, z1=3160, y1=880, side='mans_marble', top='mans_marble'),
                  dict(x0=6000, z0=1800, x1=6400, z1=2000, y1=110, side='mans_marble', top='mans_marble'),
                  dict(x0=7350, z0=2100, x1=7650, z1=2300, y1=110, side='mans_marble', top='mans_marble'),
                  dict(x0=5880, z0=2300, x1=6080, z1=2600, y1=100, side='mans_marble', top='mans_marble'),
                  dict(x0=5850, z0=1450, x1=5970, z1=1570, y1=880, side='mans_marble', top='mans_marble')],
           lights=[(6800, 700, 2300, 0.55, 1500), (6000, 500, 2900, 0.30, 700), (7500, 500, 1700, 0.30, 700),
                   (7000, 1300, 2300, 0.45, 1400), (7600, 1200, 3100, 0.40, 1200), (6200, 1200, 1700, 0.40, 1200)],
           objs=[dict(kind='file', file=8, pos=(6200, 1900), y=110),
                 dict(kind='console', pos=(5980, 2450), y=100, yaw=0x4000),
                 dict(kind='zombie', pos=(7000, 2950), yaw=0x8000, hp=30, boss=1),
                 dict(kind='cagekey', pos=(7000, 2950)),           # Bowser's drop: the Cage Key (shown once tyrant == 2)
                 dict(kind='prop', model='tank', pos=(7450, 1500), y=0, yaw=0),
                 dict(kind='prop', model='tank', pos=(6600, 1500), y=0, yaw=0),
                 dict(kind='prop', model='tank', pos=(7650, 2750), y=0, yaw=0),
                 dict(kind='prop', model='cauldron', pos=(6400, 2400), y=0, yaw=0x2000),
                 dict(kind='prop', model='cauldron', pos=(7000, 3300), y=0, yaw=0x6000),
                 dict(kind='prop', model='panel_bank', pos=(5950, 3500), y=0, yaw=0x8000),
                 dict(kind='prop', model='panel_bank', pos=(5800, 1950), y=0, yaw=0x4000),
                 dict(kind='prop', model='vial_rack', pos=(8000, 2050), y=0, yaw=0xC000),
                 dict(kind='prop', model='vial_rack', pos=(6300, 1100), y=0, yaw=0),
                 dict(kind='ammo', pos=(6000, 2900), amount=15), dict(kind='ammo', pos=(7600, 2000), amount=15),
                 dict(kind='herb_r', pos=(6500, 2700)), dict(kind='herb_g', pos=(7300, 2700))])
lab['cams'] = cams_along_x(lab, ya=0.8, inset=150, fov=55, front='N')
ROOMS.append(lab)

# ---- Luigi's cell (behind the iron bars; the gate is opened with the Cage Key, dropped by Tyrant Bowser) ----
cell = room('cell', "Luigi's Cell", 7300, 3600, 8000, 4300, 900, floor='mans_metal_diamond', wall='mans_bars', panel='mans_bars', wainscot=0,
            ambient=0.30,
            lights=[(7650, 700, 3950, 0.55, 800)],
            objs=[dict(kind='luigi', pos=(7500, 4050), yaw=0x8000)])
cell['cams'] = cams_along_x(cell, ya=0.8, inset=120, fov=58, front='N')
ROOMS.append(cell)

# ---- Escape tunnel ------------------------------------------------------------------
tunnel = room('tunnel', 'Service Tunnel', 5400, 3600, 7000, 4100, 600, floor='mans_metal_diamond', wall='mans_metal_plate', wainscot=300, ambient=0.30,
              lights=[(5800, 450, 3850, 0.45, 700), (6600, 450, 3850, 0.45, 700)],
              objs=[dict(kind='zombie', pos=(6000, 3800), yaw=0x4000), dict(kind='zombie', pos=(6500, 3900), yaw=0xC000)])
tunnel['cams'] = cams_along_x(tunnel, ya=0.9, inset=120, fov=60, front='S')
ROOMS.append(tunnel)

# ---- Escape dock (open sky) ---------------------------------------------------------
dock = room('dock', 'Escape Dock', 3800, 3300, 5000, 4400, 900, floor='mans_metal_diamond', wall='mans_stone', panel='mans_stone',
            wainscot=0, sky=True, ambient=0.55,
            boxes=[dict(x0=3900, z0=3650, x1=4300, z1=4050, y1=60, side='mans_wood', top='mans_wood')],
            lights=[(4300, 400, 3850, 0.35, 900)],
            objs=[])
dock['cams'] = [dict(pos=(4900, 700, 3400), look=(4100, 60, 3900), zone=(3800, 3300, 5000, 4400), fov=55)]
ROOMS.append(dock)

# ======================= v17 look: set dressing (concept art: green rot, thorn vines, slime) =======================
import math
RM = {r['id']: r for r in ROOMS}
GREEN_GLOW = (0.55, 1.0, 0.65)     # outdoor lamps (courtyard)
AMBER_GLOW = (1.00, 0.70, 0.36)    # indoor lamps: warm candle/gas light

def on_wall(rid, wall, at, model, y=0, inset=24):
    """Prop standing against a wall facing into the room."""
    r = RM[rid]
    if wall == 'N': pos, yaw = (at, r['z0'] + inset), 0x0000
    elif wall == 'S': pos, yaw = (at, r['z1'] - inset), 0x8000
    elif wall == 'W': pos, yaw = (r['x0'] + inset, at), 0x4000
    else: pos, yaw = (r['x1'] - inset, at), 0xC000
    return dict(kind='prop', model=model, pos=pos, y=y, yaw=yaw)

def lamp_on(rid, wall, at, y=400):
    d = on_wall(rid, wall, at, 'lamp', y=y, inset=4)
    r = RM[rid]
    off = {'N': (0, 70), 'S': (0, -70), 'W': (70, 0), 'E': (-70, 0)}[wall]
    glow = GREEN_GLOW if r.get('sky') else AMBER_GLOW
    r.setdefault('lights', []).append((d['pos'][0] + off[0], y + 30, d['pos'][1] + off[1], 0.55, 650, glow))
    return d

def portrait(rid, wall, at, n, y=330):
    RM[rid].setdefault('decor', []).append(dict(tex='mans_portrait%d' % n, wall=wall, at=at, w=110, h=140, y0=y))

def chand(rid, x, z):
    r = RM[rid]
    r.setdefault('objs', []).append(dict(kind='prop', model='chandelier', pos=(x, z), y=r['h'] - 250, yaw=0))

def add(rid, *objs):
    RM[rid].setdefault('objs', []).extend(objs)

def pot(x, z, yaw=0): return dict(kind='prop', model='pot', pos=(x, z), y=0, yaw=yaw)

# -- Courtyard: cracked cement walls, arched gates, balcony rail, overgrown grass, the ghost fountain
c = RM['court']
c.update(floor='mans_grass', wall='mans_brick', panel='mans_brick', rail=(780, 900), ambient=0.46)
# cement (sketch): square plaza around the fountain, an east-west path wall to wall, a path north to the Save Room gate;
# everything else is grass.  The pads must not overlap (coplanar quads would z-fight).
c.setdefault('pads', []).extend([
    (3200, -4300, 4800, -2700, 'mans_cement'),      # plaza
    (1500, -3800, 3200, -3200, 'mans_cement'),      # west path (to the kitchen gate)
    (4800, -3800, 6500, -3200, 'mans_cement'),      # east path (to the guardhouse gate)
    (3700, -6000, 4300, -4300, 'mans_cement'),      # north path (to the Save Room gate)
])
c['boxes'][0]['hidden'] = True                       # collision only; the fountain model is drawn instead
add('court', dict(kind='prop', model='fountain', pos=(4000, -3500), y=0, yaw=0),
    lamp_on('court', 'N', 3300, 420), lamp_on('court', 'N', 4700, 420),
    lamp_on('court', 'W', -2500, 420), lamp_on('court', 'W', -4500, 420), lamp_on('court', 'E', -2500, 420), lamp_on('court', 'E', -4500, 420),
    on_wall('court', 'N', 2750, 'vine'), on_wall('court', 'N', 5400, 'vine'),
    on_wall('court', 'W', -5200, 'vine'), on_wall('court', 'E', -5300, 'vine'), on_wall('court', 'E', -1700, 'vine'),
    pot(2600, -2000, 0x2000), pot(3500, -4700, 0x9000), pot(5300, -2100, 0x5000), pot(4650, -4900, 0xC000), pot(6200, -5300, 0x3000))

# -- Main hall (v0.2.6): two-storey atrium -- brick walls, gallery with locked doors, two staircases, blood fountain
add('hall', dict(kind='actor', actor=1, model='toad_rom', pos=(-3000, 330), y=0, yaw=0x8000))   # Toad: talk with B (see cinematics.py)
RM['hall']['boxes'].append(dict(x0=-3030, z0=300, x1=-2970, z1=360, y1=180, side='mans_wood', top='mans_wood', hidden=True))   # toad
add('hall', dict(kind='prop', model='stair_flight', pos=(-4650, -300), y=0, yaw=0), dict(kind='prop', model='stair_flight', pos=(-3150, -300), y=0, yaw=0),
    dict(kind='prop', model='hall_fountain', pos=(-3900, 620), y=0, yaw=0))
for bx in (-5050, -4275, -4025, -3775, -3525, -2775, -2525):      # gallery balustrade, gaps at the two stair heads
    add('hall', dict(kind='prop', model='balustrade', pos=(bx, -1062), y=500, yaw=0))
RM['hall']['decor'] = []     # no painted door decorations: none of them leads to a room
RM['hall']['decoy_doors'] = [dict(wall='S', at=-3900, w=480)]   # decorative double door at the entrance: no transition
add('hall', on_wall('hall', 'N', -3350, 'clock'),
    lamp_on('hall', 'W', -700, 430), lamp_on('hall', 'W', 1000, 430), lamp_on('hall', 'E', -950, 430),
    on_wall('hall', 'E', -1150, 'vine'), on_wall('hall', 'E', 1150, 'vine'), on_wall('hall', 'W', -350, 'vine'), on_wall('hall', 'W', 350, 'vine'),
    pot(-4300, 1250), pot(-3500, 1250, 0x4000))
for (mx, mz, myaw) in ((-5000, 600, 0x1000), (-5120, 790, 0x5000), (-2560, 620, 0x9000), (-2630, 800, 0xD000), (-4500, -240, 0x2000), (-3000, -250, 0x6000)):
    add('hall', dict(kind='prop', model='mushroom', pos=(mx, mz), y=0, yaw=myaw))
chand('hall', -4400, 350); chand('hall', -3400, 350); chand('hall', -3900, -500)
portrait('hall', 'W', -1150, 1); portrait('hall', 'W', 1150, 3); portrait('hall', 'E', -500, 2); portrait('hall', 'E', -200, 1)

# -- other rooms
chand('dining', 0, 0); portrait('dining', 'S', -500, 2); portrait('dining', 'S', 500, 3); portrait('dining', 'N', -600, 1)
add('dining', on_wall('dining', 'N', 600, 'vine'), pot(-800, -600),
    dict(kind='prop', model='table', pos=(0, 0), y=0, yaw=0),
    on_wall('dining', 'S', 0, 'fireplace', inset=24),
    *[dict(kind='prop', model='chair', pos=(x, -290), y=0, yaw=0) for x in (-300, 0, 300)],
    *[dict(kind='prop', model='chair', pos=(x, 290), y=0, yaw=0x8000) for x in (-300, 0, 300)])
dining['boxes'][0]['hidden'] = True                  # collision only; the table model is drawn instead
# collision for the chairs (seat + high back) and the fireplace; the models are drawn on top
for (cx, cz, back) in [(-300, -290, -1), (0, -290, -1), (300, -290, -1), (-300, 290, 1), (0, 290, 1), (300, 290, 1)]:
    dining['boxes'].append(dict(x0=cx - 65, z0=cz - 60, x1=cx + 65, z1=cz + 60, y1=95, side='mans_wood', top='mans_wood', hidden=True))
    dining['boxes'].append(dict(x0=cx - 65, z0=cz + back * 52 - 7, x1=cx + 65, z1=cz + back * 52 + 7, y1=260, side='mans_wood', top='mans_wood', hidden=True))
dining['boxes'].append(dict(x0=-230, z0=626, x1=230, z1=776, y1=300, side='mans_stone', top='mans_stone', hidden=True))   # fireplace
RM['dining'].setdefault('lights', []).append((0, 170, 546, 0.60, 650, (1.00, 0.70, 0.36)))   # fireplace glow
add('corr_n', lamp_on('corr_n', 'S', -400, 380), on_wall('corr_n', 'N', 300, 'vine'))
portrait('corr_n', 'S', 700, 3, y=300)

def desk_at(rid, box_index, yaw=0):
    """Replace a flat wood 'table' box with the modeled desk prop: collision keeps the box's
    footprint, but the box itself stops drawing and the desk model is drawn in its place."""
    b = RM[rid]['boxes'][box_index]
    cx, cz = (b['x0'] + b['x1']) / 2, (b['z0'] + b['z1']) / 2
    b['hidden'] = True
    add(rid, dict(kind='prop', model='desk', pos=(cx, cz), y=0, yaw=yaw))

add('save', lamp_on('save', 'E', -6700, 380), on_wall('save', 'N', 3700, 'vine'))
desk_at('save', 0)                                    # typewriter desk
add('corr_w', lamp_on('corr_w', 'N', -6500, 380), on_wall('corr_w', 'S', -7200, 'vine'))
add('kitchen', lamp_on('kitchen', 'S', 2800, 380), on_wall('kitchen', 'N', 3200, 'vine'), pot(3300, 560))
desk_at('kitchen', 0)                                 # dining table
RM['kitchen']['boxes'][0].update(x0=2330, z0=-110, x1=2670, z1=110)   # collision matches the desk model

# ---- kitchen dressing (reference art): brick walls, appliances along the south wall, giant mushrooms, rug, chairs ----
RM['kitchen'].update(wall='mans_brick', panel='mans_brick', wainscot=0, carpets=[(2020, -340, 2980, 340)])
def kbox(x0, x1, y1, z0=668, z1=800):
    RM['kitchen']['boxes'].append(dict(x0=x0, z0=z0, x1=x1, z1=z1, y1=y1, side='mans_wood', top='mans_wood', hidden=True))
# (fridge, stove, counter, sink-counter) run left to right along the south wall; models project -z into the room
for (x, mdl, w, h) in ((1755, 'fridge', 150, 330), (1935, 'stove', 190, 100), (2290, 'counter', 500, 100), (2800, 'sink', 500, 100)):
    add('kitchen', on_wall('kitchen', 'S', x, mdl, inset=2))
    kbox(x - w // 2, x + w // 2, h)
# cookware and little mushrooms on the worktops (y = worktop height)
add('kitchen',
    dict(kind='prop', model='kpot', pos=(1935, 750), y=100, yaw=0x1000), dict(kind='prop', model='kpot', pos=(2180, 740), y=100, yaw=0),
    dict(kind='prop', model='kpot', pos=(2950, 745), y=100, yaw=0x3000),
    dict(kind='prop', model='cup', pos=(2600, 730), y=100, yaw=0), dict(kind='prop', model='cup', pos=(2660, 750), y=100, yaw=0x2000),
    dict(kind='prop', model='mushroom', pos=(2420, 740), y=100, yaw=0x2000), dict(kind='prop', model='mushroom', pos=(2700, 730), y=100, yaw=0x6000),
    # giant mushrooms in the two north corners
    dict(kind='prop', model='mushroom_big', pos=(3270, -660), y=0, yaw=0x1000), dict(kind='prop', model='mushroom_big', pos=(1730, -670), y=0, yaw=0x5000),
    # chairs around the table (same convention as the dining room: chair faces +z, back rail on its -z side)
    *[dict(kind='prop', model='chair', pos=(x, -170), y=0, yaw=0) for x in (2420, 2580)],
    *[dict(kind='prop', model='chair', pos=(x, 170), y=0, yaw=0x8000) for x in (2420, 2580)])
for (cx, cz, back) in [(2420, -170, -1), (2580, -170, -1), (2420, 170, 1), (2580, 170, 1)]:
    kbox(cx - 65, cx + 65, 95, cz - 60, cz + 60)
    kbox(cx - 65, cx + 65, 260, cz + back * 52 - 7, cz + back * 52 + 7)
for (cx, cz) in ((3270, -660), (1730, -670)):
    kbox(cx - 35, cx + 35, 400, cz - 35, cz + 35)    # giant mushroom stalks (collision only)
# CAUTION signs above the counters and on the side walls
for (wall, at) in (('S', 2300), ('E', -250), ('N', 1900)):
    RM['kitchen'].setdefault('decor', []).append(dict(tex='mans_caution', wall=wall, at=at, w=100, h=130, y0=330))
add('guard', lamp_on('guard', 'N', 7300, 360), on_wall('guard', 'S', 7600, 'vine'))
desk_at('guard', 0)                                   # typewriter desk
chand('lib', -7000, 1700); portrait('lib', 'N', -6600, 1, y=360); portrait('lib', 'S', -7300, 2, y=360)
add('lib', lamp_on('lib', 'E', 2250, 420), on_wall('lib', 'N', -7600, 'vine'), pot(-6300, 2250))
desk_at('lib', 2)                                     # reading table (boxes 0/1 are the bookshelves)
# (the four locked doors that were here are removed: none leads to a room)
RM['land'].setdefault('decor', []).append(dict(tex='mans_paint_peach', wall='S', at=-3900, w=230, h=230, y0=420))  # Peach above it, kept inside the wall height
portrait('land', 'E', 2080, 1)
for bx in (-5050, -4275, -4025, -3775, -3525, -2775, -2525):   # balcony rail along the open edge, gaps at the two stairwells
    add('land', dict(kind='prop', model='balustrade', pos=(bx, 1825), y=0, yaw=0))
add('land', lamp_on('land', 'E', 1900, 430), lamp_on('land', 'W', 1900, 430), pot(-3900, 2640))
add('corr2', lamp_on('corr2', 'N', -800, 380), on_wall('corr2', 'S', 200, 'vine'))
chand('gal', 2200, 2700); portrait('gal', 'N', 1800, 2); portrait('gal', 'N', 2700, 3); portrait('gal', 'S', 1900, 1); portrait('gal', 'S', 2600, 2)
add('gal', lamp_on('gal', 'E', 2200, 400), on_wall('gal', 'N', 1400, 'vine'), pot(3000, 3250))
chand('bed', -900, 4200); portrait('bed', 'S', -900, 3, y=330)
add('bed', lamp_on('bed', 'E', 4400, 380), on_wall('bed', 'N', -1650, 'vine'))
add('stair', lamp_on('stair', 'N', 5000, 340), on_wall('stair', 'S', 5600, 'vine'))
add('cellar', lamp_on('cellar', 'E', 600, 380), on_wall('cellar', 'N', 6600, 'vine'), pot(7550, 900))
desk_at('cellar', 0)                                  # typewriter desk
add('lab', lamp_on('lab', 'W', 3000, 420), lamp_on('lab', 'E', 1250, 420), pot(6100, 3100, 0x2000),
    on_wall('lab', 'N', 7600, 'vine'), on_wall('lab', 'E', 3000, 'vine'))
add('tunnel', lamp_on('tunnel', 'S', 6200, 340), on_wall('tunnel', 'N', 5900, 'vine'))
add('dock', lamp_on('dock', 'S', 4400, 400), on_wall('dock', 'E', 3600, 'vine'))

# -- framed paintings (square canvases, 120 units, hung at eye level); each placed clear of doors and lamps
def painting(rid, wall, at, tex, y=300, size=120):
    RM[rid].setdefault('decor', []).append(dict(tex=tex, wall=wall, at=at, w=size, h=size, y0=y))
painting('hall', 'N', -3900, 'mans_paint_peach', y=640, size=230)   # Peach: the castle hall, above the great door
painting('lab', 'N', 6500, 'mans_paint_bowser')          # Bowser: Kamek's lab
painting('corr_w', 'S', -6000, 'mans_paint_goomba')      # Goomba: west corridor
painting('kitchen', 'N', 3000, 'mans_paint_mushroom')    # Super Mushroom: kitchen
painting('tunnel', 'N', 6800, 'mans_paint_drybones')     # Dry Bones: service tunnel


DOORS = [
    dict(id='hall_e',  room='hall',   wall='E', at=620,   to='dining_w'),
    dict(id='dining_w', room='dining', wall='W', at=0,     to='hall_e'),
    dict(id='dining_n', room='dining', wall='N', at=0,     to='corrn_s'),
    dict(id='corrn_s', room='corr_n', wall='S', at=0,     to='dining_n'),
    dict(id='corrn_e', room='corr_n', wall='E', at=-3000, to='save_w'),
    dict(id='save_w',  room='save',   wall='W', at=-6700, to='corrn_e'),
    dict(id='hall_w',  room='hall',   wall='W', at=620,   to='corrw_e', key=1),
    dict(id='corrw_e', room='corr_w', wall='E', at=0,     to='hall_w'),
    dict(id='dining_e', room='dining', wall='E', at=0,     to='kitchen_w'),
    dict(id='kitchen_w', room='kitchen', wall='W', at=0,   to='dining_e'),
    dict(id='kitchen_n', room='kitchen', wall='N', at=2500, to='court_w'),
    dict(id='court_w', room='court', wall='W', at=-3500,   to='kitchen_n'),
    dict(id='court_n', room='court', wall='N', at=4000,    to='save_s'),
    dict(id='save_s',  room='save',  wall='S', at=3350,    to='court_n'),
    dict(id='court_e', room='court', wall='E', at=-3500,   to='guard_w', key=3),
    dict(id='guard_w', room='guard', wall='W', at=-1550,   to='court_e'),
    dict(id='corrw_w', room='corr_w', wall='W', at=0,      to='lib_n'),
    dict(id='lib_n',   room='lib',   wall='N', at=-7000,   to='corrw_w'),
    dict(id='hall_stair_w', room='hall', virtual=(-4650, -100), n=(0, 1),  to='land_stair_w', stair=1),
    dict(id='hall_stair_e', room='hall', virtual=(-3150, -100), n=(0, 1),  to='land_stair_e', stair=1),
    dict(id='land_stair_w', room='land', virtual=(-4650, 2000), n=(0, 1), to='hall_stair_w', stair=2),
    dict(id='land_stair_e', room='land', virtual=(-3150, 2000), n=(0, 1), to='hall_stair_e', stair=2),
    dict(id='land_e',  room='land',  wall='E', at=2480,    to='corr2_w'),
    dict(id='corr2_w', room='corr2', wall='W', at=2700,    to='land_e'),
    dict(id='corr2_e', room='corr2', wall='E', at=2700,    to='gal_w', key=2),
    dict(id='gal_w',   room='gal',   wall='W', at=2700,    to='corr2_e'),
    dict(id='corr2_s', room='corr2', wall='S', at=-800,    to='bed_n'),
    dict(id='bed_n',   room='bed',   wall='N', at=-800,    to='corr2_s'),
    dict(id='court_hatch', room='court', virtual=(4000, -3290), n=(0, 1), to='stair_w'),
    dict(id='stair_w', room='stair', wall='W', at=350,     to='court_hatch'),
    dict(id='stair_e', room='stair', wall='E', at=350,     to='cellar_w'),
    dict(id='cellar_w', room='cellar', wall='W', at=350,   to='stair_e'),
    dict(id='cellar_s', room='cellar', wall='S', at=7000,  to='lab_n'),
    dict(id='lab_n',   room='lab',   wall='N', at=7000,    to='cellar_s'),
    dict(id='lab_s',   room='lab',   wall='S', at=6300,    to='tun_n', key=9),
    dict(id='lab_c',   room='lab',   wall='S', at=7650,    to='cell_n', key=8),     # the barred cell gate (Cage Key)
    dict(id='cell_n',  room='cell',  wall='N', at=7650,    to='lab_c', key=8),
    dict(id='tun_n',   room='tunnel', wall='N', at=6300,   to='lab_s'),
    dict(id='tun_w',   room='tunnel', wall='W', at=3850,   to='dock_e'),
    dict(id='dock_e',  room='dock',  wall='E', at=3850,    to='tun_w'),
]

# Schematic rectangles for the pause-menu map (x0, z0, x1, z1) in units of 100 world units. Rooms that connect
# touch each other here, whatever the real gaps are; Mario and the doors are placed by their position inside the
# real room rectangle.  Checked for overlaps by check_map.py.
MAPRECTS = {
    'hall': (-21, 4, -1, 22), 'dining': (-1, 5, 19, 21), 'corr_n': (-1, 0, 21, 5), 'kitchen': (19, 5, 37, 21),
    'court': (22, -45, 72, 5), 'save': (35.5, -55, 45.5, -45), 'guard': (72, -7, 83, 4),
    'corr_w': (-38, 10.5, -21, 15.5), 'lib': (-47, 15.5, -29, 29.5),
    'land': (-21, 22, -1, 34), 'corr2': (-1, 25.5, 25, 30.5), 'gal': (25, 22, 45, 33), 'bed': (2, 30.5, 20, 42.5),
    'stair': (41, 5, 57, 10), 'cellar': (57, 5, 71, 15), 'lab': (54, 16, 80, 32), 'cell': (73, 36, 80, 43),
    'tunnel': (50, 33, 66, 38), 'dock': (38, 34, 50, 45),
}

START = (-3900, 1650, 0x8000)   # (x, z, yaw): at the south wall of the hall, facing north up the carpet (the intro walks in from here)
