# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import copy
import struct
import re
import random
import os

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
        _, flag, _, race_id, level, hp, _, mp, _, demon_id, strength, _, magic, vitality, agility, luck, battle_skills, _, macca_drop, exp_drop, _ = struct.unpack('<12sH2sBBHHHHHBBBBBB12s8sHHH', rom.read(0x3C))

        # skip entry if it's a garbage/unknown demon
        if race_id == 0 or demon_name == '?':
            continue

        # Beelzebub (Human) and Beelzebub (Fly) share the same demon_id for some reason, so separate them
        if demon_name == 'Beelzebub':
            demon_id = 207

        demon = Demon(demon_id, demon_name)
        demon.offset = demon_offset
        demon.skill_offset = 0x00234CF4 + (demon_id * 0x66)
        #demon.ai_offset = 0x002999E4 + (demon_id * 0xA4)
        demon.ai_offset = 0x002999E0 + (demon_id * 0xA4)

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
        # remove jive talk flag
        demon.flag = flag & (~0x0080)
        if not demon.is_boss:
            # remove evolution fusion flag from non-boss demons
            demon.flag = demon.flag & (~0x0002)

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
        # event indicates what event happens at learn_level
        # 0x01 = skill learned normally
        # 0x05 = demon evolves
        # 0x06 = skill learned through evolution only
        # 0x07 = "demon body is changing" text thing
        event = rom.read_byte()
        skill_id = rom.read_halfword()

        if event == 0 or count >= 23:
            break

        # skip the evolution events
        if event == 0x05 or event == 0x07:
            continue

        s = {
            'level': max(0, learn_level - level),
            # disregard events currently since we are removing evolution demons
            'event': 1,
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

    #for i in range(len(skill_data)):
    for i, data in enumerate(skill_data):
        skill_id = int(data[1], 16)
        name = data[2]
        rank = int(data[3])
        skill_type = int(data[4])

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
        battle.reward = rom.read_halfword(offset + 0x02)
        battle.phase_value = rom.read_halfword(offset + 0x04)
        battle.arena = rom.read_word(offset + 0x1C)
        battle.goes_first = rom.read_halfword(offset + 0x20)
        battle.reinforcement_value = rom.read_halfword(offset + 0x22)
        battle.music = rom.read_halfword(offset + 0x24)
        all_battles[offset] = battle
        offset += 0x26

def write_demon(rom, demon, offset):
    rom.seek(offset)

    rom.write_halfword(demon.flag, offset + 0x0C)
    rom.write_byte(demon.race, offset + 0x10)
    rom.write_byte(demon.level, offset + 0x11)
    rom.write_halfword(demon.hp, offset + 0x12)
    rom.write_halfword(demon.hp, offset + 0x14)
    rom.write_halfword(demon.mp, offset + 0x16)
    rom.write_halfword(demon.mp, offset + 0x18)

    stats = struct.pack('<BBBBBB', demon.stats[0], 0x00, demon.stats[1], demon.stats[2], demon.stats[3], demon.stats[4])
    rom.write(stats, offset + 0x1C)

    rom.write_halfword(demon.macca_drop, offset + 0x36)
    rom.write_halfword(demon.exp_drop, offset + 0x38)

    # don't change boss ai or skills
    if not demon.is_boss:
        # zero out old battle skills
        rom.write(struct.pack('<16x'), offset + 0x22)

        rom.seek(offset + 0x22)
        for skill in demon.battle_skills:
            rom.write_halfword(skill)

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
    # zero out old demon skills
    offset = demon.skill_offset + 0x0A
    rom.write(struct.pack('<92x'), offset)
   
    rom.seek(offset)
    for skill in demon.skills:
        rom.write_byte(skill['level'])
        rom.write_byte(skill['event'])
        rom.write_halfword(skill['skill_id'])

def write_ai(rom, demon):
    # get rid of special demon ai scripts
    if rom.read_halfword(demon.ai_offset) != 0x46:
        # 0x46 is the default I think?
        rom.write_halfword(0x46, demon.ai_offset)

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

        # zero out old demon ai
        offset = (demon.ai_offset + 0x28) + (i * 0x28)
        rom.write(struct.pack('<40x'), offset)
        
        rom.seek(offset)
        # write the new demon ai
        for o, s in zip(odds, skill_pool):
            rom.write(struct.pack('<HHI', o, s, 0))

def write_magatamas(rom, new_magatams):
    for magatama in new_magatams:
        stats = struct.pack('<BBBBBB', magatama.stats[0], 0xFF, magatama.stats[1], magatama.stats[2], magatama.stats[3], magatama.stats[4])
        rom.seek(magatama.offset + 0x0E)
        for i in range(2):
            rom.write(stats)
        rom.seek(magatama.offset + 0x22)
        for skill in magatama.skills:
            rom.write_halfword(skill['level'])
            rom.write_halfword(skill['skill_id'])

reward_tbl_offset = 0x001FEE00
reward_tbl = []

def write_battles(rom, new_battles, preserve_boss_arenas=False):
    for b in new_battles:
        # only write magatama rewards
        if b.reward:
            b.reward_index = len(reward_tbl)
            rom.write_halfword(b.reward_index + 1, b.offset + 0x02)
            reward_tbl.append(b.reward)
        else:
            rom.write_halfword(0x00, b.offset + 0x02)
        # if 345 >= b.reward >= 320:
        #     rom.write_halfword(b.reward, b.offset + 0x02)
        rom.write_halfword(b.phase_value, b.offset + 0x04)
        rom.seek(b.offset + 0x06)
        for e in b.enemies:
            rom.write_halfword(e)
        if preserve_boss_arenas:
            rom.write_word(b.arena, b.offset + 0x1C)
        rom.write_halfword(b.goes_first, b.offset + 0x20)
        rom.write_halfword(b.reinforcement_value, b.offset + 0x22)
        rom.write_halfword(b.music, b.offset + 0x24)

    for i, r in enumerate(reward_tbl):
        offset = reward_tbl_offset + (i * 0x10)
        reward_type = 0x01                      # always an item for now, 0x02 will be flags later
        rom.write_byte(reward_type, offset)
        #rom.write_byte(1, offset + 0x01)       # Amount
        rom.write_halfword(r, offset + 0x02)

def patch_fix_tutorials(rom):
    # replaces the 1x preta and 2x sudamas tutorial fights with the unmodified, scipted will o' wisp demons
    tutorial_2_offset = 0x002BBBF8
    tutorial_3_offset = 0x002BBC1E

    rom.write(struct.pack('<H', 0x13E), tutorial_2_offset)
    rom.write(struct.pack('<HH', 0x13E, 0x13E), tutorial_3_offset)

def patch_early_spyglass(rom):
    # change the 3x preta fight's reward to spyglass
    reward_index = len(reward_tbl)
    reward_offset = reward_tbl_offset + (reward_index * 0x10)

    rom.write_halfword(reward_index + 1, 0x002B0DB0)
    rom.write_byte(1, reward_offset)            # item type
    #rom.write_byte(1, reward_offset + 0x01)     # amount
    rom.write_halfword(0x12E, reward_offset + 0x02)
    reward_tbl.append(0x12E)
    # change the selling price of the spyglass to 0 macca
    rom.write_word(0, 0x002DD614)

def remove_shop_magatamas(rom):
    # Shibuya shop
    rom.write_byte(0, 0x00230718)           # remove Iyomante
    rom.write_byte(0, 0x0023071C)           # remove Shiranui

    # Underpass shop
    rom.write_byte(0, 0x002307A2)           # remove Ankh
    rom.write_byte(0, 0x002307A6)           # remove Hifumi
    rom.write_byte(0, 0x002307AA)           # remove Kamudo

    # Asakusa shop
    rom.write_byte(0, 0x002308B6)           # remove Nirvana
    rom.write_byte(0, 0x002308BA)           # remove Gehenna

    # Asakusa Tunnel shop
    rom.write_byte(0, 0x00230920)           # remove Kamurogi
    rom.write_byte(0, 0x00230924)           # remove Vimana
    rom.write_byte(0, 0x00230928)           # remove Sophia

    # ToK shop
    rom.write_byte(0, 0x002309DE)           # remove Kailash

    # Underpass shop may be separate based on if you got Ankh from Pixie
    rom.write_byte(0, 0x00230A2C)           # remove Hifumi again(?)
    rom.write_byte(0, 0x00230A30)           # remove Kamudo again(?)

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

def fix_nihilo_summons(rom, demon_map):
    # replace the demons summoned by the nihilo minibosses
    def replace_summons(offsets):
        for off in offsets:
            replacement = demon_map[rom.read_byte(off)]
            rom.write_byte(replacement, off)
        return replacement

    yaka_summon_offsets = [0x0041A0FA, 0x0041A132, 0x0041A182]
    dis_summon_offsets = [0x0041A2CE, 0x0041A306, 0x0041A382, 0x0041A556]
    incubus_summon_offsets = [0x0041A4CE, 0x0041A506]

    replace_summons(yaka_summon_offsets)
    replace_summons(dis_summon_offsets)
    replace_summons(incubus_summon_offsets)

def fix_specter_1_reward(rom, reward_index):
    # add rewards to each of the fused versions of specter 1
    fused_reward_offsets = [0x002B2842, 0x002B2868, 0x002B288E]
    for offset in fused_reward_offsets:
        rom.write_halfword(reward_index + 1, offset)

def fix_angel_reward(rom, reward_index):
    # fix the magatama drop for the optional angel fight
    offset = 0x002B63C8
    rom.write_halfword(reward_index + 1, offset)

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

def patch_special_fusions(rom):
    rom.write(struct.pack('<18x'), 0x0022EB78)
    rom.write(struct.pack('<192x'), 0x0022EBE0)

    # rom.seek(0x0022EB78)
    # for i in range(9):
    #     rom.write_halfword(0)
    # rom.seek(0x0022EBE0)
    # for i in range(85):
    #     rom.write_halfword(0)

def patch_fix_dummy_convo(rom):
    personality_offsets = [0x002DDF58, 0x002DF5D8, 0x002DF668, 0x002DF7B8, 0x002DFB78]
    for o in personality_offsets:
        rom.write_byte(0x0C, o)

def apply_asm_patch(rom, patch_path):
    assert(os.path.exists(patch_path))
    with open(patch_path, 'r') as f:
        for line in f:
            if line.startswith(';'):
                continue
            addr, value = map(int, line.split(','))
            rom.write_byte(value, addr)

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

    # make the random mitamas and elementals not show up in rag's shop
    apply_asm_patch(rom, 'patches/rags.txt')
    # fix most non-recruitable demons and demon races
    apply_asm_patch(rom, 'patches/recruit.txt')
    # change the reward function to load from a table
    apply_asm_patch(rom, 'patches/reward.txt')
    # make the pierce skill work on magic
    if randomizer.config_magic_pierce:
        apply_asm_patch(rom, 'patches/pierce.txt')
    # make aoe healing work on the stock demons
    if randomizer.config_stock_healing:
        apply_asm_patch(rom, 'patches/healing.txt')
    # make learnable skills always visible
    if randomizer.config_visible_skills:
        apply_asm_patch(rom, 'patches/skills.txt')
    # remove hard mode price multiplier
    if randomizer.config_remove_hardmode_prices:
        apply_asm_patch(rom, 'patches/prices.txt')
    # remove skill rank from inheritance odds and make demons able to learn all inheritable skills 
    if randomizer.config_fix_inheritance:
        apply_asm_patch(rom, 'patches/inherit.txt')

    # remove magatamas from shops since they are all tied to boss drops now
    remove_shop_magatamas(rom)
    # patch the fusion table using the generated elemental results
    fix_elemental_fusion_table(rom, world.demon_generator)
    # make special fusion demons fuseable normally
    patch_special_fusions(rom)
    # swap tyrant to vile for pale rider, the harlot, & trumpeter fusion
    rom.write_byte(0x12, 0x22EDE3)
    if randomizer.config_fix_tutorial:
        print("fixing tutorials")
        patch_fix_tutorials(rom)
    # add the spyglass to 3x preta fight and reduce it's selling price
    if randomizer.config_early_spyglass:
        print("applying early spyglass patch")
        patch_early_spyglass(rom)

    # replace the pazuzu mada summons
    fix_mada_summon(rom, world.demons.values())
    # replace the demons summoned by the nihilo minibosses
    fix_nihilo_summons(rom, world.demon_map)
    # fix the magatama drop on the fused versions of specter 1
    for b in world.battles.values():
        if b.offset == world.get_check("Specter 1").offset:
            if b.reward_index:
                fix_specter_1_reward(rom, b.reward_index)
        elif b.offset == world.get_check("Futomimi").offset:
            if b.reward_index:
                fix_angel_reward(rom, b.reward_index)

    # specter_1_reward = world.get_boss("Specter 1").reward
    # if specter_1_reward:
    #     specter_1_reward = all_magatamas[specter_1_reward.name].ind
    #     specter_1_reward += 320
    #     fix_specter_1_reward(rom, specter_1_reward)
    # fix the magatama drop for the optional angel fight
    # futomimi_reward = world.get_check("Futomimi").boss.reward
    # if futomimi_reward:
    #     futomimi_reward = all_magatamas[futomimi_reward.name].ind
    #     futomimi_reward += 320
    #     fix_angel_reward(rom, futomimi_reward)
    # replace the DUMMY personality on certain demons
    patch_fix_dummy_convo(rom)