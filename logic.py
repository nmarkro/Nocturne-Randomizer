import copy
import random

import nocturne
import rules
from base_classes import *

def init_magatamas(world):
    def add_magatama(name, resistances, world):
        m = Magatama(name)
        m.resistances = resistances
        world.magatamas[name] = m

    add_magatama('Marogareh', [], world)
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
    add_magatama('Djed', ['Curse'], world)
    add_magatama('Kamurogi', ['Phys'], world)
    add_magatama('Gehenna', ['Fire'], world)
    add_magatama('Satan', ['Death'], world)
    add_magatama('Adama', ['Elec'], world)
    add_magatama('Vimana', ['Nerve'], world)
    add_magatama('Gundari', ['Force'], world)
    add_magatama('Sophia', ['Expel'], world)
    add_magatama('Kailash', [], world)
    add_magatama('Gaea', ['Phys'], world)
    add_magatama('Masakados', [], world)


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

    def add_check(name, area, world, offset):
        c = Check(name, area)
        c.offset = offset
        world.checks[name] = c

        b = Boss(name)
        b.battle = nocturne.all_battles.get(offset)
        b.phys_invalid = name in PHYS_INVALID_BOSSES
        world.bosses[name] = b

    smc = add_area('SMC', world)
    add_terminal('SMC', smc, world)
    add_check('Forneus', smc, world, 2818548)
    add_check('The Harlot', smc, world, 2857194)
    add_check('Black Rider', smc, world, 2857042)

    shibuya = add_area('Shibuya', world)
    add_terminal('Shibuya', shibuya, world)
    add_check('Mara', shibuya, world, 2845110)

    amala_network_1 = add_area('Amala Network 1', world)
    add_check('Specter 1', amala_network_1, world, 2818776)

    ginza = add_area('Ginza', world)
    add_terminal('Ginza', ginza, world)

    underpass = add_area('Ginza Underpass', world)
    add_terminal('Ginza Underpass', underpass, world)
    add_check('Troll', underpass, world, 2820106)
    add_check('Matador', underpass, world, 2857080)
    add_check('Red Rider', underpass, world, 2857004)

    ikebukuro = add_area('Ikebukuro', world)
    add_terminal('Ikebukuro', ikebukuro, world)
    add_check('Orthrus', ikebukuro, world, 2821170)
    add_check('Yaksini', ikebukuro, world, 2821208)
    add_check('Thor 1', ikebukuro, world, 2821246)
    add_check('Dante 1', ikebukuro, world, 2857270)
    add_check('Daisoujou', ikebukuro, world, 2857156)
    add_check('Hell Biker', ikebukuro, world, 2857118)

    nihilo_e = add_area('Nihilo East', world)
    add_terminal('Nihilo East', nihilo_e, world)
    add_check("Ose", nihilo_e, world, 2822462)

    ikebukuro_tunnel = add_area('Ikebukuro Tunnel', world)
    add_terminal('Ikebukuro Tunnel', ikebukuro_tunnel, world)
    add_check("Kin-Ki", ikebukuro_tunnel, world, 2825464)
    add_check("Sui-Ki", ikebukuro_tunnel, world, 2825502)
    add_check("Fuu-Ki", ikebukuro_tunnel, world, 2825540)
    add_check("Ongyo-Ki", ikebukuro_tunnel, world, 2825578)

    kabukicho_prison = add_area('Kabukicho Prison', world)
    add_terminal('Kabukicho Prison', kabukicho_prison, world)
    add_check("Mizuchi", kabukicho_prison, world, 2825388)
    add_check("Black Frost", kabukicho_prison, world, 2845148)

    asakusa = add_area('Asakusa', world)
    add_terminal('Asakusa', asakusa, world)
    add_check('Pale Rider', asakusa, world, 2856928)
    add_check('White Rider', asakusa, world, 2856966)

    obelisk = add_area('Obelisk', world)
    add_terminal('Obelisk', obelisk, world)
    add_check("Sisters", obelisk, world, 2828314)

    amala_network_2 = add_area('Amala Network 2', world)
    add_check('Specter 2', amala_network_2, world, 2828124)

    yoyogi = add_area('Yoyogi Park', world)
    add_terminal('Yoyogi Park', yoyogi, world)
    add_check("Girimehkala", yoyogi, world, 2829682)

    amala_network_3 = add_area('Amala Network 3', world)
    add_check('Specter 3', amala_network_3, world, 2828162)

    amala_temple = add_area('Amala Temple', world)
    add_terminal('Amala Temple', amala_temple, world)
    add_check("Albion", amala_temple, world, 2828808)
    add_check("Aciel", amala_temple, world, 2830442)
    add_check("Skadi", amala_temple, world, 2830480)

    mifunashiro = add_area('Mifunashiro', world)
    add_terminal('Mifunashiro', mifunashiro, world)
    add_check("Futomimi", mifunashiro, world, 2843628)

    yurakucho_tunnel = add_area('Yurakucho Tunnel', world)
    add_terminal('Yurakucho Tunnel', yurakucho_tunnel, world)
    add_check("Trumpeter", yurakucho_tunnel, world, 2857232)

    diet_building = add_area('Diet Building', world)
    add_terminal('Diet Building', diet_building, world)
    add_check("Surt", diet_building, world, 2855522)
    add_check("Mada", diet_building, world, 2855446)
    add_check("Mot", diet_building, world, 2855484)
    add_check("Mithra", diet_building, world, 2854876)
    add_check("Samael", diet_building, world, 2843552)

    lab_of_amala = add_area("Labyrinth of Amala", world)
    add_terminal("Labyrinth of Amala", lab_of_amala, world)
    add_check("Dante 2", lab_of_amala, world, 2857346)
    add_check("Beelzebub", lab_of_amala, world, 2835116)
    add_check("Metatron", lab_of_amala, world, 2835078)

    tok = add_area("ToK", world)
    add_check("Ahriman", tok, world, 2855712)
    add_check("Noah", tok, world, 2855750)
    add_check("Thor 2", tok, world, 2856320)
    add_check("Baal Avatar", tok, world, 2830670)
    add_check("Kagutsuchi", tok, world, 2835990)
    add_check("Lucifer", tok, world, 2835154)


