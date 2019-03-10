# a lot of code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import random
import struct
import copy
import math
import logging
import shutil
from collections import defaultdict

from rom import Rom
import logic
import demons
import skills
import magatamas
import boss_battles

# Config
config_balance_by_skill_rank = False		# Permutate skills based on rank
config_exp_modifier = 2						# Mulitlpy EXP values of demons
config_make_logs = True 					# Write various data to the logs/ folder
config_write_binary = True					# Write the game's binary to a separe file for easier hex reading
config_fix_tutorial = True 					# replace a few tutorial fights
config_easy_hospital = True					# Force hospital demons/boss to not have null/repel/abs phys
config_keep_marogareh_pierce = True			# Don't randomize Pierce on Maraogareh
config_easy_recruits = True					# Patch game so demon recruits always succeed after giving 2 things
config_always_go_first = True				# Always go first in randomized boss fights
config_give_pixie_estoma_riberama = True 	# Give pixie estoma and riberama

# Bosses to replace
# these are the ones I think won't cause issues, but I haven't tested them all yet
allowed_boss_ids = [
	256, 263, 266, 267, 268, 274, 276, 277, 283, 
	287, 297, 300, 301, 302, 303, 317, 320, 321, 
	322, 323, 324, 325, 329, 333, 334, 335, 337, 
	342, 343, 349, 350, 351, 352, 353, 345, 346, 
	347, 348,
]

def init_rom_data(rom_path):
	global rom
	rom = Rom(rom_path)

def generate_demon_permutation(easy_hospital = False):
	base_demons = list(map(lambda demon: demon.ind, demons.where(base_demon = True)))
	all_phys_inv = list(map(lambda demon: demon.ind, demons.where(phys_inv = True)))

	demon_sets = defaultdict(list)
	# divide demons and bosses
	for demon in demons.where():
		demon_id = 1
		# only include the allowed bosses
		if demon.is_boss or demon.name == "Dante":
			# if demon.ind in allowed_boss_ids:
			# 	demon_id = 2
			# else:
			demon_id = demon.name

		# shuffle mitamas and elementals by themselves
		if demon.race == 7 or demon.race == 8:
			demon_id = demon.race

		demon_sets[demon_id].append(demon.ind)

	# shuffle inside each set
	demon_map = {}
	for key, vals in demon_sets.items():
		keys = copy.copy(vals)

		random.shuffle(vals)
		for old_demon, new_demon in zip(keys, vals):
			demon_map[old_demon] = new_demon

		if easy_hospital:
			# get hospital demons in current set
			t_base = list(set(vals).intersection(base_demons))

			# get phys invalid demons in current set and remove all hospital demons
			t_phys = set(vals).difference(all_phys_inv)
			t_phys = list(t_phys.difference(t_base))

			if t_base:
				# iterate through each hospital demon looking for conflicts
				for demon in t_base:
					new_demon_ind = demon_map[demon]
					new_demon = demons.lookup(new_demon_ind)

					if new_demon.phys_inv:
						# choose a new demon from all non-hospital, non-phys invalid demons
						new_choice = random.choice(t_phys)

						# get the index of the new choice for swaping
						for key, value in demon_map.items():
							if value == new_choice:
								new_choice_ind = key

						# swap the two demons in the map
						demon_map[demon] = new_choice
						demon_map[new_choice_ind] = new_demon_ind

	return demon_map

def generate_skill_permutation(balance_by_rank = True, keep_pierce = False):
	# this looks familiar :thinking:
	skill_sets = defaultdict(list)

	# separare skills by rank
	for skill in skills.where():
		skill_id = skill.rank
		if not balance_by_rank:
			# still keep special skills (boss/demon specific) separate
			if skill_id < 100 and skill_id > 0:
				skill_id = 1

		# treak attack/passive/recruitment skills differently 
		skill_id += skill.skill_type * 1000

		# don't shuffle banned skills
		if skill_id <= 0:
			skill_id = skill.ind

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

