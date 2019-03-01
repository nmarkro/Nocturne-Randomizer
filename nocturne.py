# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
import copy
import struct
import re
import random

import demons
import skills
import magatamas

N_DEMONS = 383
N_MAGATAMAS = 25

# demons/bosses that absorb/repel/null phys
phys_invalid_demons = [2, 14, 87, 93, 98, 104, 105, 144, 155, 172, 202, 269, 274, 276, 277, 333, 352]

# demons/bosses that are normally in the hospital
hospital_demons = [137, 92, 97, 131, 91, 256]

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
		demon.in_hospital = demon_id in hospital_demons

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
			'magic_byte': magic_byte,
			'skill_id': skill_id,
			'offset': offset,
		}

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
		attack = int(skill_data[i][4])

		skill = skills.add_skill(skill_id, name, rank)
		skill.is_attack = bool(attack & 1)

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

def load_all(rom):
	load_demons(rom)
	load_skills(rom)
	load_magatamas(rom)

def write_all(rom, demons, magatamas):
	write_demons(rom, demons)
	write_magatamas(rom, magatamas)