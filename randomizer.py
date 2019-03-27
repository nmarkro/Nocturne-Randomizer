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

import nocturne
import logic
import races
from base_classes import *
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
config_preserve_boss_arenas = False         # Make randomized bosses apear in their normal battle arena


def init_rom_data(rom_path):
    global rom
    rom = Rom(rom_path)


def generate_demon_permutation(demon_gen, easy_hospital = False):
    def swap_demon(d1, d2):
        for key, value in demon_map.items():
            if value == d1.ind:
                demon_map[d2.ind], demon_map[key] = demon_map[key], demon_map[d2.ind]
                return

    all_demons = [d for d in nocturne.all_demons.values() if not d.is_boss]
    all_base = [d for d in all_demons if d.base_demon]
    all_elements = [d for d in all_demons if d.race == 7]
    all_mitamas = [d for d in all_demons if d.race == 8]
    all_fiends = [d for d in all_demons if d.race == 38] 

    demon_map = {}
    demon_pool = all_demons
    shuffled_pool = copy.copy(demon_pool)
    random.shuffle(shuffled_pool)

    for old_demon, new_demon in zip(demon_pool, shuffled_pool):
        demon_map[old_demon.ind] = new_demon.ind
    if easy_hospital:
        # iterate through each hospital demon looking for conflicts
        for demon in all_base:
            new_demon = nocturne.lookup_demon(demon_map.get(demon.ind))
            if new_demon.phys_inv:
                # choose a new demon from all non-hospital, non-phys invalid demons
                new_choice = random.choice([d for d in demon_pool if not d.phys_inv])
                swap_demon(demon, new_choice)
                # get the index of the new choice for swaping
                # for key, value in demon_map.items():
                #     if value == new_choice.ind:
                #         # swap the two demons in the map
                #         demon_map[demon.ind], demon_map[key] = new_choice.ind, demon_map[demon.ind]
                #         break

    for element in all_elements:
        # find the element in generated demons
        chosen_demon = None
        d = next((d for d in demon_gen.demons if d.name == element.name), None)
        # choose a demon in demon pool that is the same level as the generated demon
        candidates = [c for c in demon_pool if c.level == d.level]
        chosen_demon = random.choice(candidates)
        # find the elemental in the map and swap
        if chosen_demon:
            demon_pool.remove(chosen_demon)
            swap_demon(element, chosen_demon)
            # for key, value in demon_map.items():
            #     if value == element.ind:
            #         demon_map[chosen_demon.ind], demon_map[key] = demon_map[key], demon_map[chosen_demon.ind]
        else:
            print("Error finding mutation for " + element.name)   

    for mitama in all_mitamas:
        # find the mitama in generated demons
        chosen_demon = None
        d = next((d for d in demon_gen.demons if d.name == mitama.name), None)
        # choose a demon in demon pool that is the same level as the generated demon
        candidates = [c for c in demon_pool if c.level == d.level]
        chosen_demon = random.choice(candidates)
        # find the mitama in the map and swap
        if chosen_demon:
            demon_pool.remove(chosen_demon)
            swap_demon(mitama, chosen_demon)
            # for key, value in demon_map.items():
            #     if value == mitama.ind:
            #         demon_map[chosen_demon.ind], demon_map[key] = demon_map[key], demon_map[chosen_demon.ind]
            #         break
        else:
            print("Error finding mutation for " + mitama.name)

    # get the fiends beforehand and shuffle since there isn't a direct connection beyond demon race 
    generated_fiends = [d for d in demon_gen.demons if races.raceref[d.race] == "Fiend"]
    random.shuffle(generated_fiends)
    for fiend in all_fiends:
        # use one of the randomly selected fiends
        chosen_demon = None
        gen_fiend = generated_fiends.pop()
        # choose a demon in demon pool that is the same level as the generated demon
        candidates = [c for c in demon_pool if c.level == gen_fiend.level]
        chosen_demon = random.choice(candidates)
        # find the fiend in the map and swap
        if chosen_demon:
            demon_pool.remove(chosen_demon)
            swap_demon(fiend, chosen_demon)
            # for key, value in demon_map.items():
            #     if value == fiend.ind:
            #         demon_map[chosen_demon.ind], demon_map[key] = demon_map[key], demon_map[chosen_demon.ind]
            #         break
        else:
            print("Error finding mutation for " + fiend.name)

    #for key, value in demon_map.items():
    #    print(nocturne.lookup_demon(key).name + " -> " + nocturne.lookup_demon(value).name)

    return demon_map


