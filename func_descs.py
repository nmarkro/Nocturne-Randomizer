class param:
    def __init__(self, type, name = "unknown", desc = ""):
        self.type = type
        self.name = name
        self.desc = desc
    def short_str(self):
        return self.type + " " + self.name
    def getDesc(self):
        return self.desc
        
class func:
    def __init__(self, index, fun_name, ret_type = "void", desc = "", params = [], long_desc = ""):
        self.index = index
        self.name = fun_name
        self.ret_type = ret_type
        self.desc = desc
        self.params = params
        self.long_desc = long_desc
    def lineDesc(self):
        s = "COMM " + hex(self.index) + ": " + self.ret_type + " " + self.name + "( "
        for p in self.params:
            s+=p.short_str()+","
        s = s[:-1]#cut off the extra comma
        s+= " )"
        if self.desc != "":
            s+= " - " + self.desc
        return s
    def paragraphDesc(self):
        s = self.lineDesc() + "\n" + self.long_desc
        if self.params!=[]:
            s+="\nParams:\n"
        for p in self.params:
            if p.desc!="":
                s+=p.short_str() + " - " + p.getDesc() + "\n"
        return s

COMM_FUNS = {}

def lineDesc(givenint):
    if givenint in COMM_FUNS:
        return COMM_FUNS[givenint].lineDesc()
    else:
        return ""
def paraDesc(givenint):
    if givenint in COMM_FUNS:
        return COMM_FUNS[givenint].paragraphDesc()
    else:
        return "Nothing known about COMM "+hex(givenint)

#Params
messageIdParam = param("int","messageId","Index of message in the current message script")
flagParam = param("int","flagId","Flag corresponding to given ID")
battleIdParam = param("int","battleId","Battle of given ID")
eventIdParam = param("int","eventId","Event script of given ID")
locationIdParam = param("int","locId","ID of a location")
fieldIdParam = param("int","fieldId","ID of a field. (e.g. 35 is Mifunashiro)")
#procedureIdParam = param("int","procId","Procedure index in the current script")
endstoneParam = param("int","stoneId","ID of Netherstone, Earthstone or Heavenstone")
demonIdParam = param("int","demonId","Demon of given ID")
posParam = param("int","variableId","The return value from comm 0x94 (LOAD_POS_ASSET)")

u_int_param = param("int")
u_str_param = param("string",desc="Actual value is an index that refers to a string in the current script file. Uses a PUSHSTR command instead of a PUSHIS command.")
skill_param = param("BattleSkill","skill")
unit_param = param("BattleUnit")
support_skill_param = param("int","supportSkillId")
itemIdParam = param("int","itemId")
u_flt_param = param("float")


