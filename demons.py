# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
all_demons = {}

class Demon(object):
	def __init__(self, name):
		self.name = name

		self.race = None
		self.level = None
		self.hp = None
		self.mp = None
		self.stats = None
		self.macca_drop = None
		self.exp_drop = None

		self.battle_skills = None
		self.demon_skills = None

		self.is_boss = None
		self.phys_inv = None
		self.in_hospital = None

	def __repr__(self):
		return self.name

def add_demon(ind, name):
	x = Demon(name)
	assert(ind not in all_demons)
	x.ind = ind
	all_demons[ind] = x
	return x

def lookup(ind):
	return all_demons[ind]

# like sql
def where(**kwargs):
	return filter(lambda demon : all([key in demon.__dict__ and (val(demon.__dict__[key]) if callable(val) else demon.__dict__[key] == val) for key, val in kwargs.items()]), all_demons.values())

def find(**kwargs):
	results = where(**kwargs)
	assert(len(results) == 1)
	return results[0]