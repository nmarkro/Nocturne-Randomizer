# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
all_skills = {}

class Skill(object):
	def __init__(self, name, rank):
		self.name = name
		self.rank = rank

		# skill types
		# 0 = Passive
		# 1 = Attack
		# 2 = Recruitment
		self.skill_type = 1

	def __repr__(self):
		return self.name

def add_skill(ind, name, rank):
	x = Skill(name, rank)
	assert(ind not in all_skills)
	x.ind = ind
	all_skills[ind] = x
	return x

def lookup(ind):
	return all_skills[ind]

def where(**kwargs):
	return filter(lambda skill : all([key in skill.__dict__ and (val(skill.__dict__[key]) if callable(val) else skill.__dict__[key] == val) for key, val in kwargs.items()]), all_skills.values())

def find(**kwargs):
	results = where(**kwargs)
	assert(len(results) == 1)
	return results[0]
