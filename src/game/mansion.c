#include <PR/ultratypes.h>
#include <string.h>
#include "sound_init.h"

#include "sm64.h"
#include "area.h"
#include "audio/external.h"
#include "behavior_data.h"
#include "camera.h"
#include "engine/graph_node.h"
#include "engine/math_util.h"
#include "engine/surface_collision.h"
#include "game_init.h"
#include "ingame_menu.h"
#include "level_update.h"
#include "mario.h"
#include "object_helpers.h"
#include "object_list_processor.h"
#include "print.h"
#include "puppyprint.h"
#include "object_fields.h"
#include "mansion.h"

/* ------------------------------------------------------------------------ */
/* data                                                                     */
/* ------------------------------------------------------------------------ */

struct MansionState gMansion;
f32 gMansionFov = 50.0f;

void set_play_mode(s16 playMode);

static void str_copy(char *dst, const char *src, s32 max) {
    s32 i = 0;
    while (src[i] != '\0' && i < max - 1) { dst[i] = src[i]; i++; }
    dst[i] = '\0';
}

static void str_append(char *dst, const char *src, s32 max) {
    s32 n = 0;
    while (dst[n] != '\0') n++;
    str_copy(dst + n, src, max - n);
}

#include "mansion_data.inc.c"

static const char *const sItemNames[MI_COUNT] = {
    "", "Green Herb", "Red Herb", "Blue Herb", "Ink Ribbon", "Star Key", "Pistol",
    "Mixed Herb (GG)", "Mixed Herb (GR)", "Mixed Herb (GB)", "Handgun Ammo"
};

static const char *const sKeyNames[4] = { "Key", "Star Key", "Moon Key", "Sun Key" };

static const char *slot_name(const struct MansionSlot *s) {
    if (s->id == MI_KEY) return sKeyNames[s->extra & 3];
    return sItemNames[s->id];
}

#define NUM_FILES 7
static const char *const sFileTitles[NUM_FILES + 1] = {
    "", "Peach's Letter", "Toad Gardener's Diary", "Researcher Toad's Letter",
    "Kamek's Orders", "Specimen 42 Report", "Spore Containment Memo", "Luigi's Journal"
};
static const char *const sFileText[NUM_FILES + 1] = {
    "",
    "Dear Mario,\n\n"
    "I sent word to the castle guard and\n"
    "have heard nothing back. The gates were\n"
    "barred from the outside last night.\n"
    "Please come quickly. Something is wrong\n"
    "with the Toads. They have stopped\n"
    "talking, and none of them will look at me.\n\n"
    "I am locking myself in the tower.\n"
    "I will bake you a cake when this is over.\n\n"
    "                                       Peach",
    "Day 1 - The west garden Piranha Plants are\n"
    "growing far too fast. Toadsworth says it\n"
    "is nothing to worry about.\n"
    "Day 3 - New fertilizer from the Koopa\n"
    "Troop. Strange purple spores. The plants\n"
    "love it.\n"
    "Day 5 - Toadette got bitten. She says it\n"
    "is only a scratch. She keeps scratching.\n"
    "Day 6 - Her spots are turning purple. Her\n"
    "cap will not stay on.\n"
    "Day 7 - She does not speak anymore. Only\n"
    "groans. I locked the garden door.\n"
    "Day 8 - I itch.",
    "To my wife,\n\n"
    "If this reaches you, do not come to the\n"
    "castle. Lord Kamek's lab beneath the\n"
    "basement is not for the Kingdom. The\n"
    "Poison Mushroom spores he calls the\n"
    "P-Virus were ordered by Bowser himself:\n"
    "\"an army that never retreats.\"\n"
    "We were test subjects too.\n"
    "I left the Star Key in the room where I\n"
    "kept the typewriter. It opens the west\n"
    "passage. Do not follow me there.",
    "To: Kamek, Royal Magikoopa\n"
    "From: His Majesty\n\n"
    "The spores took on the Toads. Good.\n"
    "Now make them take on soldiers. An army\n"
    "that never retreats and never needs\n"
    "to be paid.\n"
    "Keep the Princess out of the east wing.\n"
    "Keep Mario out of the castle.\n"
    "If he gets in, make sure he does not\n"
    "get out.\n\n"
    "                                     - B.",
    "SPECIMEN 42 - Piranha Plant, mature\n\n"
    "Fed on spore-treated soil for 19 days.\n"
    "Growth: 400 percent. It ignores the\n"
    "feeding schedule now. It hunts.\n"
    "Roots have spread beneath the courtyard\n"
    "and into the foundation.\n"
    "I recommended burning it. Dr. K refused.\n"
    "He calls it the proof of concept.\n"
    "It is still growing.",
    "ALL KITCHEN STAFF\n\n"
    "Cold storage is sealed. Do not eat\n"
    "anything from the pantry. The mushroom\n"
    "stock is contaminated. Purple caps.\n"
    "Three cooks reported dizziness.\n"
    "One has not come out of the pantry since\n"
    "yesterday. We can hear him in there.\n\n"
    "Seal the door. Burn your clothes.\n"
    "Report to the lab.",
    "Day 1 - Brigade split up. I took the\n"
    "guardhouse. Radio is dead.\n"
    "Day 2 - Scratching in the walls. The\n"
    "others stopped answering.\n"
    "Day 3 - Found a stairwell behind the\n"
    "courtyard fountain. Cold air, and a\n"
    "smell I know from the garden.\n"
    "Day 4 - If you are reading this, Mario,\n"
    "I am still alive. The way down is\n"
    "under the fountain. I will wait for\n"
    "you there. Please hurry."
};

#define HEALTH_MAX     0x880
#define HEALTH_FINE    0x600
#define HEALTH_CAUTION 0x300

/* ------------------------------------------------------------------------ */
/* helpers                                                                  */
/* ------------------------------------------------------------------------ */

static inline s32 uid_get(u32 *arr, u32 uid) { return (arr[uid >> 5] >> (uid & 31)) & 1; }
static inline void uid_set(u32 *arr, u32 uid) { arr[uid >> 5] |= (1u << (uid & 31)); }

void mansion_message(const char *text) {
    str_copy(gMansion.msg, text, sizeof(gMansion.msg));
    gMansion.msgTimer = 110;
}

s32 mansion_inv_add(u8 id, u8 extra) {
    s32 i;
    for (i = 0; i < MANSION_INV_SLOTS; i++) {
        if (gMansion.inv[i].id == MI_NONE) {
            gMansion.inv[i].id = id;
            gMansion.inv[i].extra = extra;
            return TRUE;
        }
    }
    return FALSE;
}

static s32 find_room(f32 x, f32 z) {
    s32 i;
    for (i = 0; i < MANSION_NUM_ROOMS; i++) {
        if (x >= gMansionRooms[i].x0 && x <= gMansionRooms[i].x1
         && z >= gMansionRooms[i].z0 && z <= gMansionRooms[i].z1) {
            return i;
        }
    }
    return -1;
}

static s32 condition(void) {
    if (gMarioState->health >= HEALTH_FINE) return 0;     // Fine
    if (gMarioState->health >= HEALTH_CAUTION) return 1;  // Caution
    return 2;                                             // Danger
}

