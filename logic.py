import copy
import random

import rules

# should probably move these objects to a separate file
class World(object):
    def __init__(self):
        self.areas = {}
        self.terminals = {}
        self.checks = {}
        self.magatamas = {}
        self.bosses = {}
        self.state = Progression(self)

    def get_area(self, area):
        return self.areas.get(area)

    def get_check(self, check):
        return self.checks.get(check)

    def get_terminal(self, terminal):
        return self.terminals.get(terminal)

    def get_magatama(self, magatama):
        return self.magatamas.get(magatama)

    def get_boss(self, boss):
        return self.bosses.get(boss)

    def get_areas(self):
        return list(self.areas.values())

    def get_checks(self):
        return list(self.checks.values())

    def get_terminals(self):
        return list(self.terminals.values())

    def get_magatamas(self):
        return list(self.magatamas.values())

    def get_bosses(self):
        return list(self.bosses.values())


class Area(object):
    def __init__(self, name):
        self.name = name
        self.rule = lambda state: True
        self.boss_rule = lambda boss: True
        self.terminal = None
        self.checks = []
        self.changed = False

    def can_reach(self, state):
        return self.rule(state)

    def can_place(self, boss):
        return self.boss_rule(boss)


# Checks are boss locations, not the bosses themselves
class Check(object):
    def __init__(self, name, parent):
        self.name = name
        self.rule = lambda state: True
        self.area = parent
        self.boss = None
        self.area.checks.append(self)

    def can_reach(self, state):
        return self.rule(state) and self.area.can_reach(state)

    def can_place(self, boss):
        return self.area.can_place(boss)


# Bosses are the actual boss fights at each check
class Boss(object):
    def __init__(self, name):
        self.name = name
        self.check = None
        self.rule = lambda state: True
        self.reward = None
        self.phys_invalid = False

    def can_beat(self, state):
        return self.rule(state)


class Terminal(object):
    def __init__(self, name, parent):
        self.name = name
        self.area = parent
        self.area.terminal = self
        self.check = None

    def can_reach(self, state):
        return self.area.can_reach(state)


class Magatama(object):
    def __init__(self, name, resistances):
        self.name = name
        self.boss = None
        self.resistances = resistances


# State of players progression in the world
class Progression(object):
    def __init__(self, parent):
        self.world = parent
        self.terminals = {}
        self.checks = {}
        self.magatamas = {}

    def init_checks(self):
        for c in self.world.get_checks():
            self.checks[c.name] = False

        for t in self.world.get_terminals():
            self.terminals[t.name] = False

        for m in self.world.get_magatamas():
            self.magatamas[m.name] = False

    def check(self, check):
        self.checks[check] = True

    def get_terminal(self, terminal):
        self.terminals[terminal] = True

    def get_magatama(self, magatama):
        self.magatamas[magatama] = True

    def remove_terminal(self, terminal):
        self.terminals[terminal] = False

    def remove_magatama(self, magatama):
        self.magatamas[magatama] = False

    def has_checked(self, check):
        return self.checks.get(check) == True

    def has_terminal(self, terminal):
        return self.terminals.get(terminal) == True

    def has_resistance(self, resistance):
        for m in self.world.magatamas.values():
            if self.magatamas[m.name]:
                if resistance in m.resistances:
                    return True
        return False

    def can_warp(self):
        return self.has_checked('Specter 1')


def init_magatamas(world):
    def add_magatama(name, resistances, world):
        m = Magatama(name, resistances)
        world.magatamas[name] = m

    #add_magatama('Marogarah', [], world)
    add_magatama('Wadatsumi', ['Ice'], world)
    add_magatama('Ankh', ['Expel'], world)
    add_magatama('Iyomante', ['Mind'], world)
    add_magatama('Shiranui', ['Fire'], world)
    add_magatama('Hifumi', ['Force'], world)
    add_magatama('Kamudo', ['Phys'], world)
    add_magatama('Narukami', ['Elec'], world)
    add_magatama('Anathema', ['Death'], world)
    add_magatama('Miasma', ['Ice'], world)
    add_magatama('Nirvana', ['Expel'], world)
    add_magatama('Murakumo', ['Phys'], world)
    add_magatama('Geis', ['Expel'], world)
    add_magatama('Muspell', ['Nerve', 'Mind'], world)
    add_magatama('Djed', ['Curse', 'Expel', 'Death'], world)
    add_magatama('Kamurogi', ['Phys', 'Expel', 'Death'], world)
    add_magatama('Gehenna', ['Fire'], world)
    add_magatama('Satan', ['Death'], world)
    add_magatama('Adama', ['Elec', 'Expel', 'Death'], world)
    add_magatama('Vimana', ['Nerve'], world)
    add_magatama('Gundari', ['Force'], world)
    add_magatama('Sophia', ['Expel', 'Death'], world)
    add_magatama('Kailash', [], world)
    #add_magatama('Gaea', ['Phys'], world)


# Resist/Null/Absorb/Repel Phys to leave out of SMC
PHYS_INVALID_BOSSES = ['Ongyo-Ki', 'Aciel', 'Girimehkala', 'Skadi', 'Mada', 'Mot', 'The Harlot', 'Black Frost']