def generate_skill_permutation(balance_by_rank = True, keep_pierce = False):
    skill_sets = defaultdict(list)
    # separare skills by rank
    for skill in nocturne.all_skills.values():
        skill_id = skill.rank
        if not balance_by_rank:
            # still keep special skills (boss/demon specific) separate
            if skill_id < 100:
                skill_id = 1
        # treak attack/passive/recruitment skills differently 
        skill_id += skill.skill_type * 1000
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

    skill_pool = list(nocturne.all_skills.values())
    unique_pool = [s for s in skill_pool if s.rank >= 100]
    # remove unique skills from skill pool
    skill_pool = [s for s in skill_pool if s not in unique_pool]
    random.shuffle(skill_pool)
    random.shuffle(unique_pool)

    # get the total number of unique skills for the demon
    num_of_unique = 0
    for s in new_demon.skills:
        s = nocturne.lookup_skill(s['skill_id'])
        if not s:
            continue
        if s.rank >= 100:
            num_of_unique += 1
    # add any forced skills first
    if force_skills:
        for s in force_skills:
            skill = {
                'level': level,
                'skill_id': s,
                'magic_byte': 1,
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
    demon_pool = [d for d in nocturne.all_demons.values() if not d.is_boss]
    for old_demon in demon_pool:
        new_demon = demon_map[old_demon.ind]
        new_demon = nocturne.lookup_demon(new_demon)
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
                    race_ind = nocturne.race_names.index(race) + 1
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
    for old_magatama in nocturne.all_magatamas.values():
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
    new_battles = []
    for b in nocturne.all_battles.values():
        new_battle = copy.deepcopy(b)
        # check if it the battle is a scripted fight or not
        if b.is_boss:
            for i, d in enumerate(b.enemies):
                if d > 0:
                    demon = nocturne.lookup_demon(d)
                    if not demon:
                        break
                    # don't change any of the early scripted fights
                    if not demon.is_boss or demon.name not in ["Will o' Wisp", "Kodama", "Preta"]:
                        new_demon = demon_map.get(d)
                        if new_demon:
                            new_battle.enemies[i] = new_demon
                    else:
                        break
        else:
            for i, d in enumerate(b.enemies):
                if d > 0:
                    new_demon = demon_map.get(d)
                    if new_demon:
                        new_battle.enemies[i] = new_demon
        new_battles.append(new_battle)
    return new_battles

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
    boss_battles = []

    for check in world.get_checks():
        old_boss = world.get_boss(check.name)
        new_boss = check.boss

        boss_battle = copy.deepcopy(new_boss.battle)
        boss_battle.offset = check.offset

        old_boss_demon = next((nocturne.lookup_demon(d) for d in old_boss.battle.enemies if d > 0), None)
        new_boss_demon = copy.copy(next((nocturne.lookup_demon(d) for d in new_boss.battle.enemies if d > 0), None))

        if old_boss is not new_boss:
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
                    d = rebalance_demon(nocturne.lookup_demon(d), new_level, new_hp=new_hp, new_mp=new_mp, exp_mod=config_exp_modifier, stat_mod=stat_mod)
                    boss_demons.append(d)
            if config_always_go_first:
                boss_battle.goes_first = 0x0D

        # replace any vanilla magatama drops
        if 345 >= boss_battle.reward >= 320:
            boss_battle.reward = 0
        if new_boss.reward is not None:
            magatama = nocturne.all_magatamas[new_boss.reward.name]
            boss_battle.reward = magatama.ind + 320
            magatama.level = min(magatama.level, round(old_boss_demon.level/2))

        boss_battles.append(boss_battle)

    return boss_demons, boss_battles


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
    nocturne.load_all(rom)
    if config_make_logs:
        write_demon_log('logs/demons.txt', nocturne.all_demons.values())

    print('creating logical progression')
    # generate a world and come up with a logical boss and boss magatama drop progression
    # logic can sometimes get stuck shuffling bosses so keep generating until you get a valid world
    world = None
    while world is None:
        world = logic.create_world()
        world = logic.randomize_world(world, logger)

    print('randomizing demons')
    # generate demon levels and races making sure all demons are fuseable
    demon_generator = races.all_demons(races.demon_levels, races.demon_names)
    demon_generator.generate()
    # generate_demon_permutation disregards demon names for most races for better randomization (non-element/mitama)
    demon_map = generate_demon_permutation(demon_generator, config_easy_hospital)
    # randomize and rebalance all demon stats
    new_demons = randomize_demons(demon_map, demon_generator.demons, exp_mod=config_exp_modifier)

    print('randomizing battles')
    # mutate all the non-boss demons using demon_map 
    new_battles = randomize_battles(demon_map)
    # rebalance and copy boss battles
    new_bosses, new_boss_battles = randomize_boss_battles(world)
    new_demons.extend(new_bosses)
    new_battles.extend(new_boss_battles)
    if config_make_logs:
        write_demon_log('logs/random_demons.txt', new_demons)

    # magatamas have to be randomized AFTER boss battles to correctly rebalance their levels
    print('randomizing magatamas')
    new_magatamas = randomize_magatamas()

    # Add all the new demons, magatamas, and bosses to the world
    world.add_demons(new_demons)
    world.add_battles(new_battles)
    world.add_magatamas(new_magatamas)

    nocturne.write_all(rom, world)

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
    specter_1_reward = nocturne.all_magatamas[world.get_boss("Specter 1").reward.name].ind
    specter_1_reward += 320
    nocturne.fix_specter_1_reward(rom, specter_1_reward)

    print("copying iso")
    #shutil.copyfile(rom_path, output_path)
    print("writing new binary")
    if config_write_binary:
        with open('rom/SLUS_209.11', 'wb') as file:
            file.write(bytearray(rom.buffer))
    with open(output_path, 'r+b') as file:
        file.seek(0xFD009000)
        file.write(bytearray(rom.buffer))
        nocturne.patch_intro_skip(file)


if __name__ == '__main__':
    seed = None
    if len(sys.argv) > 1:
        seed = sys.argv[1].upper().strip()
    main('rom/input.iso', 'rom/output.iso', text_seed=seed)