static void zero_player_input(void) {
    struct Controller *c = gPlayer1Controller;
    c->rawStickX = 0; c->rawStickY = 0; c->stickX = 0; c->stickY = 0; c->stickMag = 0;
    c->buttonDown = 0; c->buttonPressed = 0;
}

static void heal(s32 amount) {
    gMarioState->health += amount;
    if (gMarioState->health > HEALTH_MAX) gMarioState->health = HEALTH_MAX;
}

/* ------------------------------------------------------------------------ */
/* level start / save point                                                 */
/* ------------------------------------------------------------------------ */

static void snapshot_save(void) {
    struct MarioState *m = gMarioState;
    gMansion.hasSave = TRUE;
    gMansion.saveHealth = m->health;
    gMansion.saveAmmo = gMansion.ammo;
    vec3f_copy(gMansion.savePos, m->pos);
    gMansion.saveYaw = m->faceAngle[1];
    memcpy(gMansion.saveInv, gMansion.inv, sizeof(gMansion.inv));
    memcpy(gMansion.saveBox, gMansion.box, sizeof(gMansion.box));
    gMansion.saveFiles = gMansion.files;
    memcpy(gMansion.saveCollected, gMansion.collected, sizeof(gMansion.collected));
    memcpy(gMansion.saveKilled, gMansion.killed, sizeof(gMansion.killed));
    memcpy(gMansion.saveUnlocked, gMansion.lockedUnlocked, sizeof(gMansion.lockedUnlocked));
}

static void snapshot_load(void) {
    struct MarioState *m = gMarioState;
    m->health = gMansion.saveHealth;
    gMansion.ammo = gMansion.saveAmmo;
    vec3f_copy(m->pos, gMansion.savePos);
    m->faceAngle[1] = gMansion.saveYaw;
    m->marioObj->oPosX = m->pos[0]; m->marioObj->oPosY = m->pos[1]; m->marioObj->oPosZ = m->pos[2];
    vec3f_copy(m->marioObj->header.gfx.pos, m->pos);
    memcpy(gMansion.inv, gMansion.saveInv, sizeof(gMansion.inv));
    memcpy(gMansion.box, gMansion.saveBox, sizeof(gMansion.box));
    gMansion.files = gMansion.saveFiles;
    memcpy(gMansion.collected, gMansion.saveCollected, sizeof(gMansion.collected));
    memcpy(gMansion.killed, gMansion.saveKilled, sizeof(gMansion.killed));
    memcpy(gMansion.lockedUnlocked, gMansion.saveUnlocked, sizeof(gMansion.lockedUnlocked));
}

// Called from the level script right after the normal level init (Mario exists and is placed).
s32 lvl_mansion_init(UNUSED s16 arg, UNUSED s32 unused) {
    // Items/enemies collected before the last typewriter save stay gone; anything after it is restored.
    if (gMansion.hasSave) {
        snapshot_load();
        mansion_message("Continued from your last save");
    } else if (!gMansion.started) {
        gMarioState->health = HEALTH_MAX;
    }
    gMansion.started = TRUE;
    gMansion.camIdx = -1;
    gMansion.menu = MENU_NONE;
    gMansion.doorState = 0;
    gMansion.fade = 0;
    gMansion.wantMenu = 0;
    gMansion.room = (u8) MAX(0, find_room(gMarioState->pos[0], gMarioState->pos[2]));
    return 0;
}

/* ------------------------------------------------------------------------ */
/* camera                                                                   */
/* ------------------------------------------------------------------------ */

Gfx *geo_switch_mansion_room(s32 callContext, struct GraphNode *node, UNUSED void *context) {
    if (callContext == GEO_CONTEXT_RENDER) {
        struct GraphNodeSwitchCase *sw = (struct GraphNodeSwitchCase *) node;
        sw->selectedCase = gMansion.room;
    }
    return NULL;
}

void mansion_camera(struct Camera *c) {
    const struct MansionRoom *r = &gMansionRooms[gMansion.room];
    f32 mx = gMarioState->pos[0], mz = gMarioState->pos[2];
    s32 i, pick = 0;
    s32 fresh = (gMansion.camIdx < 0 || gMansion.camRoom != gMansion.room || gMansion.camIdx >= r->camCount);

    if (gMansion.camCooldown > 0) gMansion.camCooldown--;

    // Which zone is Mario in?
    for (i = 0; i < r->camCount; i++) {
        const struct MansionCam *cam = &gMansionCams[r->camFirst + i];
        if (mx >= cam->zx0 && mx <= cam->zx1 && mz >= cam->zz0 && mz <= cam->zz1) {
            pick = i;
            break;
        }
    }

    if (fresh) {
        gMansion.camLatch = 0;
        gMansion.camCooldown = 0;
    } else if (pick != gMansion.camIdx) {
        // Hysteresis: keep the current camera until Mario is well past its zone edge,
        // and never cut twice in quick succession.
        const struct MansionCam *cur = &gMansionCams[r->camFirst + gMansion.camIdx];
        const f32 margin = 130.0f;
        s32 inside = (mx >= cur->zx0 - margin && mx <= cur->zx1 + margin
                   && mz >= cur->zz0 - margin && mz <= cur->zz1 + margin);
        if (inside || gMansion.camCooldown > 0) {
            pick = gMansion.camIdx;
        } else {
            // Cut: keep steering relative to the old camera until the stick is released or turned.
            struct Controller *ctl = gPlayer1Controller;
            if (ctl->stickMag > 10.0f) {
                gMansion.camLatch = 1;
                gMansion.camLatchYaw = c->yaw;
                gMansion.camLatchStick = atan2s(-ctl->stickY, ctl->stickX);
            }
            gMansion.camCooldown = 40;
        }
    }
    gMansion.camRoom = gMansion.room;
    {
        const struct MansionCam *cam = &gMansionCams[r->camFirst + pick];
        Vec3f pos = { cam->px, cam->py, cam->pz };
        // The focus drifts slightly toward Mario so he stays framed, but the angle stays "fixed".
        Vec3f focus = { cam->fx + (mx - cam->fx) * 0.18f, cam->fy + (gMarioState->pos[1] - cam->fy) * 0.1f,
                        cam->fz + (mz - cam->fz) * 0.18f };
        s16 yaw;

        if (gMansion.doorState == 1) {
            // door cinematic: close-up on the door from inside the room, creeping forward
            const struct MansionDoor *dd = &gMansionDoors[gMansion.doorTarget];
            f32 k = (f32) gMansion.doorTimer / 66.0f;
            f32 dist = 330.0f - 90.0f * k;
            pos[0] = dd->x + dd->nx * dist; pos[1] = 170.0f; pos[2] = dd->z + dd->nz * dist;
            focus[0] = dd->x; focus[1] = 165.0f; focus[2] = dd->z;
            gMansion.camLatch = 0;
            gMansionFov = 50;
        } else {
            gMansionFov = cam->fov;
        }
        gMansion.camIdx = pick;
        vec3f_copy(c->pos, pos);
        vec3f_copy(c->focus, focus);
        vec3f_copy(gLakituState.curPos, pos);
        vec3f_copy(gLakituState.curFocus, focus);
        vec3f_copy(gLakituState.goalPos, pos);
        vec3f_copy(gLakituState.goalFocus, focus);
        vec3f_copy(gLakituState.pos, pos);
        vec3f_copy(gLakituState.focus, focus);
        yaw = atan2s(pos[2] - focus[2], pos[0] - focus[0]);
        if (gMansion.camLatch) {
            struct Controller *ctl = gPlayer1Controller;
            s16 stickAng = atan2s(-ctl->stickY, ctl->stickX);
            if (ctl->stickMag < 10.0f || abs_angle_diff(stickAng, gMansion.camLatchStick) > 0x2800) {
                gMansion.camLatch = 0;
            }
        }
        // Mario reads c->yaw for stick direction; while latched it keeps the pre-cut orientation.
        c->yaw = gMansion.camLatch ? gMansion.camLatchYaw : yaw;
        c->nextYaw = c->yaw;
        gLakituState.yaw = yaw;
        gLakituState.nextYaw = yaw;
        gLakituState.roll = 0;
        gLakituState.posHSpeed = 0.f;
        gLakituState.posVSpeed = 0.f;
    }
}

