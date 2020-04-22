import copy
import random
import logging
import os

import nocturne
import rules
from base_classes import *

def init_magatamas(world):
    world.add_magatama('Marogareh', [], 1)
    world.add_magatama('Wadatsumi', ['Ice'], 2)
    world.add_magatama('Ankh', ['Expel'], 3)
    world.add_magatama('Iyomante', ['Mind'], 4)
    world.add_magatama('Shiranui', ['Fire'], 5)
    world.add_magatama('Hifumi', ['Force'], 6)
    world.add_magatama('Kamudo', ['Phys'], 7)
    world.add_magatama('Narukami', ['Elec'], 8)
    world.add_magatama('Anathema', ['Death'], 9)
    world.add_magatama('Miasma', ['Ice'], 10)
    world.add_magatama('Nirvana', ['Expel'], 11)
    world.add_magatama('Murakumo', ['Phys'], 12)
    world.add_magatama('Geis', ['Expel'], 13)
    world.add_magatama('Djed', ['Curse'], 14)
    world.add_magatama('Muspell', ['Nerve', 'Mind'], 15)
    world.add_magatama('Gehenna', ['Fire'], 16)
    world.add_magatama('Kamurogi', ['Phys'], 17)
    world.add_magatama('Satan', ['Death'], 18)
    world.add_magatama('Adama', ['Elec'], 19)
    world.add_magatama('Vimana', ['Nerve'], 20)
    world.add_magatama('Gundari', ['Force'], 21)
    world.add_magatama('Sophia', ['Expel'], 22)
    world.add_magatama('Gaea', ['Phys'], 23)
    world.add_magatama('Kailash', [], 24)
    world.add_magatama('Masakados', [], 25)