def create_areas(world):
    def add_area(name, world):
        a = Area(name)
        world.areas[name] = a
        return a

    def add_terminal(name, area, world):
        t = Terminal(name, area)
        world.terminals[name] = t

    def add_check(name, area, world):
        c = Check(name, area)
        world.checks[name] = c

        b = Boss(name)
        b.phys_invalid = name in PHYS_INVALID_BOSSES
        world.bosses[name] = b

    smc = add_area('SMC', world)
    add_terminal('SMC', smc, world)
    add_check('Forneus', smc, world)
    add_check('The Harlot', smc, world)
    add_check('Black Rider', smc, world)

    shibuya = add_area('Shibuya', world)
    add_terminal('Shibuya', shibuya, world)
    add_check('Mara', shibuya, world)

    amala_network_1 = add_area('Amala Network 1', world)
    add_check('Specter 1', amala_network_1, world)

    ginza = add_area('Ginza', world)
    add_terminal('Ginza', ginza, world)

    underpass = add_area('Ginza Underpass', world)
    add_terminal('Ginza Underpass', underpass, world)
    add_check('Troll', underpass, world)
    add_check('Matador', underpass, world)
    add_check('Red Rider', underpass, world)

    ikebukuro = add_area('Ikebukuro', world)
    add_terminal('Ikebukuro', ikebukuro, world)
    add_check('Orthrus', ikebukuro, world)
    add_check('Yaksini', ikebukuro, world)
    add_check('Thor 1', ikebukuro, world)
    add_check('Dante 1', ikebukuro, world)
    add_check('Daisoujou', ikebukuro, world)
    add_check('Hell Biker', ikebukuro, world)

    nihilo_e = add_area('Nihilo East', world)
    add_terminal('Nihilo East', nihilo_e, world)
    add_check("Ose", nihilo_e, world)

    ikebukuro_tunnel = add_area('Ikebukuro Tunnel', world)
    add_terminal('Ikebukuro Tunnel', ikebukuro_tunnel, world)
    add_check("Kin-Ki", ikebukuro_tunnel, world)
    add_check("Sui-Ki", ikebukuro_tunnel, world)
    add_check("Fuu-Ki", ikebukuro_tunnel, world)
    add_check("Ongyo-Ki", ikebukuro_tunnel, world)

    kabukicho_prison = add_area('Kabukicho Prison', world)
    add_terminal('Kabukicho Prison', kabukicho_prison, world)
    add_check("Mizuchi", kabukicho_prison, world)
    add_check("Black Frost", kabukicho_prison, world)

    asakusa = add_area('Asakusa', world)
    add_terminal('Asakusa', asakusa, world)
    add_check('Pale Rider', asakusa, world)
    add_check('White Rider', asakusa, world)

    obelisk = add_area('Obelisk', world)
    add_terminal('Obelisk', obelisk, world)
    add_check("Sisters", obelisk, world)

    amala_network_2 = add_area('Amala Network 2', world)
    add_check('Specter 2', amala_network_2, world)

    yoyogi = add_area('Yoyogi Park', world)
    add_terminal('Yoyogi Park', yoyogi, world)
    add_check("Girimehkala", yoyogi, world)

    amala_network_3 = add_area('Amala Network 3', world)
    add_check('Specter 3', amala_network_3, world)

    amala_temple = add_area('Amala Temple', world)
    add_terminal('Amala Temple', amala_temple, world)
    add_check("Albion", amala_temple, world)
    add_check("Aciel", amala_temple, world)
    add_check("Skadi", amala_temple, world)

    mifunashiro = add_area('Mifunashiro', world)
    add_terminal('Mifunashiro', mifunashiro, world)
    add_check("Futomimi", mifunashiro, world)

    yurakucho_tunnel = add_area('Yurakucho Tunnel', world)
    add_terminal('Yurakucho Tunnel', yurakucho_tunnel, world)
    add_check("Trumpeter", yurakucho_tunnel, world)

    diet_building = add_area('Diet Building', world)
    add_terminal('Diet Building', diet_building, world)
    add_check("Surt", diet_building, world)
    add_check("Mada", diet_building, world)
    add_check("Mot", diet_building, world)
    add_check("Mithra", diet_building, world)
    add_check("Samael", diet_building, world)

    lab_of_amala = add_area("Labyrinth of Amala", world)
    add_terminal("Labyrinth of Amala", lab_of_amala, world)
    add_check("Dante 2", lab_of_amala, world)
    add_check("Beelzebub", lab_of_amala, world)
    add_check("Metatron", lab_of_amala, world)

    tok = add_area("ToK", world)
    add_check("Ahriman", tok, world)
    add_check("Noah", tok, world)
    add_check("Thor 2", tok, world)
    add_check("Baal Avatar", tok, world)
    add_check("Kagutsuchi", tok, world)
    add_check("Lucifer", tok, world)