/* ------------------------------------------------------------------------ */
/* tank controls (RE1-style)                                                */
/* stick up = walk forward, stick down = walk back, left/right = turn in    */
/* place. Walking is the default speed; hold R to run.                      */
/* ------------------------------------------------------------------------ */

#define TANK_WALK_SPEED 16.0f
#define TANK_RUN_SPEED  32.0f
#define TANK_TURN_RATE  0x0500   // full stick: about 7 degrees per frame
#define TANK_DEADZONE   12

/* ---- pistol -------------------------------------------------------------- */

static s32 has_gun(void) {
    s32 i;
    for (i = 0; i < MANSION_INV_SLOTS; i++) if (gMansion.inv[i].id == MI_GUN) return TRUE;
    return FALSE;
}

// Nearest living zombie in front of Mario (within range and a forward cone), or NULL.
static struct Object *aim_target(struct MarioState *m) {
    struct ObjectNode *head = &gObjectLists[OBJ_LIST_GENACTOR];
    struct Object *obj = (struct Object *) head->next;
    struct Object *best = NULL;
    f32 bestDist = 1500.0f;

    while (obj != (struct Object *) head) {
        if (obj->activeFlags != ACTIVE_FLAG_DEACTIVATED && obj_has_behavior(obj, bhvMansionZombie)
            && obj->oAction != 3 && find_room(obj->oPosX, obj->oPosZ) == gMansion.room) {
            f32 dx = obj->oPosX - m->pos[0], dz = obj->oPosZ - m->pos[2];
            f32 d = sqrtf(dx * dx + dz * dz);
            s16 ang = atan2s(dz, dx);
            if (d < bestDist && abs_angle_diff(ang, m->faceAngle[1]) < 0x3000) {
                best = obj;
                bestDist = d;
            }
        }
        obj = (struct Object *) obj->header.next;
    }
    return best;
}

static void gun_fire(struct MarioState *m, struct Object *target) {
    if (gMansion.ammo == 0) {
        play_sound(SOUND_MENU_CAMERA_BUZZ, gGlobalSoundSource);
        gMansion.fireCool = 12;
        if (gMansion.msgTimer < 20) mansion_message("Out of ammo.");
        return;
    }
    gMansion.ammo--;
    gMansion.fireCool = 20;
    gMansion.flash = 3;
    play_sound(SOUND_GENERAL2_BOBOMB_EXPLOSION, gGlobalSoundSource);
    if (target != NULL && abs_angle_diff(atan2s(target->oPosZ - m->pos[2], target->oPosX - m->pos[0]), m->faceAngle[1]) < 0x1800) {
        target->oHealth--;
        target->oMoveAngleYaw = atan2s(target->oPosZ - m->pos[2], target->oPosX - m->pos[0]);
        target->oForwardVel = 14.0f;
        target->oVelY = 5.0f;
        target->oAction = (target->oHealth <= 0) ? 3 : 2;
        target->oTimer = 0;
        play_sound(SOUND_ACTION_HIT, target->header.gfx.cameraToObject);
    }
}

void mansion_tank_input(struct MarioState *m) {
    struct Controller *ctl = m->controller;
    f32 top = (ctl->buttonDown & R_TRIG) ? TANK_RUN_SPEED : TANK_WALK_SPEED;

    if (gMansion.fireCool > 0) gMansion.fireCool--;
    gMansion.aiming = 0;
    if (gMansion.menu == MENU_NONE && gMansion.doorState == 0 && has_gun() && (ctl->buttonDown & Z_TRIG)
        && !(m->action & ACT_FLAG_AIR) && m->action != ACT_BACKWARD_GROUND_KB) {
        struct Object *target = aim_target(m);
        gMansion.aiming = 1;
        // Z raises the pistol: no walking, no crouch, no jump. Left/right still turns (slower).
        m->input &= ~(INPUT_Z_DOWN | INPUT_Z_PRESSED | INPUT_A_PRESSED | INPUT_A_DOWN | INPUT_B_PRESSED | INPUT_NONZERO_ANALOG);
        if (ctl->stickX > TANK_DEADZONE || ctl->stickX < -TANK_DEADZONE) {
            m->faceAngle[1] -= (s16) (ctl->stickX * (TANK_TURN_RATE / 2) / 64);
        } else if (target != NULL) {
            // auto-aim: swing toward the nearest enemy in front when the stick is centred
            m->faceAngle[1] = approach_s16_symmetric(m->faceAngle[1],
                                                     atan2s(target->oPosZ - m->pos[2], target->oPosX - m->pos[0]), 0x500);
        }
        m->intendedMag = 0.0f;
        m->intendedYaw = m->faceAngle[1];
        if ((ctl->buttonPressed & A_BUTTON) && gMansion.fireCool == 0) gun_fire(m, target);
        return;
    }

    // Turn: sign flipped after on-device report that left/right felt inverted.
    if (ctl->stickX > TANK_DEADZONE || ctl->stickX < -TANK_DEADZONE) {
        m->faceAngle[1] -= (s16) (ctl->stickX * TANK_TURN_RATE / 64);
    }

    if (ctl->stickY > TANK_DEADZONE) {
        m->intendedMag = top * (ctl->stickY / 64.0f);
        m->intendedYaw = m->faceAngle[1];
    } else if (ctl->stickY < -TANK_DEADZONE) {
        m->intendedMag = TANK_WALK_SPEED * 0.5f * (-ctl->stickY / 64.0f);
        m->intendedYaw = (s16) (m->faceAngle[1] + 0x8000);
    } else {
        m->intendedMag = 0.0f;
        m->intendedYaw = m->faceAngle[1];
    }

    if (m->intendedMag > 0.0f) m->input |= INPUT_NONZERO_ANALOG;
}

/* ------------------------------------------------------------------------ */
/* per-frame update                                                         */
/* ------------------------------------------------------------------------ */

void mansion_pre_update(void) {
    if (gMansion.msgTimer > 0) gMansion.msgTimer--;
    if (gMansion.flash > 0) gMansion.flash--;
    gMansion.nearPrompt = 0;

    if (gMansion.doorState != 0) {
        zero_player_input();
    }
}

/* RE1-style door cinematic: the camera cuts to a close-up of the door, the door swings open onto
   darkness while the camera creeps forward, then it fades out and Mario appears on the far side. */
