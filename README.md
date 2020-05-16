### Nocturne-Randomizer

This is a randomizer for Shin Megami Tensei: Nocturne.

The randomization includes: boss shuffle, enemy/demon shuffle, skill randomization, Magatama and key item drops by bosses, and race randomizer for fusion logic.

We are currently in the alpha/beta stages, and the randomizer itself is not complete with Labyrinth of Amala being blocked off. Expect changes to be frequent and game balance to be shaky.

The list of added features and changes to the randomizer can be seen on this document: https://docs.google.com/document/d/1pZ_aiLmRK1lYKKDy6A23m2iAVeU1wcVut1-mGM4vkLM

Feel free to join the Nocturne Randomizer discord: https://discord.gg/d25ZAha

### Credits

The randomizer was created and programmed by NMarkro and PinkPajamas, with additional help from:

ChampionBeef (early testing and feedback)

TGEnigma (for the AtlusScriptToolchain tools used during development)

Krisan Thyme (file format and tools documentation)

Zombero (documentation from hardtye hack)

### Running the randomizer
Windows users can download the latest from https://github.com/nmarkro/Nocturne-Randomizer/releases

Unzip and run nocturne_rando.exe

Using PCSX2 v1.5.0 or higher is recommended (download from https://pcsx2.net/download/development/dev-windows.html)

### Running the randomizer from source

Install python 3 at https://python.org

Run with: python3 randomizer.py

### Using the HostFS export format
Run nocturne_rando.exe (or from source) and follow the prompts to export to HostFS

Navigate to your PCSX2's "inis" folder and change the line "HostFs=disabled" to "HostFs=enabled" in "PCSX2_vm.ini"

Select your base, unmodified Nocturne ISO in PCSX2 and use "System -> Run ELF" and select "out/SLUS_209.11.ELF" from the randomizer's folder to boot your randomized version of Nocturne 