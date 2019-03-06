# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import copy
import struct
import re
import random

import demons
import skills
import magatamas
import boss_battles

N_DEMONS = 383
N_MAGATAMAS = 25

# demons/bosses that absorb/repel/null phys
phys_invalid_demons = [2, 14, 87, 93, 98, 104, 105, 144, 155, 172, 202, 269, 274, 276, 277, 333, 334, 352]

# demons/bosses that are normally in the hospital/shibuya
base_demons = [137, 92, 97, 131, 91, 126, 103, 135, 136, 256]

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

		demon = demons.add_demon(demon_id, demon_name)
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
			#skill = ord(battle_skills[j : j + 1])
			if skill > 0:
				s.append(skill)

		# battle skills are the skills that show up when you analyze enemy demons (they also show up in demon ai)
		demon.battle_skills = s
		demon.skills = load_demon_skills(rom, demon_id)

		demon.is_boss = bool(i >= 255)

		# keep track of phys invalid demons and demons in the hospital for "Easy Hospital"
		demon.phys_inv = demon_id in phys_invalid_demons
		demon.base_demon = demon_id in base_demons

		demon.offset = demon_offset

def load_demon_skills(rom, demon_id):
	skill_offset = 0x00234CF4

	s = []

	rom.save_offsets()

	offset = skill_offset + (demon_id * 0x66)
	rom.seek(offset + 0x0A)

	count = 0
	while True:
		# level at which they learn the skill 
		level = rom.read_byte()
		# lmao idk what this is, has something to do with evolutions maybe?
		magic_byte = rom.read_byte()
		skill_id = rom.read_halfword()

		if magic_byte == 0 or count >= 17:
			break

		skill = {
			'level': level,
			# hopefully fix evolution demons with no skills
			#'magic_byte': magic_byte,
			'magic_byte': 1,
			'skill_id': skill_id,
			'offset': offset,
		}

		if skill not in s:
			s.append(skill)
			count += 1

	rom.load_offsets()
	return s


def load_skills(rom):
	skill_data = open('data/skill_data.txt', 'r').read().strip()
	pattern = re.compile(r"([\dABCDEF]{3}) ([\w\'\&\- ]+) (\d+) (\d+)")

	skill_data = list(map(lambda s: re.search(pattern, s), skill_data.split('\n')))

	for i in range(len(skill_data)):
		skill_id = int(skill_data[i][1], 16)
		name = skill_data[i][2]
		rank = int(skill_data[i][3])
		skill_type = int(skill_data[i][4])

		skill = skills.add_skill(skill_id, name, rank)
		skill.skill_type = skill_type

def load_magatamas(rom):
	magatama_offset = 0x0023AE3A

	magatama_names = open('data/magatama_names.txt', 'r').read().strip()
	magatama_names = magatama_names.split('\n')

	rom.seek(magatama_offset)
	for i in range(N_MAGATAMAS):
		magatama_name = magatama_names[i]

		magatama_offset = rom.r_offset
		_, strength, _, magic, vitality, agility, luck, _, skills = struct.unpack('<14sBBBBBB14s32s', rom.read(0x42))

		magatama = magatamas.add_magatama(i, magatama_name)
		magatama.stats = [strength, magic, vitality, agility, luck]
		
		s = []
		for j in range(0, len(skills), 4):
			level, skill_id = struct.unpack('<HH', skills[j : j + 4])
			if skill_id > 0:
				skill = {
					'level': level,
					'skill_id': skill_id,
				}
				s.append(skill)
		magatama.skills = s
		magatama.offset = magatama_offset

def load_boss_battles(rom):
	battle_offset = 0x002AFFE0
	N_BATTLES = 1270

	rom.seek(battle_offset)
	for i in range(N_BATTLES):
		offset = rom.r_offset
		is_boss, item_drop, phase_value, demons, arena, first_turn, reinforcement_value, music = struct.unpack('<HHH22sIHHH', rom.read(0x26))

		if is_boss == 0x01FF:
			boss = 0
			data = []
			for j in range(0, 22, 2):
				demon_id = struct.unpack('<H', demons[j : j + 2])[0]
				data.append(demon_id)
				if demon_id >= 100:
					boss = demon_id

			battle = boss_battles.add_battle(i, boss, offset)
			battle.phase_value = phase_value
			battle.data = data
			battle.arena = arena
			battle.first_turn = first_turn
			battle.reinforcement_value = reinforcement_value
			battle.music = music

def write_demons(rom, new_demons):
	for demon in new_demons:
		rom.seek(demon.offset)

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
			rom.seek(demon.offset + 0x22)
			for i in range(8):
				if i < len(demon.battle_skills):
					skill = demon.battle_skills[i]
					rom.write_halfword(skill)
				else:
					rom.write_halfword(0)

			write_skills(rom, demon)
			write_ai(rom, demon)

def write_skills(rom, demon):
	for i in range(len(demon.skills)):
		skill = demon.skills[i]
		offset = (skill['offset'] + 0x0A) + (i * 0x04)
		rom.seek(offset)
		rom.write_byte(skill['level'])
		rom.write_byte(skill['magic_byte'])
		rom.write_halfword(skill['skill_id'])

def write_ai(rom, demon):
	ai_offset = 0x002999E4

	offset = (ai_offset + (demon.ind * 0xA4)) + 0x24

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

def patch_easy_demon_recruits(rom):
	# patch the flag check during demon recruiting to use an always(?) zero flag as oppsed to the forneus flag
	patch = 0x24040000						# li a0, 0x0
	rom.write_word(patch, 0x00171584)		# replaces li a0, 0x8
	rom.write_word(patch, 0x001720E4)		# replaces li a0, 0x8
	rom.write_word(patch, 0x001715D8)		# replaces li a0, 0x8
	rom.write_word(patch, 0x00171670)		# replaces li a0, 0x8
	rom.write_word(patch, 0x00171A18)		# replaces li a0, 0x8
	rom.write_word(patch, 0x001719D4)		# replaces li a0, 0x8
	rom.write_word(patch, 0x001737E4)		# replaces li a0, 0x8

def patch_fix_tutorials(rom):
	# replaces the 1x preta and 2x sudamas tutorial fights with the unmodified, scipted will o' wisp demons
	tutorial_2_offset = 0x002BBBF8
	tutorial_3_offset = 0x002BBC1E

	rom.write(struct.pack('<H', 0x13E), tutorial_2_offset)
	rom.write(struct.pack('<HH', 0x13E, 0x13E), tutorial_3_offset)

def patch_unlock_compendium(rom):
	# this a real hack-y way of doing this that I need to fix later (probably with a hooked function)
	# makes entering the SMC terminal (which is forced) unlock the compendium
	rom.write_halfword(0x0028, 0x001FD1A6)	# set the SMC termnal flag to be the same flag as the compedium flag

def load_all(rom):
	load_demons(rom)
	load_skills(rom)
	load_magatamas(rom)
	load_boss_battles(rom)

def write_all(rom, demons, magatamas):
	write_demons(rom, demons)
	write_magatamas(rom, magatamas)