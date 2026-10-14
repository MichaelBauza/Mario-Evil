#include <PR/ultratypes.h>
#include <string.h>

#include "sm64.h"
#include "audio/external.h"
#include "camera.h"
#include "game_init.h"
#include "level_update.h"
#include "mario.h"
#include "object_list_processor.h"
#include "engine/math_util.h"
#include "print.h"
#include "puppyprint.h"
#include "behavior_data.h"
#include "mansion.h"
#include "mansion_cine.h"

#include "mansion_cine_data.inc.h"

/* A group is a run of steps that play at the same time (a step with par=1 joins the step before it).
   Each member keeps its own start snapshot, indexed by its position in the group. */
#define CINE_MAX_GROUP 6

static Vec3f sCamPos, sCamFocus;          // the camera the cinematic is showing now
static f32   sCamFov;
static Vec3f sSnapPos[CINE_MAX_GROUP], sSnapFocus[CINE_MAX_GROUP];
static f32   sSnapFov[CINE_MAX_GROUP];
static s16   sSnapYaw[CINE_MAX_GROUP];

/* Walking drives Mario through his own walk action: the tank controls read the forward stick, so the
   cinematic feeds a forward push matched to its walk speed (set after the pad is cleared each frame). */
static s32   sWalkFeed;
static s16   sWalkStickY;

static const struct CineScript *cur_script(void) { return &gCines[gMansion.cine - 1]; }

static s32 group_len(s32 first) {
    const struct CineScript *cs = cur_script();
    s32 n = 1;
    while (first + n < cs->nSteps && n < CINE_MAX_GROUP && cs->steps[first + n].par) n++;
    return n;
}

/* Find a live actor by number. Looked up every frame so no pointer outlives a level reload. */
static struct Object *find_actor(u8 id) {
    s32 l;
    for (l = 0; l < NUM_OBJ_LISTS; l++) {
        struct ObjectNode *head = &gObjectLists[l];
        struct ObjectNode *n;
        for (n = head->next; n != head; n = n->next) {
            struct Object *o = (struct Object *) n;
            if (obj_has_behavior(o, bhvMansionActor) && (o->oBehParams & 0xFF) == id) return o;
        }
    }
    return NULL;
}

/* 0 at the start of a step, 1 at the end; smoothstep so camera and prop moves ease in and out. */
static f32 ease(s32 t, u16 frames) {
    f32 p;
    if (frames == 0) return 1.0f;
    p = (f32) t / (f32) frames;
    if (p > 1.0f) p = 1.0f;
    return p * p * (3.0f - 2.0f * p);
}

static f32 linear(s32 t, u16 frames) {
    f32 p;
    if (frames == 0) return 1.0f;
    p = (f32) t / (f32) frames;
    return p > 1.0f ? 1.0f : p;
}

static void group_begin(void) {
    const struct CineScript *cs = cur_script();
    s32 first = gMansion.cineStep, n = group_len(first), k;
    gMansion.cineT = 0;
    gMansion.cineChars = 0;
    for (k = 0; k < n; k++) {
        const struct CineStep *st = &cs->steps[first + k];
        if (st->op == CINE_CAM) {
            vec3f_copy(sSnapPos[k], sCamPos);
            vec3f_copy(sSnapFocus[k], sCamFocus);
            sSnapFov[k] = sCamFov;
        } else if (st->op == CINE_MOVE || st->op == CINE_ROT) {
            struct Object *a = find_actor(st->actor);
            if (a != NULL) {
                sSnapPos[k][0] = a->oPosX; sSnapPos[k][1] = a->oPosY; sSnapPos[k][2] = a->oPosZ;
                sSnapYaw[k] = a->oFaceAngleYaw;
            }
        } else if (st->op == CINE_WALK) {
            vec3f_copy(sSnapPos[k], gMarioState->pos);
            set_mario_action(gMarioState, ACT_WALKING, 0);
        }
    }
}

/* Mario is put back on his feet when a walk ends. */
static void walk_stop(void) {
    gMarioState->forwardVel = 0.0f;
    set_mario_action(gMarioState, ACT_IDLE, 0);
}