#define DOOR_ANIM_LEN    66
#define DOOR_OPEN_START  10
#define DOOR_OPEN_END    50
#define DOOR_FADE_START  52
#define DOOR_W 300
#define DOOR_H 340

extern const Gfx mansion_door_begin_dl[];
extern const Gfx mansion_door_end_dl[];

static f32 door_open_amount(void) {
    f32 t = ((f32) gMansion.doorTimer - DOOR_OPEN_START) / (DOOR_OPEN_END - DOOR_OPEN_START);
    if (t < 0.f) t = 0.f;
    if (t > 1.f) t = 1.f;
    return t * t * (3.f - 2.f * t);
}

static void set_vtx(Vtx *v, s32 x, s32 y, s32 z, s32 u, s32 w, u8 r, u8 g, u8 b) {
    v->v.ob[0] = x; v->v.ob[1] = y; v->v.ob[2] = z;
    v->v.flag = 0;
    v->v.tc[0] = u; v->v.tc[1] = w;
    v->v.cn[0] = r; v->v.cn[1] = g; v->v.cn[2] = b; v->v.cn[3] = 0xFF;
}

Gfx *geo_mansion_door_anim(s32 callContext, struct GraphNode *node, UNUSED void *context) {
    if (callContext == GEO_CONTEXT_RENDER && gMansion.doorState == 1) {
        const struct MansionDoor *d = &gMansionDoors[gMansion.doorTarget];
        struct GraphNodeGenerated *gen = (struct GraphNodeGenerated *) node;
        Vtx *v = alloc_display_list(8 * sizeof(Vtx));
        Gfx *dl = alloc_display_list(8 * sizeof(Gfx));
        Gfx *g = dl;
        s32 ax = (d->nz != 0) ? 1 : 0;     // along-wall axis matches the generator (x for N/S walls, z for E/W)
        s32 az = (d->nz != 0) ? 0 : 1;
        s16 ang = (s16) (door_open_amount() * 0x3800);
        f32 sn = sins(ang), cs = coss(ang);
        s32 hx = d->x - ax * DOOR_W / 2 + d->nx * 9, hz = d->z - az * DOOR_W / 2 + d->nz * 9;       // hinge
        s32 ex = hx + (s32) (ax * DOOR_W * cs) - (s32) (d->nx * DOOR_W * sn);                      // free end
        s32 ez = hz + (s32) (az * DOOR_W * cs) - (s32) (d->nz * DOOR_W * sn);
        f32 dim = 1.0f - 0.55f * sn;
        u8 lr = (u8) (d->lr * dim), lg = (u8) (d->lg * dim), lb = (u8) (d->lb * dim);
        s32 ox0 = d->x - ax * DOOR_W / 2 + d->nx * 7, oz0 = d->z - az * DOOR_W / 2 + d->nz * 7;
        s32 ox1 = d->x + ax * DOOR_W / 2 + d->nx * 7, oz1 = d->z + az * DOOR_W / 2 + d->nz * 7;

        SET_GRAPH_NODE_LAYER(gen->fnNode.node.flags, LAYER_TRANSPARENT_INTER);

        // 0-3: the dark doorway behind the leaf
        set_vtx(&v[0], ox0, 0,      oz0, 0, 0, 0, 0, 0);
        set_vtx(&v[1], ox1, 0,      oz1, 0, 0, 0, 0, 0);
        set_vtx(&v[2], ox1, DOOR_H, oz1, 0, 0, 0, 0, 0);
        set_vtx(&v[3], ox0, DOOR_H, oz0, 0, 0, 0, 0, 0);
        // 4-7: the swinging door leaf, texture mapped once across its face
        set_vtx(&v[4], hx, 0,      hz, 0,    1020, lr, lg, lb);
        set_vtx(&v[5], ex, 0,      ez, 1020, 1020, lr, lg, lb);
        set_vtx(&v[6], ex, DOOR_H, ez, 1020, 0,    lr, lg, lb);
        set_vtx(&v[7], hx, DOOR_H, hz, 0,    0,    lr, lg, lb);

        gSPDisplayList(g++, mansion_door_begin_dl);
        gSPVertex(g++, v, 8, 0);
        gSP2Triangles(g++, 0, 1, 2, 0x0, 0, 2, 3, 0x0);
        gSP2Triangles(g++, 4, 5, 6, 0x0, 4, 6, 7, 0x0);
        gSPDisplayList(g++, mansion_door_end_dl);
        gSPEndDisplayList(g);
        return dl;
    }
    return NULL;
}

static s32 door_locked(s32 idx) {
    const struct MansionDoor *d = &gMansionDoors[idx];
    return d->key != 0 && !(gMansion.lockedUnlocked[idx >> 3] & (1 << (idx & 7)));
}

static s32 inv_find_key(u8 keyid) {
    s32 i;
    for (i = 0; i < MANSION_INV_SLOTS; i++) {
        if (gMansion.inv[i].id == MI_KEY && gMansion.inv[i].extra == keyid) return i;
    }
    return -1;
}

static void door_teleport(void) {
    const struct MansionDoor *dst = &gMansionDoors[gMansionDoors[gMansion.doorTarget].dest];
    struct MarioState *m = gMarioState;
    f32 h;

    m->pos[0] = dst->sx;
    m->pos[2] = dst->sz;
    h = find_floor_height(m->pos[0], m->pos[1] + 200.f, m->pos[2]);
    m->pos[1] = h;
    m->vel[0] = m->vel[1] = m->vel[2] = 0.f;
    m->forwardVel = 0.f;
    m->faceAngle[1] = dst->yaw;
    m->marioObj->oPosX = m->pos[0]; m->marioObj->oPosY = m->pos[1]; m->marioObj->oPosZ = m->pos[2];
    vec3f_copy(m->marioObj->header.gfx.pos, m->pos);
    m->marioObj->header.gfx.angle[1] = dst->yaw;
    set_mario_action(m, ACT_IDLE, 0);
    gMansion.room = dst->room;
    gMansion.camIdx = -1;
}

