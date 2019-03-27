# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import copy
import struct
import re
import random

import randomizer
import races
from base_classes import Demon, Skill, Magatama, Battle

N_DEMONS = 383
N_MAGATAMAS = 25
N_BATTLES = 1270

all_demons = {}
all_magatamas = {}
all_battles = {}
all_skills = {}

# demons/bosses that absorb/repel/null phys
PHYS_INVALID_DEMONS = [2, 14, 87, 93, 98, 104, 105, 144, 155, 172, 202, 269, 274, 276, 277, 333, 334, 352]

# demons/bosses that are normally in the hospital/shibuya
BASE_DEMONS = [61, 137, 92, 97, 131, 91, 126, 103, 135, 136]

SHADY_BROKER = {
    167: 208,        # Pisaca
    124: 209,        # Nue
    144: 210,        # Arahabaki
    131: 211,        # Preta
    122: 212,        # Mothman
    105: 213,        # Girimehkala
}

def load_demons(rom):
    demon_offset = 0x0024A7F0

    demon_names = open('data/demon_names.txt', 'r').read().strip()
    demon_names = demon_names.split('\n')

    rom.seek(demon_offset)
    for i in range(N_DEMONS):
        demon_name = demon_names[i]

        demon_offset = rom.r_offset
        _, race_id, level, hp, _, mp, _, demon_id, strength, _, magic, vitality, agility, luck, battle_skills, _, macca_drop, exp_drop, _ = struct.unpack('<16sBBHHHHHBBBBBB12s8sHHH', rom.read(0x3C))

        # skip entry if it's a garbage/unknown demon
        if race_id == 0 or demon_name =='?':
            continue

        # Beelzebub (Human) and Beelzebub (Fly) share the same demon_id for some reason, so separate them
        if demon_name == 'Beelzebub':
            demon_id = 207

        demon = Demon(demon_id, demon_name)
        demon.offset = demon_offset
        demon.skill_offset = 0x00234CF4 + (demon_id * 0x66)
        demon.ai_offset = 0x002999E4 + (demon_id * 0xA4)

        demon.race = race_id
        demon.level = level
        demon.hp = hp
        demon.mp = mp
        demon.stats = [strength, magic, vitality, agility, luck]
        demon.macca_drop = macca_drop
        demon.exp_drop = exp_drop

        s = []
        for j in range(0, len(battle_skills), 2):
            skill = struct.unpack('<H', battle_skills[j : j + 2])[0]
            if skill > 0:
                s.append(skill)

        # battle skills are the skills that show up when you analyze enemy demons (used for demon ai later)
        demon.battle_skills = s
        demon.skills = load_demon_skills(rom, demon.skill_offset, level)

        demon.is_boss = bool(i >= 255)

        # keep track of phys invalid demons and demons in the hospital for "Easy Hospital" and early buff/debuff distribution
        demon.phys_inv = demon_id in PHYS_INVALID_DEMONS
        demon.base_demon = demon_id in BASE_DEMONS

        if demon_id in SHADY_BROKER.keys():
            demon.shady_broker = SHADY_BROKER[demon_id]

        all_demons[demon_id] = demon

def lookup_demon(ind):
    return all_demons.get(ind)

race_names = []
def load_races():
    names = open('data/race_names.txt', 'r').read().strip()
    names = names.split('\n')
    race_names.extend(names)

def load_demon_skills(rom, skill_offset, level):
    demon_skills = []

    rom.save_offsets()
    rom.seek(skill_offset + 0x0A)

    count = 0
    while True:
        # level at which they learn the skill 
        learn_level = rom.read_byte()
        # magic_byte indicates what event happens at learn_level
        # 0x01 = skill learned normally
        # 0x05 = skill learned through evolution only
        # 0x06 = demon evolves
        # 0x07 = "demon body is changing" text thing
        magic_byte = rom.read_byte()
        skill_id = rom.read_halfword()

        if magic_byte == 0 or count >= 23:
            break

        # skip the evolution message
        if magic_byte == 7:
            continue

        s = {
            'level': max(0, learn_level - level),
            # disregard magic_bytes currently since we are removing evolution demons
            'magic_byte': 1,
            'skill_id': skill_id,
        }

        for skill in demon_skills:
            if skill['skill_id'] == s['skill_id']:
                continue

        demon_skills.append(s)
        count += 1

    rom.load_offsets()
    return demon_skills

