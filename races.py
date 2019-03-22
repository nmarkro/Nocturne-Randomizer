import random
import copy
import math

#Removed races are:
#Tyrant (Vile x Fury is the only combination with others removed)
#Evolution only (Wargod, Genma, Dragon, Avian and Entity)
#and unique fusion (Raptor and Seraph)
#   All unique fusions are removed

#Tyrant replacing fiends (Pale Rider, The Harlot and Trumpeter) needs another race to replace. 
#   Vile or Diety are good options to replace, so thematically Vile should probably be the replacement.
#Vile x Fury could be: 
#   Avatar (2nd lowest fusion count outside of Tyrant)
#   Diety (3rd lowest fusion count)
#   Femme (2nd lowest fusion count ratio at 2.222)
#   Foul or Fairy (tied for 3rd lowest fusion count ratio at 2.25)
#For reference, Tyrant has a ratio of 0.4
#The ratios are pretty evenly distributed from 2.22 to 6 except for Fury (8) and Lady (10.66)


raceref = ["X", "Deity", "Megami", "Fury", "Lady",\
           "Kishin", "Holy", "Yoma", "Fairy", "Divine",\
           "Fallen", "Snake", "Beast", "Jirae", "Brute",\
           "Femme", "Vile", "Night", "Wilder", "Haunt",\
           "Foul", "Avatar", "Fiend", "Erthys", "Aeros",\
           "Aquans", "Flaemis", "Element and Mitama", "Mitama"]
vanilla_race_fusion_results = [0, 12, 18, 24, 32,\
            28, 18, 16, 18, 16,\
            18, 16, 22, 16, 28,\
            20, 24, 40, 16, 22,\
            18, 8, 0, 0, 0,\
            0, 0, 0]
vanilla_race_ratio = [0, 2.4, 3.6, 8, 10.67,\
            3.11, 3.6, 2.29, 2.25, 2.29,\
            3, 3.2, 3.67, 2.67, 3.5, \
            2.22, 6, 5, 2.67, 3.14, \
            2.25, 2.67, 0, 0, 0,\
            0, 0, 0]