static void update_doors(void) {
    struct MarioState *m = gMarioState;
    s32 i;

    if (gMansion.doorState == 1) {
        gMansion.doorTimer++;
        if (gMansion.doorTimer == 6) play_sound(SOUND_GENERAL_OPEN_WOOD_DOOR, gGlobalSoundSource);
        gMansion.fade = (gMansion.doorTimer > DOOR_FADE_START)
            ? MIN(255, (gMansion.doorTimer - DOOR_FADE_START) * 255 / (DOOR_ANIM_LEN - DOOR_FADE_START)) : 0;
        if (gMansion.doorTimer >= DOOR_ANIM_LEN) {
            door_teleport();
            gMansion.doorState = 2;
            gMansion.doorTimer = 0;
        }
        return;
    }
    if (gMansion.doorState == 2) {
        gMansion.doorTimer++;
        gMansion.fade = MAX(0, 255 - gMansion.doorTimer * 255 / 14);
        if (gMansion.doorTimer >= 14) { gMansion.doorState = 0; gMansion.fade = 0; }
        return;
    }
    if (!(m->action & ACT_FLAG_MOVING) || m->forwardVel < 8.f || (m->action & ACT_FLAG_AIR)) {
        gMansion.doorPush = 0;
        return;
    }
    for (i = 0; i < MANSION_NUM_DOORS; i++) {
        const struct MansionDoor *d = &gMansionDoors[i];
        f32 dx, dz, dist, fx, fz;
        if (d->room != gMansion.room) continue;
        dx = d->x - m->pos[0];
        dz = d->z - m->pos[2];
        dist = sqrtf(dx * dx + dz * dz);
        if (dist > 230.f) continue;
        fx = sins(m->faceAngle[1]);
        fz = coss(m->faceAngle[1]);
        // moving toward the door means facing opposite to the door's inward normal
        if (fx * -d->nx + fz * -d->nz < 0.6f) continue;
        if (++gMansion.doorPush < 6) return;
        if (door_locked(i)) {
            s32 k = inv_find_key(d->key);
            if (k < 0) {
                if (gMansion.msgTimer < 20) { mansion_message("The door is locked."); play_sound(SOUND_MENU_CAMERA_BUZZ, gGlobalSoundSource); }
                gMansion.doorPush = 0;
                return;
            }
            gMansion.inv[k].id = MI_NONE;
            gMansion.lockedUnlocked[i >> 3] |= (1 << (i & 7));
            gMansion.lockedUnlocked[gMansionDoors[i].dest >> 3] |= (1 << (gMansionDoors[i].dest & 7));
            {
                char kb[40];
                str_copy(kb, "Used the ", sizeof(kb));
                str_append(kb, sKeyNames[d->key & 3], sizeof(kb));
                str_append(kb, ". It unlocks.", sizeof(kb));
                mansion_message(kb);
            }
        }
        gMansion.doorState = 1;
        gMansion.doorTimer = 0;
        gMansion.doorTarget = i;
        gMansion.doorPush = 0;
        m->forwardVel = 0.f;
        m->vel[0] = m->vel[1] = m->vel[2] = 0.f;
        set_mario_action(m, ACT_IDLE, 0);
        return;
    }
    gMansion.doorPush = 0;
}

void mansion_post_update(void) {
    struct MarioState *m = gMarioState;
    s32 r = find_room(m->pos[0], m->pos[2]);
    if (r >= 0 && gMansion.doorState == 0) gMansion.room = r;
    update_doors();
    if (gMansion.aiming && gMansion.doorState == 0) {
        // arm out, holding the pistol: freeze the punch animation on its extended frame
        set_mario_animation(m, MARIO_ANIM_FIRST_PUNCH);
        m->marioObj->header.gfx.animInfo.animFrame = 3;
    }
    if (gMansion.doorState == 1) m->marioObj->header.gfx.node.flags |= GRAPH_RENDER_INVISIBLE;
    else m->marioObj->header.gfx.node.flags &= ~GRAPH_RENDER_INVISIBLE;
}

s32 mansion_wants_pause(void) {
    if (gMansion.doorState != 0) return FALSE;
    if (gMansion.wantMenu != MENU_NONE) return TRUE;
    return (gPlayer1Controller->buttonPressed & START_BUTTON) != 0;
}

void mansion_enter_pause(void) {
    gMansion.menu = (gMansion.wantMenu != MENU_NONE) ? gMansion.wantMenu : MENU_ITEMS;
    gMansion.wantMenu = MENU_NONE;
    gMansion.sel = 0;
    gMansion.boxSel = 0;
    gMansion.boxSide = 0;
    gMansion.comboSrc = -1;
    play_sound(SOUND_MENU_MESSAGE_APPEAR, gGlobalSoundSource);
}

/* ------------------------------------------------------------------------ */
/* inventory menu (runs while the game is in PLAY_MODE_PAUSED)              */
/* ------------------------------------------------------------------------ */

static s32 menu_dir(s32 *dx, s32 *dy) {
    struct Controller *c = gPlayer1Controller;
    s32 sx = 0, sy = 0;
    *dx = *dy = 0;
    if (c->buttonPressed & L_JPAD) *dx = -1;
    if (c->buttonPressed & R_JPAD) *dx = 1;
    if (c->buttonPressed & U_JPAD) *dy = -1;
    if (c->buttonPressed & D_JPAD) *dy = 1;
    if (c->stickX < -40) sx = -1; else if (c->stickX > 40) sx = 1;
    if (c->stickY > 40) sy = -1; else if (c->stickY < -40) sy = 1;
    if (sx != 0 && sx != gMansion.stickLatchX) *dx = sx;
    if (sy != 0 && sy != gMansion.stickLatchY) *dy = sy;
    gMansion.stickLatchX = sx;
    gMansion.stickLatchY = sy;
    return *dx != 0 || *dy != 0;
}

static void close_menu(void) {
    gMansion.menu = MENU_NONE;
    raise_background_noise(1);
    gCameraMovementFlags &= ~CAM_MOVE_PAUSE_SCREEN;
    set_play_mode(PLAY_MODE_NORMAL);
}

static void use_item(s32 slot) {
    struct MansionSlot *s = &gMansion.inv[slot];
    s32 full = gMarioState->health >= HEALTH_MAX;
    switch (s->id) {
        case MI_HERB_G:  if (full) { mansion_message("You don't need that now."); return; } heal(0x300); break;
        case MI_HERB_GG: if (full) { mansion_message("You don't need that now."); return; } heal(0x500); break;
        case MI_HERB_GR: if (full) { mansion_message("You don't need that now."); return; } heal(HEALTH_MAX); break;
        case MI_HERB_GB: if (full) { mansion_message("You don't need that now."); return; } heal(0x400); break;
        case MI_HERB_R:  mansion_message("Red herbs do nothing alone. Combine with Green."); return;
        case MI_HERB_B:  mansion_message("Blue herbs do nothing alone. Combine with Green."); return;
        case MI_KEY:     mansion_message("Walk into the locked door to use it."); return;
        case MI_RIBBON:  mansion_message("Use it at a typewriter."); return;
        default: return;
    }
    s->id = MI_NONE;
    play_sound(SOUND_MENU_STAR_SOUND, gGlobalSoundSource);
    mansion_message("You feel better.");
}

static u8 combine_result(u8 a, u8 b) {
    if ((a == MI_HERB_G && b == MI_HERB_G)) return MI_HERB_GG;
    if ((a == MI_HERB_G && b == MI_HERB_R) || (a == MI_HERB_R && b == MI_HERB_G)) return MI_HERB_GR;
    if ((a == MI_HERB_G && b == MI_HERB_B) || (a == MI_HERB_B && b == MI_HERB_G)) return MI_HERB_GB;
    return MI_NONE;
}

