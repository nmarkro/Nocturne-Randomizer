# a lot of code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import random
import struct
import copy
import math
import logging
import shutil
import hashlib
import string
import sys
from collections import defaultdict

import logic
import demons
import skills
import magatamas
import boss_battles
import races
from rom import Rom

# Config
config_balance_by_skill_rank = False        # Permutate skills based on rank
config_exp_modifier = 2                     # Mulitlpy EXP values of demons
config_make_logs = True                     # Write various data to the logs/ folder
config_write_binary = True                  # Write the game's binary to a separe file for easier hex reading
config_fix_tutorial = True                  # replace a few tutorial fights
config_easy_hospital = True                 # Force hospital demons/boss to not have null/repel/abs phys
config_keep_marogareh_pierce = True         # Don't randomize Pierce on Maraogareh
config_easy_recruits = True                 # Patch game so demon recruits always succeed after giving 2 things (bugged?)
config_always_go_first = True               # Always go first in randomized boss fights
config_give_pixie_estoma_riberama = True    # Give pixie estoma and riberama
config_early_spyglass = True                # Adds the Spyglass as a drop on the 3x Preta fight
config_visible_skills = True                # Make all learnable skills visable


def init_rom_data(rom_path):
    global rom
    rom = Rom(rom_path)


def generate_demon_permutation(demon_gen, easy_hospital = False):
    base_demons = list(map(lambda demon: demon.ind, demons.where(base_demon = True)))
    all_phys_inv = list(map(lambda demon: demon.ind, demons.where(phys_inv = True)))
    all_elements = list(map(lambda demon: demon.ind, demons.where(race = 7, is_boss=False)))
    all_mitamas = list(map(lambda demon: demon.ind, demons.where(race = 8, is_boss=False)))
    all_fiends = list(map(lambda demon: demon.ind, demons.where(race = 38, is_boss=False)))

    demon_map = {}
    demon_pool = list(copy.copy(demons.where(is_boss=False)))
    shuffled_pool = copy.copy(demon_pool)
    random.shuffle(shuffled_pool)

    for old_demon, new_demon in zip(demon_pool, shuffled_pool):
        demon_map[old_demon.ind] = new_demon.ind
    if easy_hospital:
        # iterate through each hospital demon looking for conflicts
        for demon in base_demons:
            new_demon_ind = demon_map.get(demon)
            new_demon = demons.lookup(new_demon_ind)
            if new_demon.phys_inv:
                # choose a new demon from all non-hospital, non-phys invalid demons
                new_choice = random.choice(demon_pool)
                # get the index of the new choice for swaping
                for key, value in demon_map.items():
                    if value == new_choice.ind:
                        # swap the two demons in the map
                        demon_map[demon], demon_map[key] = new_choice.ind, demon_map[demon]
                        break

    for element in all_elements:
        # fix element permutations to fit generated level
        element = demons.lookup(element)
        # find the element in generated demons
        chosen_demon = None
        d = next((d for d in demon_gen.demons if d.name == element.name), None)
        # choose a demon in demon pool that is the same level as the generated demon
        candidates = [c for c in demon_pool if c.level == d.level]
        chosen_demon = random.choice(candidates)
        # find the elemental in the map and swap
        if chosen_demon:
            demon_pool.remove(chosen_demon)
            for key, value in demon_map.items():
                if value == element.ind:
                    demon_map[chosen_demon.ind], demon_map[key] = demon_map[key], demon_map[chosen_demon.ind]
        else:
            print("Error finding mutation for " + element.name)   

    for mitama in all_mitamas:
        # do the same as above but for Mitamas
        mitama = demons.lookup(mitama)
        # find the mitama in generated demons
        chosen_demon = None
        d = next((d for d in demon_gen.demons if d.name == mitama.name), None)
        # choose a demon in demon pool that is the same level as the generated demon
        candidates = [c for c in demon_pool if c.level == d.level]
        chosen_demon = random.choice(candidates)
        # find the mitama in the map and swap
        if chosen_demon:
            demon_pool.remove(chosen_demon)
            for key, value in demon_map.items():
                if value == mitama.ind:
                    demon_map[chosen_demon.ind], demon_map[key] = demon_map[key], demon_map[chosen_demon.ind]
                    break
        else:
            print("Error finding mutation for " + mitama.name)

    # get the fiends beforehand and shuffle since there isn't a direct connection beyond demon race 
    generated_fiends = [d for d in demon_gen.demons if races.raceref[d.race] == "Fiend"]
    random.shuffle(generated_fiends)
    for fiend in all_fiends:
        # even more of the same but for fiends
        fiend = demons.lookup(fiend)
        # use one of the randomly selected fiends
        chosen_demon = None
        gen_fiend = generated_fiends.pop()
        # choose a demon in demon pool that is the same level as the generated demon
        candidates = [c for c in demon_pool if c.level == gen_fiend.level]
        chosen_demon = random.choice(candidates)
        # find the fiend in the map and swap
        if chosen_demon:
            demon_pool.remove(chosen_demon)
            for key, value in demon_map.items():
                if value == fiend.ind:
                    demon_map[chosen_demon.ind], demon_map[key] = demon_map[key], demon_map[chosen_demon.ind]
                    break
        else:
            print("Error finding mutation for " + fiend.name)

    #for key, value in demon_map.items():
    #    print(demons.lookup(key).name + " -> " + demons.lookup(value).name)

    return demon_map


