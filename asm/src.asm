.ps2

.open "out/SLUS_209.11", "out/output.elf", 0xFF000
.include "src/pierce.asm"
.include "src/skills.asm"
.include "src/healing.asm"
.include "src/recruit.asm"
.include "src/shops.asm"

.close