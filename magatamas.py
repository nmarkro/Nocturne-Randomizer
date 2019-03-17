# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
all_magatamas = {}

class Magatama(object):
    def __init__(self, name):
        self.name = name

        self.stats = None
        self.skills = None

    def __repr__(self):
        return self.name

def add_magatama(ind, name):
    x = Magatama(name)
    assert(ind not in all_magatamas)
    x.ind = ind
    all_magatamas[ind] = x
    return x

def lookup(ind):
    return all_magatamas.get(ind)

def where(**kwargs):
    return filter(lambda magatama : all([key in magatama.__dict__ and (val(magatama.__dict__[key]) if callable(val) else magatama.__dict__[key] == val) for key, val in kwargs.items()]), all_magatamas.values())

def find(**kwargs):
    results = where(**kwargs)
    assert(len(results) == 1)
    return results[0]
