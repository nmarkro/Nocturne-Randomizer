.org 0x002410C4
.func HEALING_NOP
    nop
.endfunc

.org 0x0022D5FC
.func HEALING_AOE
    lhu v0,0xE(v1)
    andi v0,0x800
    bnez v0,0x0022D614
.endfunc