#Functions
comm0 = func(0,"MSG",desc="Displays message of index of messageId.",params=[messageIdParam])
comm1 = func(1,"MSG_WND_DSP",desc="Displays message window",long_desc="\tThe message window display is shown for nearly every message.\n\tOne example where the message window does not appear is during the death cutscene.")
comm2 = func(2,"MSG_WND_CLS",desc="Closes message window")
comm3 = func(3,"MSG_DEC",desc="Displays decision message of index of messageID.",params=[messageIdParam])
unused_desc = "This is an unused function. If you see this in used code then that's probably a problem."
comm4 = func(4,"UNUSED_4",desc=unused_desc)
comm5 = func(5,"UNUSED_5",desc=unused_desc)
comm6 = func(6,"REMOVE_END_STONE",desc="Removes one of the 3 endgame stones.",params=[endstoneParam])
flag_long_desc = "\tThe flags are used for keeping track of triggers.\n\tThey can be important for story progression, for very minor things like short one-time message displays, or even used for the fusability of story demons like the fiends."
comm7 = func(7,"BIT_CHK","bool","Returns flag of the given index", [flagParam], long_desc=flag_long_desc +"\n\tIt's more common to check if the bit is on. The way it's checked if its off is: 'PUSHIS 0, PUSHIS ID, COMM 7, PUSHREG, EQ' - 3 extra instructions that could've been simplified with a NEGATE instruction.")
comm8 = func(8,"BIT_ON",desc="Turns on flag of the given index", params=[flagParam], long_desc=flag_long_desc)
comm9 = func(9,"BIT_OFF",desc="Turns off flag of the given index", params=[flagParam], long_desc=flag_long_desc)
commA = func(0xa,"RND","int",params=[u_int_param], desc="Returns a random int from 0 to given int.")
#commB = ???. Shows up only in some events for a total of 30 times. 5 of which are in copy-pasted code in the heal spring???
#commC = Shows up 4 times. 3 of which is before conception and the 4th is during waking up cutscene.
commD = func(0xD,"POP",desc="(Guess) Removes a single value from the stack.")
commE = func(0xE,"WAIT",desc="Waits 1/30 of a second * given param", params=[u_int_param])
commF = func(0xF,"FADE_IN",desc="Flashes the screen with color (param2) and fades back at (param1) centiseconds.", params=[u_int_param,u_int_param])
comm10 = func(0x10,"FADE_OUT",desc="Fades the screen with color (param2) and fades in at (param1) centiseconds.", params=[u_int_param,u_int_param])
comm11 = func(0x11,"UNUSED_11",desc=unused_desc)
#comm12
#comm13 "CAM_PATH_MOVE"
#comm14
comm15 = func(0x15,"LOAD_DEMON_MODEL", params=[demonIdParam,u_int_param])
#comm16
#comm17
comm18 = func(0x18,"UNUSED_18",desc=unused_desc)
#comm19
comm1A = func(0x1a,"CAMERA_SHAKE",params=[u_int_param,u_int_param,u_int_param])
#comm1B
#comm1C
#comm1D
#comm1E
comm1F = func(0x1F,"UNUSED_1F",desc=unused_desc)
#comm20 = Shows up once in waking up cutscene
#comm21 "PMV_LOAD"
#comm22 "PMV_RUN2"
#comm23 "FLD_EVENT_END2". No parameters. Used in events.
#comm24 = Shows up only in e500 6 times. Known as "PUT"
#comm25 = Shows up once in 4th Kalpa
#comm26 "UNIT_ALL_CLEAR". Unused
comm27 = func(0x27,"GET_PHASE","int",desc="Returns current Kagutsuchi phase as 0-8")
#comm28 "CALL_EVENT_BATTLE". Pretty useful.
#comm29 "UNIT_ALL_CLEAR". Unused.
#comm2A "IMAGE_LOAD"
#comm2B
#comm2C
#comm2D "IMAGE_DISPLAY"
#comm2E
comm2F = func(0x2F,"UNUSED_2F",desc=unused_desc)
comm32 = func(0x32,"UNUSED_32",desc=unused_desc)
comm39 = func(0x39,"UNUSED_39",desc=unused_desc)
comm3A = func(0x3A,"UNUSED_3A",desc=unused_desc)
comm3B = func(0x3B,"UNUSED_3B",desc=unused_desc)
#comm46 = Shows up in 799 and 810, which are unknown events
comm4A = func(0x4A,"POSITION_MODEL",params=[u_int_param,u_int_param],desc="(guess) Takes the return from the loaded position of the 1st param, and loads the return from the loaded model in the 2nd param")
comm4C = func(0x4C,"UNUSED_4C",desc=unused_desc)
comm4F = func(0x4F,"UNUSED_4F",desc=unused_desc)
#comm50 = Unconfirmed: Display video cutscene.
#comm54 = Shows up in 799, which is unknown
#comm57 = Puzzle boy related (play when already done?)
comm58 = func(0x58,"UNUSED_58",desc=unused_desc)
comm59 = func(0x59,"UNUSED_59",desc=unused_desc)
comm5A = func(0x5A,"UNUSED_5A",desc=unused_desc)
comm5B = func(0x5B,"UNUSED_5B",desc=unused_desc)
comm5C = func(0x5C,"UNUSED_5C",desc=unused_desc)
#comm5D = Shows up 3 times
comm5E = func(0x5E,"BUTTON_CHECK","int",params=[u_int_param,u_int_param],desc="Checks if button is pressed. Used for Enter/Open (X) labels.")
comm60 = func(0x60,"RM_FLD_CONTROL",desc="Remove player control",long_desc="\tTypically done to display a message, to be combined later with 0x61: GIVE_FLD_CONTROL()")
comm61 = func(0x61,"GIVE_FLD_CONTROL",desc="Give player back control",long_desc="\tThis is typically used after a message is displayed to return control to the player. If not done it'll softlock.")
comm62 = func(0x62,"UNUSED_62",desc=unused_desc)
#comm63 = Shows up only in obelisk, but a lot of times. 
#comm64 = Shows up only in obelisk 7 times
#comm65 = Shows up only in obelisk, but a bunch of times
comm66 = func(0x66,"CALL_EVENT",params=[eventIdParam],desc="Calls event script of the given ID")
comm67 = func(0x67,"CALL_BATTLE",params=[battleIdParam],desc="Initiates a battle of the given ID")
#comm6D = Shows up once in intro. Label as unused?
comm70 = func(0x70,"ADD_ITEM",params=[itemIdParam,u_int_param],desc="Adds items to your inventory.")
#comm72 = Shows up a bunch in 500
#comm74 = Shows up 5 times in seemingly unrelated events
comm76 = func(0x76,"UNUSED_76",desc=unused_desc)
comm78 = func(0x78,"UNUSED_78",desc=unused_desc)
comm7D = func(0x7D,"UNUSED_7D",desc=unused_desc)
#comm7F = Shows up in ai.bf 3 times
#comm80 = Shows up in ai.bf 3 times
comm84 = func(0x84,"UNUSED_84",desc=unused_desc)
#comm90 single parameter that is a location. Used for the location callback on Dante 1.
#comm91 No parameters. Only shows up in field scripts. Total of 46.
#comm92 No parameters. Only shows up in field scripts. Total of 38.
#comm93 1 parameter of 0 or 1. Only shows up in event scripts. Total of 19
comm94 = func(0x94,"LOAD_POS_ASSET","int",params=[u_str_param],desc="Loads external assets such as cameras or positions")
#comm95 6 parameters, 1st is a demon model. Seems related to manikins?
#comm96 3 parameters. Total 18
comm97 = func(0x97,"CALL_NEXT",params=[u_int_param,fieldIdParam,locationIdParam],desc="Sets a callback to a field and position in that field. 1st param is universally 1.")
#comm98 2 parameters. Int and Position. VERY common in Diet building.
#comm99 event only. 190 count
comm9A = func(0x9A,"UNUSED_9A",desc=unused_desc)#Shows up in 501, 502, 503 which are unused events.
#comm9B takes BED file. Shows up twice outside of events. Once in Nihilo and once in initialization of ToK1.
#comm9C very rare and only in events: Gozu Tennoh 2nd, Fusion, Evolution.
#comm9D takes BED file. Total of 412
#comm9E event only. Total of 175.
#comm9F event only. Total of 68. Shows up most in Hikiawa in Ikebukuro cutscene (termial model related?)
commA2 = func(0xA2,"UNUSED_A2",desc=unused_desc)
commA8 = func(0xA8,"UNUSED_A8",desc=unused_desc)
commA9 = func(0xA9,"UNUSED_A9",desc=unused_desc)
commB1 = func(0xB1,"UNUSED_B1",desc=unused_desc)
commBF = func(0xBF,"UNUSED_BF",desc=unused_desc)
commC0 = func(0xC0,"UNUSED_C0",desc=unused_desc)
commC1 = func(0xC1,"UNUSED_C1",desc=unused_desc)