def create_areas(world):
    smc = world.add_area('SMC')
    world.add_terminal(smc, 0x441)
    world.add_check('Forneus', smc, 2818548)
    world.add_check('Black Rider', smc, 2857042)

    shibuya = world.add_area('Shibuya')
    world.add_terminal(shibuya, 0x481)
    world.add_check('Mara', shibuya, 2845110)
    world.add_flag('Eggplant', 0x3F6)

    amala_network_1 = world.add_area('Amala Network 1')
    world.add_check('Specter 1', amala_network_1, 2818776)

    ginza = world.add_area('Ginza')
    world.add_terminal(ginza, 0x4C1)
    world.add_check('Troll', ginza, 2820106)

    underpass = world.add_area('Ginza Underpass')
    world.add_terminal(underpass, 0x521)
    world.add_check('Matador', underpass, 2857080)
    world.add_check('Red Rider', underpass, 2857004)

    ikebukuro = world.add_area('Ikebukuro')
    world.add_terminal(ikebukuro, 0x5A1)
    world.add_check('Orthrus', ikebukuro, 2821170)
    world.add_check('Yaksini', ikebukuro, 2821208)
    world.add_check('Thor 1', ikebukuro, 2821246)
    world.add_check('Dante 1', ikebukuro, 2857270)
    world.add_check('Daisoujou', ikebukuro, 2857156)
    world.add_check('Hell Biker', ikebukuro, 2857118)

    nihilo_e = world.add_area('Nihilo East')
    world.add_terminal(nihilo_e, 0x4E1)
    world.add_check("Berith", nihilo_e, 2822386)
    world.add_check("Kaiwan", nihilo_e, 2822424)
    world.add_check("Ose", nihilo_e, 2822462)

    ikebukuro_tunnel = world.add_area('Ikebukuro Tunnel')
    world.add_terminal(ikebukuro_tunnel, 0x541)
    world.add_check("Kin-Ki", ikebukuro_tunnel, 2825464)
    world.add_check("Sui-Ki", ikebukuro_tunnel, 2825502)
    world.add_check("Fuu-Ki", ikebukuro_tunnel, 2825540)
    world.add_check("Ongyo-Ki", ikebukuro_tunnel, 2825578)

    kabukicho_prison = world.add_area('Kabukicho Prison')
    world.add_terminal(kabukicho_prison, 0x581)
    world.add_check("Mizuchi", kabukicho_prison, 2825388)

    asakusa = world.add_area('Asakusa')
    world.add_terminal(asakusa, 0x5C1)
    world.add_check('Pale Rider', asakusa, 2856928)
    world.add_check("Black Frost", asakusa, 2845148)
    world.add_check('White Rider', asakusa, 2856966)
    world.add_check('Bishamon 1', asakusa, 2845186)
    world.add_flag("Apocalypse Stone", 0x3F4)

    obelisk = world.add_area('Obelisk')
    world.add_terminal(obelisk, 0x4E2)
    world.add_check("Sisters", obelisk, 2828314)

    amala_network_2 = world.add_area('Amala Network 2')
    world.add_check('Specter 2', amala_network_2, 2828124)

    yoyogi = world.add_area('Yoyogi Park')
    world.add_terminal(yoyogi, 0x461)
    world.add_check("Girimehkala", yoyogi, 2829682)
    world.add_check('The Harlot', yoyogi, 2857194)
    world.add_flag('Golden Goblet', 0x3F5)

    amala_network_3 = world.add_area('Amala Network 3') 
    world.add_check('Specter 3', amala_network_3, 2828162)

    amala_temple = world.add_area('Amala Temple')
    world.add_terminal(amala_temple, 0x6A1)
    world.add_check("Albion", amala_temple, 2828808)
    world.add_check("Aciel", amala_temple, 2830442)
    world.add_check("Skadi", amala_temple, 2830480)
    world.add_flag("Black Key", 0x3F1)
    world.add_flag("White Key", 0x3F2)
    world.add_flag("Red Key", 0x3F3)

    mifunashiro = world.add_area('Mifunashiro')
    world.add_terminal(mifunashiro, 0x6E1)
    world.add_check("Futomimi", mifunashiro, 2843628)

    yurakucho_tunnel = world.add_area('Yurakucho Tunnel')
    world.add_terminal(yurakucho_tunnel, 0x501)
    world.add_check("Trumpeter", yurakucho_tunnel, 2857232)

    diet_building = world.add_area('Diet Building')
    world.add_terminal( diet_building, 0x681)
    world.add_check("Surt", diet_building, 2855522)
    world.add_check("Mada", diet_building, 2855446)
    world.add_check("Mot", diet_building, 2855484)
    world.add_check("Mithra", diet_building, 2854876)
    world.add_check("Samael", diet_building, 2843552)

    lab_of_amala = world.add_area("Labyrinth of Amala")
    world.add_terminal(lab_of_amala, 0x751)
    world.add_check("Dante 2", lab_of_amala, 2857346)
    world.add_check("Beelzebub", lab_of_amala, 2835116)
    world.add_check("Metatron", lab_of_amala, 2835078)

    tok = world.add_area("ToK")
    world.add_check("Ahriman", tok, 2855712)
    world.add_check("Noah", tok, 2855750)
    world.add_check("Thor 2", tok, 2856320)
    world.add_check("Baal Avatar", tok, 2830670)
    world.add_check("Kagutsuchi", tok, 2835990)
    world.add_check("Lucifer", tok, 2835154)

    pyramidion = world.add_flag('Pyramidion', 0x3da)
    earthstone = world.add_flag('Earthstone', None)
    netherstone = world.add_flag('Netherstone', None)
    heavenstone = world.add_flag('Heavenstone', None)
    world.get_check('Samael').flag_rewards = [pyramidion]
    world.get_check('Ahriman').flag_rewards = [earthstone]
    world.get_check('Noah').flag_rewards = [netherstone]
    world.get_check('Baal Avatar').flag_rewards = [heavenstone]

    bandou = world.add_area('Bandou Shrine')
    world.add_check("Bishamon 2", bandou, 2848606)
    world.add_check("Jikoku", bandou, 2848644)
    world.add_check("Koumoku", bandou, 2854344)
    world.add_check("Zouchou", bandou, 2854382)


# Bosses not to randomize
BANNED_BOSSES = ['Ongyo-Ki', 'Specter 1', 'Specter 2', 'Specter 3', 'Ahriman', 'Noah', 'Thor 2', 'Baal Avatar', 'Kagutsuchi', 'Lucifer']

def create_world():
    world = World()
    create_areas(world)
    init_magatamas(world)
    rules.set_rules(world)
    world.state.init_checks()

    return world

def randomize_bosses(boss_pool, check_pool, logger, attempts=100):
    random.shuffle(boss_pool)
    # try to place the smc banned bosses first
    boss_pool = sorted(boss_pool, key=lambda b: b.smc_banned)
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

def collect_possible_rewards(state, excluded_checks=[]):
    checks = [c for c in state.world.get_checks() if c.name not in excluded_checks]
    can_progress = True
    while can_progress:
        for a in state.world.get_areas():
            if a.terminal_flag and a.can_reach(state):
                state.get_terminal(a.name)
        can_progress = [c for c in checks if c.can_beat(state)]
        for c in can_progress:
            state.check(c.name)
            if c.boss.reward:
                state.get_reward(c.boss.reward)
            for f in c.flag_rewards:
                state.get_reward(f)
            checks.remove(c)
    return state