#Vile x Fury set to Avatar
fusion_result = [\
  [0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
    #Di,Me,Fu,La,Ki,Ho,Yo,Fa,Dv,Fl,Sn,Be,Ji,Br,Fe,Vi,Ni,Wi,Ha,Fo,Av,Fi
  [0,-1,0 ,0 ,0 ,3 ,2 ,2 ,18,2 ,3 ,5 ,21,14,5 ,4 ,0 ,16,0 ,0 ,0 ,2 ,0],\
  [0,0 ,-1,1 ,3 ,4 ,9 ,5 ,10,6 ,9 ,8 ,6 ,4 ,15,8 ,3 ,10,16,0, 0 ,1 ,0],\
  [0,0 ,1 ,-1,16,4 ,5 ,6 ,14,1 ,16,5 ,21,15,4 ,4 ,21,4 ,0 ,0 ,0 ,6 ,1],\
  [0,0 ,3 ,16,-1,3 ,21,17,7 ,2 ,3 ,15,11,12,3 ,5 ,0 ,5 ,19,16,16,3 ,0],\
  [0,3 ,4 ,4 ,3 ,-1,4 ,15,14,16,17,15,6 ,11,11,4 ,0 ,15,0 ,0 ,0 ,6 ,0],\
  [0,2 ,9 ,5 ,21,4 ,-1,9 ,2 ,8 ,12,5 ,21,12,15,4 ,0 ,8 ,0 ,0 ,0 ,2 ,0,],\
  [0,2 ,5 ,6 ,17,15,9 ,-1,6 ,11,13,17,10,12,15,14,13,9 ,12,13,11,9 ,17],\
  [0,17,10,14,7 ,14,2 ,6 ,-1,2 ,7 ,7 ,9 ,7 ,17,19,17,11,7 ,17,19,9 ,17],\
  [0,2 ,6 ,1 ,2 ,16,8 ,11,2 ,-1,16,8 ,6 ,17,7 ,12,10,11,10,13,8 ,2 ,16],\
  [0,3 ,9 ,16,3 ,17,12,13,7 ,16,-1,12,17,14,13,18,14,19,17,17,16,9 ,3],\
  [0,5 ,8 ,5 ,15,15,5 ,17,7 ,8 ,12,-1,14,10,12,5 ,5 ,10,17,14,10,4 ,14],\
  [0,21,6 ,21,11,6 ,21,10,9 ,6 ,17,14,-1,7 ,15,20,20,8 ,13,18,18,11,17],\
  [0,14,4 ,15,12,11,12,12,7 ,17,14,10,7 ,-1,8 ,18,19,20,14,16,15,5 ,18],\
  [0,5 ,15,4 ,3 ,11,15,15,17,7 ,13,12,15,8 ,-1,12,19,5 ,8 ,20,18,5 ,19],\
  [0,4 ,8 ,4 ,5 ,4 ,4 ,14,19,12,18,5 ,20,18,12,-1,14,13,10,20,18,5 ,4],\
  [0,0 ,3 ,16,0 ,0 ,0 ,13,17,10,14,5 ,20,19,19,14,-1,4 ,20,20,19,1 ,3],\
  [0,16,10,4 ,5 ,15,8 ,9 ,11,11,19,10,8 ,20,5 ,13,4 ,-1,12,7 ,14,6 ,4],\
  [0,0 ,16,0 ,19,0 ,0 ,12,7 ,10,17,17,13,14,8 ,10,20,12,-1,13,12,0 ,17],\
  [0,0 ,0 ,0 ,16,0 ,0 ,13,17,13,17,14,18,16,20,20,20,7 ,13,-1,14,0 ,20],\
  [0,0 ,0 ,0 ,16,0 ,0 ,11,19,8 ,16,10,18,15,18,18,19,14,12,14,-1,0 ,19],\
  [0,2 ,1 ,6 ,3 ,6 ,2 ,9 ,9 ,2 ,9 ,4 ,11,5 ,5 ,5 ,1 ,6 ,0 ,0 ,0 ,-1,0],\
  [0,0 ,0 ,1 ,0 ,0 ,0 ,17,17,16,3 ,14,17,18,19,4 ,3 ,4 ,17,20,19,0 ,-1]]  

demon_names = ["Will o' Wisp", "Pixie", "Kodama","Preta","Shikigami","Hua Po","Slime","Zhen","Datsue-Ba","Erthys","Jack Frost","Mou-Ryo","Apsaras","Lilim","High Pixie","Aeros","Angel","Choronzon","Inugami","Shiisaa","Sudama","Isora","Nozuchi","Aquans","Bicorn","Blob","Minakata","Yaka","Archangel","Fomor","Nekomata","Uzume","Koppa","Pyro Jack","Chatterskull","Flaemis","Forneus","Momunofu","Taraka","Unicorn","Makami","Badb Catha","Dis","Gui Xian","Kikuri-Hime","Ara Mitama","Incubus","Oni","Raiju","Cai-Zhi","Kelpie","Senri","Zouchou","Black Ooze","Karasu","Naga","Pisaca","Principality","Eligor","Nigi Mitama","Arahabaki","Matador","Sarasvati","Nue","Kusi Mitama","Shikome","Baphomet","Koumoku","Power","Valkyrie","Mizuchi","Orthrus","Saki Mitama","Sarutahiko","Feng Huang","Berith","Daisoujou","Onkot","Raja Naga","Succubus","Horus","Kurama","Troll","Okuninushi","Kushinada","Virtue","Hell Biker","Phantom","Baihu","Mothman","Setanta","Yaksini","Dionysus","Ikusa","Jinn","Long","Mikazuchi","Ose","Pazuzu","Sakahagi","Hanuman","Oberon","Yatagarasu","Atavaka","Kaiwan","Purski","Sati","Legion","Titan","Dominion","Cu Chulainn","Dakini","Efreet","Jikoku","Loki","Shadow","White Rider","Loa","Laksmi","Shiki-Ouji","Sparna","Wu Kong","Chimera","Gogmagog","Quetzacoatl","Red Rider","Amaterasu","Queen Mab","Parvati","Titania","Clotho","Decarabia","Ganesha","Girimehkala","Kin-Ki","Barong","Beiji-Weng","Black Rider","Cerberus","Sui-Ki","Futomimi","Garuda","Gurr","Lachesis","Pale Rider","Rakshasa","Albion","Scathach","Throne","Odin","Tao Tie","Black Frost","Fuu-Ki","Yurlungur","Atropos","Kali","Flauros","Abaddon","The Harlot","Nyx","Bishamon","Rangda","Samael","Uriel","Skadi","Surt","Hresvelgr","Thor","Aciel","Trumpeter","Mithra","Dante","Lilith","Ongyo-Ki","Mada","Beelzebub","Raphael","Gabriel","Michael","Mot","Vishnu","Beelzebub (Fly)","Metatron","Shiva"]

demon_levels = [1,2,3,4,4,5,6,6,7,7,7,7,8,8,10,11,11,11,13,13,13,14,14,15,15,16,17,17,18,18,18,18,19,19,20,20,20,20,20,21,22,23,23,24,24,25,25,25,25,26,26,27,27,28,28,28,28,28,29,29,30,30,30,31,32,32,33,33,33,33,34,34,35,35,36,37,37,37,37,37,38,38,38,39,41,41,42,42,43,43,43,43,44,44,44,44,45,45,45,45,46,46,46,47,47,48,48,49,49,50,52,52,52,52,52,52,52,53,54,54,54,54,55,55,55,55,56,56,57,57,58,58,58,58,59,60,61,61,61,62,63,63,63,63,63,63,64,64,64,65,65,66,66,66,67,67,68,69,69,70,72,72,73,73,74,74,75,76,77,77,78,80,80,81,83,84,84,87,90,91,93,95,95,95]

demon_count = 184
element_mitama_count = 8
fiend_count = 10
level_min = 1
level_max = 95
race_min = 1
race_max = 21
race_fiend = 22
race_erthys = 23
race_aeros = 24
race_aquans = 25
race_flaemis = 26
race_element_mitama = 27
race_mitama = 28
vanilla_evolution_only_count = 23
element_mitama_level_max = 40
minimum_level_diff = 4
#level range for creating a new demon from existing demons
logical_lowfuse_min = 3
logical_lowfuse_max = 8

def avg_fuse(d1,d2):
    return math.ceil((d1+d2)/2.0)

class all_demons:
    def __init__(self, levels, names):
        self.spare_levels = copy.deepcopy(levels)
        self.spare_names = copy.deepcopy(names)
        self.demons = []
        self.initial_ten_demons = []
        self.elemental_results = [-1, 0, 0, 0, 0,\
           0, 0, 0, 0, 0,\
           0, 0, 0, 0, 0,\
           0, 0, 0, 0, 0,\
           0, 0, -1, -1, -1,\
           -1, -1, -1]
        self.elemental_result_count = 21
        self.elemental_result_count_each = 4 #4 races provide 
        self.unused_results = len(self.elemental_results) - self.elemental_result_count #6
        self.generation_error = False
    def print_elemental_results(self):
        for i in range(len(self.elemental_results)):
            if self.elemental_results[i] == race_erthys:
                print(raceref[i],"makes Erthys")
            elif self.elemental_results[i] == race_aeros:
                print(raceref[i],"makes Aeros")
            elif self.elemental_results[i] == race_aquans:
                print(raceref[i],"makes Aquans")
            elif self.elemental_results[i] == race_flaemis:
                print(raceref[i],"makes Flaemis")
            elif self.elemental_results[i] == 0:
                print(raceref[i],"does not turn into an element")
    def grab_name(self):
        if len(self.spare_names) == 1:
            r=0
        elif len(self.spare_names) == 0:
            print("Warning in grab_name() - Need name and there's no name left.")
            return "UNKNOWN NAME"
        else:
            r = random.randint(0,len(self.spare_names)-1)
        name = self.spare_names[r]
        del self.spare_names[r]
        return name
    def grab_spare_level(self,low_level=0,high_level=99,get_next_past_cap=False):
        viable = list(filter(lambda x: x > low_level and x < high_level, self.spare_levels))
        if not viable:
            if get_next_past_cap:
                for i in self.spare_levels:
                    if i > low_level:
                        self.spare_levels.remove(i)
                        return i
            return 0
        if len(viable) == 1:
            self.spare_levels.remove(viable[0])
            return viable[0]
        r = random.randint(0,len(viable)-1)
        self.spare_levels.remove(viable[r])
        return viable[r]
    def add_demon(self,demon1):
        self.demons.append(demon1)
    def find_lower_of_race(self,demon1):
        return self.find_highest_race_level(demon1.race,demon1.level)
        '''level=0
        for d in self.demons:
            if d.race == demon1.race and d.level < demon1.level and level < d.level:
                level = d.level
        return level'''
    def find_highest_race_level(self,race,lvl):
        level=0
        for d in self.demons:
            if d.race == race and level < d.level and d.level < lvl:
                level = d.level
        return level
    def all_reverse_races(self,demon1):
        reverse_races = []
        for i in range(race_max+1):
            for j in range(race_max+1):
                if fusion_result[i][j] == demon1.race:
                    reverse_races.append((i,j))
        return reverse_races
    def low_reverse_fuse(self,demon1,half_flag=False):
        reverse_races = self.all_reverse_races(demon1)
        lower_race_level = self.find_lower_of_race(demon1)
        for rr in reverse_races:
            r1 = 0
            r2 = 0
            for d in self.demons:
                if d.level < demon1.level:
                    if d.race == rr[0]:
                        if half_flag and lower_race_level <= d.level: #possibly avg_fuse(lower_race_level,d.level-1) <= d.level
                            return rr[0]
                        if d.level > r1:
                            r1 = d.level
                        if r2 > 0:
                            if avg_fuse(r1,r2) >= lower_race_level:
                                return rr[0]
                    if d.race == rr[1]:
                        if half_flag and lower_race_level <= d.level:
                            return rr[1]
                        if d.level > r2:
                            r2 = d.level
                        if r1 > 0:
                            if avg_fuse(r1,r2) >= lower_race_level:
                                return rr[1]
        return 0

    #randomizes the races that produce the elementals
    #sets it self.elemental_results
    #returns an array of 4 that has a random race that turns into the respective element in order of: Erthys, Aeros, Aquans and Flaemis
    def randomize_elemental_results(self):
        erce = self.elemental_result_count_each
        e = [race_erthys]*erce + [race_aquans]*erce + [race_aeros]*erce + [race_flaemis]*erce + [0] * (self.elemental_result_count - (erce*4))
        random.shuffle(e)
        self.elemental_results = [-1] + e + [-1]*5
        #return 4 races of each element
        ret = [0,0,0,0]
        r = random.randint(1,len(e))
        while self.elemental_results[r] != race_erthys:
            r = random.randint(1,len(e))
        ret[0] = r
        while self.elemental_results[r] != race_aeros:
            r = random.randint(1,len(e))
        ret[1] = r
        while self.elemental_results[r] != race_aquans:
            r = random.randint(1,len(e))
        ret[2] = r
        while self.elemental_results[r] != race_flaemis:
            r = random.randint(1,len(e))
        ret[3] = r
        return ret
        
    #set aside 8 for elements/mitama, reserve 4 pairs below for elemental fusions
    #16 demons below the threshold. 13th-16th are mitamas. 12th is elemental, 9th-11th is next, 6th-8th is next, 3rd-5th is next. Other two not picked must go to the previous elemental.
    #returns 8 demons used in logic to fuse the elementals
    def randomize_elementals_mitamas(self, elemental_races):
        used_levels = []
        current_element_mitama_max = element_mitama_level_max
        rand_divider = random.randint(40,48) #magic numberz
        max_iterations = 1000
        #this snippet is ugly but it was needed to get a good looking spread
        for i in range(4):
            if len(self.spare_levels) < 0:
                print("Error: Not enough spare levels to use in randomize_elementals_mitamas()")
                self.generation_error=True
                return 0
            r = random.randint(rand_divider,len(self.spare_levels)-1)
            while self.spare_levels[r] > current_element_mitama_max or self.spare_levels[r] in used_levels:
                r = random.randint(rand_divider,len(self.spare_levels)-1)
                max_iterations-=1
                if max_iterations == 0:
                    print("Locked up :(. Please try again.")
                    return 0
            used_levels.append(self.spare_levels[r])
            del self.spare_levels[r]
            current_element_mitama_max -= minimum_level_diff
        current_element_mitama_max = self.spare_levels[rand_divider]
        for i in range(4):
            r = random.randint(0,rand_divider)
            while self.spare_levels[r] > current_element_mitama_max or self.spare_levels[r] in used_levels:
                r = random.randint(0,rand_divider)
                max_iterations-=1
                if max_iterations == 0:
                    print("Locked up :(. Please try again.")
                    return 0
            used_levels.append(self.spare_levels[r])
            del self.spare_levels[r]
            current_element_mitama_max -= 2
        for i in range(8):
            r = random.randint(0,rand_divider)
            while self.spare_levels[r] > current_element_mitama_max or self.spare_levels[r] in used_levels:
                r = random.randint(0,rand_divider)
                max_iterations-=1
                if max_iterations == 0:
                    print("Locked up :(. Please try again.")
                    return 0
            used_levels.append(self.spare_levels[r])
            del self.spare_levels[r]
            
            
        used_levels.sort()
        order = [0,1,2,3]
        random.shuffle(order)
        self.add_demon(demon(used_levels[12+order[0]],"Ara Mitama", race_mitama))
        self.add_demon(demon(used_levels[12+order[1]],"Nigi Mitama", race_mitama))
        self.add_demon(demon(used_levels[12+order[2]],"Kusi Mitama", race_mitama))
        self.add_demon(demon(used_levels[12+order[3]],"Saki Mitama", race_mitama))
        del used_levels[12:16]
        self.spare_names.remove("Ara Mitama")
        self.spare_names.remove("Nigi Mitama")
        self.spare_names.remove("Kusi Mitama")
        self.spare_names.remove("Saki Mitama")
        random.shuffle(order)
        random_demons = []
        self.spare_names.remove("Erthys")
        self.spare_names.remove("Aeros")
        self.spare_names.remove("Aquans")
        self.spare_names.remove("Flaemis")
        for i in order:
            if i == 0:
                self.add_demon(demon(used_levels[-1], "Erthys", race_erthys))
            elif i == 1:
                self.add_demon(demon(used_levels[-1], "Aeros", race_aeros))
            elif i == 2:
                self.add_demon(demon(used_levels[-1], "Aquans", race_aquans))
            elif i == 3:
                self.add_demon(demon(used_levels[-1], "Flaemis", race_flaemis))
            del used_levels[-1]
            #TODO - make sure these two are 3+ levels apart
            for j in range(2):
                if (len(used_levels) == 0):
                    print("Error: Not enough levels given in randomize_elementals_mitamas()")
                    self.generation_error = True
                    return 0
                r = random.randint(0,len(used_levels)-1)
                d = demon(used_levels[r], self.grab_name(), elemental_races[i])
                self.add_demon(d)
                random_demons.append(d)
                del used_levels[r]
        if not len(used_levels) == 0:
            print(used_levels)
            print("Warning: Unused levels in randomize_elementals_mitamas()")
        return random_demons
    def find_base_ten_demons(self, supplied_demons):
        initial_ten = copy.deepcopy(self.spare_levels[:10])
        #print("Initial initial ten",initial_ten)
        #if any of the supplied demons are below any of the initial_ten, then put it in the initial_ten
        #each of the supplied demons above the initial ten need to be fusable from the initial_ten. It could be multiple steps but it might just be easiest to do one step
        sd_levels=[]
        for s in supplied_demons:
            sd_levels.append(s.level)
        comb_levels = copy.deepcopy(initial_ten) + sd_levels
        comb_levels.sort()
        in_ten = []
        i=0
        while i < len(initial_ten):
            if initial_ten[i] != comb_levels[i + len(in_ten)]:
                in_ten.append(comb_levels[i+len(in_ten)])
            else:
                i+=1
        initial_ten = initial_ten[:10-len(in_ten)]
        #print("Adjusted Initial ten",initial_ten)
        
        for s in supplied_demons:
            in_ten_flag = False
            for t in in_ten:
                if s.level == t:
                    in_ten_flag = True
                    self.initial_ten_demons.append(s)
            if not in_ten_flag:
                if self.low_reverse_fuse(s)==0:
                    lr = self.find_lower_of_race(s)
                    rr = self.all_reverse_races(s)
                    half_found_race = self.low_reverse_fuse(s,half_flag=True)
                    if half_found_race > 0: #one half was found, but not the other
                        #l = self.find_highest_race_level(result_race,s.level) #find the level of that half
                        other_races = []
                        for r in rr:
                            if r[0]==half_found_race:
                                other_races.append(r[1])
                            elif r[1]==half_found_race:
                                other_races.append(r[0])
                        if len(other_races) >= 2:
                            chosen_race = other_races[random.randint(0,len(other_races)-1)]
                        elif len(other_races) == 1:
                            chosen_race = other_races[0]
                        else:
                            print("Error: find_base_ten_demons() I thought I found a fusion but I was wrong :(. Please redo")
                            print("lr ",lr," hfr ",half_found_race," s.race ",s.race, " or ",other_races)
                            print("rr ",rr)
                            self.generation_error = True
                            
                        least = -1
                        for ind in range(len(initial_ten)):
                            if lr < initial_ten[ind] and least == -1:
                                least = ind
                        if least > -1: #if there's a viable one with the initial_ten
                            nd = demon(initial_ten[least],self.grab_name(),chosen_race)
                            self.add_demon(nd)
                            self.spare_levels.remove(initial_ten[least])
                            del initial_ten[least]
                            self.initial_ten_demons.append(nd)
                            
                        else: #
                            #find a level between lower of race and current demon's level in spare_levels
                            viable = list(filter(lambda x: x > lr and x < s.level and x > initial_ten[-1], self.spare_levels))
                            if not viable:
                                print("Error: find_base_ten_demons() could not find a fusion for LVL", s.level, raceref[s.race], s.name)
                                self.generation_error = True
                            else:
                                ri = viable[random.randint(0,len(viable)-1)]
                                self.add_demon(demon(ri,self.grab_name(), chosen_race))
                                self.spare_levels.remove(ri)
                                
                    else:
                        viable = list(filter(lambda x: x > lr and x <s.level and x > initial_ten[-1], self.spare_levels))
                        
                        if len(viable) < 2:
                            print("Error: find_base_ten_demons() could not find a fusion for LVL", s.level, raceref[s.race], s.name)
                            self.generation_error = True
                        else:
                            random.shuffle(viable)
                            if len(rr) > 1:
                                chosen_race_pair = rr[random.randint(0,len(rr)-1)]
                            else:
                                chosen_race_pair = rr[0]
                            self.add_demon(demon(viable[0], self.grab_name(), chosen_race_pair[0]))
                            self.add_demon(demon(viable[1], self.grab_name(), chosen_race_pair[1]))
                            self.spare_levels.remove(viable[0])
                            self.spare_levels.remove(viable[1])
        initial_ten_races = []
        for dit in self.initial_ten_demons:
            if dit.race not in initial_ten_races:
                initial_ten_races.append(dit.race)
            #print("Initial ten demon:",dit.level,raceref[dit.race],dit.name)
        for it in initial_ten: #any remaining initial_ten
            rand_r = random.randint(race_min,race_max)
            while rand_r in initial_ten_races:
                rand_r = random.randint(race_min,race_max)
            initial_ten_races.append(rand_r)
            nd = demon(it,self.grab_name(),rand_r)
            self.add_demon(nd)
            self.spare_levels.remove(it)
            self.initial_ten_demons.append(nd)
            #print("Initial ten demon (rand):",it,raceref[rand_r],nd.name)
        #print("Initial ten races",initial_ten_races)
        #Look at all of the base 10 and fuse them together. If there isn't a result then make a demon of the lowest level allowed. Hopefully that should fill in enough low level slots for fill_demon_slots() to finish it off.
        for i in range(len(self.initial_ten_demons)-1):
            for j in range(i+1,len(self.initial_ten_demons)):
                if fusion_result[self.initial_ten_demons[i].race][self.initial_ten_demons[j].race] > 0 and not self.fuse_demon(self.initial_ten_demons[i],self.initial_ten_demons[j],allow_underfuse=True):
                    self.add_demon(demon(self.spare_levels[0],self.grab_name(),fusion_result[self.initial_ten_demons[i].race][self.initial_ten_demons[j].race]))
                    del self.spare_levels[0]
    #Takes "spare_levels" and fills in each of the demons in randomly.
    #It prioritizes fusion results of demons that already exist
    #It does not take elementals into account as that's a previous step
    def fill_demon_slots(self):
        existing_fusion_combos = []
        #put together all pairs that should be fused
        for d1 in self.demons:
            for d2 in self.demons:
                #Not the same race, not elemental. Fiend ok. Must produce result.
                if d1.race >= race_min and d1.race <= race_fiend and d2.race >= race_min and d2.race <= race_fiend and d1.race != d2.race and fusion_result[d1.race][d2.race] > 0:
                    existing_fusion_combos.append((d1,d2))
        #hopefully existing_fusion_combos will never be empty and it'll be spare_levels to be empty
        #remaining_fiends = fiend_count
        fiend_levels = random.sample(self.spare_levels,fiend_count)
        for fl in fiend_levels:
            self.spare_levels.remove(fl)
        unfusable_levels = []
        
        while existing_fusion_combos and self.spare_levels: #while both lists are not empty
            
            random_pair_index = random.randint(0,min(len(existing_fusion_combos)-1,5))
            d1 = existing_fusion_combos[random_pair_index][0]
            d2 = existing_fusion_combos[random_pair_index][1]
            del existing_fusion_combos[random_pair_index]
            result_d = self.fuse_demon(d1,d2,allow_underfuse=True)
            new_d_level = 0
            new_d_race = fusion_result[d1.race][d2.race]
            if result_d is None:
                #Make a new demon without worrying about a min level of that race
                min_lvl = max(d1.level,d2.level)
                new_d_level = self.grab_spare_level(min_lvl + logical_lowfuse_min, min_lvl + logical_lowfuse_max,get_next_past_cap=True)
                '''
                if not new_d_level: #if there was no level to grab in that range, ignore max cap
                    print("Minor warning: Maxcap ignored in fill_demon_slots(). At 20+ish times in one seed logic should be tweaked.")
                    new_d_level = self.grab_spare_level(min_lvl + logical_lowfuse_min)
                if not new_d_level:
                    #This should almost always never happen. If it does it's probably bad.
                    print("Warning: in fill_demon_slots() - Tried to make a new demon of race",raceref[new_d_race],"but there were no levels left and there are also no demons of that race. This should only be super rare. If you see this outside of one in a million, then fusion logic either needs to be tweaked or it's bugged.")
                else:
                '''
                if new_d_level:
                    new_d = demon(new_d_level,self.grab_name(),new_d_race)
                    self.add_demon(new_d)
                    #add the new demon in fusion combos to keep the generation going
                    for nd in self.demons:
                        if nd.race >= race_min and nd.race <= race_fiend and new_d.race >= race_min and new_d.race <= race_fiend and nd.race != new_d.race and fusion_result[nd.race][new_d.race] > 0:
                            existing_fusion_combos.append((nd,new_d))
                
            elif result_d.level < avg_fuse(d1.level,d2.level):
                #Make a new demon that's at least level result_d + minimum_level_diff
                min_lvl = max(result_d.level, d1.level, d2.level)
                new_d_level = self.grab_spare_level(min_lvl + logical_lowfuse_min, min_lvl + logical_lowfuse_max, get_next_past_cap=True)
                '''if not new_d_level: #ignore max cap if one in the range wasn't found
                    print("Minor warning: Maxcap ignored in fill_demon_slots()")
                    new_d_level = self.grab_spare_level(min_lvl + logical_lowfuse_min)
                if not new_d_level:
                    print("Minor warning: In fill_demon_slots() - Tried to make a new demon of race",raceref[new_d_race],"but there were no levels left of ",len(self.spare_levels),". If number left is high then logic tweaking might be necessary.")
                else:
                '''
                if new_d_level:
                    new_d = demon(new_d_level,self.grab_name(),new_d_race)
                    self.add_demon(new_d)
                    #add the new demon in fusion combos to keep the generation going
                    for nd in self.demons:
                        if nd.race >= race_min and nd.race <= race_fiend and new_d.race >= race_min and new_d.race <= race_fiend and nd.race != new_d.race and fusion_result[nd.race][new_d.race] > 0:
                            existing_fusion_combos.append((nd,new_d))
                    
            #else don't make a new demon. There's already a minfuse of the demon pair.
            #Before we loop again, make another demon if the lowest level in spare_levels is less than this demon pair.
            #This is so levels don't get stranded behind
            if self.spare_levels and self.spare_levels[0] < new_d_level:
                d1s = []
                done = False
                for nd in self.demons:
                    if nd.level < self.spare_levels[0] and nd.race < race_erthys:
                        d1s.append(nd)
                random.shuffle(d1s)
                for i in range(len(d1s)-1):
                    for j in range(i+1,len(d1s)):
                        if not done and fusion_result[d1s[i].race][d1s[j].race] > 0 and not self.fuse_demon(d1s[i],d1s[j],allow_underfuse=False):
                            self.add_demon(demon(self.spare_levels[0],self.grab_name(),fusion_result[d1s[i].race][d1s[j].race]))
                            #print("Straggled level",self.spare_levels[0],"- Using",d1s[i].level,raceref[d1s[i].race],"x",d1s[j].level,raceref[d1s[j].race],"- result race:",raceref[fusion_result[d1s[i].race][d1s[j].race]])
                            done = True
                            del self.spare_levels[0]
                
                #if not done and remaining_fiends > 0 and self.spare_levels[0] not in fiend_levels:
                    #use the bad slot for a fiend
                    #fiend_levels.append(self.spare_levels[0])
                    #del self.spare_levels[0]
                if not done:
                    print("Error in fill_demon_slots(). Could not find any demon that could be made at level",self.spare_levels[0])
                    self.generation_error=True
                    unfusable_levels.append(self.spare_levels[0])
                    del self.spare_levels[0]
        #if existing_fusion_combos isn't empty that's fine and even preferred
        for fl in fiend_levels:
            self.add_demon(demon(fl,self.grab_name(),race_fiend))
        if self.spare_levels:
            print("Warning in fill_demon_slots() - Couldn't generate all demons. Levels remaining:",self.spare_levels)
        #print("Unfusable levels:",unfusable_levels)
        #print("Fiend levels:",fiend_levels)
    #allow_underfuse = True: If the race result is there, but the highest level of that race is below the level of the fusion result, then return the highest level. allow_underfuse = False: instead of returning highest level, return an empty result.
    #empty result is always None
    #does not do Elemental Fusions, but that's a separate part of logic anyway
    def fuse_demon(self,demon1,demon2,allow_underfuse=False):
        fuse_race = fusion_result[demon1.race][demon2.race]
        if fuse_race <= 0:
            return None
        fused_lvl = avg_fuse(demon1.level, demon2.level)
        highest_lvl_of_race = 0
        highest_lvl_below_fuse = 0
        ret_demon = None
        high_demon = None
        for d in self.demons:
            if d.race == fuse_race:
                if d.level > highest_lvl_of_race:
                    highest_lvl_of_race = d.level
                    high_demon = d
                if d.level > fused_lvl and d.level > highest_lvl_below_fuse:
                    highest_lvl_below_fuse = d.level
                    ret_demon = d
        if allow_underfuse and ret_demon is None and high_demon is not None:
            return high_demon
        return ret_demon
    def generate(self, generation_attempts=100):
        if generation_attempts == 0:
            print("Failed to generate fusion logic.")
            return -1
        backup_names = copy.deepcopy(self.spare_names)
        backup_levels = copy.deepcopy(self.spare_levels)
        ret1 = self.randomize_elemental_results()
        ret2 = self.randomize_elementals_mitamas(ret1)
        if ret2 == 0
            print("Error(s) in generation. Regenerating...")
            self.__init__(backup_levels,backup_names)
            return self.generate(generation_attempts-1)
        self.find_base_ten_demons(ret2)
        self.fill_demon_slots()
        if self.generation_error:
            print("Error(s) in generation. Regenerating...")
            self.__init__(backup_levels,backup_names)
            return self.generate(generation_attempts-1)
        return 0
    
class demon:
    def __init__(self, level, name, race):
        self.level = level
        self.name = name
        self.race = race
    def str(self):
        return "LVL",self.level,raceref[self.race],self.name
        
#old code
'''
def fuse_demon(self,demon1,demon2):
    #TODO
    possible_list = []
    
    lowest_pair = 100
    if pair1 == pair2:
        return (-2,pair1[1])
    if pair1[1] > race_max:
        return (-3,pair1[1])
    if pair2[1] > race_max:
        return (-3,pair2[1])
    result_race = fusion_result[pair1[1]][pair2[1]]
    if result_race < race_min or result_race > race_max:
        return (-1,result_race)
    avg_level = math.ceil(pair1[0] + pair2[0] / 2.0)
    for p in pairs:
        if p[1] == result_race:
            if lowest_pair == 100:
                lowest_pair = p[0]
            elif lowest_pair < p[0] and p[0] > avg_level:
                lowest_pair = p[0]
    if lowest_pair == 100:
        return (0,0)
    return (lowest_pair, result_race)
        
def pair_special_races(level,names):
    pairs = []
    spare_levels = copy.deepcopy(levels)
    spare_names = copy.deepcopy(names)
    
    for i in range(element_mitama_count):
        r = random.randint(0,len(spare_levels)-1)
        while spare_levels[r] > element_mitama_level_threshold:
            r = random.randint(0,len(spare_levels)-1)
        pairs.append((spare_levels[r], race_element_mitama, spare_names[r]))
        del spare_levels[r]
        del spare_names[r]
    for i in range(fiend_count):
        r = random.randint(0,len(spare_levels)-1)
        pairs.append((spare_levels[r], race_fiend, spare_names[r]))
        del spare_levels[r]
        del spare_names[r]
    l = len(spare_levels)
    return (pairs, spare_levels, spare_names)
    
def pair_races(levels, names):
    pairs = []
    spare_levels = copy.deepcopy(levels)
    spare_names = copy.deepcopy(names)
    
    for i in range(element_mitama_count):
        r = random.randint(0,len(spare_levels)-1)
        while spare_levels[r] > element_mitama_level_threshold:
            r = random.randint(0,len(spare_levels)-1)
        pairs.append((spare_levels[r], race_element_mitama, spare_names[r]))
        del spare_levels[r]
        del spare_names[r]
    for i in range(fiend_count):
        r = random.randint(0,len(spare_levels)-1)
        pairs.append((spare_levels[r], race_fiend, spare_names[r]))
        del spare_levels[r]
        del spare_names[r]
    l = len(spare_levels)
    for i in range(l):
        r = random.randint(0,len(spare_levels)-1)
        rrace = random.randint(race_min,race_max)
        pairs.append((spare_levels[r], rrace, spare_names[r]))
        del spare_levels[r]
        del spare_names[r]
    return pairs

def fuse(pair1, pair2, pairs):
    lowest_pair = 100
    if pair1 == pair2:
        return (-2,pair1[1])
    if pair1[1] > race_max:
        return (-3,pair1[1])
    if pair2[1] > race_max:
        return (-3,pair2[1])
    result_race = fusion_result[pair1[1]][pair2[1]]
    if result_race < race_min or result_race > race_max:
        return (-1,result_race)
    avg_level = math.ceil(pair1[0] + pair2[0] / 2.0)
    for p in pairs:
        if p[1] == result_race:
            if lowest_pair == 100:
                lowest_pair = p[0]
            elif lowest_pair < p[0] and p[0] > avg_level:
                lowest_pair = p[0]
    if lowest_pair == 100:
        return (0,0)
    return (lowest_pair, result_race)
    
def fuse_all(pairs):
    counts = {}
    for p in pairs:
        counts[(p[0], p[1])] = [0,p[2],raceref[p[1]]]
    for p1 in pairs:
        for p2 in pairs:
            result = fuse(p1,p2,pairs)
            if result[0] > 0:
                counts[result][0] = counts[result][0] + 1
    return counts
'''
# random.seed()

# a = all_demons(demon_levels, demon_names)
# a.generate()
# for d in a.demons:
#     print(d.str())
# a.print_elemental_results()
# print("Spare levels: ", a.spare_levels)

#randomize the races that produces elementals. - Done randomize_elemental_results()

#set aside 8 for elements/mitama, reserve 4 pairs below for elemental fusions
    #16 demons below the threshold. 13th-16th are mitamas. 12th is elemental, 9th-11th is next, 6th-8th is next, 3rd-5th is next. Other two not picked must go to the previous elemental.
#randomize the races that fuse each of the elementals. 4 for each elemental and a 5th for none.
    #force one pair of demons of the same race of each elemental to be below the elemental. Note if any of these are within the first 10 minus elementals or if they're after.
    #If they're after, reverse fuse each one and the intermediates until bottom 10.
#Fill in the rest of bottom 10 with random demons
#Take a current highest level of each race. When two demons are fused and current highest level is less than the fusion result, add 2-5 levels to the fusion result to get the new demon and add it to the pool.
#Repeat this process until all levels are accounted for. This may not work, but we can try it.
#def randomize_fusions(levels, names):
    

#print(fuse_all(pair_races(demon_levels,demon_names)))