commC3 = func(0xC3,"HUD_DSP",params=[u_int_param],desc="Displays or removes the HUD using an octet mask.")

commCC = func(0xCC,"UNUSED_CC",desc=unused_desc)
commD1 = func(0xD1,"UNUSED_D1",desc=unused_desc)
commD2 = func(0xD2,"UNUSED_D2",desc=unused_desc)
commD3 = func(0xD3,"UNUSED_D3",desc=unused_desc)
commD5 = func(0xD5,"UNUSED_D5",desc=unused_desc)
commDF = func(0xDF,"UNUSED_DF",desc=unused_desc)
commFB = func(0xFB,"UNUSED_FB",desc=unused_desc)
commFD = func(0xFD,"UNUSED_FD",desc=unused_desc)
commFF = func(0xFF,"UNUSED_FF",desc=unused_desc)
comm102 = func(0x102,"UNUSED_102",desc=unused_desc)
comm10B = func(0x10B,"UNUSED_10B",desc=unused_desc)
comm10C = func(0x10C,"UNUSED_10C",desc=unused_desc)
comm10D = func(0x10D,"UNUSED_10D",desc=unused_desc)
comm118 = func(0x118,"UNUSED_118",desc=unused_desc)
comm11B = func(0x11B,"UNUSED_11B",desc=unused_desc)
comm11C = func(0x11C,"UNUSED_11C",desc=unused_desc)
comm120 = func(0x120,"UNUSED_120",desc=unused_desc)

