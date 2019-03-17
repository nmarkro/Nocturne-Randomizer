# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
all_boss_battles = {}

class BossBattle(object):
    def __init__(self, boss, offset):
        self.boss = boss
        self.offset = offset

        self.data = []

    def __repr__(self):
        return str(self.boss)

def add_battle(ind, boss, offset):
    x = BossBattle(boss, offset)
    assert(ind not in all_boss_battles)
    x.ind = ind
    all_boss_battles[ind] = x
    return x

def lookup(ind):
    return all_boss_battles[ind]

def where(**kwargs):
    return filter(lambda battle : all([key in battle.__dict__ and (val(battle.__dict__[key]) if callable(val) else battle.__dict__[key] == val) for key, val in kwargs.items()]), all_boss_battles.values())

def find(**kwargs):
    results = where(**kwargs)
    assert(len(results) == 1)
    return results[0]
