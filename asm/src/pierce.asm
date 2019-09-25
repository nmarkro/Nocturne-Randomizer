.org 0x00265B80
.func PIERCE_HOOK
    j PIERCE_FUNC
    lui a0, 0x003D
.endfunc

.org 0x002FE2D0
.func PIERCE_FUNC
    sll v0,v1,0x03
    addu v0,a0
    lbu v0,0x6998(v0)
    slti v0,0x0006
    j PIERCE_HOOK+0x10
    xori v1,v0,0x0001
.endfunc

.org 0x00266250
.func PIERCE_NOP
    nop
.endfunc