comm121 = func(0x121,"NAME_CHARCTER",desc="Brings up the character name screen. Exclusively for the introduction of the game.",params=[u_int_param,u_int_param])

comm132 = func(0x132,"UNUSED_132",desc=unused_desc)
comm133 = func(0x133,"UNUSED_133",desc=unused_desc)
comm134 = func(0x134,"UNUSED_134",desc=unused_desc)
comm135 = func(0x135,"UNUSED_135",desc=unused_desc)
comm136 = func(0x136,"UNUSED_136",desc=unused_desc)
comm137 = func(0x137,"UNUSED_137",desc=unused_desc)
comm14A = func(0x14A,"UNUSED_14A",desc=unused_desc)
comm14D = func(0x14D,"UNUSED_14D",desc=unused_desc)
comm154 = func(0x154,"UNUSED_154",desc=unused_desc)

comm158 = func(0x158,"ADD_STOCK",desc="Adds demon stock. By default starts at 8 and should NEVER go past 12.",params=[u_int_param])

comm167 = func(0x167,"UNUSED_167",desc=unused_desc)
comm16C = func(0x16C,"UNUSED_16C",desc=unused_desc)
comm16D = func(0x16D,"UNUSED_16D",desc=unused_desc)
comm16E = func(0x16E,"UNUSED_16E",desc=unused_desc)
comm16F = func(0x16F,"UNUSED_16F",desc=unused_desc)
#187-1E0 is unused
#1E1-1E7 exists
#1F0-1FB exists
comm211 = func(0x211,"UNUSED_211",desc=unused_desc)
comm212 = func(0x212,"UNUSED_212",desc=unused_desc)
comm215 = func(0x215,"CREATE_BOUNDRY",params=[u_int_param])
comm21E = func(0x21e,"CREATE_BOUNDRY_FROM_POS",params=[posParam])

#comm21F is the last one.

