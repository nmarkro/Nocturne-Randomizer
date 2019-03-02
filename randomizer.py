# a lot of code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import random
import struct
import copy
import math
from collections import defaultdict

from rom import Rom
import demons
import skills
import magatamas

# Config
config_balance_by_skill_rank = False	# Permutate skills based on rank
config_exp_modifier = 2					# Mulitlpy EXP values of demons
config_make_logs = True 				# Write various data to the logs/ folder
config_write_binary = True 				# Write the game's binary to a separe file for easier hex reading
config_fix_tutorial = True 				# replace a few tutorial fights
config_balance_mp = True 				# multiply mp values of enemy demons so they can use higher ranked skills at a lower level
config_easy_hospital = True				# Force hospital demons/boss to not have null/repel/abs phys
config_keep_marogareh_pierce = True		# Don't randomize Pierce on Maraogareh
config_easy_recruits = True				# Patch game so demon recruits always succeed after giving 2 things

# Bosses to replace
# these are the ones I think won't cause issues, but I haven't tested them all yet
allowed_boss_ids = [
	256, 262, 263, 265, 266, 267, 268, 269, 274, 276, 277, 278, 283, 284, 285, 
	286, 287, 297, 300, 301, 302, 303, 317, 320, 321, 322, 323, 324, 325, 329, 
	333, 334, 335, 337, 342, 343, 345, 346, 347, 348, 349, 350, 351, 352, 353
]

def init_rom_data(rom_path):
	global rom
	rom = Rom(rom_path)

def generate_demon_permutation(easy_hospital = False):
	all_hospital = list(map(lambda demon: demon.ind, demons.where(in_hospital = True)))
	all_phys_inv = list(map(lambda demon: demon.ind, demons.where(phys_inv = True)))

	demon_sets = defaultdict(list)
	# divide demons and bosses
	for demon in demons.where():
		demon_id = 1
		# only include the allowed bosses
		if demon.is_boss:
			if demon.ind in allowed_boss_ids:
				demon_id = 2
			else:
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
			t_hosp = list(set(vals).intersection(all_hospital))

			# get phys invalid demons in current set and remove all hospital demons
			t_phys = set(vals).difference(all_phys_inv)
			t_phys = list(t_phys.difference(t_hosp))

			if t_hosp:
				# iterate through each hospital demon looking for conflicts
				for demon in t_hosp:
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
		# treak attack skills differently 
		if skill.is_attack:
			skill_id += 1000

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

def randomize_stats(old_stats, req_min = True):
	# todo: make this not kinda shit
	# get total number of stat points
	total_stats = sum(old_stats)

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

def randomize_skills(old_level, new_demon):
	new_skills = []
	new_battle_skills = []

	skill_map = generate_skill_permutation(config_balance_by_skill_rank)

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
			skill['level'] -= old_level
			skill['level'] += new_demon.level
			# make sure skills don't go over or under level
			skill['level'] = min(skill['level'], 100)
			skill['level'] = max(skill['level'], 0)

		new_skills.append(skill)
		
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
				if skill.is_attack:
					new_battle_skills.append(skill.ind)
					count += 1
			except KeyError:
				pass

			# arbitrary limit on battle skills
			if count >= 3:
				break

	return [new_skills, new_battle_skills]


def randomize_demons(demon_map, exp_modifier=1, balance_mp=False):
	new_demons = []

	if config_make_logs:
		f = open("logs/demon_spoiler.txt", "w")

	for ind in demon_map:
		# copy the new demon to change it's stats
		old_demon = demons.lookup(ind)
		new_demon = copy.copy(demons.lookup(demon_map[ind]))

		# remember old level to fix skills later
		old_level = new_demon.level

		# take the new demons level, stats, hp, and mp for balancing
		new_demon.level = old_demon.level
		new_demon.hp = old_demon.hp

		# multiply mp 
		mp = old_demon.mp
		if balance_mp:
			# 5x for now
			mp = int(mp * 5)
			mp = min(mp, 0xFFFF)
		new_demon.mp = mp

		new_demon.stats = randomize_stats(old_demon.stats)

		# multiply exp
		exp = int(math.floor(old_demon.exp_drop * exp_modifier))
		exp = min(exp, 0xFFFF)

		new_demon.macca_drop = old_demon.macca_drop
		new_demon.exp_drop = exp

		# don't change the skills of bosses
		if not new_demon.is_boss:
			new_demon.skills, new_demon.battle_skills = randomize_skills(old_level, new_demon)
			
		new_demons.append(new_demon)

		if config_make_logs:
			f.write(str(old_demon) + " -> " + str(new_demon) + "\n")

	if config_make_logs:
		f.close()

	return new_demons

def randomize_magatamas():
	new_magatamas = []

	for old_magatama in magatamas.where():
		skill_map = generate_skill_permutation(config_balance_by_skill_rank, config_keep_marogareh_pierce)
		new_magatama = copy.copy(old_magatama)

		new_magatama.stats = randomize_stats(old_magatama.stats, False)

		new_skills = []
		for skill in new_magatama.skills:
			ind = skill['skill_id']
			new_skill = skill_map.get(ind)
			if new_skill:
				skill['skill_id'] = new_skill
			new_skills.append(skill)

		new_magatama.skills = new_skills
		new_magatamas.append(new_magatama)
	return new_magatamas

def randomize_battles(demon_map):
	battle_offset = 0x002AFFE0
	N_BATTLES = 1270

	offset = battle_offset + 6

	for i in range(N_BATTLES):
		# max # of demons is 10?
		for j in range(0, 20, 2):
			old_demon = rom.read_halfword(offset + j)
			if old_demon > 0:
				new_demon = demon_map.get(old_demon)
				if new_demon:
					rom.write_halfword(new_demon, offset + j)
			#else:
			#	break
		offset += 0x26

def fix_tutorials():
	# replaces the 1x preta and 2x sudamas tutorial fights with the unmodified, scipted will o' wisp demons
	tutorial_2_offset = 0x002BBBF8
	tutorial_3_offset = 0x002BBC1E

	rom.write(struct.pack('<H', 0x13E), tutorial_2_offset)
	rom.write(struct.pack('<HH', 0x13E, 0x13E), tutorial_3_offset)

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

	print('opening iso')
	init_rom_data(rom_path)

	print('initializing data')
	import nocturne
	nocturne.load_all(rom)

	if config_make_logs:
		write_demon_log('logs/demons.txt', demons.where())

	print('randomizing demons')
	demon_map = generate_demon_permutation(config_easy_hospital)
	new_demons = randomize_demons(demon_map, config_exp_modifier, config_balance_mp)
	if config_make_logs:
		write_demon_log('logs/random_demons.txt', new_demons)

	print('randomizing battles')
	randomize_battles(demon_map)

	if config_fix_tutorial:
		print("fixing tutorials")
		fix_tutorials()

	print('randomizing magatamas')
	new_magatamas = randomize_magatamas()

	print("applying easy recruits patch")
	if config_easy_recruits:
		nocturne.patch_demon_recruits(rom)

	print("copying iso")
	copyfile(rom_path, output_path)

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