def load_skills(rom):
    skill_data = open('data/skill_data.txt', 'r').read().strip()
    pattern = re.compile(r"([\dABCDEF]{3}) ([\w\'\&\- ]+) (\d+) (\d+)")

    skill_data = list(map(lambda s: re.search(pattern, s), skill_data.split('\n')))

    for i in range(len(skill_data)):
        skill_id = int(skill_data[i][1], 16)
        name = skill_data[i][2]
        rank = int(skill_data[i][3])
        skill_type = int(skill_data[i][4])

        skill = Skill(skill_id, name, rank)
        skill.skill_type = skill_type

        all_skills[skill_id] = skill

def lookup_skill(ind):
    return all_skills.get(ind)

def load_magatamas(rom):
    magatama_offset = 0x0023AE3A

    magatama_names = open('data/magatama_names.txt', 'r').read().strip()
    magatama_names = magatama_names.split('\n')

    rom.seek(magatama_offset)
    for i in range(N_MAGATAMAS):
        m_name = magatama_names[i]

        m_offset = rom.r_offset
        _, strength, _, magic, vitality, agility, luck, _, skills = struct.unpack('<14sBBBBBB14s32s', rom.read(0x42))

        m = Magatama(m_name)
        m.ind = i
        m.stats = [strength, magic, vitality, agility, luck]
        
        m.level = None

        s = []
        for j in range(0, len(skills), 4):
            level, skill_id = struct.unpack('<HH', skills[j : j + 4])

            if m.level is None:
                m.level = level

            if skill_id > 0:
                skill = {
                    'level': level - m.level,
                    'skill_id': skill_id,
                }
                s.append(skill)
        m.skills = s
        m.offset = m_offset
        all_magatamas[m.name] = m

def load_battles(rom):
    offset = 0x002AFFE0

    for i in range(N_BATTLES):
        enemies = []

        for j in range(0, 18, 2):
            enemy_id = rom.read_halfword(offset + 6 + j)
            enemies.append(enemy_id)

        battle = Battle(offset)
        battle.enemies = enemies
        battle.is_boss = rom.read_halfword(offset) == 0x01FF
        battle.reward = rom.read_halfword(offset + 2)
        battle.phase_value = rom.read_halfword(offset + 4)
        battle.arena = rom.read_word(offset + 0x1C)
        battle.goes_first = rom.read_halfword(offset + 0x20)
        battle.reinforcement_value = rom.read_halfword(offset + 0x22)
        battle.music = rom.read_halfword(offset + 0x24)
        all_battles[offset] = battle
        offset += 0x26

def write_demon(rom, demon, offset):
    rom.seek(offset)

    rom.write_byte(demon.race, rom.w_offset + 0x10)
    rom.write_byte(demon.level, rom.w_offset + 0x11)
    rom.write_halfword(demon.hp, rom.w_offset + 0x12)
    rom.write_halfword(demon.hp, rom.w_offset + 0x14)
    rom.write_halfword(demon.mp, rom.w_offset + 0x16)
    rom.write_halfword(demon.mp, rom.w_offset + 0x18)

    stats = struct.pack('<BBBBBB', demon.stats[0], 0x00, demon.stats[1], demon.stats[2], demon.stats[3], demon.stats[4])
    rom.write(stats, rom.w_offset + 0x1C)

    rom.write_halfword(demon.macca_drop, rom.w_offset + 0x36)
    rom.write_halfword(demon.exp_drop, rom.w_offset + 0x38)

    # don't change boss ai or skills
    if not demon.is_boss:
        rom.seek(offset + 0x22)
        for i in range(8):
            if i < len(demon.battle_skills):
                skill = demon.battle_skills[i]
                rom.write_halfword(skill)
            else:
                rom.write_halfword(0)

        write_skills(rom, demon)
        write_ai(rom, demon)

def write_demons(rom, new_demons):
    for demon in new_demons:
        write_demon(rom, demon, demon.offset)

        if demon.shady_broker is not None:
            shady_broker_offset = 0x0024A7B4 + (demon.shady_broker)*0x3C
            write_demon(rom, demon, shady_broker_offset)
            # set the race_id back to 0 on the shady_broker demons to disable them from fusions and stuff
            rom.write_byte(0, shady_broker_offset + 0x10)

