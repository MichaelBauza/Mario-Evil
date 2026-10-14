#include <PR/ultratypes.h>
#include <string.h>

#include "sm64.h"
#include "audio/external.h"
#include "camera.h"
#include "game_init.h"
#include "mario.h"
#include "level_update.h"
#include "object_list_processor.h"
#include "engine/math_util.h"
#include "print.h"
#include "puppyprint.h"
#include "behavior_data.h"
#include "mansion.h"
#include "mansion_cine.h"

#include "mansion_cine_data.inc.h"

/* Runtime camera and actor interpolation. The camera is rebuilt every frame from these. */
static Vec3f sCamPos, sCamFocus;
static f32   sCamFov;
static Vec3f sFromPos, sFromFocus;
static f32   sFromFov;
static Vec3f sActorFrom;
static s16   sActorYawFrom;

static const struct CineScript *cur_script(void) { return &gCines[gMansion.cine - 1]; }
static const struct CineStep *cur_step(void) { return &cur_script()->steps[gMansion.cineStep]; }

/* Find a live actor by number. Looked up every frame so no pointer outlives a level reload. */
static struct Object *find_actor(u8 id) {
    s32 l;
    for (l = 0; l < NUM_OBJ_LISTS; l++) {
        struct ObjectNode *head = &gObjectLists[l];
        struct ObjectNode *n;
        for (n = head->next; n != head; n = n->next) {
            struct Object *o = (struct Object *) n;
            if (o->behavior == bhvMansionActor && (o->oBehParams & 0xFF) == id) return o;
        }
    }
    return NULL;
}

/* 0 at the start of a step, 1 at the end; smoothstep so moves ease in and out. */
static f32 ease(s32 t, u16 frames) {
    f32 p;
    if (frames == 0) return 1.0f;
    p = (f32) t / (f32) frames;
    if (p > 1.0f) p = 1.0f;
    return p * p * (3.0f - 2.0f * p);
}

static void step_begin(void) {
    const struct CineStep *st = cur_step();
    gMansion.cineT = 0;
    gMansion.cineChars = 0;
    if (st->op == CINE_CAM) {
        vec3f_copy(sFromPos, sCamPos);
        vec3f_copy(sFromFocus, sCamFocus);
        sFromFov = sCamFov;
    } else if (st->op == CINE_MOVE || st->op == CINE_ROT) {
        struct Object *a = find_actor(st->actor);
        if (a != NULL) {
            sActorFrom[0] = a->oPosX; sActorFrom[1] = a->oPosY; sActorFrom[2] = a->oPosZ;
            sActorYawFrom = a->oFaceAngleYaw;
        }
    }
}

static void cine_end(void) {
    gMansion.cineSeen |= 1u << (gMansion.cine - 1);
    gMansion.cine = 0;
    gMansion.camIdx = -1;      // next frame the gameplay camera re-picks its angle
    gMansion.camLatch = 0;
    gMansion.camCooldown = 0;
}

static void cine_next(void) {
    gMansion.cineStep++;
    if (gMansion.cineStep >= cur_script()->nSteps) {
        cine_end();
    } else {
        step_begin();
    }
}

static void cine_start(s32 i) {
    if (gCines[i].nSteps == 0) return;
    gMansion.cine = i + 1;
    gMansion.cineStep = 0;
    vec3f_copy(sCamPos, gLakituState.pos);
    vec3f_copy(sCamFocus, gLakituState.focus);
    sCamFov = gMansionFov;
    step_begin();
}

void mansion_cine_check(void) {
    s32 i;
    struct MarioState *m = gMarioState;
    if (gMansion.cine || gMansion.doorState || gMansion.endTimer > 0 || gMansion.escape == 3) return;
    for (i = 0; i < gMansionCineCount; i++) {
        const struct CineScript *cs = &gCines[i];
        if (gMansion.cineSeen & (1u << i)) continue;
        if (m->pos[0] >= cs->zx0 && m->pos[0] <= cs->zx1 && m->pos[2] >= cs->zz0 && m->pos[2] <= cs->zz1) {
            cine_start(i);
            return;
        }
    }
}