static void cine_end(void) {
    sWalkFeed = 0;
    if (cur_script()->once) gMansion.cineSeen |= 1u << (gMansion.cine - 1);
    gMansion.cineCool = 20;
    gMansion.cine = 0;
    gMansion.camIdx = -1;      // next frame the gameplay camera re-picks its angle
    gMansion.camLatch = 0;
    gMansion.camCooldown = 0;
    walk_stop();
}

/* Advance past the group that just finished. */
static void group_next(s32 n) {
    gMansion.cineStep += n;
    if (gMansion.cineStep >= cur_script()->nSteps) {
        cine_end();
    } else {
        group_begin();
    }
}

static void cine_start(s32 i) {
    if (gCines[i].nSteps == 0) return;
    gMansion.cine = i + 1;
    gMansion.cineStep = 0;
    sWalkFeed = 0;
    vec3f_copy(sCamPos, gLakituState.pos);
    vec3f_copy(sCamFocus, gLakituState.focus);
    sCamFov = gMansionFov;
    group_begin();
}

void mansion_cine_check(void) {
    s32 i;
    struct MarioState *m = gMarioState;
    if (gMansion.cineCool > 0) gMansion.cineCool--;
    if (gMansion.cine || gMansion.doorState || gMansion.endTimer > 0 || gMansion.escape == 3) return;
    if (gMansion.menu != MENU_NONE || gMansion.wantMenu || gMansion.cineCool > 0) return;   // not while the title or pause menu is up or pending
    for (i = 0; i < gMansionCineCount; i++) {
        const struct CineScript *cs = &gCines[i];
        if (cs->once && (gMansion.cineSeen & (1u << i))) continue;
        if (cs->talkActor != 255) {
            /* talk: near the actor, the prompt shows; B starts it */
            struct Object *a = find_actor(cs->talkActor);
            f32 dx, dz;
            if (a == NULL) continue;
            dx = a->oPosX - m->pos[0];
            dz = a->oPosZ - m->pos[2];
            if (dx * dx + dz * dz > (f32) cs->talkRadius * (f32) cs->talkRadius) continue;
            gMansion.nearPrompt = 5;
            if (gPlayer1Controller->buttonPressed & B_BUTTON) {
                cine_start(i);
                return;
            }
            continue;
        }
        if (gMansion.cineSeen & (1u << i)) continue;
        if (m->pos[0] >= cs->zx0 && m->pos[0] <= cs->zx1 && m->pos[2] >= cs->zz0 && m->pos[2] <= cs->zz1) {
            cine_start(i);
            return;
        }
    }
}