def write_skills(rom, demon):
    for i in range(len(demon.skills)):
        skill = demon.skills[i]
        offset = (demon.skill_offset + 0x0A) + (i * 0x04)
        rom.seek(offset)
        rom.write_byte(skill['level'])
        rom.write_byte(skill['magic_byte'])
        rom.write_halfword(skill['skill_id'])
        
    for i in range(len(demon.skills), 23):
        rom.write_word(0, demon.skill_offset + 0x0A + (i * 0x4))

def write_ai(rom, demon):
    offset = demon.ai_offset + 0x24

    # todo: make generating odds more random
    total_odds = [
        [100,],
        [50, 50],
        [40, 30, 30],
        [25, 25, 25, 25],
        [20, 20, 20, 20, 20],
    ]

    # 3 sets of ai skills
    for i in range(3):
        skill_pool = copy.copy(demon.battle_skills)

        # add basic attack to skill pool and shuffle
        skill_pool.append(0x8000)
        random.shuffle(skill_pool)

        # can only write a max of 5 skills per set
        num_of_skills = min(len(skill_pool), 5)
        odds = total_odds[num_of_skills - 1]

        # write the new demon ai
        for j in range(num_of_skills):
            skill = skill_pool[j]
            rom.write(struct.pack('<HHI', odds[j], skill_pool[j], 0), offset)
            offset += 0x08

        # fill the rest with zeros
        for j in range(num_of_skills, 5):
            rom.write(struct.pack('<Q', 0), offset)
            offset += 0x08

def write_magatamas(rom, new_magatams):
    for magatama in new_magatams:
        stats = struct.pack('<BBBBBB', magatama.stats[0], 0xFF, magatama.stats[1], magatama.stats[2], magatama.stats[3], magatama.stats[4])
        rom.write(stats, magatama.offset + 0x0E)
        rom.write(stats, magatama.offset + 0x14)
        for i in range(len(magatama.skills)):
            skill = magatama.skills[i]
            s = magatama.offset + 0x22 + (i * 4)
            rom.write_halfword(skill['level'], s)
            rom.write_halfword(skill['skill_id'], s + 2)

def write_battles(rom, new_battles, preserve_boss_arenas=False):
    for b in new_battles:
        # only write magatama rewards
        if 345 >= b.reward >= 320:
            rom.write_halfword(b.reward, b.offset + 0x02)
        rom.write_halfword(b.phase_value, b.offset + 0x04)
        for i, e in enumerate(b.enemies):
            rom.write_halfword(e, b.offset + 0x06 + (i * 2))
        if preserve_boss_arenas:
            rom.write_word(b.arena, b.offset + 0x1C)
        rom.write_halfword(b.goes_first, b.offset + 0x20)
        rom.write_halfword(b.reinforcement_value, b.offset + 0x22)
        rom.write_halfword(b.music, b.offset + 0x24)

def patch_easy_demon_recruits(rom):
    # patch the flag check during demon recruiting to use an always(?) zero flag as oppsed to the forneus flag
    # this also doesn't work half the time for some fucking reason
    patch = 0x24040000                      # li a0, 0x0
    rom.write_word(patch, 0x00171584)       # replaces li a0, 0x8
    rom.write_word(patch, 0x001720E4)       # replaces li a0, 0x8
    rom.write_word(patch, 0x001715D8)       # replaces li a0, 0x8
    rom.write_word(patch, 0x00171670)       # replaces li a0, 0x8
    rom.write_word(patch, 0x00171A18)       # replaces li a0, 0x8
    rom.write_word(patch, 0x001719D4)       # replaces li a0, 0x8
    rom.write_word(patch, 0x001737E4)       # replaces li a0, 0x8

def patch_fix_tutorials(rom):
    # replaces the 1x preta and 2x sudamas tutorial fights with the unmodified, scipted will o' wisp demons
    tutorial_2_offset = 0x002BBBF8
    tutorial_3_offset = 0x002BBC1E

    rom.write(struct.pack('<H', 0x13E), tutorial_2_offset)
    rom.write(struct.pack('<HH', 0x13E, 0x13E), tutorial_3_offset)