def generate_skill_permutation(balance_by_rank = True, keep_pierce = False):
    skill_sets = defaultdict(list)
    # separare skills by rank
    for skill in skills.where():
        skill_id = skill.rank
        if not balance_by_rank:
            # still keep special skills (boss/demon specific) separate
            if skill_id < 100:
                skill_id = 1
        # treak attack/passive/recruitment skills differently 
        skill_id += skill.skill_type * 1000
        # don't shuffle banned skills
        # if skill_id <= 0:
        #    skill_id = skill.ind
        if keep_pierce:
            if skill.ind == 357:
                skill_id = skill.ind
        skill_sets[skill_id].append(skill.ind)

    # shuffle inside each set
    skill_map = {}
    for key, vals in skill_sets.items():
        keys = copy.copy(vals)
        random.shuffle(vals)
        for old_skill, new_skill in zip(keys, vals):
            skill_map[old_skill] = new_skill

    return skill_map


def randomize_stats(total_stats, req_min = True):
    # todo: make this not kinda shit
    # get total number of stat points
    if req_min:
        # remove 5 for the min 1 point per stat
        total_stats -= 5
        new_stats = [1, 1, 1, 1, 1]
    else:
        new_stats = [0, 0, 0, 0, 0]
    # keep track of non-maxed stats
    valid_stats = [0, 1, 2, 3, 4]
    # distribute stats randomly one at a time
    for i in range(total_stats):
        while True:
            # sanity check incase there are no more valid stats
            if len(valid_stats) == 0:
                break
            choice = random.choice(valid_stats)
            # make sure stats don't go past max
            if new_stats[choice] >= 40:
                new_stats[choice] = 40
                valid_stats.remove(choice)
            else:
                new_stats[choice] += 1
                break

    return new_stats


