.definelabel REWARD_TABLE,0x002FDE00

.org 0x00269368
.func REWARD_HOOK
    lhu t1, 0x02(v0)        // load the table index as a halfword instead of a byte
    beqz t1, 0x00269438
    nop
    j REWARD_FUNC
.endfunc

.org 0x002FDC20
.func REWARD_FUNC
    addiu v0, t1, -0x1
    sll v0, 0x4             // Reward Table entries are 16 bytes long
    li at, REWARD_TABLE
    addu at, v0

    dmove s2, zero
    start_loop:
    addiu s2, 0x1
    lbu a0, (at)
    beqz a0, return
    nop

    li v0, 0x01             // reward type = item
    beq a0, v0, is_item
    nop

    li v0, 0x02             // reward type = flag
    beq a0, v0, is_flag
    nop

    b return
    nop

    is_item:
    lbu t1, 0x02(at)        // load item id
    j REWARD_GIVE_ITEM
    lbu t2, 0x03(at)        // load amount
    slti t1, s2, 0x4
    bnez t1, start_loop
    addiu at, 0x4           // each entry is 4 bytes long
    b return
    nop

    is_flag:
    j REWARD_SET_FLAG
    lhu a0, 0x02(at)        // load flag id
    slti t1, s2, 0x4
    bnez t1, start_loop
    addiu at, 0x4           // each entry is 4 bytes long

    return:
    j REWARD_HOOK + 0xD0
    nop
.endfunc

// This function is essentially copy pasted from the original code
.func REWARD_GIVE_ITEM
    addiu sp, -0x28
    sd v0, (sp)
    sd v1, 0x8(sp)
    sd a1, 0x10(sp)
    sd a2, 0x18(sp)
    sd a3, 0x20(sp)

    dmove a1, zero
    dmove t0, a3
    addiu t3, s0, 0xC
    addiu a2, a1, 0x90
    nop

    check_item_exists_loop_start:
    addiu a1, 0x1
    addu v1, t0, a2
    lbu v0, (v1)
    bne v0, t1, check_item_exists_loop_end
    slti a0, a1, 0x0004
    addu v1, t3, a2
    lbu v0, (v1)
    addu v0, t2
    b return2
    sb v0, (v1)
    check_item_exists_loop_end:
    bnez a0, check_item_exists_loop_start
    addiu a2, a1, 0x90

    dmove a1, zero
    dmove t0, a3
    addiu t3, s0, 0xC
    addiu a2, a1, 0x90
    nop

    give_new_item_loop_start:
    addiu a1, 0x01
    addu a0, t0, a2
    lbu v0, (a0)
    bnez v0, give_new_item_loop_end
    slti v1, a1, 0x0004
    addu v0, t3, a2
    sb t1, (a0)
    b return2
    sb t2, (v0)

    give_new_item_loop_end:
    bnez v1, give_new_item_loop_start
    addiu a2, a1, 0x90

    return2:
    ld v0, (sp)
    ld v1, 0x8(sp)
    ld a1, 0x10(sp)
    ld a2, 0x18(sp)
    ld a3, 0x20(sp)
    j is_item + 0xC
    addiu sp, 0x28
.endfunc

// This function is essentially copy pasted from the original code
.func REWARD_SET_FLAG
    addiu sp, -0x28
    sd v0, (sp)
    sd v1, 0x8(sp)
    sd a1, 0x10(sp)
    sd a2, 0x18(sp)
    sd a3, 0x20(sp)

    slti v1, a0, 0x0000
    addiu a3, a0, 0x1F
    dmove v0, a0
    lw a2, -0x5750(gp)
    movn v0, a3, v1
    li a1, 0x1
    sra v0, 0x05
    sllv a1, a0
    sll v0, v0, 0x02
    addiu v0, 0x840
    addu a2, v0
    lw v1, (a2)
    or v1, a1
    sw v1, (a2)

    ld v0, (sp)
    ld v1, 0x8(sp)
    ld a1, 0x10(sp)
    ld a2, 0x18(sp)
    ld a3, 0x20(sp)
    j is_flag + 0x8
    addiu sp, 0x28
.endfunc