# Bosses not to randomize
BANNED_BOSSES = ['Ongyo-Ki', 'Specter 1', 'Specter 2', 'Specter 3', 'Dante 1', 'Dante 2', 'Ahriman', 'Noah', 'Thor 2', 'Baal Avatar', 'Kagutsuchi', 'Lucifer']

def create_world():
    world = World()
    create_areas(world)
    init_magatamas(world)
    rules.set_rules(world)
    world.state.init_checks()

    return world

def randomize_bosses(boss_pool, check_pool, logger, attempts=100):
    random.shuffle(boss_pool)
    random.shuffle(check_pool)
    while boss_pool:
        if attempts < 0:
            raise Exception("Stuck: Could not randomize bosses")
        boss = boss_pool.pop()
        candidates = [c for c in check_pool if c.boss is None and c.can_place(boss)]
        # can't place boss yet, re-add to the beginning of the boss pool
        if not candidates:
            boss_pool.insert(0, boss)
            attempts -= 1
            continue
        chosen_check = random.choice(candidates)
        boss.check = chosen_check
        chosen_check.boss = boss
        logger.info("Placing " + boss.name + " at check: " + chosen_check.name)


def randomize_world(world, logger, attempts=100):
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
    try:
        randomize_bosses(boss_pool, check_pool, logger)
    except:
        print('Error generating world, trying again')
        return None

    # Remove the starting Magatama and Gaea (24 st magatama)
    marogareh = world.get_magatama('Marogareh')
    state.get_magatama(marogareh.name)
    magatama_pool.remove(marogareh)
    gaea = world.get_magatama('Gaea')
    magatama_pool.remove(gaea)
    masakados = world.get_magatama('Masakados')
    magatama_pool.remove(masakados)
    # shuffle magatamas for more random rewards
    random.shuffle(magatama_pool)

    # keep track of bosses beaten for placing magatamas
    bosses_progressed = []
    while world.get_check('Lucifer') in check_pool:
        if attempts < 0:
            print('Error generating world, trying again')
            return None

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
            try:
                randomize_bosses(new_boss_pool, check_pool, logger)
            except:
                print('Error generating world, trying again')
                return None
            attempts -= 1
            continue
        
        can_progress = False
        shuffled_bosses = copy.copy(bosses_progressed)
        random.shuffle(shuffled_bosses)
        # try to assign magatamas that unlock progression 
        while not can_progress:
            for magatama in magatama_pool:
                state.get_magatama(magatama.name)
                completeable_checks = [c for c in check_pool if c.can_reach(state) and c.boss.can_beat(state)]
                can_progress = bool(completeable_checks)
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