void mansion_paused_update(void) {
    struct Controller *c = gPlayer1Controller;
    s32 dx, dy;
    s32 moved = menu_dir(&dx, &dy);

    if (c->buttonPressed & START_BUTTON) { close_menu(); return; }

    if (gMansion.menu == MENU_ITEMS) {
        if (moved) {
            s32 col = gMansion.sel & 1, row = gMansion.sel >> 1;
            col = (col + dx + 2) & 1;
            row = (row + dy + 3) % 3;
            gMansion.sel = row * 2 + col;
            play_sound(SOUND_MENU_CHANGE_SELECT, gGlobalSoundSource);
        }
        if (c->buttonPressed & B_BUTTON) { close_menu(); return; }
        if (c->buttonPressed & R_TRIG) { gMansion.menu = MENU_FILES; gMansion.fileSel = 0; play_sound(SOUND_MENU_MESSAGE_NEXT_PAGE, gGlobalSoundSource); return; }
        if (c->buttonPressed & Z_TRIG) {
            if (gMansion.comboSrc < 0) {
                if (gMansion.inv[gMansion.sel].id != MI_NONE) gMansion.comboSrc = gMansion.sel;
            } else gMansion.comboSrc = -1;
            play_sound(SOUND_MENU_CLICK_FILE_SELECT, gGlobalSoundSource);
        }
        if (c->buttonPressed & A_BUTTON) {
            struct MansionSlot *s = &gMansion.inv[gMansion.sel];
            if (gMansion.comboSrc >= 0 && gMansion.comboSrc != gMansion.sel) {
                u8 r = combine_result(gMansion.inv[gMansion.comboSrc].id, s->id);
                if (r != MI_NONE) {
                    s->id = r;
                    gMansion.inv[gMansion.comboSrc].id = MI_NONE;
                    play_sound(SOUND_MENU_STAR_SOUND, gGlobalSoundSource);
                } else {
                    mansion_message("Those cannot be combined.");
                    play_sound(SOUND_MENU_CAMERA_BUZZ, gGlobalSoundSource);
                }
                gMansion.comboSrc = -1;
            } else if (s->id != MI_NONE) {
                use_item(gMansion.sel);
            }
        }
    } else if (gMansion.menu == MENU_FILES) {
        if (dy || dx) {
            gMansion.fileSel = (gMansion.fileSel + (dx ? dx : dy) + NUM_FILES) % NUM_FILES;
            play_sound(SOUND_MENU_CHANGE_SELECT, gGlobalSoundSource);
        }
        if (c->buttonPressed & (B_BUTTON | R_TRIG)) { gMansion.menu = MENU_ITEMS; play_sound(SOUND_MENU_MESSAGE_NEXT_PAGE, gGlobalSoundSource); }
    } else if (gMansion.menu == MENU_BOX) {
        if (dx) { gMansion.boxSide ^= 1; play_sound(SOUND_MENU_CHANGE_SELECT, gGlobalSoundSource); }
        if (dy) {
            if (gMansion.boxSide == 0) gMansion.sel = (gMansion.sel + dy + MANSION_INV_SLOTS) % MANSION_INV_SLOTS;
            else gMansion.boxSel = (gMansion.boxSel + dy + MANSION_BOX_SLOTS) % MANSION_BOX_SLOTS;
            play_sound(SOUND_MENU_CHANGE_SELECT, gGlobalSoundSource);
        }
        if (c->buttonPressed & B_BUTTON) { close_menu(); return; }
        if (c->buttonPressed & A_BUTTON) {
            struct MansionSlot *from, *to;
            s32 i;
            if (gMansion.boxSide == 0) { from = &gMansion.inv[gMansion.sel]; to = NULL;
                for (i = 0; i < MANSION_BOX_SLOTS; i++) if (gMansion.box[i].id == MI_NONE) { to = &gMansion.box[i]; break; }
            } else { from = &gMansion.box[gMansion.boxSel]; to = NULL;
                for (i = 0; i < MANSION_INV_SLOTS; i++) if (gMansion.inv[i].id == MI_NONE) { to = &gMansion.inv[i]; break; }
            }
            if (from->id != MI_NONE && to != NULL) { *to = *from; from->id = MI_NONE; play_sound(SOUND_MENU_CLICK_FILE_SELECT, gGlobalSoundSource); }
            else play_sound(SOUND_MENU_CAMERA_BUZZ, gGlobalSoundSource);
        }
    }
    if (gMansion.msgTimer > 0) gMansion.msgTimer--;
}

/* ------------------------------------------------------------------------ */
/* HUD                                                                      */
/* ------------------------------------------------------------------------ */

static const char *const sCondText[3] = {
    "<COL_40E060FF>FINE<COL_--------> ", "<COL_F0D030FF>CAUTION<COL_--------> ", "<COL_F03030FF>DANGER<COL_--------> "
};

static void num_to_str(char *dst, s32 n) {
    char tmp[12];
    s32 i = 0, j = 0;
    if (n < 0) { dst[j++] = '-'; n = -n; }
    if (n == 0) tmp[i++] = '0';
    while (n > 0 && i < 11) { tmp[i++] = '0' + (n % 10); n /= 10; }
    while (i > 0) dst[j++] = tmp[--i];
    dst[j] = '\0';
}

#define SAFE_L 26
#define SAFE_R (SCREEN_WIDTH - 26)