def patch_early_spyglass(rom):
    # change the 3x preta fight's reward to spyglass
    rom.write_halfword(0x012E, 0x002B0DB0)
    # change the selling price of the spyglass to 0 macca
    rom.write_word(0, 0x002DD614)

def remove_shop_magatamas(rom):
    # Shibuya shop
    # remove Iyomante
    rom.write_byte(0, 0x00230718)
    # remove Shiranui
    rom.write_byte(0, 0x0023071C)

    # Underpass shop
    # remove Ankh
    rom.write_byte(0, 0x002307A2)
    # remove Hifumi
    rom.write_byte(0, 0x002307A6)
    # remove Kamudo
    rom.write_byte(0, 0x002307AA)

    # Asakusa shop
    # remove Nirvana
    rom.write_byte(0, 0x002308B6)
    # remove Gehenna
    rom.write_byte(0, 0x002308BA)

    # Asakusa Tunnel shop
    # remove Kamurogi
    rom.write_byte(0, 0x00230920)
    # remove Vimana
    rom.write_byte(0, 0x00230924)
    # remove Sophia
    rom.write_byte(0, 0x00230928)

    # ToK shop
    # remove Kailash
    rom.write_byte(0, 0x002309DE)

    # Underpass shop may be separate based on if you got Ankh from Pixie
    # remove Hifumi again(?)
    rom.write_byte(0, 0x00230A2C)
    # remove Kamudo again(?)
    rom.write_byte(0, 0x00230A30)

def patch_visible_skills(rom):
    # makes learnable skills always visible
    # code from Zombero's hardtype romhack
    patch = 0x0640003D                      # bltz s2, 0x002383C8
    rom.write_word(patch, 0x001392D0)       # replaces bnez s2, 0x002383C8

def patch_magic_pierce(rom):
    # makes the pierce skill work on magic
    # code from Zombero's hardtype romhack
    hook1 = 0x080BF8B4                      # j 0x2FE2D0 (free space)
    hook2 = 0x3C04003E                      # lui a0, 0x003E
    rom.write_word(hook1, 0x00166B80)       # replaces addiu,fp,0x7998
    rom.write_word(hook2, 0x00166B84)       # replaces sll v0,v0,0x02
    # function in free space
    rom.write_word(0x00111080, 0x1FF2D0)    # sll v0,s1,0x02
    rom.write_word(0x00441021, 0x1FF2D4)    # addu v0, a0
    rom.write_word(0x080996E2, 0x1FF2D8)    # j 0x265B88

def patch_stock_aoe_healing(rom):
    # makes aoe healing affect the stock
    # code from Zombero's hardtype romhack
    nop = 0x00000000                        # nop
    patch = 0x3042FFFF                      # andi v0,0xFFFF
    rom.write_word(nop, 0x001420C4)         # replaces beqz v1,0x002410E0
    rom.write_word(nop, 0x00191948)         # replaces beqz v0,0x0029096C
    rom.write_word(patch, 0x0012E600)       # replaces andi v0,0x0002

def fix_elemental_fusion_table(rom, demon_generator):
    fusion_table_offset = 0x0022E270

    # ids use for conversion to fusion table ids
    elem_table_ids = {
        races.race_flaemis: 0x24,
        races.race_aquans: 0x25,
        races.race_aeros: 0x26,
        races.race_erthys: 0x27,
    }

    # make all races not fuse into elementals
    for i in range(32):
        rom.write_byte(0, fusion_table_offset + i + (i*32))
    
    # use the generated elemental results to change the fusion table
    for race, elemental in zip(races.raceref, demon_generator.elemental_results):
        if elemental > 0:
            race_id = race_names.index(race)
            race_table_offset = fusion_table_offset + (race_id * 32)
            rom.write_byte(elem_table_ids[elemental], race_table_offset + race_id)

def fix_mada_summon(rom, new_demons):
    # replace the pazuzu mada summons in it's ai with a demon that is equal or less in level than mada
    pazuzu_summon_offset = 0x002A6F86
    mada = next((d for d in new_demons if d.name == "Mada (Boss)"), None)
    candidates = [d.ind for d in new_demons if d.level <= mada.level and not d.is_boss]
    if mada and candidates:
        rom.write_byte(random.choice(candidates), pazuzu_summon_offset)

