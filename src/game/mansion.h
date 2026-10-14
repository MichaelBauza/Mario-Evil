#ifndef MANSION_H
#define MANSION_H

#include <PR/ultratypes.h>
#include "types.h"

// Mario EVIL: survival-horror systems layered on the SM64 engine (built on the LEVEL_BBH slot).

#define MANSION_INV_SLOTS 6
#define MANSION_BOX_SLOTS 12
#define MANSION_MAX_UIDS  128

enum MansionItem {
    MI_NONE, MI_HERB_G, MI_HERB_R, MI_HERB_B, MI_RIBBON, MI_KEY, MI_GUN,
    MI_HERB_GG, MI_HERB_GR, MI_HERB_GB, MI_COUNT
};

enum MansionMenu { MENU_NONE, MENU_ITEMS, MENU_FILES, MENU_BOX };

struct MansionRoom { s16 x0, z0, x1, z1; u8 camFirst, camCount; const char *name; };
struct MansionCam  { s16 zx0, zz0, zx1, zz1; s16 px, py, pz; s16 fx, fy, fz; u8 fov; };
struct MansionDoor { u8 room; s16 x, z; s8 nx, nz; u8 dest; u8 key; s16 sx, sz; u16 yaw; };

struct MansionSlot { u8 id; u8 extra; };

struct MansionState {
    // runtime
    u8  room;
    s8  camIdx;
    u8  started;
    u8  doorState;      // 0 idle, 1 fading out, 2 fading in
    u8  doorTarget;
    s16 doorTimer;
    u8  fade;
    u8  doorPush;
    u8  lockedUnlocked[8];   // bit per door index
    // messages
    char msg[40];
    s16 msgTimer;
    // menu
    u8  menu;
    s8  sel;
    s8  boxSel;
    s8  comboSrc;
    s8  fileSel;
    u8  boxSide;
    u8  wantMenu;
    u8  wantFile;
    s8  stickLatchX, stickLatchY;
    // persistent
    struct MansionSlot inv[MANSION_INV_SLOTS];
    struct MansionSlot box[MANSION_BOX_SLOTS];
    u32 files;
    u32 collected[MANSION_MAX_UIDS / 32];
    u32 killed[MANSION_MAX_UIDS / 32];
    // RAM save point (typewriter)
    u8  hasSave;
    s16 saveHealth;
    f32 savePos[3];
    s16 saveYaw;
    struct MansionSlot saveInv[MANSION_INV_SLOTS];
    struct MansionSlot saveBox[MANSION_BOX_SLOTS];
    u32 saveFiles;
    u32 saveCollected[MANSION_MAX_UIDS / 32];
    u32 saveKilled[MANSION_MAX_UIDS / 32];
    u8  saveUnlocked[8];
    u8  nearPrompt;     // 0 none, 1 open box, 2 typewriter
};

extern struct MansionState gMansion;
extern f32 gMansionFov;
extern const struct MansionRoom gMansionRooms[];
extern const struct MansionCam gMansionCams[];
extern const struct MansionDoor gMansionDoors[];

struct Camera;
struct GraphNode;

s32  lvl_mansion_init(s16 arg, s32 unused);
void mansion_pre_update(void);
void mansion_post_update(void);
void mansion_camera(struct Camera *c);
void mansion_render_hud(void);
s32  mansion_wants_pause(void);
void mansion_enter_pause(void);
void mansion_paused_update(void);
Gfx *geo_switch_mansion_room(s32 callContext, struct GraphNode *node, void *context);

void mansion_message(const char *text);
s32  mansion_inv_add(u8 id, u8 extra);

void bhv_mansion_pickup_init(void);
void bhv_mansion_pickup_loop(void);
void bhv_mansion_file_init(void);
void bhv_mansion_file_loop(void);
void bhv_mansion_typewriter_loop(void);
void bhv_mansion_itembox_loop(void);
void bhv_mansion_zombie_init(void);
void bhv_mansion_zombie_loop(void);

#endif // MANSION_H
