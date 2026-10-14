// Generated from mario_evil/script_template.c by gen_level.py -- do not edit by hand
#include <ultra64.h>
#include "sm64.h"
#include "behavior_data.h"
#include "model_ids.h"
#include "seq_ids.h"
#include "dialog_ids.h"
#include "segment_symbols.h"
#include "level_commands.h"

#include "game/level_update.h"
#include "game/mansion.h"

#include "levels/scripts.h"

#include "actors/common1.h"

#include "make_const_nonconst.h"
#include "levels/bbh/header.h"

static const LevelScript script_func_local_objects[] = {
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ -2750, 10, -650, /*angle*/ 0, 0, 0, /*behParam*/ 0x01010001, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ -4300, 10, 650, /*angle*/ 0, 0, 0, /*behParam*/ 0x01000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 450, 0, 450, /*angle*/ 0, 180, 0, /*behParam*/ 0x03000002, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_04, /*pos*/ -800, 10, 600, /*angle*/ 0, 0, 0, /*behParam*/ 0x02010003, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 500, 0, -3000, /*angle*/ 0, 270, 0, /*behParam*/ 0x03000004, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ -1000, 10, -3000, /*angle*/ 0, 0, 0, /*behParam*/ 0x02000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0A, /*pos*/ 3700, 120, -2750, /*angle*/ 0, 180, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionTypewriter),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_09, /*pos*/ 3250, 10, -3350, /*angle*/ 0, 0, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionItemBox),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_07, /*pos*/ 3800, 10, -3300, /*angle*/ 0, 0, 0, /*behParam*/ 0x04010005, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_06, /*pos*/ 3750, 10, -3050, /*angle*/ 0, 0, 0, /*behParam*/ 0x05010106, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0B, /*pos*/ 3350, 10, -3250, /*angle*/ 0, 0, 0, /*behParam*/ 0x06010007, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 3500, 10, -3350, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0F0008, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -6600, 0, 0, /*angle*/ 0, 90, 0, /*behParam*/ 0x03000009, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ -6900, 10, -150, /*angle*/ 0, 0, 0, /*behParam*/ 0x03000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_05, /*pos*/ -6900, 10, 150, /*angle*/ 0, 0, 0, /*behParam*/ 0x0301000A, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 2900, 0, 450, /*angle*/ 0, 180, 0, /*behParam*/ 0x0300000B, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 2000, 0, -450, /*angle*/ 0, 90, 0, /*behParam*/ 0x0300000C, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ 1850, 10, 600, /*angle*/ 0, 0, 0, /*behParam*/ 0x0101000D, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 3250, 10, 600, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0C000E, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ 2500, 120, 0, /*angle*/ 0, 0, 0, /*behParam*/ 0x06000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 3000, 0, -1400, /*angle*/ 0, 270, 0, /*behParam*/ 0x0300000F, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 4800, 0, -1900, /*angle*/ 0, 90, 0, /*behParam*/ 0x03000010, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 5600, 0, -1300, /*angle*/ 0, 180, 0, /*behParam*/ 0x03000011, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ 2200, 10, -2050, /*angle*/ 0, 0, 0, /*behParam*/ 0x01010012, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 2250, 10, -1700, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0A0013, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ 6100, 10, -2000, /*angle*/ 0, 0, 0, /*behParam*/ 0x05000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0A, /*pos*/ 7700, 110, -1950, /*angle*/ 0, 0, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionTypewriter),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_09, /*pos*/ 7100, 10, -1250, /*angle*/ 0, 90, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionItemBox),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_07, /*pos*/ 7800, 10, -1250, /*angle*/ 0, 0, 0, /*behParam*/ 0x04010014, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_04, /*pos*/ 7500, 10, -1200, /*angle*/ 0, 0, 0, /*behParam*/ 0x02010015, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 7300, 10, -1200, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0F0016, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ 7600, 110, -1950, /*angle*/ 0, 0, 0, /*behParam*/ 0x07000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -6600, 0, 2100, /*angle*/ 0, 180, 0, /*behParam*/ 0x03000017, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -7500, 0, 2100, /*angle*/ 0, 270, 0, /*behParam*/ 0x03000018, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ -7600, 10, 1200, /*angle*/ 0, 0, 0, /*behParam*/ 0x01010019, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_05, /*pos*/ -6400, 10, 1200, /*angle*/ 0, 0, 0, /*behParam*/ 0x0301001A, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0C, /*pos*/ -7000, 10, 2150, /*angle*/ 0, 0, 0, /*behParam*/ 0x0501021B, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ -7000, 120, 1750, /*angle*/ 0, 0, 0, /*behParam*/ 0x04000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -3300, 0, 2800, /*angle*/ 0, 180, 0, /*behParam*/ 0x0300001C, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ -4300, 10, 2300, /*angle*/ 0, 0, 0, /*behParam*/ 0x0101001D, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ -2800, 10, 2250, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0A001E, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -300, 0, 2700, /*angle*/ 0, 90, 0, /*behParam*/ 0x0300001F, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ -1000, 10, 2550, /*angle*/ 0, 0, 0, /*behParam*/ 0x01010020, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 1700, 0, 3100, /*angle*/ 0, 270, 0, /*behParam*/ 0x03000021, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 2800, 0, 2300, /*angle*/ 0, 180, 0, /*behParam*/ 0x03000022, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0D, /*pos*/ 2200, 150, 2700, /*angle*/ 0, 0, 0, /*behParam*/ 0x05010323, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_04, /*pos*/ 2900, 10, 3100, /*angle*/ 0, 0, 0, /*behParam*/ 0x02010024, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 1500, 10, 2300, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0C0025, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -500, 0, 4400, /*angle*/ 0, 180, 0, /*behParam*/ 0x03000026, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ -300, 10, 3900, /*angle*/ 0, 0, 0, /*behParam*/ 0x01010027, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_05, /*pos*/ -1600, 10, 4600, /*angle*/ 0, 0, 0, /*behParam*/ 0x03010028, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ -300, 10, 4650, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0A0029, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 5300, 0, 330, /*angle*/ 0, 270, 0, /*behParam*/ 0x0300002A, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_05, /*pos*/ 5000, 10, 180, /*angle*/ 0, 0, 0, /*behParam*/ 0x0301002B, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0A, /*pos*/ 7520, 110, 150, /*angle*/ 0, 180, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionTypewriter),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_09, /*pos*/ 6450, 10, 925, /*angle*/ 0, 90, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionItemBox),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_07, /*pos*/ 6500, 10, 100, /*angle*/ 0, 0, 0, /*behParam*/ 0x0401002C, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_07, /*pos*/ 7600, 10, 550, /*angle*/ 0, 0, 0, /*behParam*/ 0x0401002D, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 7550, 10, 880, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0F002E, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ 6700, 10, 880, /*angle*/ 0, 0, 0, /*behParam*/ 0x0101002F, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_04, /*pos*/ 7250, 10, 880, /*angle*/ 0, 0, 0, /*behParam*/ 0x02010030, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ 6200, 120, 1900, /*angle*/ 0, 0, 0, /*behParam*/ 0x08000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_10, /*pos*/ 5980, 110, 2450, /*angle*/ 0, 90, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionConsole),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_12, /*pos*/ 7000, 0, 2950, /*angle*/ 0, 180, 0, /*behParam*/ 0x1E000131, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_11, /*pos*/ 7560, 10, 3000, /*angle*/ 0, 225, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionLuigi),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 6000, 10, 2900, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0F0032, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0E, /*pos*/ 7600, 10, 2550, /*angle*/ 0, 0, 0, /*behParam*/ 0x0A0F0033, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_04, /*pos*/ 6500, 10, 2700, /*angle*/ 0, 0, 0, /*behParam*/ 0x02010034, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_03, /*pos*/ 7300, 10, 2700, /*angle*/ 0, 0, 0, /*behParam*/ 0x01010035, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 6000, 0, 3800, /*angle*/ 0, 90, 0, /*behParam*/ 0x03000036, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ 6500, 0, 3900, /*angle*/ 0, 270, 0, /*behParam*/ 0x03000037, /*beh*/ bhvMansionZombie),

    RETURN(),
};

