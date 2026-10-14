#include "seq_macros.inc"

.section .rodata
.align 0

// Mario EVIL main-menu music: one long sampled note (Beneath the Floorboards), re-triggered forever.
sequence_start:
seq_setmutebhv 0x20
seq_setmutescale 0
seq_setvol 127
seq_settempo 120
seq_initchannels 0x0001
seq_startchannel 0, .title_channel
.title_loop:
seq_delay 20000
seq_jump .title_loop

.title_channel:
chan_largenoteson
chan_setinstr 0
chan_setvol 127
chan_setpan 64
chan_setlayer 0, .title_layer
.title_channel_loop:
chan_delay 20000
chan_jump .title_channel_loop

.title_layer:
layer_note1 39, 15770, 127
layer_jump .title_layer
