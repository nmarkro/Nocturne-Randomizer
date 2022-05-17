import copy
import random
import logging

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
    world.add_magatama('Muspell', [], 15) #Muspell is not good enough for ailment based bosses
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
    world.add_flag("Ongyo-Key", 0x3F7)

    mifunashiro = world.add_area('Mifunashiro')
    world.add_terminal(mifunashiro, 0x6E1)
    world.add_check("Futomimi", mifunashiro, 2843628)
    world.add_check("Archangels", mifunashiro, 2843590)

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
BANNED_BOSSES = ["Lucifer"]

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
        # logger.info("Placing " + boss.name + " at check: " + chosen_check.name)

# returns a reward that unlocks new checks
# assumes with the current state there are no completeable checks
def find_progressive_reward(state, check_pool, reward_pool):
    for r in reward_pool:
        state.get_reward(r)
        completeable_checks = [c for c in check_pool if c.can_reach(state) and c.boss.can_beat(state) and c.name not in ["Kaiwan", "Berith", "Archangels"] and c.boss.name != "Kagutsuchi"] #Remove broken reward checks
        can_progress = bool(completeable_checks)
        if can_progress:
            return r
        else:
            state.remove_reward(r)
    return None

def randomize_world(world, logger, config_vanilla_tok, attempts=100):
    state = world.state
    area_pool = world.get_areas()
    flag_pool = world.get_flags()
    check_pool = world.get_checks()
    magatama_pool = world.get_magatamas()
    boss_pool = world.get_bosses()
    # Remove banned bosses from randomized pool
    vanilla = []
    for banned in BANNED_BOSSES:
        vanilla.append(banned)
    #If vanilla tower flag is set, add tok bosses to the ban list
    if config_vanilla_tok:
        vanilla.append("Ahriman")
        vanilla.append("Noah")
        vanilla.append("Thor 2")
        vanilla.append("Baal Avatar")
        vanilla.append("Kagutsuchi")
    for boss_name in vanilla:
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
    state.get_magatama('Marogareh')
    magatama_pool.remove(world.get_magatama('Marogareh'))
    # magatama_pool.remove(world.get_magatama('Gaea'))
    magatama_pool.remove(world.get_magatama('Masakados'))
    # remove the fixed flags and terminal flags
    flag_pool = [f for f in flag_pool if not f.is_terminal]
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

    # keep track of bosses beaten for placing magatamas
    bosses_progressed = []
    while world.get_check('Kagutsuchi') in check_pool:
        if attempts < 0:
            print('Error generating world, trying again')
            return None

        # keep beating bosses and unlocking terminals until stuck
        has_progressed = True
        while has_progressed:
            has_progressed = False
            for area in area_pool:
                # unlock terminals the player can reach
                if area.terminal_flag:
                    if area.can_reach(state) and not state.has_terminal(area.name):
                        state.get_terminal(area.name)
                        logger.info("Getting Terminal: " + area.terminal_flag.name)
                        has_progressed = True
            # beat bosses the player can reach and beat
            for check in check_pool:
                if check.can_reach(state) and check in check_pool:
                    if check.boss.can_beat(state):
                        state.check(check.name)
                        check_pool.remove(check)
                        logger.info("Beating " + check.boss.name + " at check: " + check.name)
                        if check.boss.reward:
                            state.get_reward(check.boss.reward)
                            logger.info("Getting reward: " + check.boss.reward.name)
                        for f in check.flag_rewards:
                            state.get_reward(f)
                            logger.info("Getting Flag: " + f.name)
                        has_progressed = True
                        bosses_progressed.append(check.boss)
        # check for game completion 
        if world.get_check('Kagutsuchi') not in check_pool:
            break
        logger.info("Can no longer progress\n")

        '''
        # didn't beat any bosses this passthrough, rerandomize unchecked bosses and try again
        if not bosses_progressed:
            logger.info("Re-randomizing unchecked bosses\n")
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
            continue'''
        
        # try to assign rewards that unlock progression 
        can_progress = False
        shuffled_bosses = copy.copy([b for b in bosses_progressed if b.check.area.name != 'ToK'])
        random.shuffle(shuffled_bosses)
        chosen_reward = find_progressive_reward(state, check_pool, reward_pool)
        if chosen_reward == None or not bosses_progressed:
            logger.info("Re-randomizing unchecked bosses\n")
            new_boss_pool = []
            for check in check_pool:
                if check.boss.name not in vanilla:
                    new_boss_pool.append(check.boss)
                    check.boss = None
            try:
                randomize_bosses(new_boss_pool, check_pool, logger)
            except:
                print('Error generating world, trying again')
                return None
            attempts -= 1
            continue

        chosen_boss = None
        # try to give the chosen reward to a boss with no magatama or flag reward 
        no_reward_boss_pool = [b for b in shuffled_bosses if b.reward == None and b.check.flag_rewards == [] and b.name != "Kagutsuchi" and b.check.name not in ["Kaiwan", "Berith", "Archangels"]]
        if no_reward_boss_pool != []:
            chosen_boss = random.choice(no_reward_boss_pool)
        else:
            for b in shuffled_bosses:
                if b.can_add_reward(chosen_reward) and b.name != "Kagutsuchi" and b.check.name not in ["Kaiwan", "Berith", "Archangels"]:
                    chosen_boss = b
                    break
            else:
                print('Error generating world, trying again')
                return None
        logger.info("Adding " + chosen_reward.name + " to boss " + chosen_boss.name + " at check " + chosen_boss.check.name + "\n")
        chosen_boss.add_reward(chosen_reward)
        reward_pool.remove(chosen_reward)

    logger.info("Placing unused rewards")
    # reverse to add rewards to bosses from the beginning of the game
    bosses_progressed.reverse()
    while reward_pool:
        reward = reward_pool.pop()
        chosen_boss = None
        # try to give the chosen reward to a boss with no magatama or flag reward 
        no_reward_boss_pool = [b for b in bosses_progressed if b.check.area.name != 'ToK' and b.reward == None and b.check.flag_rewards == [] and b.name != "Kagutsuchi" and b.check.name not in ["Kaiwan", "Berith", "Archangels"]]
        if no_reward_boss_pool != []:
            chosen_boss = no_reward_boss_pool.pop()
        else:
            for b in bosses_progressed:
                if b.check.area.name != 'ToK' and b.can_add_reward(reward) and b.name != "Kagutsuchi" and b.check.name not in ["Kaiwan", "Berith", "Archangels"]:
                    chosen_boss = b
                    break
            else:
                print('Error generating world, trying again')
                return None
        logger.info("Adding " + reward.name + " to boss " + chosen_boss.name + " at check " + chosen_boss.check.name)
        chosen_boss.add_reward(reward)

    logger.info("Complete spoiler:")
    for check in world.get_checks():
        boss = check.boss
        if boss.reward:
            logger.info("Boss " + boss.name + " is at check " + check.name + " with reward " + boss.reward.name)
        else:
            logger.info("Boss " + boss.name + " is at check " + check.name)
        for f in check.flag_rewards:
            logger.info("Check " + check.name + " gives " + f.name)
    return world

if __name__ == '__main__':
    logger = logging.getLogger('')
    with open('logs/spoiler.log', 'w') as f:
        f.write('')
    logging.basicConfig(filename='logs/spoiler.log', level=logging.INFO)

    world = None
    while world == None:
        world = create_world()
        world = randomize_world(world, logger)
