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
#include "actors/group15.h"

#include "make_const_nonconst.h"
#include "levels/bbh/header.h"

static const LevelScript script_func_local_objects[] = {
/*@@OBJECTS@@*/
    RETURN(),
};

const LevelScript level_bbh_entry[] = {
    INIT_LEVEL(),
    LOAD_YAY0(        /*seg*/ 0x07, _bbh_segment_7SegmentRomStart, _bbh_segment_7SegmentRomEnd),
    LOAD_YAY0(        /*seg*/ 0x08, _common0_yay0SegmentRomStart, _common0_yay0SegmentRomEnd),
    LOAD_RAW(         /*seg*/ 0x0F, _common0_geoSegmentRomStart,  _common0_geoSegmentRomEnd),
    LOAD_YAY0(        /*seg*/ 0x06, _group15_yay0SegmentRomStart, _group15_yay0SegmentRomEnd),   // real Toad from the SM64 ROM
    LOAD_RAW(         /*seg*/ 0x0D, _group15_geoSegmentRomStart,  _group15_geoSegmentRomEnd),
    ALLOC_LEVEL_POOL(),
    MARIO(/*model*/ MODEL_MARIO, /*behParam*/ 0x00000001, /*beh*/ bhvMario),
    JUMP_LINK(script_func_global_1),
/*@@LOADS@@*/
    LOAD_MODEL_FROM_GEO(MODEL_TOAD, toad_geo),
    AREA(/*index*/ 1, mansion_geo_area),
        OBJECT(/*model*/ MODEL_NONE, /*pos*/ @@START_X@@, 20, @@START_Z@@, /*angle*/ 0, @@START_YAW@@, 0, /*behParam*/ 0x000A0000, /*beh*/ bhvInstantActiveWarp),
        WARP_NODE(/*id*/ 0x0A, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        WARP_NODE(/*id*/ 0xF0, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        WARP_NODE(/*id*/ 0xF1, /*destLevel*/ LEVEL_BBH, /*destArea*/ 0x01, /*destNode*/ 0x0A, /*flags*/ WARP_NO_CHECKPOINT),
        JUMP_LINK(script_func_local_objects),
        TERRAIN(/*terrainData*/ mansion_collision),
        SET_BACKGROUND_MUSIC(/*settingsPreset*/ 0x0006, /*seq*/ SEQ_LEVEL_SPOOKY),
        TERRAIN_TYPE(/*terrainType*/ TERRAIN_SPOOKY),
    END_AREA(),

    FREE_LEVEL_POOL(),
    MARIO_POS(/*area*/ 1, /*yaw*/ @@START_YAW@@, /*pos*/ @@START_X@@, 0, @@START_Z@@),
    CALL(/*arg*/ 0, /*func*/ lvl_init_or_update),
    CALL(/*arg*/ 0, /*func*/ lvl_mansion_init),
    CALL_LOOP(/*arg*/ 1, /*func*/ lvl_init_or_update),
    CLEAR_LEVEL(),
    SLEEP_BEFORE_EXIT(/*frames*/ 1),
    EXIT(),
};