#Put 'em in
COMM_FUNS[0] = comm0
COMM_FUNS[1] = comm1
COMM_FUNS[2] = comm2
COMM_FUNS[3] = comm3
COMM_FUNS[4] = comm4
COMM_FUNS[5] = comm5
COMM_FUNS[6] = comm6
COMM_FUNS[7] = comm7
COMM_FUNS[8] = comm8
COMM_FUNS[9] = comm9
COMM_FUNS[0xa] = commA
COMM_FUNS[0xD] = commD
COMM_FUNS[0xE] = commE
COMM_FUNS[0xF] = commF
COMM_FUNS[0x10] = comm10
COMM_FUNS[0x11] = comm11
COMM_FUNS[0x15] = comm15
COMM_FUNS[0x18] = comm18
COMM_FUNS[0x1A] = comm1A
COMM_FUNS[0x1F] = comm1F
COMM_FUNS[0x27] = comm27
COMM_FUNS[0x2F] = comm2F
COMM_FUNS[0x32] = comm32
COMM_FUNS[0x39] = comm39
COMM_FUNS[0x3A] = comm3A
COMM_FUNS[0x3B] = comm3B
COMM_FUNS[0x4C] = comm4C
COMM_FUNS[0x4F] = comm4F
COMM_FUNS[0x58] = comm58
COMM_FUNS[0x59] = comm59
COMM_FUNS[0x5A] = comm5A
COMM_FUNS[0x5B] = comm5B
COMM_FUNS[0x5C] = comm5C
COMM_FUNS[0x5E] = comm5E
COMM_FUNS[0x60] = comm60
COMM_FUNS[0x61] = comm61
COMM_FUNS[0x62] = comm62
COMM_FUNS[0x66] = comm66
COMM_FUNS[0x67] = comm67
COMM_FUNS[0x70] = comm70
COMM_FUNS[0x76] = comm76
COMM_FUNS[0x78] = comm78
COMM_FUNS[0x7D] = comm7D
COMM_FUNS[0x84] = comm84
COMM_FUNS[0x94] = comm94
COMM_FUNS[0x97] = comm97
COMM_FUNS[0xA2] = commA2
COMM_FUNS[0xA8] = commA8
COMM_FUNS[0xA9] = commA9
COMM_FUNS[0xB1] = commB1
COMM_FUNS[0xBF] = commBF
COMM_FUNS[0xC0] = commC0
COMM_FUNS[0xC1] = commC1
COMM_FUNS[0xC3] = commC3
COMM_FUNS[0xCC] = commCC
COMM_FUNS[0xD1] = commD1
COMM_FUNS[0xD2] = commD2
COMM_FUNS[0xD3] = commD3
COMM_FUNS[0xD5] = commD5
COMM_FUNS[0xDF] = commDF
COMM_FUNS[0xFB] = commFB
COMM_FUNS[0xFD] = commFD
COMM_FUNS[0xFF] = commFF
COMM_FUNS[0x102] = comm102
COMM_FUNS[0x10B] = comm10B
COMM_FUNS[0x10C] = comm10C
COMM_FUNS[0x10D] = comm10D
COMM_FUNS[0x118] = comm118
COMM_FUNS[0x11B] = comm11B
COMM_FUNS[0x11C] = comm11C
COMM_FUNS[0x120] = comm120
COMM_FUNS[0x121] = comm121
COMM_FUNS[0x132] = comm132
COMM_FUNS[0x133] = comm133
COMM_FUNS[0x134] = comm134
COMM_FUNS[0x135] = comm135
COMM_FUNS[0x136] = comm136
COMM_FUNS[0x137] = comm137
COMM_FUNS[0x14A] = comm14A
COMM_FUNS[0x14D] = comm14D
COMM_FUNS[0x154] = comm154
COMM_FUNS[0x158] = comm158
COMM_FUNS[0x167] = comm167
COMM_FUNS[0x16C] = comm16C
COMM_FUNS[0x16D] = comm16D
COMM_FUNS[0x16E] = comm16E
COMM_FUNS[0x16F] = comm16F
COMM_FUNS[0x211] = comm211
COMM_FUNS[0x212] = comm212
COMM_FUNS[0x215] = comm215
COMM_FUNS[0x21E] = comm21E

#Stuff entirely off of TGEnigma's descriptions. TGE doesn't distinguish between int and void.

comm13 = func(0x13,"CAM_PATH_MOVE",params=[u_int_param,u_int_param])
comm21 = func(0x21,"PMV_LOAD","int?",params=[u_int_param,u_int_param])
comm22 = func(0x22,"PMV_RUN2","int?",params=[u_int_param])
comm23 = func(0x23,"FLD_EVENT_END2","int?")
comm24 = func(0x24,"PUT","int?",params=[u_int_param], desc="Unused function")
comm26 = func(0x26,"UNIT_ALL_CLEAR","int?", desc="Unused function")
comm28 = func(0x28,"CALL_EVENT_BATTLE","int?",params=[u_int_param,u_int_param])
comm29 = func(0x29,"UNIT_ALL_CLEAR","int?", desc="Unused function")
comm2A = func(0x2a,"IMAGE_LOAD","int?",params=[u_str_param])
comm2D = func(0x2d,"IMAGE_DISPLAY","int?",params=[u_int_param])
comm30 = func(0x30,"AI_ACT_ATTACK","int?")
comm31 = func(0x31,"AI_ACT_ESCAPE","int?")
comm33 = func(0x33,"AI_ACT_SKILL","int?",params=[skill_param])
comm34 = func(0x34,"AI_TAR_RND","int?")
comm35 = func(0x35,"AI_TARGET_MINE","int?")
comm3D = func(0x3d,"AI_ACT_WAIT","int?")
comm48 = func(0x48,"SET_SKY_A","int?",params=[u_int_param,u_int_param])
comm4E = func(0x4e,"FLD_EVENT_END","int?")
comm6B = func(0x6b,"OBJ_PATH_MOVE","int?",params=[u_int_param,u_int_param,u_int_param])
comm6C = func(0x6c,"OBJ_PATH_WAIT","int?",params=[u_int_param])
comm72 = func(0x72,"PUTS","int?",params=[u_str_param])
comm7B = func(0x7B,"AI_CHK_MYHP","bool",params=[u_int_param])
comm7E = func(0x7E,"AI_CHK_TURN_EQUAL","bool",params=[u_int_param])