const LevelScript level_bbh_entry[] = {
    INIT_LEVEL(),
    LOAD_YAY0(        /*seg*/ 0x07, _bbh_segment_7SegmentRomStart, _bbh_segment_7SegmentRomEnd),
    LOAD_YAY0(        /*seg*/ 0x08, _common0_yay0SegmentRomStart, _common0_yay0SegmentRomEnd),
    LOAD_RAW(         /*seg*/ 0x0F, _common0_geoSegmentRomStart,  _common0_geoSegmentRomEnd),
    ALLOC_LEVEL_POOL(),
    MARIO(/*model*/ MODEL_MARIO, /*behParam*/ 0x00000001, /*beh*/ bhvMario),
    JUMP_LINK(script_func_global_1),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_03, mansion_geo_item_herb_g),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_04, mansion_geo_item_herb_r),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_05, mansion_geo_item_herb_b),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_06, mansion_geo_item_key),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_07, mansion_geo_item_ribbon),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_08, mansion_geo_item_file),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_09, mansion_geo_item_box),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0A, mansion_geo_item_typewriter),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0B, mansion_geo_item_gun),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0C, mansion_geo_item_key2),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0D, mansion_geo_item_key3),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0E, mansion_geo_item_ammo),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0F, mansion_geo_held_gun),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_10, mansion_geo_item_console),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_11, mansion_geo_item_luigi),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_12, mansion_geo_boss_tyrant),

    AREA(/*index*/ 1, mansion_geo_area),
        OBJECT(/*model*/ MODEL_NONE, /*pos*/ -2800, 20, 0, /*angle*/ 0, 270, 0, /*behParam*/ 0x000A0000, /*beh*/ bhvInstantActiveWarp),
        WARP_NODE(/*id*/ 0x0A, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        WARP_NODE(/*id*/ 0xF0, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        WARP_NODE(/*id*/ 0xF1, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        JUMP_LINK(script_func_local_objects),
        TERRAIN(/*terrainData*/ mansion_collision),
        SET_BACKGROUND_MUSIC(/*settingsPreset*/ 0x0006, /*seq*/ SEQ_LEVEL_SPOOKY),
        TERRAIN_TYPE(/*terrainType*/ TERRAIN_SPOOKY),
    END_AREA(),

    FREE_LEVEL_POOL(),
    MARIO_POS(/*area*/ 1, /*yaw*/ 270, /*pos*/ -2800, 0, 0),
    CALL(/*arg*/ 0, /*func*/ lvl_init_or_update),
    CALL(/*arg*/ 0, /*func*/ lvl_mansion_init),
    CALL_LOOP(/*arg*/ 1, /*func*/ lvl_init_or_update),
    CLEAR_LEVEL(),
    SLEEP_BEFORE_EXIT(/*frames*/ 1),
    EXIT(),
};