def fix_nihilo_summons(rom, new_demons):
    # replace the demons summoned by the nihilo minibosses
    def replace_summons(offsets, candidates):
        replacement = random.choice(candidates)
        for off in offsets:
            rom.write_byte(replacement, off)
        return replacement

    yaka_summon_offsets = [0x0041A0FA, 0x0041A132, 0x0041A182]
    dis_summon_offsets = [0x0041A2CE, 0x0041A306, 0x0041A382, 0x0041A556]
    incubus_summon_offsets = [0x0041A4CE, 0x0041A506]

    yaka_level = next((d.level for d in all_demons.values() if d.name == "Yaka"), None)
    dis_level = next((d.level for d in all_demons.values() if d.name == "Dis"), None)
    incubus_level = next((d.level for d in all_demons.values() if d.name == "Incubus"), None)

    yaka_candidates = [d.ind for d in new_demons if d.level == yaka_level and not d.is_boss]
    dis_candidates = [d.ind for d in new_demons if d.level == dis_level and not d.is_boss]
    incubus_candidates = [d.ind for d in new_demons if d.level == incubus_level and not d.is_boss]

    replace_summons(yaka_summon_offsets, yaka_candidates)
    replace_summons(dis_summon_offsets, dis_candidates)
    replace_summons(incubus_summon_offsets, incubus_candidates)

def fix_specter_1_reward(rom, reward):
    # add rewards to each of the fused versions of specter 1
    fused_reward_offsets = [0x002B2842, 0x002B2868, 0x002B288E]
    for offset in fused_reward_offsets:
        rom.write_halfword(reward, offset)

def patch_intro_skip(iso_file):
    # overwrite an unused event script with ours
    e506_offset = 0x3F1C7800
    with open('patches/e506.bf', 'rb') as event_file:
        iso_file.seek(e506_offset)
        iso_file.write(event_file.read())

    # hook the beginning of e601 to call our e506
    e601_hook_offset = 0x4049A254
    e601_hook = bytearray([0x1D, 0x00, 0xFA, 0x01, 0x08, 0x00, 0x66, 0x00])
    iso_file.seek(e601_hook_offset)
    iso_file.write(e601_hook)

    # write 0 to the vanilla stock increases to prevent >12 stock
    iso_file.seek(0x45D3469A)
    iso_file.write(bytes(0))
    iso_file.seek(0x49CB58B6)
    iso_file.write(bytes(0))


def load_all(rom):
    load_demons(rom)
    load_races()
    load_skills(rom)
    load_magatamas(rom)
    load_battles(rom)

def write_all(rom, world):
    write_demons(rom, world.demons.values())
    write_magatamas(rom, world.magatamas.values())
    write_battles(rom, world.battles.values())

    # make the pierce skill work on magic
    patch_magic_pierce(rom)
    # make aoe healing work on the stock demons
    patch_stock_aoe_healing(rom)
    # remove magatamas from shops since they are all tied to boss drops now
    remove_shop_magatamas(rom)
    # patch the fusion table using the generated elemental results
    fix_elemental_fusion_table(rom, world.demon_generator)
    if randomizer.config_fix_tutorial:
        print("fixing tutorials")
        patch_fix_tutorials(rom)
    # this just doesn't work half the time :(
    if randomizer.config_easy_recruits:
        print("applying easy recruits patch")
        patch_easy_demon_recruits(rom)
    # add the spyglass to 3x preta fight and reduce it's selling price
    if randomizer.config_early_spyglass:
        print("applying early spyglass patch")
        patch_early_spyglass(rom)
    # make learnable skills always visible
    if randomizer.config_visible_skills:
        patch_visible_skills(rom)

    # replace the pazuzu mada summons
    fix_mada_summon(rom, world.demons.values())
    # replace the demons summoned by the nihilo minibosses
    fix_nihilo_summons(rom, world.demons.values())
    # fix the magatama drop on the fused versions of specter 1
    specter_1_reward = all_magatamas[world.get_boss("Specter 1").reward.name].ind
    specter_1_reward += 320
    fix_specter_1_reward(rom, specter_1_reward)