def randomize_world(world, logger, attempts=100):
    if attempts <= 0:
        logger.info('Error generating world, returning None')
        return None
    
    if os.path.exists('logs'):
        with open('logs/spoiler.log', 'w') as f:
            f.write('')

    state = world.state
    flag_pool = [f for f in world.get_flags() if not f.is_terminal]
    magatama_pool = world.get_magatamas()
    boss_pool = world.get_bosses()
    # Remove banned bosses from randomized pool
    for boss_name in BANNED_BOSSES:
        boss = world.get_boss(boss_name)
        boss_pool.remove(boss)
        check = world.get_check(boss.name)
        check.boss = boss
        boss.check = check
    # Do the initial randomization of bosses
    logger.info('Randomizing bosses')
    try:
        randomize_bosses(boss_pool, state.world.get_checks(), logger)
    except:
        logger.info('Error generating world, trying again')   
        logger.info("")
        logger.info("========================================")
        logger.info("")
        return randomize_world(create_world(), logger, attempts - 1)

    logger.info("")
    logger.info("========================================")
    logger.info("")

    # Remove the starting Magatama and Gaea (24 st magatama)
    state.get_magatama('Marogareh')
    magatama_pool.remove(world.get_magatama('Marogareh'))
    # magatama_pool.remove(world.get_magatama('Gaea'))
    magatama_pool.remove(world.get_magatama('Masakados'))
    # remove the fixed flags and terminal flags
    flag_pool.remove(world.get_flag('Pyramidion'))
    flag_pool.remove(world.get_flag('Earthstone'))
    flag_pool.remove(world.get_flag('Netherstone'))
    flag_pool.remove(world.get_flag('Heavenstone'))

    # give a random bonus starting magatama
    random.shuffle(magatama_pool)
    world.bonus_magatama = magatama_pool.pop()
    state.get_magatama(world.bonus_magatama.name)
    logger.info('Bonus Magatama: {}'.format(world.bonus_magatama.name))

    reward_pool = magatama_pool + flag_pool
    random.shuffle(reward_pool)

    # create a starting state where the player has every reward
    for r in reward_pool:
        state.get_reward(r)

    reward_attempts = 100
    while reward_pool:
        if reward_attempts <= 0:
            logger.info('Error generating world, trying again')
            logger.info("")
            logger.info("========================================")
            logger.info("")
            return randomize_world(create_world(), logger, attempts - 1)
        # remove rewards one-by-one and attempt to place them in a check that the player can beat without the reward
        r = reward_pool.pop()
        state.remove_reward(r)

        # create a test state with all unplaced rewards (excluding the current reward) that tries to collect all placed rewards
        test_state = collect_possible_rewards(copy.deepcopy(state))
        # try to add the reward to any completed checks in our test state
        shuffled_checks = [c for c in state.world.get_checks() if test_state.has_checked(c.name)]
        random.shuffle(shuffled_checks)
        for c in shuffled_checks:
            if c.boss.can_add_reward(r):
                c.boss.add_reward(r)
                logger.info('Adding {} to check {}'.format(r.name, c.name))
                break
        else:
            # couldn't find a place to put the reward
            # re-collect the reward and add it to the beginning of the pool
            reward_pool.insert(0, r)
            state.get_reward(r)
            reward_attempts -= 1

    logger.info("")
    logger.info("========================================")
    logger.info("")

    # reset the state to the beginning and do a test playthrough to make sure it's completable
    # also for generating a spoiler log
    state.init_checks()
    state.get_magatama('Marogareh')
    state.get_magatama(world.bonus_magatama.name)

    while not state.has_checked('Kagutsuchi'):
        for a in state.world.get_areas():
            if a.terminal_flag and a.can_reach(state):
                state.get_terminal(a.name)
        for c in [c for c in state.world.get_checks() if not state.has_checked(c.name)]:
            if c.can_beat(state):
                state.check(c.name)
                logger.info("Beating boss {} at check {}".format(c.boss.name, c.name))
                if c.boss.reward:
                    logger.info("Getting reward " + c.boss.reward.name)
                    state.get_reward(c.boss.reward)
                for f in c.flag_rewards:
                    logger.info("Getting flag reward " + f.name)
                    state.get_reward(f)

    logger.info('Finished generating world in {} attempt(s)'.format(101 - attempts))
    return world

if __name__ == '__main__':
    logger = logging.getLogger('')
    logging.basicConfig(filename='logs/spoiler.log', level=logging.INFO)

    world = create_world()
    world = randomize_world(world, logger)