/* One member of the running group. Returns TRUE when it is finished. */
static s32 member_step(const struct CineStep *st, s32 k, s32 t) {
    switch (st->op) {
        case CINE_CAM: {
            f32 e = ease(t, st->frames);
            s32 j;
            for (j = 0; j < 3; j++) {
                sCamPos[j]   = sSnapPos[k][j]   + ((f32) st->v[j]     - sSnapPos[k][j])   * e;
                sCamFocus[j] = sSnapFocus[k][j] + ((f32) st->v[j + 3] - sSnapFocus[k][j]) * e;
            }
            sCamFov = sSnapFov[k] + ((f32) st->v[6] - sSnapFov[k]) * e;
            return t >= st->frames;
        }
        case CINE_MOVE: {
            struct Object *a = find_actor(st->actor);
            f32 e = ease(t, st->frames);
            if (a != NULL) {
                a->oPosX = sSnapPos[k][0] + ((f32) st->v[0] - sSnapPos[k][0]) * e;
                a->oPosY = sSnapPos[k][1] + ((f32) st->v[1] - sSnapPos[k][1]) * e;
                a->oPosZ = sSnapPos[k][2] + ((f32) st->v[2] - sSnapPos[k][2]) * e;
            }
            return t >= st->frames;
        }
        case CINE_ROT: {
            struct Object *a = find_actor(st->actor);
            f32 e = ease(t, st->frames);
            if (a != NULL) {
                a->oFaceAngleYaw = (s16) (sSnapYaw[k] + (s16) (st->v[0] - sSnapYaw[k]) * e);
            }
            return t >= st->frames;
        }
        case CINE_WALK: {
            struct MarioState *m = gMarioState;
            f32 e = linear(t, st->frames);
            f32 dx = (f32) st->v[0] - sSnapPos[k][0], dz = (f32) st->v[2] - sSnapPos[k][2];
            f32 dist = sqrtf(dx * dx + dz * dz);
            s16 yaw = atan2s(dz, dx);
            s32 j;
            /* Position is set here, before Mario's own physics runs; the walk speed keeps the walk animation going. */
            m->pos[0] = sSnapPos[k][0] + dx * e;
            m->pos[1] = sSnapPos[k][1] + ((f32) st->v[1] - sSnapPos[k][1]) * e;
            m->pos[2] = sSnapPos[k][2] + dz * e;
            f32 speed = (st->frames > 0) ? dist / (f32) st->frames : 0.0f;
            s32 done = (t >= st->frames);
            /* walk action: forward speed = stickY / 4 under tank controls, so stickY = 4 * speed */
            m->forwardVel = speed;
            m->faceAngle[1] = yaw;
            m->intendedYaw = yaw;
            for (j = 0; j < 3; j++) m->vel[j] = 0.0f;
            if (!done) {
                s32 y = (s32) (4.0f * speed + 0.5f);
                sWalkStickY = (s16) (y < 16 ? 16 : (y > 64 ? 64 : y));
                sWalkFeed = 1;
            }
            return done;
        }
        case CINE_WAIT:
            return t >= st->frames;
        case CINE_SFX:
            play_sound(st->sfx, gGlobalSoundSource);
            return TRUE;
        default:
            return TRUE;
    }
}

/* Called after the pad is cleared, so the walk's forward push survives. */
void mansion_cine_feed_input(void) {
    struct Controller *ctl = gPlayer1Controller;
    if (!gMansion.cine || !sWalkFeed) return;
    ctl->stickX = 0; ctl->rawStickX = 0;
    ctl->stickY = sWalkStickY; ctl->rawStickY = sWalkStickY;
    ctl->stickMag = sWalkStickY;
}

void mansion_cine_pre(void) {
    const struct CineScript *cs;
    const struct CineStep *first;
    struct Controller *ctl = gPlayer1Controller;
    s32 n, k, t, allDone = 1;
    if (!gMansion.cine) return;
    sWalkFeed = 0;
    cs = cur_script();
    first = &cs->steps[gMansion.cineStep];
    t = gMansion.cineT;

    if (first->op == CINE_TEXT) {
        /* dialogue: one page at a time; A reveals the page, then A moves on */
        s32 total = (s32) strlen(first->line0) + (s32) strlen(first->line1);
        if (ctl->buttonPressed & (A_BUTTON | B_BUTTON)) {
            if (gMansion.cineChars < total) {
                gMansion.cineChars = total;
            } else {
                group_next(1);
                return;
            }
        }
        if (gMansion.cine && gMansion.cineChars < total && (t % 2) == 0) gMansion.cineChars++;
        if (gMansion.cine) gMansion.cineT++;
        return;
    }

    n = group_len(gMansion.cineStep);
    for (k = 0; k < n; k++) {
        if (!member_step(&cs->steps[gMansion.cineStep + k], k, t)) allDone = 0;
    }
    if (allDone) {
        for (k = 0; k < n; k++) {
            if (cs->steps[gMansion.cineStep + k].op == CINE_WALK) { walk_stop(); break; }
        }
        group_next(n);
    } else {
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

/* Dialogue box: speaker name, two lines revealed a character at a time, A to reveal / advance. */
void mansion_cine_render(void) {
    const struct CineStep *st;
    s32 total, n0, k0, k1;
    char b0[48], b1[48];
    if (!gMansion.cine) return;
    st = &cur_script()->steps[gMansion.cineStep];
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