comm86 = func(0x86,"AI_CHK_ENHOJO","bool",params=[support_skill_param],desc="Returns if enemy has the specified support skill active")
comm87 = func(0x87,"AI_CHK_FRHOJO","bool",params=[support_skill_param],desc="Returns if an ally has the specified support skill active")
comm8E = func(0x8E,"BGM_PLAY_E","int?",params=[u_int_param,u_int_param])
comm9A = func(0x9A,"D3P_LOAD","int?",params=[u_str_param])
commA5 = func(0xa5,"SCR_RUN","int?",params=[u_int_param,u_int_param])
commB0 = func(0xb0,"MODEL_LIGHT_DIR","int?",params=[u_int_param,u_int_param,u_flt_param,u_flt_param,u_flt_param])
commB5 = func(0xb5,"SCENE_LIGHT_DIR","int?",params=[u_int_param,u_flt_param,u_flt_param,u_flt_param])
commC6 = func(0xc6,"LIGHT_PATH_MOVE","int?",params=[u_int_param,u_int_param])
commC8 = func(0xc8,"BE_LOAD","int?",params=[u_int_param])
commC9 = func(0xc9,"MODEL_BE","int?",params=[u_int_param,u_int_param])
commCB = func(0xcb,"EFFECT_BE","int?",params=[u_int_param,u_int_param])
commCC = func(0xcc,"TEX_BE","int?",params=[u_int_param,u_int_param])
commCE = func(0xce,"EFFBED_START","int?",params=[u_int_param,u_int_param])
commD0 = func(0xd0,"EFFBED_BE","int?",params=[u_int_param,u_int_param])
commD1 = func(0xd1,"EFFECT_PATH_MOVE","int?",params=[u_int_param,u_int_param])
commD2 = func(0xd2,"EFFECT_PATH_WAIT","int?",params=[u_int_param])
commD4 = func(0xd4,"EFFMG1_BE","int?",params=[u_int_param,u_int_param])
commD6 = func(0xd6,"EFFMG2_BE","int?",params=[u_int_param,u_int_param])
commD7 = func(0xd7,"EFFMG1_POS","int?",params=[u_int_param,u_int_param,u_int_param])
commD8 = func(0xd8,"EFFMG2_POS","int?",params=[u_int_param,u_int_param,u_int_param,u_int_param,u_int_param])
commE2 = func(0xe2,"AI_ACT_SKILL_PARAM","int?",params=[skill_param,unit_param])
commF7 = func(0xf7,"BE_READ","int?",params=[u_int_param])
commF8 = func(0xf8,"BE_OK","int?",params=[u_int_param])
commF9 = func(0xf9,"BE_DEL","int?",params=[u_int_param])
comm103 = func(0x103,"ON","int?",params=[u_int_param,u_int_param,u_str_param,u_int_param])
comm104 = func(0x104,"OFF","int?",params=[u_int_param,u_int_param,u_str_param,u_int_param])
comm10E = func(0x10e,"NPC_ON","int?",params=[u_int_param,u_int_param,u_str_param])
comm10F = func(0x10f,"NPC_OFF","int?",params=[u_int_param,u_int_param,u_str_param])
comm110 = func(0x110,"GIMIC_HOJI","int?",params=[u_int_param,u_int_param,u_int_param,u_int_param])
comm129 = func(0x129,"BLUR2_PARA","int?",params=[u_flt_param,u_flt_param,u_int_param])
comm12D = func(0x12D,"FILTER2_PARA","int?",params=[u_int_param])
comm132 = func(0x132,"MFILTER_PARA","int?",params=[u_int_param])
comm138 = func(0x138,"BGM_PLAY_E_TRANS","int?",params=[u_int_param,u_int_param])
comm15B = func(0x15B,"AI_TAR_AI","int?",desc="Targets unit that isn't the main character")
comm168 = func(0x168,"EFFBED_START2","int?",params=[u_int_param,u_int_param,u_int_param])
comm1F2 = func(0x1F2,"ITEMBOX_RND","int?")
comm1F9 = func(0x1F9,"DANTE_STANCE_SET","int?",params=[u_int_param])
comm202 = func(0x202,"FLD_WARP_CALL_FIELD","int?")
comm20F = func(0x20F,"FLD_CALL_WAPEX","int?",params=[u_int_param])
comm210 = func(0x210,"FLD_BGM_PLAY","int?",params=[u_int_param])