def randomize_skills(old_level, new_demon, force_skill=None):
	new_skills = []
	new_battle_skills = []

	skill_map = generate_skill_permutation(config_balance_by_skill_rank)

	is_pixie = new_demon.name == 'Pixie'

	for skill in new_demon.skills:
		ind = skill['skill_id']
		try:
			old_skill = skills.lookup(ind)
			new_skill = skills.lookup(skill_map[ind])

			skill['skill_id'] = new_skill.ind
		except KeyError:
			pass

		# fix skill levels
		if skill['level'] > 0:
			if is_pixie:
				skill['level'] = new_demon.level + 1
			else:
				skill['level'] -= old_level
				skill['level'] += new_demon.level

			# make sure skills don't go over or under level
			skill['level'] = min(skill['level'], 100)
			skill['level'] = max(skill['level'], 0)

		new_skills.append(skill)

	if force_skill is not None:
		extend_skills = []

		for s in force_skill:
			# check if the demon already has the skill
			has_skill = False

			for skill in new_skills:
				if skill['skill_id'] == s:
					has_skill = True
					break

			if not has_skill:
				skill = {
					'level': 0,
					'skill_id': s,
					'magic_byte': 1,
					'offset': new_demon.skills[0]['offset']
				}

				extend_skills.append(skill)
				# print('Giving skill: ' + str(s) + ' to ' + str(new_demon))

		for i in range(len(extend_skills)):
			new_skills.pop()
		
		new_skills.reverse()
		new_skills.extend(extend_skills)
		new_skills.reverse()

	# Use the newly generated demon skills for battle skills
	for battle_skill in new_demon.battle_skills:
		try:
			old_skill = skills.lookup(battle_skill)
			new_skill = skills.lookup(skill_map[battle_skill])

			battle_skill = new_skill.ind
			new_battle_skills.append(battle_skill)
		except KeyError:
			pass

	# try to give the demon battle skills if it doesn't have them
	if len(new_battle_skills) == 0 and len(new_skills) > 0:
		count = 0
		for skill in new_skills:
			try:
				skill = skills.lookup(skill['skill_id'])
				if skill.skill_type == 1:
					new_battle_skills.append(skill.ind)
					count += 1
			except KeyError:
				pass

			# arbitrary limit on battle skills
			if count >= 3:
				break

	return [new_skills, new_battle_skills]


def swap_demons(old_demon, new_demon, exp_modifier=1, stat_modifier=1):
	# remember old level to fix skills later
	old_level = new_demon.level

	# take the new demons level, stats, hp, and mp for balancing
	new_demon.level = old_demon.level
	new_demon.hp = round(old_demon.hp * stat_modifier)
	if new_demon.name == "Mara (Boss)":
		new_demon.hp = min(new_demon.hp, 4000)
	if old_demon.name == "Atropos 2 (Boss)":
		new_demon.hp = new_demon.hp * 3
	if new_demon.name == "Atropos 2 (Boss)" or new_demon.name == "Clotho 2 (Boss)" or new_demon.name == "Lachesis 2 (Boss)":
		new_demon.hp = round(new_demon.hp / 3)
	new_demon.mp = round(old_demon.mp * stat_modifier)

	# reduce the level if the demon is a boss appearing early
	if old_level > new_demon.level and new_demon.is_boss:
		new_demon.level = int(math.floor(new_demon.level * 3 / 4))

	new_demon.stats = randomize_stats(math.floor(sum(old_demon.stats) * stat_modifier))

	# multiply exp
	exp = int(math.floor(old_demon.exp_drop * exp_modifier * stat_modifier))
	exp = min(exp, 0xFFFF)

	new_demon.macca_drop = round(old_demon.macca_drop * stat_modifier)
	new_demon.exp_drop = exp

	return new_demon

def randomize_demons(demon_map, exp_modifier=1):
	new_demons = []

	# buffs/debuffs to give to base demons
	skills_to_distribute = [52, 53, 54, 57, 64, 65, 66, 67, 77]
	random.shuffle(skills_to_distribute)

	if config_make_logs:
		f = open("logs/demon_spoiler.txt", "w")

	for ind in demon_map:
		# copy the new demon to change it's stats
		old_demon = demons.lookup(ind)
		new_demon = copy.copy(demons.lookup(demon_map[ind]))

		if not new_demon.is_boss:
			old_level = new_demon.level
			new_demon = swap_demons(old_demon, new_demon, exp_modifier)

			# distribute basic buffs to the base demons
			if old_demon.base_demon and len(skills_to_distribute) > 0:
				skill = [skills_to_distribute.pop()]
				new_demon.skills, new_demon.battle_skills = randomize_skills(old_level, new_demon, skill)
			elif new_demon.name == 'Pixie' and config_give_pixie_estoma_riberama:
				new_demon.skills, new_demon.battle_skills = randomize_skills(old_level, new_demon, [73, 74])
			else:
				new_demon.skills, new_demon.battle_skills = randomize_skills(old_level, new_demon)
			
			new_demons.append(new_demon)

			if config_make_logs:
				f.write(str(old_demon) + " -> " + str(new_demon) + "\n")

	if config_make_logs:
		f.close()

	return new_demons