def randomize_skills(new_demon, force_skills=None):
    new_skills = []
    new_battle_skills = []
    is_pixie = bool(new_demon.name == "Pixie")

    starting_skills = random.randint(2, 4)
    total_skills = starting_skills + random.randint(4, 6)
    level = 0

    skill_pool = list(skills.where())
    unique_pool = list(skills.where(rank=100))
    # remove unique skills from skill pool
    skill_pool = [s for s in skill_pool if s not in unique_pool]
    random.shuffle(skill_pool)
    random.shuffle(unique_pool)

    # get the total number of unique skills for the demon
    num_of_unique = 0
    for skill in new_demon.skills:
        try:
            skill = skills.lookup(skill['skill_id'])
        except KeyError:
            continue
        if skill.rank >= 100:
            num_of_unique += 1
    # add any forced skills first
    if force_skills:
        for s in force_skills:
            skill = {
                'level': level,
                'skill_id': s,
                'magic_byte': 1,
                'offset': new_demon.skills[0]['offset']
            }
            new_skills.append(skill)
            for p in skill_pool:
                if p.ind == s:
                    skill_pool.remove(p)
                    break
            total_skills -= 1
    # this is mainly for Dante who has like 10 unique skills
    if num_of_unique > total_skills:
        total_skills = num_of_unique
    # randomly select nonunique skills
    chosen_skills = random.sample(skill_pool, total_skills - num_of_unique)
    # randomly select unique skills and add it to the list + shuffle
    chosen_skills += random.sample(unique_pool, num_of_unique)
    random.shuffle(chosen_skills)

    for i in range(total_skills):
        chosen_skill = chosen_skills.pop()

        if chosen_skill.skill_type == 1 and len(new_battle_skills) < 8:
            new_battle_skills.append(chosen_skill.ind)

        if len(new_skills) >= starting_skills:
            if is_pixie or level == 0:
                level = new_demon.level + 1
            else:
                level += 1

        skill = {
            'level': level,
            'skill_id': chosen_skill.ind,
            'magic_byte': 1,
            'offset': new_demon.skills[0]['offset']
        }
        new_skills.append(skill)

    return [new_skills, new_battle_skills]


def rebalance_demon(old_demon, new_level, stats=None, new_hp=-1, new_mp=-1, new_exp=-1, new_macca=-1, exp_mod=1, stat_mod=1):
    new_demon = copy.copy(old_demon)
    level_mod = new_level / old_demon.level
    new_demon.level = int(new_level)
    if stats:
        total_stats = sum(stats) * stat_mod
    else:
        # generate stats based on level if they aren't supplied
        total_stats = (20+new_level) * stat_mod
    new_demon.stats = randomize_stats(int(total_stats))
    if new_hp > 0:
        new_demon.hp = new_hp
    else:
        # generate hp based on level and vitality stat if they aren't supplied
        new_demon.hp = (6*new_demon.level) + (6*new_demon.stats[3])
    new_demon.hp = min(int(new_demon.hp), 0xFFFF)
    if new_mp > 0:
        new_demon.mp = new_mp
    else:
        # generate mp based on level and magic stat if they aren't supplied
        new_demon.mp = (3*new_demon.level) + (3*new_demon.stats[2])
    new_demon.mp = min(int(new_demon.mp), 0xFFFF)
    if new_exp > 0:
        exp = new_exp * exp_mod
    else:
        # this gives horrible values if the level difference is extreme
        exp = round(old_demon.exp_drop * exp_mod * stat_mod * level_mod)
    new_demon.exp_drop = int(min(exp, 0xFFFF))
    if new_macca > 0:
        macca = new_macca
    else:
        # this gives horrible values if the level difference is extreme
        macca = round(old_demon.macca_drop * stat_mod * level_mod)
    new_demon.macca_drop = int(min(macca, 0xFFFF))

    return new_demon


