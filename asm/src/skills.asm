.org 0x002382D0
.func SKILLS_VISIBLE
    bltz s2,0x02383C8
.endfunc

.org 0x00222C68
.func INHERIT_ALL_HOOK
    j INHERIT_ALL_FUNC
.endfunc

.org 0x002FEFD0
.func INHERIT_ALL_FUNC
    andi v0, a0, 0x200
    slti v0, v0, 0x1FF
    j INHERIT_ALL_HOOK + 0x8
.endfunc

.org 0x00222C7C
.func INHERIT_EQ_SKILL_TIER
    li a2, 0x63
    li v0, 0x1
.endfunc