void mansion_cine_pre(void) {
    const struct CineStep *st;
    struct Controller *ctl = gPlayer1Controller;
    s32 t, finished = 0;
    if (!gMansion.cine) return;
    st = cur_step();
    t = gMansion.cineT;

    switch (st->op) {
        case CINE_CAM: {
            f32 e = ease(t, st->frames);
            s32 k;
            for (k = 0; k < 3; k++) {
                sCamPos[k]   = sFromPos[k]   + ((f32) st->v[k]     - sFromPos[k])   * e;
                sCamFocus[k] = sFromFocus[k] + ((f32) st->v[k + 3] - sFromFocus[k]) * e;
            }
            sCamFov = sFromFov + ((f32) st->v[6] - sFromFov) * e;
            finished = (t >= st->frames);
            break;
        }
        case CINE_MOVE: {
            struct Object *a = find_actor(st->actor);
            f32 e = ease(t, st->frames);
            if (a != NULL) {
                a->oPosX = sActorFrom[0] + ((f32) st->v[0] - sActorFrom[0]) * e;
                a->oPosY = sActorFrom[1] + ((f32) st->v[1] - sActorFrom[1]) * e;
                a->oPosZ = sActorFrom[2] + ((f32) st->v[2] - sActorFrom[2]) * e;
            }
            finished = (t >= st->frames);
            break;
        }
        case CINE_ROT: {
            struct Object *a = find_actor(st->actor);
            f32 e = ease(t, st->frames);
            if (a != NULL) {
                a->oFaceAngleYaw = (s16) (sActorYawFrom + (s16) (st->v[0] - sActorYawFrom) * e);
            }
            finished = (t >= st->frames);
            break;
        }
        case CINE_WAIT:
            finished = (t >= st->frames);
            break;
        case CINE_SFX:
            play_sound(st->sfx, gGlobalSoundSource);
            finished = 1;
            break;
        case CINE_TEXT: {
            s32 total = (s32) strlen(st->line0) + (s32) strlen(st->line1);
            if (ctl->buttonPressed & (A_BUTTON | B_BUTTON)) {
                if (gMansion.cineChars < total) {
                    gMansion.cineChars = total;       // first press reveals the whole page
                } else {
                    finished = 1;
                }
            }
            if (!finished && gMansion.cineChars < total && (t % 2) == 0) gMansion.cineChars++;
            break;
        }
        default:
            finished = 1;
            break;
    }

    if (finished) {
        cine_next();
    } else if (gMansion.cine) {
        gMansion.cineT++;
    }
}

s32 mansion_cine_camera(struct Camera *c) {
    Vec3f pos, focus;
    s16 yaw;
    if (!gMansion.cine) return FALSE;
    vec3f_copy(pos, sCamPos);
    vec3f_copy(focus, sCamFocus);
    vec3f_copy(c->pos, pos);
    vec3f_copy(c->focus, focus);
    vec3f_copy(gLakituState.curPos, pos);
    vec3f_copy(gLakituState.curFocus, focus);
    vec3f_copy(gLakituState.goalPos, pos);
    vec3f_copy(gLakituState.goalFocus, focus);
    vec3f_copy(gLakituState.pos, pos);
    vec3f_copy(gLakituState.focus, focus);
    yaw = atan2s(pos[2] - focus[2], pos[0] - focus[0]);
    c->yaw = yaw;
    c->nextYaw = yaw;
    gLakituState.yaw = yaw;
    gLakituState.nextYaw = yaw;
    gLakituState.roll = 0;
    gLakituState.posHSpeed = 0.f;
    gLakituState.posVSpeed = 0.f;
    gMansionFov = sCamFov;
    return TRUE;
}

/* Dialogue box: speaker name, two lines revealed a character at a time, A to skip / advance. */
void mansion_cine_render(void) {
    const struct CineStep *st;
    s32 total, n0, k0, k1;
    char b0[48], b1[48];
    if (!gMansion.cine) return;
    st = cur_step();
    if (st->op != CINE_TEXT) return;

    total = (s32) strlen(st->line0) + (s32) strlen(st->line1);
    n0 = (s32) strlen(st->line0);
    k0 = MIN(gMansion.cineChars, n0);
    k1 = MAX(0, MIN(gMansion.cineChars - n0, (s32) strlen(st->line1)));
    memcpy(b0, st->line0, k0); b0[k0] = 0;
    memcpy(b1, st->line1, k1); b1[k1] = 0;

    prepare_blank_box();
    render_blank_box(16, 146, SCREEN_WIDTH - 16, 222, 0, 0, 0, 220);
    finish_blank_box();
    if (st->speaker != NULL) print_small_text(28, 152, st->speaker, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    print_small_text(28, 170, b0, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    print_small_text(28, 186, b1, PRINT_TEXT_ALIGN_LEFT, PRINT_ALL, 1);
    if (gMansion.cineChars >= total && (gMansion.cineT / 10) % 2 == 0) {
        print_small_text(SCREEN_WIDTH - 28, 206, "A", PRINT_TEXT_ALIGN_RIGHT, PRINT_ALL, 1);
    }
}
