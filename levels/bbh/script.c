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
#include "actors/group12.h"
#include "mario_evil/gen_actors/mv_toad/mv_toad.h"

#include "make_const_nonconst.h"
#include "levels/bbh/header.h"

static const LevelScript script_func_local_objects[] = {

    RETURN(),
};

const LevelScript level_bbh_entry[] = {
    INIT_LEVEL(),
    LOAD_YAY0(        /*seg*/ 0x07, _bbh_segment_7SegmentRomStart, _bbh_segment_7SegmentRomEnd),
    LOAD_YAY0(        /*seg*/ 0x08, _common0_yay0SegmentRomStart, _common0_yay0SegmentRomEnd),
    LOAD_RAW(         /*seg*/ 0x0F, _common0_geoSegmentRomStart,  _common0_geoSegmentRomEnd),
    LOAD_YAY0(        /*seg*/ 0x06, _group12_yay0SegmentRomStart, _group12_yay0SegmentRomEnd),   // real Bowser + Toad from the SM64 ROM
    LOAD_RAW(         /*seg*/ 0x0D, _group12_geoSegmentRomStart,  _group12_geoSegmentRomEnd),
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
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_12, mansion_geo_prop_fountain),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_13, mansion_geo_prop_chandelier),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_14, mansion_geo_prop_lamp),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_15, mansion_geo_prop_pot),
    LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_16, mansion_geo_prop_clock),
    LOAD_MODEL_FROM_GEO(0xE8, mansion_geo_prop_stairs),
    LOAD_MODEL_FROM_GEO(0xE9, mansion_geo_prop_vine),
    LOAD_MODEL_FROM_GEO(0xEA, mansion_geo_prop_table),
    LOAD_MODEL_FROM_GEO(0xEB, mansion_geo_prop_desk),
    LOAD_MODEL_FROM_GEO(0xEC, mansion_geo_prop_chair),
    LOAD_MODEL_FROM_GEO(0xED, mansion_geo_prop_fireplace),
    LOAD_MODEL_FROM_GEO(0xEE, mansion_geo_prop_fridge),
    LOAD_MODEL_FROM_GEO(0xEF, mansion_geo_prop_stove),
    LOAD_MODEL_FROM_GEO(0xF0, mansion_geo_prop_counter),
    LOAD_MODEL_FROM_GEO(0xF1, mansion_geo_prop_sink),
    LOAD_MODEL_FROM_GEO(0xF2, mansion_geo_prop_kpot),
    LOAD_MODEL_FROM_GEO(0xF3, mansion_geo_prop_cup),
    LOAD_MODEL_FROM_GEO(0xF4, mansion_geo_prop_mushroom),
    LOAD_MODEL_FROM_GEO(0xF5, mansion_geo_prop_mushroom_big),
    LOAD_MODEL_FROM_GEO(0xF6, mansion_geo_prop_stair_flight),
    LOAD_MODEL_FROM_GEO(0xF7, mansion_geo_prop_balustrade),
    LOAD_MODEL_FROM_GEO(0xF8, mansion_geo_prop_hall_fountain),

    LOAD_MODEL_FROM_GEO(MODEL_TOAD, mvtoad_geo),
    LOAD_MODEL_FROM_GEO(MODEL_BOWSER, bowser_geo),
    AREA(/*index*/ 1, mansion_geo_area),
        OBJECT(/*model*/ MODEL_NONE, /*pos*/ -2440, 20, 0, /*angle*/ 0, 270, 0, /*behParam*/ 0x000A0000, /*beh*/ bhvInstantActiveWarp),
        WARP_NODE(/*id*/ 0x0A, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        WARP_NODE(/*id*/ 0xF0, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        WARP_NODE(/*id*/ 0xF1, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        JUMP_LINK(script_func_local_objects),
        TERRAIN(/*terrainData*/ mansion_collision),
        SET_BACKGROUND_MUSIC(/*settingsPreset*/ 0x0006, /*seq*/ SEQ_LEVEL_SPOOKY),
        TERRAIN_TYPE(/*terrainType*/ TERRAIN_SPOOKY),
    END_AREA(),

    FREE_LEVEL_POOL(),
    MARIO_POS(/*area*/ 1, /*yaw*/ 270, /*pos*/ -2440, 0, 0),
    CALL(/*arg*/ 0, /*func*/ lvl_init_or_update),
    CALL(/*arg*/ 0, /*func*/ lvl_mansion_init),
    CALL_LOOP(/*arg*/ 1, /*func*/ lvl_init_or_update),
    CLEAR_LEVEL(),
    SLEEP_BEFORE_EXIT(/*frames*/ 1),
    EXIT(),
};