static void draw_debug(void) {
    char buf[64];
    char n[14];
    buf[0] = '\0';
    str_append(buf, "x", sizeof(buf)); num_to_str(n, (s32) gMarioState->pos[0]); str_append(buf, n, sizeof(buf));
    str_append(buf, " z", sizeof(buf)); num_to_str(n, (s32) gMarioState->pos[2]); str_append(buf, n, sizeof(buf));
    str_append(buf, " cam", sizeof(buf)); num_to_str(n, gMansion.camIdx); str_append(buf, n, sizeof(buf));
    str_append(buf, " hp", sizeof(buf)); num_to_str(n, (s32) gMarioState->health >> 8); str_append(buf, n, sizeof(buf));
    print_small_text(SAFE_L, 22, buf, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
}

static void draw_box(s32 x1, s32 y1, s32 x2, s32 y2, u8 r, u8 g, u8 b, u8 a) {
    prepare_blank_box();
    render_blank_box(x1, y1, x2, y2, r, g, b, a);
    finish_blank_box();
}

// Draws text word-wrapped to maxW pixels. Returns the y after the last line.
static s32 draw_wrapped(s32 x, s32 y, const char *text, s32 maxW, s32 lineH) {
    char line[96];
    s32 len = 0;
    const char *p = text;

    line[0] = '\0';
    while (TRUE) {
        // grab the next word (leading spaces stay attached so indents survive)
        char word[48];
        s32 wl = 0;
        s32 brk = FALSE;
        while (*p == ' ' && wl < 40) word[wl++] = *p++;
        while (*p != '\0' && *p != ' ' && *p != '\n' && wl < 46) word[wl++] = *p++;
        word[wl] = '\0';
        if (len > 0 && wl > 0) {
            char test[144];
            str_copy(test, line, sizeof(test));
            str_append(test, " ", sizeof(test));
            str_append(test, word, sizeof(test));
            if (get_text_width(test, 1) > maxW) {
                print_small_text(x, y, line, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
                y += lineH;
                line[0] = '\0'; len = 0;
            }
        }
        if (wl > 0) {
            if (len > 0) { str_append(line, " ", sizeof(line)); len++; }
            str_append(line, word, sizeof(line));
            len += wl;
        }
        if (*p == ' ') { p++; }            // single separating space (extra ones are in the next word)
        if (*p == '\n') { p++; brk = TRUE; }
        if (brk || *p == '\0') {
            print_small_text(x, y, line, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
            y += lineH;
            line[0] = '\0'; len = 0;
            if (*p == '\0') break;
        }
    }
    return y;
}

static void draw_footer(const char *text) {
    print_small_text(SCREEN_WIDTH / 2, 208, text, PRINT_TEXT_ALIGN_CENTRE, PRINT_ALL, 1);
}

static void draw_menu(void) {
    s32 i;
    draw_box(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 190);
    print_small_text(SAFE_L, 16, "STATUS", PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    if (has_gun()) {
        char ab[24];
        char nb[14];
        str_copy(ab, "Handgun ammo: ", sizeof(ab));
        num_to_str(nb, gMansion.ammo); str_append(ab, nb, sizeof(ab));
        print_small_text(SAFE_L, 30, ab, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    }
    print_small_text(SAFE_R, 16, sCondText[condition()], PRINT_TEXT_ALIGN_RIGHT, PRINT_ALL, 1);
    {
        s32 w = (gMarioState->health * 120) / HEALTH_MAX;
        u8 cr = condition() == 0 ? 60 : (condition() == 1 ? 230 : 230);
        u8 cg = condition() == 0 ? 220 : (condition() == 1 ? 200 : 40);
        draw_box(SAFE_R - 120, 32, SAFE_R, 40, 40, 40, 40, 255);
        draw_box(SAFE_R - 120, 32, SAFE_R - 120 + w, 40, cr, cg, 40, 255);
    }

    if (gMansion.menu == MENU_ITEMS || gMansion.menu == MENU_BOX) {
        for (i = 0; i < MANSION_INV_SLOTS; i++) {
            s32 x, y, sel, bw, bh;
            const struct MansionSlot *s = &gMansion.inv[i];
            if (gMansion.menu == MENU_ITEMS) { x = SAFE_L + (i & 1) * 138; y = 58 + (i >> 1) * 40; bw = 130; bh = 32; }
            else { x = SAFE_L; y = 52 + i * 18; bw = 128; bh = 16; }
            sel = (i == gMansion.sel) && (gMansion.menu == MENU_ITEMS || gMansion.boxSide == 0);
            draw_box(x, y, x + bw, y + bh, sel ? 110 : 40, sel ? 110 : 40, sel ? 40 : 50, 230);
            if (gMansion.comboSrc == i) draw_box(x, y + bh - 2, x + bw, y + bh, 240, 160, 40, 255);
            if (s->id != MI_NONE) print_small_text(x + 6, y + (bh > 20 ? 10 : 3), slot_name(s), PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
        }
    }
    if (gMansion.menu == MENU_BOX) {
        print_small_text(SAFE_L + 150, 44, "ITEM BOX", PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
        for (i = 0; i < MANSION_BOX_SLOTS; i++) {
            s32 x = SAFE_L + 150, y = 58 + i * 15;
            s32 sel = (i == gMansion.boxSel) && gMansion.boxSide == 1;
            if (sel) draw_box(x - 2, y - 1, SAFE_R, y + 13, 110, 110, 40, 230);
            if (gMansion.box[i].id != MI_NONE) print_small_text(x + 4, y, slot_name(&gMansion.box[i]), PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
        }
        draw_footer("D-Pad: select   A: move   B: close");
    } else if (gMansion.menu == MENU_ITEMS) {
        draw_footer("A: use  Z: combine  R: files  B: close");
    } else if (gMansion.menu == MENU_FILES) {
        s32 f = gMansion.fileSel + 1;
        s32 have = (gMansion.files >> f) & 1;
        char head[48];
        char nbuf[14];
        head[0] = '\0';
        str_append(head, "FILE ", sizeof(head));
        num_to_str(nbuf, f); str_append(head, nbuf, sizeof(head));
        str_append(head, "/7   ", sizeof(head));
        str_append(head, have ? sFileTitles[f] : "- - -", sizeof(head));
        print_small_text(SAFE_L, 46, "<", PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
        print_small_text(SAFE_L + 14, 46, head, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
        print_small_text(SAFE_R, 46, ">", PRINT_TEXT_ALIGN_RIGHT, PRINT_ALL, 1);
        draw_box(SAFE_L - 4, 60, SAFE_R + 4, 202, 30, 28, 24, 235);
        if (have) {
            draw_wrapped(SAFE_L + 4, 64, sFileText[f], (SAFE_R - SAFE_L) - 8, 10);
        } else {
            print_small_text(SAFE_L + 4, 64, "You have not found this file yet.", PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
        }
        draw_footer("Left/Right: change file   B: back");
    }
}

void mansion_render_hud(void) {
    s32 prompt = gMansion.nearPrompt;
    if (gMansion.menu != MENU_NONE) {
        draw_menu();
        if (gMansion.msgTimer > 0) print_small_text(SCREEN_WIDTH / 2, 186, gMansion.msg, PRINT_TEXT_ALIGN_CENTRE, PRINT_ALL, 1);
        return;
    }
    draw_debug();
    // condition (bottom left)
    print_small_text(SAFE_L, SCREEN_HEIGHT - 32, sCondText[condition()], PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    print_small_text(SAFE_L, 10, gMansionRooms[gMansion.room].name, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    if (gMansion.msgTimer > 0) {
        print_small_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 56, gMansion.msg, PRINT_TEXT_ALIGN_CENTRE, PRINT_ALL, 1);
    } else if (prompt == 1) {
        print_small_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 56, "B: Open item box", PRINT_TEXT_ALIGN_CENTRE, PRINT_ALL, 1);
    } else if (prompt == 2) {
        print_small_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 56, "B: Save (uses 1 Ink Ribbon)", PRINT_TEXT_ALIGN_CENTRE, PRINT_ALL, 1);
    }
    if (has_gun()) {
        char ab[24];
        char nb[14];
        str_copy(ab, gMansion.ammo > 0 ? "AMMO " : "<COL_F03030FF>AMMO ", sizeof(ab));
        num_to_str(nb, gMansion.ammo); str_append(ab, nb, sizeof(ab));
        print_small_text(SAFE_R, SCREEN_HEIGHT - 32, ab, PRINT_TEXT_ALIGN_RIGHT, PRINT_ALL, 1);
        if (gMansion.aiming) print_small_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 32, "A: Fire", PRINT_TEXT_ALIGN_CENTRE, PRINT_ALL, 1);
    }
    if (gMansion.flash > 0) draw_box(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 255, 240, 200, 50);
    if (gMansion.fade > 0) draw_box(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, gMansion.fade);
}

/* ------------------------------------------------------------------------ */
/* objects                                                                  */
/* ------------------------------------------------------------------------ */

#define UID (o->oBehParams & 0xFF)

void bhv_mansion_pickup_init(void) {
    if (uid_get(gMansion.collected, UID)) {
        obj_mark_for_deletion(o);
        return;
    }
    o->oHomeY = o->oPosY;
    cur_obj_scale(1.0f);
}

// Objects only exist (visibly and actively) while Mario is in the room they were placed in.
static s32 obj_in_current_room(void) {
    if (find_room(o->oPosX, o->oPosZ) == gMansion.room) {
        cur_obj_unhide();
        return TRUE;
    }
    cur_obj_hide();
    return FALSE;
}

void bhv_mansion_pickup_loop(void) {
    u8 id = (o->oBehParams >> 24) & 0xFF;
    u8 amount = (o->oBehParams >> 16) & 0xFF;
    u8 extra = (o->oBehParams >> 8) & 0xFF;
    char buf[48];
    char nb[14];

    if (!obj_in_current_room()) return;
    o->oPosY = o->oHomeY + 6.0f * sins(o->oTimer * 0x500);
    if (o->oDistanceToMario < 120.0f && gMansion.menu == MENU_NONE) {
        if (id == MI_AMMO) {
            // ammo goes straight to the weapon, it doesn't take an inventory slot
            u32 total = gMansion.ammo + (amount ? amount : 10);
            gMansion.ammo = (u8) MIN(total, 99);
            uid_set(gMansion.collected, UID);
            str_copy(buf, "Picked up: Handgun Ammo (+", sizeof(buf));
            num_to_str(nb, amount ? amount : 10); str_append(buf, nb, sizeof(buf));
            str_append(buf, ")", sizeof(buf));
            mansion_message(buf);
            play_sound(SOUND_GENERAL_COIN, gGlobalSoundSource);
            obj_mark_for_deletion(o);
        } else if (mansion_inv_add(id, extra)) {
            struct MansionSlot tmp;
            tmp.id = id; tmp.extra = extra;
            uid_set(gMansion.collected, UID);
            str_copy(buf, "Picked up: ", sizeof(buf));
            str_append(buf, slot_name(&tmp), sizeof(buf));
            if (id == MI_GUN) str_append(buf, ". Hold Z to aim, A to fire.", sizeof(buf));
            mansion_message(buf);
            play_sound(SOUND_GENERAL_COIN, gGlobalSoundSource);
            obj_mark_for_deletion(o);
        } else if (gMansion.msgTimer < 20) {
            mansion_message("Your inventory is full.");
        }
    }
}

void bhv_mansion_file_init(void) {
    u8 f = (o->oBehParams >> 24) & 0xFF;
    if ((gMansion.files >> f) & 1) { obj_mark_for_deletion(o); return; }
    o->oHomeY = o->oPosY;
}

void bhv_mansion_file_loop(void) {
    u8 f = (o->oBehParams >> 24) & 0xFF;
    if (!obj_in_current_room()) return;
    o->oPosY = o->oHomeY + 6.0f * sins(o->oTimer * 0x500);
    if (o->oDistanceToMario < 120.0f && gMansion.menu == MENU_NONE && gMansion.wantMenu == MENU_NONE) {
        gMansion.files |= (1u << f);
        gMansion.wantMenu = MENU_FILES;
        gMansion.fileSel = f - 1;
        play_sound(SOUND_MENU_MESSAGE_APPEAR, gGlobalSoundSource);
        obj_mark_for_deletion(o);
    }
}

void bhv_mansion_typewriter_loop(void) {
    if (o->oDistanceToMario < 190.0f && gMansion.menu == MENU_NONE) {
        gMansion.nearPrompt = 2;
        if (gPlayer1Controller->buttonPressed & B_BUTTON) {
            s32 i, found = -1;
            for (i = 0; i < MANSION_INV_SLOTS; i++) if (gMansion.inv[i].id == MI_RIBBON) { found = i; break; }
            if (found < 0) {
                mansion_message("You need an Ink Ribbon to save.");
                play_sound(SOUND_MENU_CAMERA_BUZZ, gGlobalSoundSource);
            } else {
                gMansion.inv[found].id = MI_NONE;
                snapshot_save();
                mansion_message("Game saved.");
                play_sound(SOUND_MENU_STAR_SOUND, gGlobalSoundSource);
            }
        }
    }
}

void bhv_mansion_itembox_loop(void) {
    if (o->oDistanceToMario < 190.0f && gMansion.menu == MENU_NONE) {
        gMansion.nearPrompt = 1;
        if ((gPlayer1Controller->buttonPressed & B_BUTTON) && gMansion.wantMenu == MENU_NONE) {
            gMansion.wantMenu = MENU_BOX;
        }
    }
}

/* ---- zombies ---------------------------------------------------------- */

void bhv_mansion_zombie_init(void) {
    if (uid_get(gMansion.killed, UID)) {
        obj_mark_for_deletion(o);
        return;
    }
    o->oHealth = (o->oBehParams >> 24) & 0xFF;
    if (o->oHealth == 0) o->oHealth = 3;
    o->oAction = 0;
    o->oGravity = -4.0f;
    o->oFriction = 0.9f;
    o->oBuoyancy = 1.5f;
    cur_obj_scale(1.7f);
    cur_obj_init_animation(0);
}

void bhv_mansion_zombie_loop(void) {
    struct MarioState *m = gMarioState;
    f32 dist = o->oDistanceToMario;

    if (!obj_in_current_room()) return;
    if (gMansion.menu != MENU_NONE) return;
    if (o->oSubAction > 0) o->oSubAction--;   // bite / hit cooldown

    switch (o->oAction) {
        case 0: // lurk until Mario is near
            o->oForwardVel = 0.0f;
            if (dist < 1100.0f) {
                o->oAction = 1;
                play_sound(SOUND_OBJ_GOOMBA_ALERT, o->header.gfx.cameraToObject);
            }
            break;
        case 1: // shamble toward Mario
            cur_obj_rotate_yaw_toward(o->oAngleToMario, 0x120);
            o->oForwardVel = 4.5f;
            if (dist < 115.0f && o->oSubAction == 0 && !(m->action & ACT_FLAG_INVULNERABLE) && m->invincTimer == 0) {
                m->interactObj = o;
                m->hurtCounter += 8;    // two wedges of health
                m->faceAngle[1] = obj_angle_to_object(m->marioObj, o);
                m->forwardVel = -14.0f;
                set_mario_action(m, ACT_BACKWARD_GROUND_KB, 0);
                play_sound(SOUND_MARIO_ATTACKED, m->marioObj->header.gfx.cameraToObject);
                o->oSubAction = 70;
                o->oForwardVel = 0.0f;
            }
            if (o->oSubAction > 0 && o->oSubAction > 40) o->oForwardVel = 0.0f;
            break;
        case 2: // staggered
            o->oForwardVel *= 0.85f;
            if (o->oTimer > 14) o->oAction = 1;
            break;
        case 3: // dying
            o->oForwardVel = 0.0f;
            o->header.gfx.scale[1] *= 0.93f;
            if (o->oTimer > 36) {
                uid_set(gMansion.killed, UID);
                obj_mark_for_deletion(o);
                return;
            }
            break;
    }

    // Mario's punches and kicks
    if (o->oAction != 3 && (m->action & ACT_FLAG_ATTACKING) && dist < 170.0f && o->oSubAction < 60) {
        s16 toZombie = obj_angle_to_object(m->marioObj, o);
        if (abs_angle_diff(toZombie, m->faceAngle[1]) < 0x3000 && o->oHealth > 0) {
            if (!(o->oInteractStatus & 0x1)) {
                o->oHealth--;
                o->oInteractStatus |= 0x1;
                o->oMoveAngleYaw = toZombie;
                o->oForwardVel = 22.0f;
                o->oVelY = 8.0f;
                play_sound(SOUND_ACTION_HIT, o->header.gfx.cameraToObject);
                o->oAction = (o->oHealth <= 0) ? 3 : 2;
                o->oTimer = 0;
            }
        }
    } else {
        o->oInteractStatus &= ~0x1;
    }

    cur_obj_move_standard(-78);
}