def randomize_demons(demon_map, generated_demons, exp_mod=1):
    new_demons = []
    # buffs/debuffs to give to base demons
    skills_to_distribute = [52, 53, 54, 57, 64, 65, 66, 67, 77]
    random.shuffle(skills_to_distribute)
    # take the stats from old_demon and use them to rebalance the new_demon permutation
    for old_demon in demons.where(is_boss=False):
        new_demon = demon_map[old_demon.ind]
        new_demon = demons.lookup(new_demon)
        #print(old_demon.name + " -> " + new_demon.name)
        new_demon = rebalance_demon(new_demon, old_demon.level, stats=old_demon.stats, new_exp=old_demon.exp_drop, new_macca=old_demon.macca_drop, exp_mod=exp_mod)
        assigned_new_race = False
        # don't change elemental race
        if new_demon.race == 7:
            d = next((d for d in generated_demons if races.raceref[d.race] == new_demon.name), None)
            if d:
                generated_demons.remove(d)
                assigned_new_race = True
        # don't change mitama race
        elif new_demon.race == 8:
            d = next((d for d in generated_demons if d.name == new_demon.name), None)
            if d:
                generated_demons.remove(d)
                assigned_new_race = True
        # don't change fiend race
        elif new_demon.race == 38:
            d = next((d for d in generated_demons if races.raceref[d.race] == "Fiend" and d.level == old_demon.level), None)
            if d:
                generated_demons.remove(d)
                assigned_new_race = True
        # change the race based on the generated demons
        else:
            for d in generated_demons:
                race = races.raceref[d.race]
                if race in ['Erthys', 'Aeros', 'Aquans', 'Flaemis'] or race == "Mitama" or race == "Fiend":
                    continue
                elif old_demon.level == d.level:
                    generated_demons.remove(d)
                    race_ind = demons.race_names.index(race) + 1
                    new_demon.race = race_ind
                    assigned_new_race = True
                    break
        if not assigned_new_race:
            print("Error: Could not rebalance " + new_demon.name)
            return
        new_demon.base_demon = bool(old_demon.base_demon)
        if old_demon.base_demon:
            old_demon.base_demon = False
        # distribute basic buffs to the base demons
        if new_demon.name == 'Pixie' and config_give_pixie_estoma_riberama:
            new_demon.skills, new_demon.battle_skills = randomize_skills(new_demon, [73, 74])
        elif new_demon.base_demon and len(skills_to_distribute) > 0:
            skill = [skills_to_distribute.pop()]
            new_demon.skills, new_demon.battle_skills = randomize_skills(new_demon, skill)
        else:
            new_demon.skills, new_demon.battle_skills = randomize_skills(new_demon)
        #print(str(vars(new_demon)) + "\n")
        new_demons.append(new_demon)

    return new_demons


def randomize_magatamas():
    new_magatamas = []
    # make one skill_map for all magatamas to prevent duplicate skills
    skill_map = generate_skill_permutation(config_balance_by_skill_rank, config_keep_marogareh_pierce)
    for old_magatama in magatamas.where():
        new_magatama = copy.copy(old_magatama)
        new_magatama.stats = randomize_stats(sum(new_magatama.stats), False)
        new_skills = []
        for skill in new_magatama.skills:
            ind = skill['skill_id']
            new_skill = skill_map.get(ind)
            if new_skill:
                skill['skill_id'] = new_skill
            skill['level'] = skill['level'] + new_magatama.level
            new_skills.append(skill)
        new_magatama.skills = new_skills
        new_magatamas.append(new_magatama)

    return new_magatamas


def randomize_battles(demon_map):
    battle_offset = 0x002AFFE0
    N_BATTLES = 1270
    # should move this to nocturne.py to stay consistent with other writes
    offset = battle_offset
    for i in range(N_BATTLES):
        is_boss = rom.read_halfword(offset) == 0x01FF
        offset += 6
        # check if it the battle is a scripted fight or not
        if is_boss:
            for j in range(0, 18, 2):
                old_demon = rom.read_halfword(offset + j)
                if old_demon > 0:
                    try:
                        demon = demons.lookup(old_demon)
                    except KeyError:
                        break
                    # don't change any of the early scripted fights
                    if not demon.is_boss or demon.name not in ["Will o' Wisp", "Kodama", "Preta"]:
                        new_demon = demon_map.get(old_demon)
                        if new_demon:
                            rom.write_halfword(new_demon, offset + j)
                    else:
                        break
        else:
            # max # of demons is 9
            for j in range(0, 18, 2):
                old_demon = rom.read_halfword(offset + j)
                if old_demon > 0:
                    new_demon = demon_map.get(old_demon)
                    if new_demon:
                        rom.write_halfword(new_demon, offset + j)
        offset += 0x20


# Additional demons in certain boss fights
boss_extras = {
    'Albion (Boss)': [279, 280, 280, 281, 282], # Urizen, Luvah, Tharmas, Urthona
    'White Rider (Boss)': [359, 359],           # Virtue
    'Red Rider (Boss)': [360, 360],             # Power
    'Black Rider (Boss)': [361, 361],           # Legion
    'Pale Rider (Boss)': [358, 358],            # Loa
    'Atropos 2 (Boss)': [326, 327]              # Clotho, Lachesis
}