def randomize_magatamas():
	new_magatamas = []
	# make one skill_map for all magatamas to prevent duplicate skills
	skill_map = generate_skill_permutation(config_balance_by_skill_rank, config_keep_marogareh_pierce)
		
	for old_magatama in magatamas.where():
		new_magatama = copy.copy(old_magatama)

		new_magatama.stats = randomize_stats(sum(old_magatama.stats), False)

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

	offset = battle_offset

	for i in range(N_BATTLES):
		is_boss = rom.read_halfword(offset) == 0x01FF

		if is_boss:
			offset += 0x26
			continue

		offset += 6
		# max # of demons is 11?
		for j in range(0, 22, 2):
			old_demon = rom.read_halfword(offset + j)
			if old_demon > 0:
				new_demon = demon_map.get(old_demon)
				if new_demon:
					rom.write_halfword(new_demon, offset + j)
		offset += 0x20

boss_extras = {
	'Albion (Boss)': [279, 280, 280, 281, 282],	# Urizen, Luvah, Tharmas, Urthona
	'White Rider (Boss)': [359, 359],			# Virtue
	'Red Rider (Boss)': [360, 360],				# Power
	'Black Rider (Boss)': [361, 361],			# Legion
	'Pale Rider (Boss)': [358, 358],  			# Loa
	'Atropos 2 (Boss)': [326, 327]				# Clotho, Lachesis
}

def randomize_boss_battles(world):
	boss_demons = []

	for battle in boss_battles.where():
		old_boss_battle = battle.boss
		new_boss_battle = None

		for check in world.get_checks():
			if check.name == old_boss_battle:
				new_boss = check.boss
				break

		if new_boss is not None:
			new_boss_battle = list(boss_battles.where(boss = new_boss.name))[0]
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

			extras = boss_extras.get(new_boss_demon.name)

			swapped_demon = copy.copy(swap_demons(old_boss_demon, new_boss_demon, config_exp_modifier))
			boss_demons.append(swapped_demon)

			stat_mod = 1
			if extras is not None:
				stat_mod = 1 / (len(extras) + 1)
				if new_boss_demon.name == 'Atropos 2 (Boss)' or old_boss_battle == new_boss.name:
					stat_mod = 1
				for d in extras:
					boss_demons.append(swap_demons(old_boss_demon, demons.lookup(d), config_exp_modifier, stat_mod))

			reward = 0
			if new_boss.reward is not None:
				for magatama in magatamas.where():
					if magatama.name == new_boss.reward.name:
						reward = magatama.ind + 320
						magatama.level = min(magatama.level, round(swapped_demon.level/2))

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

# lmao good luck reading whatever mess this outputs
def write_demon_log(output_path, demons):
	with open(output_path, "w") as file:
		for demon in demons:
			string = "%s %d %d %d " % (demon, demon.level, demon.hp, demon.mp)
			string += str(demon.stats)
			string += " %d %d \n" % (demon.macca_drop, demon.exp_drop)
			string += str(demon.battle_skills) + "\n"
			string += str(demon.skills)
			file.write(string + "\n")

def main(rom_path, output_path):
	random.seed()

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
	world = logic.create_world()
	world = logic.randomize_world(world, logger)

	print('randomizing demons')
	demon_map = generate_demon_permutation(config_easy_hospital)
	new_demons = randomize_demons(demon_map, config_exp_modifier)

	print('randomizing battles')
	randomize_battles(demon_map)
	new_bosses = randomize_boss_battles(world)
	new_demons.extend(new_bosses)
	if config_make_logs:
		write_demon_log('logs/random_demons.txt', new_demons)

	if config_fix_tutorial:
		print("fixing tutorials")
		nocturne.patch_fix_tutorials(rom)

	print('randomizing magatamas')
	new_magatamas = randomize_magatamas()

	if config_easy_recruits:
		print("applying easy recruits patch")
		nocturne.patch_easy_demon_recruits(rom)

	print("copying iso")
	#shutil.copyfile(rom_path, output_path)

	print("writing new binary")
	nocturne.write_all(rom, new_demons, new_magatamas)

	if config_write_binary:
		with open('rom/SLUS_209.11', 'wb') as file:
			file.write(bytearray(rom.buffer))

	with open(output_path, 'r+b') as file:
		file.seek(0xFD009000)
		file.write(bytearray(rom.buffer))

if __name__ == '__main__':
	main('rom/input.iso', 'rom/output.iso')