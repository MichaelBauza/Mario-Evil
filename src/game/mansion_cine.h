#ifndef MANSION_CINE_H
#define MANSION_CINE_H

#include <PR/ultratypes.h>

/* Mario EVIL cinematics. Authored in mario_evil/cinematics.py, generated into mansion_cine_data.inc.h. */

enum CineOp { CINE_CAM, CINE_TEXT, CINE_MOVE, CINE_ROT, CINE_WAIT, CINE_SFX, CINE_WALK };

struct CineStep {
    u8  op;                  // enum CineOp
    u8  actor;               // MOVE / ROT: actor number
    u8  par;                 // 1 = runs at the same time as the step before it (a group)
    u16 frames;              // duration of MOVE / ROT / CAM / WAIT (0 = instant)
    s16 v[7];                // CAM: pos xyz, focus xyz, fov.  MOVE / WALK: xyz.  ROT: yaw in v[0]
    const char *speaker;     // TEXT: speaker name, or NULL
    const char *line0;       // TEXT: dialogue lines (one page)
    const char *line1;
    u32 sfx;                 // SFX: sound macro
};

struct CineScript {
    s16 zx0, zz0, zx1, zz1;  // trigger zone (world units)
    u16 nSteps;
    const struct CineStep *steps;
};

extern const struct CineScript gCines[];
extern const s32 gMansionCineCount;

struct Camera;

void mansion_cine_check(void);                  // post-update: start a cinematic if Mario walks into its zone
void mansion_cine_pre(void);                    // pre-update: advance the running cinematic (reads A)
s32  mansion_cine_camera(struct Camera *c);     // camera override; TRUE if a cinematic is driving the camera
void mansion_cine_render(void);                 // dialogue box

#endif