# Bosses not to randomize
BANNED_BOSSES = ['Ongyo-Ki', 'Specter 1', 'Specter 2', 'Specter 3', 'Dante 1', 'Dante 2', 'Ahriman', 'Noah', 'Thor 2', 'Baal Avatar', 'Kagutsuchi', 'Lucifer']

def create_world():
    world = World()
    create_areas(world)
    init_magatamas(world)
    rules.set_rules(world)
    world.state.init_checks()

    return world

def randomize_bosses(boss_pool, check_pool, logger):
    random.shuffle(boss_pool)
    while boss_pool:
        boss = boss_pool.pop()
        chosen_check = None
        candidates = [c for c in check_pool if c.boss is None and c.can_place(boss)]
        chosen_check = random.choice(candidates)
        # can't place boss yet, re-add to the beginning of the boss pool
        if chosen_check is None:
            boss_pool.insert(0, boss)
            continue
        boss.check = chosen_check
        chosen_check.boss = boss
        logger.info("Placing " + boss.name + " at check: " + chosen_check.name)


def randomize_world(world, logger):
    state = world.state
    area_pool = world.get_areas()
    terminal_pool = world.get_terminals()
    check_pool = world.get_checks()
    magatama_pool = world.get_magatamas()
    boss_pool = world.get_bosses()
    # Remove banned bosses from randomized pool
    for boss_name in BANNED_BOSSES:
        boss = next((b for b in boss_pool if b.name == boss_name), None)
        boss_pool.remove(boss)
        check = world.get_check(boss.name)
        check.boss = boss
        boss.check = check
    # Do the initial randomization of bosses
    logger.info('Randomizing bosses')
    randomize_bosses(boss_pool, check_pool, logger)

    # Remove the starting Magatama and Gaea (24 st magatama)
    # marogarah = world.get_magatama('Marogarah')
    # state.get_magatama(marogarah.name)
    # magatama_pool.remove(marogarah)
    # gaea = world.get_magatama('Gaea')
    # magatama_pool.remove(gaea)
    # shuffle magatamas for more random rewards
    random.shuffle(magatama_pool)

    # keep track of bosses beaten for placing magatamas
    bosses_progressed = []
    while world.get_check('Lucifer') in check_pool:
        # keep beating bosses and unlocking terminals until stuck
        has_progressed = True
        while has_progressed:
            has_progressed = False
            for area in area_pool:
                # unlock terminals the player can reach
                if area.terminal in terminal_pool:
                    if area.terminal.can_reach(state):
                        state.get_terminal(area.terminal.name)
                        terminal_pool.remove(area.terminal)
                        logger.info("Getting Terminal: " + area.terminal.name)
                        has_progressed = True
                # beat bosses the player can reach and beat
                for check in area.checks:
                    if check.can_reach(state) and check in check_pool:
                        if check.boss.can_beat(state):
                            state.check(check.name)
                            check_pool.remove(check)
                            logger.info("Beating " + check.boss.name + " at check: " + check.name)
                            has_progressed = True
                            bosses_progressed.append(check.boss)
        # check for game completion 
        if world.get_check('Lucifer') not in check_pool:
            break
        logger.info("Can no longer progress\n")

        # didn't beat any bosses this passthrough, rerandomize unchecked bosses and try again
        if not bosses_progressed:
            #logger.info("Re-randomizing unchecked bosses\n")
            new_boss_pool = []
            for check in check_pool:
                if check.boss.name not in BANNED_BOSSES:
                    new_boss_pool.append(check.boss)
                    check.boss = None
            randomize_bosses(new_boss_pool, check_pool, logger)
            continue
        
        can_progress = False
        shuffled_bosses = copy.copy(bosses_progressed)
        random.shuffle(shuffled_bosses)
        # try to assign magatamas that unlock progression 
        while not can_progress:
            for magatama in magatama_pool:
                state.get_magatama(magatama.name)
                completeable_checks = [c for c in check_pool if c.can_reach(state) and c.boss.can_beat(state)]
                can_progress = bool(completeable_checks is not None)
                if not can_progress:
                    state.remove_magatama(magatama.name)
                else:
                    boss = shuffled_bosses.pop()
                    logger.info("Adding " + magatama.name + " to boss " + boss.name + " at check " + boss.check.name + "\n")
                    boss.reward = magatama
                    magatama.boss = boss
                    magatama_pool.remove(magatama)
                    bosses_progressed.remove(boss)
                    break

    logger.info("Placing unused Magatamas")
    # reverse to add magatamas to bosses from the beginning of the game
    bosses_progressed.reverse()
    while magatama_pool and bosses_progressed:
        boss = bosses_progressed.pop()
        if boss.check.area.name != 'ToK':
            reward = magatama_pool.pop()
            logger.info("Adding " + reward.name + " to boss " + boss.name + " at check " + boss.check.name)
            boss.reward = reward
            reward.boss = boss

    logger.info("Complete spoiler:")
    for check in world.get_checks():
        boss = check.boss
        if boss.reward:
            logger.info("Boss " + boss.name + " is at check " + check.name + " with reward " + boss.reward.name)
        else:
            logger.info("Boss " + boss.name + " is at check " + check.name)
    return world