COMM_FUNS[0x13] = comm13
COMM_FUNS[0x21] = comm21
COMM_FUNS[0x22] = comm22
COMM_FUNS[0x23] = comm23
COMM_FUNS[0x24] = comm24
COMM_FUNS[0x26] = comm26
COMM_FUNS[0x28] = comm28
COMM_FUNS[0x29] = comm29
COMM_FUNS[0x2a] = comm2A
COMM_FUNS[0x2d] = comm2D
COMM_FUNS[0x30] = comm30
COMM_FUNS[0x31] = comm31
COMM_FUNS[0x33] = comm33
COMM_FUNS[0x34] = comm34
COMM_FUNS[0x35] = comm35
COMM_FUNS[0x3d] = comm3D
COMM_FUNS[0x48] = comm48
COMM_FUNS[0x4e] = comm4E
COMM_FUNS[0x6b] = comm6B
COMM_FUNS[0x6c] = comm6C
COMM_FUNS[0x72] = comm72
COMM_FUNS[0x7b] = comm7B
COMM_FUNS[0x7e] = comm7E
COMM_FUNS[0x86] = comm86
COMM_FUNS[0x87] = comm87
COMM_FUNS[0x8e] = comm8E
COMM_FUNS[0x9a] = comm9A
COMM_FUNS[0xa5] = commA5
COMM_FUNS[0xb0] = commB0
COMM_FUNS[0xb5] = commB5
COMM_FUNS[0xc6] = commC6
COMM_FUNS[0xc8] = commC8
COMM_FUNS[0xc9] = commC9
COMM_FUNS[0xcb] = commCB
COMM_FUNS[0xcc] = commCC
COMM_FUNS[0xce] = commCE
COMM_FUNS[0xd0] = commD0
COMM_FUNS[0xd1] = commD1
COMM_FUNS[0xd2] = commD2
COMM_FUNS[0xd4] = commD4
COMM_FUNS[0xd6] = commD6
COMM_FUNS[0xd7] = commD7
COMM_FUNS[0xd8] = commD8
COMM_FUNS[0xe2] = commE2
COMM_FUNS[0xf7] = commF7
COMM_FUNS[0xf8] = commF8
COMM_FUNS[0xf9] = commF9
COMM_FUNS[0x103] = comm103
COMM_FUNS[0x104] = comm104
COMM_FUNS[0x10e] = comm10E
COMM_FUNS[0x10f] = comm10F
COMM_FUNS[0x110] = comm110
COMM_FUNS[0x129] = comm129
COMM_FUNS[0x12d] = comm12D
COMM_FUNS[0x132] = comm132
COMM_FUNS[0x138] = comm138
COMM_FUNS[0x15b] = comm15B
COMM_FUNS[0x168] = comm168
COMM_FUNS[0x1f2] = comm1F2
COMM_FUNS[0x1f9] = comm1F9
COMM_FUNS[0x202] = comm202
COMM_FUNS[0x20f] = comm20F
COMM_FUNS[0x210] = comm210
