; adaption of the hostfs patch file by TGE
; skip mount of dds3.ddt/img
.org 0x00101CDC
.func HOSTFS_MOUNT_NOP
    nop
.endfunc

; set host base directory to './dds3data'
.org 0x0052DEF8
.func HOSTFS_DDS3_PATH
    .ascii "./dds3data"
    .halfword 0x0000 
.endfunc

; set primary device id to 1 (host)
.org 0x00101D64
.func HOSTFS_PRIMARY_DEVICE
    addiu a0, zero, 0x0001
.endfunc

; patch special treatment of movie files
.org 0x002BF270
.func HOSTFS_MOVIE_FILES
    addiu a0, zero, 0x0007
.endfunc

; patch device ids
.org 0x002BF304
.func HOSTFS_DEVICE_IDS
    lbu a1, 0xD7EE(gp)
    sw v0, 0x0000(s2)
    lbu v0, 0xD7EE(gp)
.endfunc