def randomize_boss_battles(world):
    boss_demons = []
    for battle in boss_battles.where():
        old_boss_battle = battle.boss
        new_boss_battle = None
        new_boss = next((c.boss for c in world.get_checks() if c.name == old_boss_battle), None)
        if new_boss is not None:
            new_boss_battle = next(boss_battles.where(boss = new_boss.name))
            old_boss_demon = None
            new_boss_demon = None
            for d in battle.data:
                if d > 0:
                    old_boss_demon = copy.copy(demons.lookup(d))
                    break

            for d in new_boss_battle.data:
                if d > 0:
                    new_boss_demon = copy.copy(demons.lookup(d))
                    break

            new_level = old_boss_demon.level
            if new_level < new_boss_demon.level:
                new_level /= 2

            new_hp = old_boss_demon.hp
            new_mp = old_boss_demon.mp

            # if the new boss is replacing the Sisters triple hp and mp 
            if old_boss_demon.name == "Atropos 2 (Boss)":
                new_hp *= 3
                new_mp *= 3
            # if the new boss is the Sisters divide the hp pool evenly between the 3
            if new_boss_demon.name == "Atropos 2 (Boss)":
                new_hp = round(new_hp / 3)
                new_mp = round(new_mp / 3)
            # if the new boss is mara half it's HP with a cap of 4000
            if new_boss_demon.name == "Mara (Boss)":
                new_hp = round(new_hp / 2)
                new_hp = min(new_hp, 4000)
            new_exp = old_boss_demon.exp_drop
            new_macca = old_boss_demon.macca_drop
            balanced_demon = rebalance_demon(new_boss_demon, new_level, new_hp=new_hp, new_mp=new_mp, new_exp=new_exp, new_macca=new_macca, exp_mod=config_exp_modifier, stat_mod=1)
            boss_demons.append(balanced_demon)
            # balance any extra demons that show up in the fight
            extras = boss_extras.get(new_boss_demon.name)
            if extras:
                new_hp = -1
                new_mp = -1
                new_level = balanced_demon.level
                stat_mod = 1
                if new_boss_demon.name in ['White Rider (Boss)', 'Red Rider (Boss)', 'Black Rider (Boss)', 'Pale Rider (Boss)']:
                    stat_mod = 0.1
                    new_level = round(new_level * 0.6)
                elif new_boss_demon.name == 'Albion (Boss)':
                    stat_mod = 0.5
                    new_level = round(new_level * 0.75)
                elif new_boss_demon.name == "Atropos 2 (Boss)":
                    new_hp = balanced_demon.hp
                    new_mp = balanced_demon.mp
                for d in extras:
                    d = rebalance_demon(demons.lookup(d), new_level, new_hp=new_hp, new_mp=new_mp, exp_mod=config_exp_modifier, stat_mod=stat_mod)
                    boss_demons.append(d)

            # write the boss battle
            # should move this to nocturne.py to stay consistent with other writes
            reward = 0
            if new_boss.reward is not None:
                magatama = next((m for m in magatamas.where() if m.name == new_boss.reward.name), None)
                reward = magatama.ind + 320
                magatama.level = min(magatama.level, round(balanced_demon.level/2))

            offset = battle.offset
            rom.write_halfword(reward, offset + 0x02)
            rom.write_halfword(new_boss_battle.phase_value, offset + 0x04)
            for i in range(len(new_boss_battle.data)):
                rom.write_halfword(new_boss_battle.data[i], offset + 0x06 + (i * 2))
            rom.write_word(new_boss_battle.arena, offset + 0x1C)
            if config_always_go_first:
                rom.write_halfword(0x0D, offset + 0x20)
            else:
                rom.write_halfword(new_boss_battle.first_turn, offset + 0x20)
            rom.write_halfword(new_boss_battle.reinforcement_value, offset + 0x22)
            rom.write_halfword(new_boss_battle.music, offset + 0x24)

    return boss_demons      


