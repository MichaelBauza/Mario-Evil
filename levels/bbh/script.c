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
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_0A, /*pos*/ 3700, 120, -2750, /*angle*/ 0, 0, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionTypewriter),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_09, /*pos*/ 3250, 10, -3350, /*angle*/ 0, 0, 0, /*behParam*/ 0x00000000, /*beh*/ bhvMansionItemBox),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_07, /*pos*/ 3800, 10, -3300, /*angle*/ 0, 0, 0, /*behParam*/ 0x04010005, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_06, /*pos*/ 3300, 10, -2650, /*angle*/ 0, 0, 0, /*behParam*/ 0x05010106, /*beh*/ bhvMansionPickup),
    OBJECT(/*model*/ MODEL_GOOMBA, /*pos*/ -6600, 0, 0, /*angle*/ 0, 90, 0, /*behParam*/ 0x03000007, /*beh*/ bhvMansionZombie),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_08, /*pos*/ -7300, 10, 0, /*angle*/ 0, 0, 0, /*behParam*/ 0x03000000, /*beh*/ bhvMansionFile),
    OBJECT(/*model*/ MODEL_LEVEL_GEOMETRY_05, /*pos*/ -7300, 10, 150, /*angle*/ 0, 0, 0, /*behParam*/ 0x03010008, /*beh*/ bhvMansionPickup),

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