def write_demon_log(output_path, demons):
    with open(output_path, "w") as file:
        for demon in demons:
            file.write(str(vars(demon)) + "\n\n")


def main(rom_path, output_path, text_seed=None):
    if text_seed is None:
        text_seed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    print("ROM Seed: " + text_seed)
    seed = int(hashlib.sha256(text_seed.encode('utf-8')).hexdigest(), 16)
    random.seed(seed)

    logger = logging.getLogger('')
    if config_make_logs:
        logging.basicConfig(filename='logs/spoiler.log', level=logging.INFO)

    print('opening iso')
    init_rom_data(rom_path)

    print('initializing data')
    import nocturne
    nocturne.load_all(rom)
    if config_make_logs:
        write_demon_log('logs/demons.txt', demons.where())

    print('creating logical progression')
    # generate a world and come up with a logical boss and boss magatama drop progression
    world = logic.create_world()
    world = logic.randomize_world(world, logger)

    print('randomizing demons')
    # generate demon levels and races making sure all demons are fuseable
    demon_generator = races.all_demons(races.demon_levels, races.demon_names)
    demon_generator.generate()
    # generate_demon_permutation disregards demon names for most races for better randomization (non-element/mitama)
    demon_map = generate_demon_permutation(demon_generator, config_easy_hospital)
    #for d in demon_generator.demons:
    #    print(d.str())
    #demon_generator.print_elemental_results()
    # randomize and rebalance all demon stats
    new_demons = randomize_demons(demon_map, demon_generator.demons, exp_mod=config_exp_modifier)

    print('randomizing battles')
    randomize_battles(demon_map)
    new_bosses = randomize_boss_battles(world)
    new_demons.extend(new_bosses)
    if config_make_logs:
        write_demon_log('logs/random_demons.txt', new_demons)

    # magatamas have to be randomized AFTER boss battles to correctly rebalance their levels
    print('randomizing magatamas')
    new_magatamas = randomize_magatamas()

    # make the pierce skill work on magic
    nocturne.patch_magic_pierce(rom)
    # make aoe healing work on the stock demons
    nocturne.patch_stock_aoe_healing(rom)
    # remove magatamas from shops since they are all tied to boss drops now
    nocturne.remove_shop_magatamas(rom)
    # patch the fusion table using the generated elemental results
    nocturne.fix_elemental_fusion_table(rom, demon_generator)
    if config_fix_tutorial:
        print("fixing tutorials")
        nocturne.patch_fix_tutorials(rom)
    # this just doesn't work half the time :(
    if config_easy_recruits:
        print("applying easy recruits patch")
        nocturne.patch_easy_demon_recruits(rom)
    # add the spyglass to 3x preta fight and reduce it's selling price
    if config_early_spyglass:
        print("applying early spyglass patch")
        nocturne.patch_early_spyglass(rom)
    # make learnable skills always visible
    if config_visible_skills:
        nocturne.patch_visible_skills(rom)

    # replace the pazuzu mada summons
    nocturne.fix_mada_summon(rom, new_demons)
    # fix the magatama drop on the fused versions of specter 1
    specter_1_reward = next((m.ind for m in magatamas.where() if m.name == world.get_boss("Specter 1").reward.name), None)
    specter_1_reward += 320
    nocturne.fix_specter_1_reward(rom, specter_1_reward)

    print("copying iso")
    shutil.copyfile(rom_path, output_path)
    print("writing new binary")
    nocturne.write_all(rom, new_demons, new_magatamas)
    if config_write_binary:
        with open('rom/SLUS_209.11', 'wb') as file:
            file.write(bytearray(rom.buffer))
    with open(output_path, 'r+b') as file:
        file.seek(0xFD009000)
        file.write(bytearray(rom.buffer))


if __name__ == '__main__':
    seed = None
    if len(sys.argv) > 1:
        seed = sys.argv[1].upper().strip()
    main('rom/input.iso', 'rom/output.iso', text_seed=seed)