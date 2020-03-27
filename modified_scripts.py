import nocturne_script_assembler as assembler
import customizer_values as custom_vals

from io import BytesIO
from os import path

from fs.Iso_FS import *
from fs.DDS3_FS import *
from fs.LB_FS import *

''' Assembler bf_script modification functions:
def changeProcByIndex(self, instructions, relative_labels, index):
def changeMessageByIndex(self, message_obj, index):
def appendProc(self, instructions, relative_labels, proc_label):
def appendMessage(self, message_str, message_label_str, is_decision = False, name_id = 0):
def appendPUSHSTR(self,str):
def getMessageIndexByLabel(self, label_str):
def getPUSHSTRIndexByStr(self, str):
def getProcIndexByLabel(self, label_str):
def getProcInstructionsLabelsByIndex(self, proc_index):
'''

'''
#Example of procedure replacement:
f0##_obj = get_script_obj_by_name(dds3, 'f0##')
f0##_xxx_room = f0##_obj.getProcIndexByLabel("PROC_LABEL")
f0##_xxx_insts = [
    inst("PROC",f0##_xxx_room),
    #Insert instructions here
    inst("END")
]
f0##_xxx_labels = [
    assembler.label("BRANCH_LABEL",LINE_NUMBER)
]

f0##_obj.changeProcByIndex(f0##_xxx_insts, f0##_xxx_labels, f0##_xxx_room)
f0##_lb = push_bf_into_lb(f0##_obj, 'f0##')
dds3.add_new_file(custom_vals.LB0_PATH['f0##'], f0##_lb)
'''

#instruction creation shortcut
def inst(opcode_str,operand=0):
    return assembler.instruction(assembler.OPCODES[opcode_str],operand)
    
# gets the script object from dds3 fs by provided path
def get_script_obj_by_path(dds3, script_path):
    script = bytearray(dds3.get_file_from_path(script_path).read())
    return assembler.parse_binary_script(script)

def get_script_obj_by_name(dds3,script_name):
    return get_script_obj_by_path(dds3,custom_vals.SCRIPT_OBJ_PATH[script_name])

def push_bf_into_lb(bf_obj, name):
    # get the field lb and parse it
    lb_data = dds3.get_file_from_path(custom_vals.LB0_PATH[name])
    lb = LB_FS(lb_data)
    lb.read_lb()
    # add the uncompressed, modified BF file to the LB and add it to the dds3 fs
    return lb.export_lb({'BF': BytesIO(bytearray(bf_obj.toBytes()))})

def insert_callback(field_string, location_insert, fun_name_insert, overwrite_warning=True):
    if len(fun_name_insert) > 15:
        print("ERROR: In insert_callback().",fun_name_insert,"is over 15 characters long")
        return
    file_path = custom_vals.WAP_PATH[field_string]
    wap_file = dds3.get_file_from_path(file_path).read()
    #print("Inserting",fun_name_insert,"as callback for",field_string,". wap_file len:",len(wap_file))
    if wap_file[location_insert] != 0 and overwrite_warning:
        print("WARNING: Callback insertion of",fun_name_insert,"overwriting data.")
    wap_file = wap_file[:location_insert] + bytes([2]) + bytes(assembler.ctobb(fun_name_insert,15)) + wap_file[location_insert+16:]
    dds3.add_new_file(file_path,BytesIO(wap_file))

print ("Parsing ISO")
# open the ISO and parse it
iso = IsoFS('rom/input.iso')
iso.read_iso()

print ("Getting DDT")
# get the ddt and write it out to disk
ddt_file = iso.get_file_from_path('DDS3.DDT;1')

#if not os.path.isfile('rom/old_DDS3.IMG'): #save some dev time
with open('rom/old_DDS3.DDT', 'wb') as file:
    file.write(ddt_file.read())

print ("Getting Atlus FileSystem IMG")
# get the img and write it out to disk in chucks due to size
with open('rom/old_DDS3.IMG', 'wb') as file:
    for chunk in iso.read_file_in_chunks('DDS3.IMG;1'):
        file.write(chunk)

print ("Parsing Atlus FileSystem IMG")
# parse the dds3 fs
dds3 = DDS3FS('rom/old_DDS3.DDT', 'rom/old_DDS3.IMG')
dds3.read_dds3()

print ("Patching scripts")
# Replace e506.bf (intro) with a custom one to set a bunch of initial values.
with open('patches/e506.bf','rb') as file:
    e506 = BytesIO(file.read())
dds3.add_new_file('/event/e500/e506/scr/e506.bf', e506) #custom_vals.SCRIPT_OBJ_PATH['e506']

#Missing stuff:
#Exiting SMC cutscene. 475 or 476
#Pixie for west yoyogi (splash appeared so skip that)
#Great Underpass splash

# get the 601 event script and add our hook
#add in extra flag sets for cutscene removal
e601_obj = get_script_obj_by_name(dds3, 'e601')
e601_insts = [
    inst("PROC",0), 
    inst("PUSHIS",0x440), #SMC Splash removal
    inst("COMM",8),
    inst("PUSHIS",0x480), #Shibuya Splash removal
    inst("COMM",8),
    inst("PUSHIS",0x9), #Chiaki removal. Can be a setting, but it's not shortened yet.
    inst("COMM",8),
    inst("PUSHIS",0xa), #Initial Cathedral cutscene
    inst("COMM",8),
    inst("PUSHIS",0xb), #Hijiri Shibuya removal
    inst("COMM",8),
    inst("PUSHIS",0xa2), #Fountain cutscene removal
    inst("COMM",8),
    inst("PUSHIS",0x404), #SMC exit cutscene removal
    inst("COMM",8),
    inst("PUSHIS",0x4a0), #Amala Network 1 cutstscene 1
    inst("COMM",8),
    inst("PUSHIS",0x4a1), #AN1c2
    inst("COMM",8),
    inst("PUSHIS",0x4a2), #AN1c3. (looks weird but eh)
    inst("COMM",8),
    inst("PUSHIS",0x4a4), #AN1c4
    inst("COMM",8),
    inst("PUSHIS",0x4a5), #AN1c5
    inst("COMM",8),
    inst("PUSHIS",0x4c0), #Ginza splash
    inst("COMM",8),
    inst("PUSHIS",0x4c3), #Harumi Warehouse splash
    inst("COMM",8),
    inst("PUSHIS",0x510), #Ginza Underpass splash
    inst("COMM",8),
    inst("PUSHIS",0x512), #Underpass Manikin 1
    inst("COMM",8),
    inst("PUSHIS",0x513), #UM2
    inst("COMM",8),
    inst("PUSHIS",0x514), #UM3
    inst("COMM",8),
    inst("PUSHIS",0x515), #UM4
    inst("COMM",8),
    inst("PUSHIS",0x560), #Thor Gauntlet shorten
    inst("COMM",8),
    inst("PUSHIS",0x540), #Ikebukuro enter flag 1
    inst("COMM",8),
    inst("PUSHIS",0x54a), #Ikebukuro 2
    inst("COMM",8),
    inst("PUSHIS",0x931), #Ikebukuro 3
    inst("COMM",8),
    inst("PUSHIS",0x56c), #Ikebukuro 4
    inst("COMM",8),
    inst("PUSHIS",0x54b), #Ikebukuro 5
    inst("COMM",8),
    inst("PUSHIS",0x54c), #Ikebukuro 6
    inst("COMM",8),
    inst("PUSHIS",0x54d), #Ikebukuro 7
    inst("COMM",8),
    inst("PUSHIS",0x912), #Ikebukuro 8
    inst("COMM",8),
    inst("PUSHIS",0x4ec), #East Nihilo textbox. 4e0 should NOT be set.
    inst("COMM",8),
    inst("PUSHIS",0x4f4), #Kaiwan maze 1
    inst("COMM",8),
    inst("PUSHIS",0x4f5), #Kaiwan maze 2
    inst("COMM",8),
    inst("PUSHIS",0x4f6), #Kaiwan maze 3
    inst("COMM",8),
    inst("PUSHIS",0x700), #Kaiwan empty cube
    inst("COMM",8),
    inst("PUSHIS",0x6c5), #Kaiwan scene 1
    inst("COMM",8),
    inst("PUSHIS",0x6c6), #Kaiwan scene 2
    inst("COMM",8),
    inst("PUSHIS",0x6c7), #Kaiwan scene 3
    inst("COMM",8),
    inst("PUSHIS",0x580), #Kabukicho Splash
    inst("COMM",8),
    inst("PUSHIS",0x583), #Cutscene before Mizuchi
    inst("COMM",8),
    inst("PUSHIS",0x594), #Cutscene with Futomimi after Mizuchi
    inst("COMM",8),
    inst("PUSHIS",0x5a0), #Ikebukuro Tunnel Splash
    inst("COMM",8),
    inst("PUSHIS",0x5e0), #Amala Network 2 Splash
    inst("COMM",8),
    inst("PUSHIS",0x600), #Asakusa Tunnel Splash
    inst("COMM",8),
    inst("PUSHIS",0x640), #Obelisk Splash
    inst("COMM",8),
    inst("PUSHIS",0x650), #Sisters Talk (Consider to keep on, but change their models to the randomized boss)
    inst("COMM",8),
    inst("PUSHIS",0x680), #Diet Building Splash
    inst("COMM",8),
    inst("PUSHIS",0x69E), #Diet Building Message 1
    inst("COMM",8),
    inst("PUSHIS",0x688), #Diet Building Message 2
    inst("COMM",8),
    inst("PUSHIS",0x689), #Diet Building Message 3
    inst("COMM",8),
    inst("PUSHIS",0x760), #1st Kalpa splash
    inst("COMM",8),
    inst("PUSHIS",0x780), #2nd Kalpa splash
    inst("COMM",8),
    inst("PUSHIS",0x7a0), #3rd Kalpa splash
    inst("COMM",8),
    inst("PUSHIS",0x7c0), #4th Kalpa splash
    inst("COMM",8),
    inst("PUSHIS",0x7e0), #5th Kalpa splash
    inst("COMM",8),
    inst("PUSHIS",506), 
    inst("COMM",0x66), 
    inst("END",0)
]
e601_obj.changeProcByIndex(e601_insts,[],0) #empty list is relative branch labels
# convert the script object to a filelike object and add it to the dds3 file system
e601_data = BytesIO(bytearray(e601_obj.toBytes()))
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e601'], e601_data)
#Don't need to put it into a LB file because it is an event script, not a field script.

# Shorten 618 (intro)
# Cutscene removal in SMC f015

# SMC area flag
# get the uncompressed field script from the folder instead of the LB
f015_obj = get_script_obj_by_path(dds3, '/fld/f/f015/f015.bf')
tri_preta_room_index = f015_obj.getProcIndexByLabel("012_start")
f015_012_start_insts = [
    inst("PROC",tri_preta_room_index),
    inst("PUSHIS",0),
    inst("PUSHIS",0x21),
    inst("COMM",7), #Check flag
    inst("PUSHREG"), #Push the result of previous operation as a parameter, in this case, 0 == flagcheck(7)
    inst("EQ"), #Check if flag 0x21 is 0 (unset)
    inst("PUSHIS",0x452),
    inst("COMM",7),
    inst("PUSHREG"), #Check if flag 0x452 is 1 (set)
    inst("AND"), #If both
    inst("IF",0), #Branch to label number 0 in our label list if true
    inst("PUSHIS",0x21),
    inst("COMM",8), #Set flag 0x21
    inst("PUSHIS",0x1f7),
    inst("PUSHIS",0xf),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next procedure index f (probably this one?)
    inst("PUSHIS",0x5D),
    inst("COMM",0x67), #Initiate battle 0x5D
    inst("END"), #Label: _END - Line number 19 (20th)
    inst("PUSHIS",0), #Line number 20 (21st) Label: _366
    inst("PUSHIS",0x453),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0x452),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("AND"),
    inst("IF",1), #Branch to END if (flag 0x453 is unset) is true
    inst("PUSHSTR",0), # - "01cam_01" - fixed camera
    inst("COMM",0x94), #Set cam
    inst("PUSHREG"),
    inst("COMM",0xA3),
    inst("PUSHIS",1),
    inst("MINUS"),
    inst("COMM",0x12), #Go to fixed camera.
    inst("COMM",1), #Open text box
    inst("PUSHIS",0xe),
    inst("COMM",0), #Print out message index e (You got pass)
    inst("COMM",2),
    inst("PUSHIS",0x3d1),
    inst("COMM",8), #Set flag 0x3d1
    inst("PUSHIS",0x453),
    inst("COMM",8), #Set flag 0x453
    inst("COMM",0x61), #Give player control back
    inst("END")
]
f015_012_start_labels = [
    assembler.label("PRETA_FIGHT_DONE",20), #both needs to be changed if above procedure is shifted
    assembler.label("GATE_PASS_OBTAINED",19) #given number is line number
]
f015_obj.changeProcByIndex(f015_012_start_insts, f015_012_start_labels, tri_preta_room_index)

#Forneus
forneus_room_index = f015_obj.getProcIndexByLabel("002_start") #index 18 / 0x12
#Can't figure out what flag 769 is for. I'll just not set it and see what happens.
#Flag 8 is definitely the defeat forneus flag.
#000_dh_plus is the one that has the magatama text that is called after beating forneus. Proc index 60 / 0x3c
f015_002_start_insts = [
    inst("PROC",forneus_room_index),
    inst("PUSHIS",0),
    inst("PUSHIS",0x8),
    inst("COMM",7), #Check Forneus fought flag
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0), #Branch to first label if fought
    inst("PUSHIS",1),
    inst("PUSHIS",0x44f),
    inst("COMM",7), #2F check
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0),
    inst("PUSHIS",8),
    inst("COMM",8), #Set Forneus fought flag
    inst("PUSHIS",0x1f4),
    inst("PUSHIS",0xf),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0xe),
    inst("COMM",0x67), #Fight Forneus
    inst("END"),
    inst("PUSHIX", 7),
    inst("COMM",0x16), #No idea what this does
    inst("END") #Label 0 here
]
#print 0 positions: 002_01eve_04, 005_01eve_05, 007_01eve_06, 007_01eve_08
f015_002_start_labels = [
    assembler.label("FORNEUS_DEAD",24)
]
f015_obj.changeProcByIndex(f015_002_start_insts, f015_002_start_labels, forneus_room_index)

f015_obj.changeMessageByIndex(assembler.message("Forneus reward placeholder","FORNEUS_REWARD"),0x5b)

#TODO: Shorten Black Rider
f015_lb = push_bf_into_lb(f015_obj, 'f015')
dds3.add_new_file(custom_vals.LB0_PATH['f015'], f015_lb)

#Cutscene removal in Shibuya f017
#TODO: Shorten Mara

#Shorten e623. e623_trm
#COMMs: 95 6p, 
#   TERMINAL: 11A
#       If result of 11A is the same as reg 6 -> _11: END
#       94*3 (cam), 13, 4B, 73, 1, 0;D "Did you decide to enter?", 3;E, 2, IF -> _9
#       94*3 (cam), 13, E, 1, 0;F "I'll send you over", 8;D, 45, 23, E;1, 50;4
#   _6: 52-PUSH, IF -> _7
#       D. GOTO _6
#   _7: 51, 8;5B, 10;1-1, E;1, 97;(26f,12,1): END
#   _9: If reg 3 is eq 1 -> _TERMINAL
#       E;1E, 1, 0;10 "Tell me when you're ready", 2, 4B;(A,1), 73
#       GOTO TERMINAL
#I give up

#Cutscene removal in Amala Network 1 f018
#4A0, 4A1, 4A2 (looks weird but eh).
#Shorten cutscene for 4A3 in 002_start - 4A7 gets set going in and unset immediately. Remove 55 - 164.
f018_obj = get_script_obj_by_name(dds3, 'f018')
f018_02_room = f018_obj.getProcIndexByLabel("002_start")
f018_02_insts, f018_02_labels = f018_obj.getProcInstructionsLabelsByIndex(f018_02_room)
precut = 55
postcut = 164
diff = postcut - precut
f018_02_insts = f018_02_insts[:precut] + f018_02_insts[postcut:]
for l in f018_02_labels:
    if l.label_offset > precut:
        l.label_offset-=diff
        if l.label_offset < 0:
            l.label_offset = 1
            #TODO: Do better than just move the labels
f018_obj.changeProcByIndex(f018_02_insts, f018_02_labels, f018_02_room)
#TODO: Change remaining text to make a little more sense.
#TODO: Make it not softlock if 4A2 wasn't already set.

#4A4 needs to be set for this
#4A5 is ???
#Shorten cutscene for 4A6 in 007_start (shared) - 4A8 gets set going in and unset immediately. Remove lines 91 - 272
f018_07_room = f018_obj.getProcIndexByLabel("007_start")
f018_07_insts, f018_07_labels = f018_obj.getProcInstructionsLabelsByIndex(f018_07_room)
precut = 91
postcut = 272
diff = postcut - precut
f018_07_insts = f018_07_insts[:precut] + f018_07_insts[postcut:]
for l in f018_07_labels:
    if l.label_offset > precut:
        l.label_offset-=diff
        if l.label_offset < 0:
            l.label_offset = 1
            #TODO: Do better than just move the labels
            
f018_obj.changeProcByIndex(f018_07_insts, f018_07_labels, f018_07_room)

#Shorten cutscene for Specter 1 in 009_start (shared) - 4AB is defeated flag. 4A9 gets set going in. 4AA gets set during cutscene.
# 171 - 247
#return: 4AB set
f018_09_room = f018_obj.getProcIndexByLabel("009_start")
f018_09_insts, f018_09_labels = f018_obj.getProcInstructionsLabelsByIndex(f018_09_room)
f018_09_insert_insts = [ #Instructions to be inserted before fighting specter 1
    inst("PUSHSTR", 697), #"atari_hoji_01"
    inst("PUSHIS", 0),
    inst("PUSHIS", 0),
    inst("COMM",0x108), #Remove the barrier
    inst("PUSHIS", 2),
    inst("PUSHSTR", 711), #"md_hoji_01"
    inst("PUSHIS", 0),
    inst("PUSHIS", 0),
    inst("COMM",0x104), #Remove the visual barrier
    inst("PUSHIS", 0xe),
    inst("COMM", 8) #set flag 0xE
]
#change 0x16 for specter 1 reward.
f018_obj.changeMessageByIndex(assembler.message("Specter 1 reward placeholder","SPEC1_REWARD"),0x16)
precut1 = 35
postcut1 = 161
precut2 = 171
postcut2 = 247
diff1 = postcut1 - precut1
diff2 = postcut2 - precut2
f018_09_insts = f018_09_insts[:precut1] + f018_09_insts[postcut1:precut2] + f018_09_insert_insts + f018_09_insts[postcut2:]
for l in f018_09_labels:
    if l.label_offset > precut1:
        if l.label_offset > precut2:
            l.label_offset-=diff2
            l.label_offset+=len(f018_09_insert_insts)
        l.label_offset-=diff1
        if l.label_offset < 0:
            l.label_offset = 1
            #TODO: Do better than just move the labels
f018_obj.changeProcByIndex(f018_09_insts, f018_09_labels, f018_09_room)
f018_lb = push_bf_into_lb(f018_obj, 'f018')
dds3.add_new_file(custom_vals.LB0_PATH['f018'], f018_lb)

#75E gets set going into LoA Lobby.
#4C2 gets set leaving LoA Lobby.

#Cutscene removal in Ginza (Hijiri mostly) f019
#Optional: Shorten Troll (already short)
#Should be done as an entry point
f019_obj = get_script_obj_by_name(dds3,"f019")
f019_troll_rwms_index = f019_obj.appendMessage("Troll reward placeholder","TROLL_REWARD")
f019_troll_callback_str = "TROLL_CB"
f019_troll_callback_insts = [
    inst("PROC",len(f019_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",2),
    inst("PUSHIS",f019_troll_rwms_index),
    inst("COMM",0),
    inst("COMM",1),
    inst("COMM",0x61),
    inst("END")
]
f019_obj.appendProc(f019_troll_callback_insts,[],f019_troll_callback_str)
insert_callback('f019',0x1350,f019_troll_callback_str)
f019_lb = push_bf_into_lb(f019_obj, 'f019')
dds3.add_new_file(custom_vals.LB0_PATH['f019'], f019_lb)

#Cutscene removal in Ginza Underpass f022
#Shorten Matador
#4C3 is Harumi Warehouse splash.
#510 is Ginza underpass splash
#512, 513, (517?), 514, 515 - Underpass Manikin cutscenes. 511 is underpass terminal.
#522 - Gatewatch Manikin, 523 - Collector Manikin, 520 - Yes to Collector Manikin.
#4C4 and 4C5 for Troll Cutscene. Should be shortened and not removed.
#529 & 4D6 - Giving the bill to collector. 
#4D6 unset talking to gatekeeper. Set: 526, 75C
#11 set fighting Matador in e740 (is it?). After, set: 751 and 3E9. Also 921 and 108

#Plan: Don't even call e740
#Original Callback after e740 is 013_shuku_mes. Index 27 (0x1b)
#Callback seems to work, so we can use 013_shuku_mes
f022_obj = get_script_obj_by_name(dds3, 'f022')
f022_mata_room = f022_obj.getProcIndexByLabel("013_01eve_01")
f022_013_e1_insts = [
    inst("PROC",f022_mata_room),
    inst("PUSHIS",0),
    inst("PUSHIS",0x108),
    inst("COMM",7), #Check Matador fought flag
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0), #Branch to label 0 if fought
    inst("PUSHIS",0x108),
    inst("COMM",8), #Set Matador fought flag
    inst("PUSHIS",0x751), #Possibly open LoA flag
    inst("COMM",8), 
    inst("PUSHIS",0x3e9), #Matador's Candelabra
    inst("COMM",8), 
    inst("PUSHIS",0x921), #Gets set, but not sure what it does? Maybe this is the textbox flag.
    inst("COMM",8),
    inst("PUSHIS",0x2e4),
    inst("PUSHIS",0x16),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x404),
    inst("COMM",0x67), #Fight Matador
    inst("END"),#Label 0 here
]
f022_013_e1_labels = [
    assembler.label("MATADOR_GONE",21)
]
f022_mata_callback = f022_obj.getProcIndexByLabel("013_shuku_mes")
f022_mata_callback_insts = [
    inst("PROC",f022_mata_callback),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x1d),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f022_obj.changeMessageByIndex(assembler.message("Matador reward placeholder","MATA_REWARD"),0x1d)
f022_obj.changeProcByIndex(f022_mata_callback_insts,[],f022_mata_callback)

f022_obj.changeProcByIndex(f022_013_e1_insts, f022_013_e1_labels, f022_mata_room)
f022_lb = push_bf_into_lb(f022_obj, 'f022')
dds3.add_new_file(custom_vals.LB0_PATH['f022'], f022_lb)

#Cutscene removal in Ikebukuro f023
#913 set in Ikebukuro. 54b 54c 54d - 540, 549, 56C, 931, 75E
#Shorten Daisoujou

f023_obj = get_script_obj_by_name(dds3, 'f023')
f023_03_room = f023_obj.getProcIndexByLabel("003_01eve_02")
f023_03_insts = [
    inst("PROC",f023_03_room),
    inst("PUSHIS",0x1a), #Story trigger to enable Daisoujou
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x753), #Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x107), #Didn't already beat him
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("AND"), #If not (f[1a] == 1 and f[753] == 0 and f[107] == 0)
    inst("IF",0), #End label
    inst("COMM",0x60),#RM_FLD_CONTROL
    inst("COMM",1), #MSG_WND_DSP
    inst("PUSHIS",0x1d), #"Do you want to stay here"
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x1e), #Yes/no
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #If no is selected, go to label 1. Differs from label 0 in that you set 0x753
    inst("PUSHIS",0x3e7), #set 3e7, 923, 107
    inst("COMM",8),
    inst("PUSHIS",0x923),
    inst("COMM",8),
    inst("PUSHIS",0x107),
    inst("COMM",8),
    inst("PUSHIS",0x2e6),
    inst("PUSHIS",0x17),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x406),
    inst("COMM",0x67), #Fight Daisoujou
    inst("END"),
    inst("PUSHIS",0x753),
    inst("COMM",8),
    inst("COMM",0x61),#GIVE_FLD_CONTROL
    inst("END")
]
f023_03_labels = [
    assembler.label("DAISOUJOU_FOUGHT",43),
    assembler.label("DAISOUJOU_RAN",40)
]

f023_obj.changeProcByIndex(f023_03_insts, f023_03_labels, f023_03_room)

f023_03_room_2 = f023_obj.getProcIndexByLabel("003_01eve_01") #Completely copy-pasted from the above, but is triggered from a different position. Just call the other one dammit.
f023_03_2_insts = [
    inst("PROC",f023_03_room_2),
    inst("CALL",f023_03_room),
    inst("END"),
]

f023_obj.changeProcByIndex(f023_03_2_insts, [], f023_03_room_2)
f023_daisoujou_callback_str = "DAI_CB"
f023_daisoujou_rwms_index = f023_obj.appendMessage("Daisoujou reward placeholder", "DAI_REWARD")

f023_proclen = len(f023_obj.p_lbls().labels)
f023_daisoujou_rwmspr_insts = [ #reward message proc
    inst("PROC",f023_proclen),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f023_daisoujou_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f023_obj.appendProc(f023_daisoujou_rwmspr_insts, [], f023_daisoujou_callback_str)
insert_callback('f023',0x284,f023_daisoujou_callback_str)
#seek to 0x284 of f023.wap. write 02 then "DAI_RWMSPR"

#pushis 0x32a, comm 0x66 is call dante
#set bit 0x100
#dante start code is short enough I'll just rewrite the whole thing
f023_01_dante_proc = f023_obj.getProcIndexByLabel("001_01eve_03")
f023_01_dante_insts = [
    inst("PROC",f023_01_dante_proc),
    inst("PUSHIS",0),
    inst("PUSHIS",0x100),
    inst("COMM",7),#Check that Dante isn't beaten
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0x549),
    inst("COMM",7),#Check that Thor is beaten
    inst("PUSHREG"),
    inst("AND"),
    inst("IF",0),#end proc if not both
    inst("PUSHIS",0x100),
    inst("COMM",8), #Set 0x100
    inst("PUSHIS",0x2d3),
    inst("PUSHIS",0x17),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("PUSHIS",1033),
    inst("COMM",0x67), #Fight Dante
    inst("END")
]
f023_01_dante_labels = [
    assembler.label("DANTE_FOUGHT",19)
]
f023_obj.changeProcByIndex(f023_01_dante_insts, f023_01_dante_labels, f023_01_dante_proc)

f023_dante_callback_str = "DANTE_CB"
f023_dante_reward_index = f023_obj.appendMessage("Dante reward placeholder", "DANTE_REWARD")
f023_dante_reward_insts = [
    inst("PROC",f023_proclen + 1), #+1 from Daisoujou one.
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f023_dante_reward_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f023_obj.appendProc(f023_dante_reward_insts, [], f023_dante_callback_str)
insert_callback('f023',0x220,f023_dante_callback_str)

f023_lb = push_bf_into_lb(f023_obj, 'f023')
dds3.add_new_file(custom_vals.LB0_PATH['f023'], f023_lb)

#Cutscene removal in Mantra HQ f024
#560 on. Put into jail cell scene.
#Shorten Thor Gauntlet
#   We can use 001_start to optionally warp to Thor Gauntlet. All it has is the "Chiaki Left" message, which we just straight up don't need. It uses flag 0x572.

f024_obj = get_script_obj_by_name(dds3, 'f024')
f024_01_room = f024_obj.getProcIndexByLabel("001_start")
f024_thor_gauntlet_msg_index = f024_obj.appendMessage("Do you want to go directly to the Thor gauntlet?", "THOR_GAUNTLET_MSG")
f024_thor_gauntlet_msg_no_index = f024_obj.appendMessage("If you would like to do the Thor gauntlet, go to the center room^non the 3rd floor.", "THOR_GAUNTLET_MSG_NO")
f024_yesno_sel = 174 #that is the literal label name

f024_01_insts = [
    inst("PROC",f024_01_room),
    inst("PUSHIS", 0),
    inst("PUSHIS", 0x572), #Make sure this gets set when you fight Thor.
    inst("COMM", 7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF", 0), #End label
    inst("PUSHIS", 0x572), 
    inst("COMM", 8), #set the bit to not show the messsage again.
    inst("COMM", 0x60),
    inst("COMM", 1),
    inst("PUSHIS", f024_thor_gauntlet_msg_index),
    inst("COMM", 0),
    inst("PUSHIS",0),
    inst("PUSHIS", f024_yesno_sel),
    inst("COMM", 3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #Semi-end label. Show the "no" textbox and give control back.
    inst("COMM", 0x61),
    inst("COMM", 2),
    inst("PUSHIS",0x565),
    inst("COMM",0x8), #TODO in here. Close the Thor gauntlet jail if that setting is on.
    inst("PUSHIS",0x1f4),
    inst("PUSHIS",0x18),
    inst("PUSHIS",0x1),
    inst("COMM",0x97),
    inst("PUSHIS",0x53),
    inst("COMM",0x67),
    inst("END"),
    inst("PUSHIS", f024_thor_gauntlet_msg_no_index),
    inst("COMM",0),
    inst("COMM", 0x61),
    inst("COMM", 2),
    inst("END")
]
f024_01_labels = [
    assembler.label("_01_END",34),
    assembler.label("_01_NO", 30)
]

f024_obj.changeProcByIndex(f024_01_insts, f024_01_labels, f024_01_room)

f024_10_room = f024_obj.getProcIndexByLabel("010_start")
f024_10_insts, f024_10_labels = f024_obj.getProcInstructionsLabelsByIndex(f024_10_room)
f024_10_insert_insts = [
    inst("PUSHIS", 82), #Orthrus's ID
    inst("PUSHIS",6),
    inst("COMM",0x15),
    inst("PUSHREG"),
    inst("POPLIX",0x3a), #store the result in a global variable
    inst("PUSHSTR",1576), #01pos_12
    inst("COMM",0x94),
    inst("PUSHREG"),
    inst("PUSHLIX",0x3a),
    inst("COMM",0x4a),
    inst("PUSHLIX",0x3a),
    inst("COMM",0x21e)
]
f024_10_insert_insts_thor_pre = [
    inst("PUSHIS", 22), #Thor's ID
    inst("PUSHIS",6),
    inst("COMM",0x15),
    inst("PUSHREG"),
    inst("POPLIX",0x39), #store the result in a global variable
    inst("PUSHSTR",1576), #01pos_12
    inst("COMM",0x94),
    inst("PUSHREG"),
    inst("PUSHLIX",0x39),
    inst("COMM",0x4a),
    inst("PUSHLIX",0x39),
    inst("COMM",0x21e)
]
#from  726-881
f024_obj.changeMessageByIndex(assembler.message("Thor reward placeholder","THOR_REWARD"),97)
f024_10_insert_insts_thor_post = [ #double-check the flags here. Dante might not spawn.
    inst("COMM",0x60), #remove player control
    inst("PUSHIS",0x567), #Don't fight Thor in here again.
    inst("COMM",8),
    inst("PUSHIS",0x840), #??? Flag on
    inst("COMM",8),
    inst("PUSHIS",0x549), #Dante Flag. 0x100 needs to not be set for this to work correctly.
    inst("COMM",8),
    inst("COMM",1), #display message window
    inst("PUSHIS",97), #Magatama get message
    inst("COMM",0),
    inst("COMM",2), #close message window
    inst("PUSHIS",0x21),
    inst("COMM",0x20f)#warp
]
precut1 = 125
postcut1 = 335
precut2 = 549 
postcut2 = 649
precut3 = 726
postcut3 = 881
diff1 = (postcut1 - precut1) - len(f024_10_insert_insts)
diff2 = (postcut2 - precut2) - len(f024_10_insert_insts_thor_pre)
diff3 = (postcut3 - precut3) - len(f024_10_insert_insts_thor_post)

f024_10_insts = f024_10_insts[:precut1] + f024_10_insert_insts + f024_10_insts[postcut1:precut2] + f024_10_insert_insts_thor_pre + f024_10_insts[postcut2:precut3] + f024_10_insert_insts_thor_post + f024_10_insts[postcut3:]
#TODO: Put the Orthrus model and collision
#TODO: Shorten pre and post-Thor.

for l in f024_10_labels:
    if l.label_offset > precut1:
        if l.label_offset < postcut1:
            l.label_offset=1
        else:
            if l.label_offset > precut2:
                if l.label_offset < postcut2:
                    l.label_offset = 1
                else:
                    if l.label_offset > precut3:
                        if l.label_offset < postcut3:
                            l.label_offset = 1
                        else:
                            l.label_offset-=diff3
                    l.label_offset-=diff2
            l.label_offset-=diff1
        if l.label_offset < 0:
            l.label_offset = 1
            #TODO: Do better than just move the labels

f024_obj.changeProcByIndex(f024_10_insts, f024_10_labels, f024_10_room)

f024_lb = push_bf_into_lb(f024_obj, 'f024')
assembler.bytesToFile(f024_obj.toBytes(),"piped_scripts/f024.bf")
#outfile = open("piped_scripts/f024.bfasm",'w')
#outfile.write(f024_obj.exportASM())
#outfile.close()
dds3.add_new_file(custom_vals.LB0_PATH['f024'], f024_lb)
dds3.add_new_file(custom_vals.LB0_PATH['f024b'], f024_lb) #for some reason there's regular, b and c
dds3.add_new_file(custom_vals.LB0_PATH['f024c'], f024_lb)

#Cutscene removal in East Nihilo f020
#Shorten Koppa & Incubus encounter
#Fix visual puzzle bug.
#Shorten Berith cutscene - Add text box for Berith reward. (0xf4 in f020.wap)
#How to do Kaiwans??? - Automatically have all switches already hit?
#Shorten spiral staircase down cutscene
#Shorten Ose
#018 is 1st block maze
#019 is 2nd block maze
#020 is 3rd block maze with kaiwans

#001_start, 002_start, 014_start - cut these completely. They turn on the 0x4e0 flag for initializing the block puzzles. 001 works (which is vanilla behavior) but has a cutscene associated with it. 002 and 014 also set the flag but don't do the stuff needed. The stuff done with the 4e0 flag also appears in 018 so we'll just use that code (it'd be ideal to insert it there, but it's already there).
f020_obj = get_script_obj_by_name(dds3, 'f020')
f020_01_room = f020_obj.getProcIndexByLabel("001_start")
f020_01_insts = [
    inst("PROC",f020_01_room),
    inst("END")
]
f020_02_room = f020_obj.getProcIndexByLabel("002_start")
f020_02_insts = [
    inst("PROC",f020_02_room),
    inst("END")
]
f020_14_room = f020_obj.getProcIndexByLabel("014_start")
f020_14_insts = [
    inst("PROC",f020_14_room),
    inst("END")
]
no_labels = []
f020_obj.changeProcByIndex(f020_01_insts, no_labels, f020_01_room)
f020_obj.changeProcByIndex(f020_02_insts, no_labels, f020_02_room)
f020_obj.changeProcByIndex(f020_14_insts, no_labels, f020_14_room)

#008_start - koppa / incubus. cut 47 - 179
f020_08_room = f020_obj.getProcIndexByLabel("008_start")
f020_08_insts, f020_08_labels = f020_obj.getProcInstructionsLabelsByIndex(f020_08_room)
precut = 48
postcut = 179
diff = postcut-precut

#turn on 4eb, submerge the floor, display message saying the kilas were inserted
#kilas: 3d2, 3d3, 3d4, 3d5
#inserted kilas: 4ea, 4e7, 4e8, 4e9
#start poplix with 0x58
f020_08_auto_kila_label_index = len(f020_08_labels)
f020_08_insert_insts_autokilacheck = [
    #if (4e7 or 3d2) and (4ea or 3d3) and (4e8 or 3d4) and (4e9 or 3d5):
    inst("PUSHIS",0x4e7), #Kila 1 inserted or in inventory
    inst("COMM",7),
    inst("PUSHREG"),
    inst("POPLIX",0x58),
    inst("PUSHIS",0x3d2),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHLIX",0x58),
    inst("OR"),
    inst("POPLIX",0x60),

    inst("PUSHIS",0x4ea), #Kila 2 inserted or in inventory
    inst("COMM",7),
    inst("PUSHREG"),
    inst("POPLIX",0x5a),
    inst("PUSHIS",0x3d3),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHLIX",0x5a),
    inst("OR"),
    inst("POPLIX",0x61),

    inst("PUSHIS",0x4e8), #Kila 3 inserted or in inventory
    inst("COMM",7),
    inst("PUSHREG"),
    inst("POPLIX",0x5c),
    inst("PUSHIS",0x3d4),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHLIX",0x5c),
    inst("OR"),
    inst("POPLIX",0x62),

    inst("PUSHIS",0x4e9), #Kila 4 inserted or in inventory
    inst("COMM",7),
    inst("PUSHREG"),
    inst("POPLIX",0x5e),
    inst("PUSHIS",0x3d5),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHLIX",0x5e),
    inst("OR"),
    inst("POPLIX",0x63),

    inst("PUSHIS",0x4eb), #Haven't completed insertion yet
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("EQ"),
    inst("POPLIX",0x64),
    
    inst("PUSHIS",0x4e3), #4e3 set and 6d9 unset. For Koppa / Incubus. (Note: Possibly doesn't work, but doesn't seem to harm things either way. It's also a super edge-case scenario for randomizing kilas in with other stuff.)
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x6d9),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("EQ"),
    inst("AND"),
    inst("PUSHIS",0),
    inst("EQ"),
    inst("POPLIX",0x65),

    #58 := 4e7, 59 := 3d2, 5a := 4ea, 5b := 3d3, 5c := 4e8, 5d := 3d4, 5e := 4e9, 5f := 3d5
    inst("PUSHLIX",0x60),
    inst("PUSHLIX",0x61),
    inst("AND"),
    inst("PUSHLIX",0x62),
    inst("AND"),
    inst("PUSHLIX",0x63),
    inst("AND"),
    inst("PUSHLIX",0x64),
    inst("AND"),
    inst("PUSHLIX",0x65),
    inst("AND"),
    inst("PUSHIS",0),
    inst("EQ"),
    inst("IF",f020_08_auto_kila_label_index)
]
for l in f020_08_labels:
    if l.label_offset > precut:
        l.label_offset-=diff
        if l.label_offset < 0:
            l.label_offset = 1
    l.label_offset += len(f020_08_insert_insts_autokilacheck)
f020_08_auto_kila_label_offset = len(f020_08_insts) + len(f020_08_insert_insts_autokilacheck) - diff
f020_08_labels.append(assembler.label("AUTO_INSERT_KILA",f020_08_auto_kila_label_offset))
auto_kila_text = f020_obj.appendMessage("Kilas automatically inserted.", "AUTO_KILA")
f020_08_insert_insts_autokila_do = [
    inst("END"),#My math is off by one so instead of making it correct I'm adding what's supposed to be the instruction before to here to make it work. :)
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",auto_kila_text),
    inst("COMM",0),
    inst("COMM",2),#first display a the message

    inst("PUSHIS",0), #Mostly copied code. It works but I don't even know what half of this does.
    inst("PUSHSTR",1457), #path_hoji_01
    inst("COMM",0x94), 
    inst("PUSHREG"),
    inst("PUSHSTR",1443), #atari_hoji_01
    inst("COMM",0x94),
    inst("PUSHREG"),
    inst("COMM",0x6b),
    inst("PUSHSTR",1470), #atari_hoji_02
    inst("PUSHIS",0),
    inst("PUSHIS",0),
    inst("COMM",0x107),
    inst("PUSHIS",0),
    inst("PUSHSTR",1484), #md_hoji_03
    inst("PUSHIS",0),
    inst("PUSHIS",0),
    inst("COMM",0x104),
    inst("PUSHIS",0x64),
    inst("COMM",0x215),
    inst("PUSHIS",1),
    inst("PUSHSTR",1495), #md_hoji_04
    inst("PUSHIS",0),
    inst("PUSHIS",0),
    inst("COMM",0x103),
    inst("PUSHIS",1),
    inst("PUSHIS",8),
    inst("PUSHIS",0),
    inst("COMM",0x112),
    inst("PUSHIS",3),
    inst("PUSHIS",8),
    inst("PUSHIS",0),
    inst("COMM",0x111),
    inst("PUSHIS",0x4eb),
    inst("COMM",8),
    
    inst("COMM",0x61),
    inst("END")
]

f020_08_insts = [f020_08_insts[0]] + f020_08_insert_insts_autokilacheck + f020_08_insts[1:precut] + f020_08_insts[postcut:-1] + f020_08_insert_insts_autokila_do
#TODO: make sure 4e0 is NOT set in e506, or replace it altogether.
f020_obj.changeProcByIndex(f020_08_insts, f020_08_labels, f020_08_room)
#Cut waits on switches. These numbers are the index of the pushis instruction with the next one being the comm e (wait) instruction. 
f020_18_01_waits = [47,58,67,76,146,215,220, 234, 246]
f020_18_02_waits = [47,58,64,69,78,135,191,196,210,222]
f020_19_01_waits = [47,58,67,76,130,183,188,202,214]
f020_19_02_waits = [47,58,67,76,121,165,170,184,196]
f020_19_03_waits = [47,58,67,76,130,183,188,202,214]
#20 room kaiwan flags are: 4f4,4f5,4f6
#28 room kaiwan flags are: 6c5,6c6,6c7
f020_20_01_waits = [24,50,59,79,98,124,140,146,155,225,243,257,262,279] 
f020_20_02_waits = [24,50,59,79,98,124,140,146,155,225,243,257,262,279]
f020_20_03_waits = [24,50,59,79,98,129,145,156,165,210,228,242,247,264]
f020_20_04_waits = [24,50,59,79,98,124,140,146,155,216,234,248,253,270]
f020_20_05_waits = [61,72,81,90,164,237,242,256,268]
f020_20_06_waits = [61,72,81,90,139,187,192,206,218]
f020_20_07_waits = [61,72,81,90,155,219,224,238,250]
f020_proc_waits = [("018_01eve_01",f020_18_01_waits), ("018_01eve_02",f020_18_02_waits), ("019_01eve_01",f020_19_01_waits), ("019_01eve_02",f020_19_02_waits), ("019_01eve_03",f020_19_03_waits), ("020_01eve_01",f020_20_01_waits), ("020_01eve_02",f020_20_02_waits), ("020_01eve_03",f020_20_03_waits), ("020_01eve_04",f020_20_04_waits), ("020_01eve_05",f020_20_05_waits), ("020_01eve_06",f020_20_06_waits), ("020_01eve_07",f020_20_07_waits)]
for p_name, p_waits in f020_proc_waits:
    p_proc = f020_obj.getProcIndexByLabel(p_name)
    p_insts, p_labels = f020_obj.getProcInstructionsLabelsByIndex(p_proc)
    new_insts = []
    curr_cut = 0
    for p_wait in p_waits:
        new_insts.extend(p_insts[curr_cut:p_wait])
        curr_cut = p_wait+2 #2 because a wait is 2 instructions
        for label in p_labels:
            if label.label_offset > len(new_insts):
                label.label_offset-=2
    new_insts.extend(p_insts[curr_cut:])
    f020_obj.changeProcByIndex(new_insts,p_labels,p_proc)

#Shorten Ose.
#Door event is 013_01eve_01
#Cut out 50-58 (inclusive both)
#Ose ID is 117
precut = 50
postcut = 59
diff = postcut - precut
f020_13_proc = f020_obj.getProcIndexByLabel("013_01eve_01")
f020_13_insts, f020_13_labels = f020_obj.getProcInstructionsLabelsByIndex(f020_13_proc)
f020_13_insert_insts = [
    inst("PUSHIS",0x56c),#I don't know what these flags do, but they are set here.
    inst("COMM",8),
    inst("PUSHIS",0x56d),
    inst("COMM",8),
    inst("PUSHIS",0x27a),
    inst("PUSHIS",0x14),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",117),
    inst("COMM",0x67) #Fight Ose
]
#Callback: f020.wap at 0x7fc
for l in f020_13_labels:
    if l.label_offset > precut:
        l.label_offset-=diff
        l.label_offset+=len(f020_13_insert_insts)
f020_13_insts = f020_13_insts[:precut] + f020_13_insert_insts + f020_13_insts[postcut:]
f020_obj.changeProcByIndex(f020_13_insts,f020_13_labels,f020_13_proc)

f020_lb = push_bf_into_lb(f020_obj, 'f020')
dds3.add_new_file(custom_vals.LB0_PATH['f020'], f020_lb)

f003_obj = get_script_obj_by_name(dds3, 'f003')
f003_proclen = len(f003_obj.p_lbls().labels)
f003_ose_callback_message = f003_obj.appendMessage("Ose reward placeholder","OSE_REWARD")
f003_ose_callback_proc_str = "OSE_CB"
f003_ose_callback_insts = [
    inst("PROC",f003_proclen),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f003_ose_callback_message),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END"),
]
f003_obj.appendProc(f003_ose_callback_insts,[],f003_ose_callback_proc_str)
f003_lb = push_bf_into_lb(f003_obj, 'f003')
dds3.add_new_file(custom_vals.LB0_PATH['f003'], f003_lb)
insert_callback('f020', 0x7fc, f003_ose_callback_proc_str)
#The callback is in f020, but the proc is in f003 (outside Ginza).
#interesting note: 001_01eve_08 happens going from Rainbow Bridge to Shiba, 001_01eve_07 happens going from Shiba to Rainbow Bridge. Probably responsible for changing encounter tables.


#kilas: 3d2, 3d3, 3d4, 3d5
#inserted kilas: 4ea, 4e7, 4e8, 4e9
#probably just want to do path_hoji_01 and other stuff.
#4e7 - 3d2, 4ea - 3d3, 4e8 - 3d4, 4e9 - 3d5
#best way to auto-insert kilas is to have the respective flags also set.
#change 008_start to include a fast version of descending the floor to reveal the spiral down to ose. It will only happen if 4e7, 4ea, 4e8 and 4e9 are set (kila insertion flags).
#Kaiwan flags: 0x700, 0x6c5, 0x6c6, 0x6c7
#013_01eve_01 is event that calls ose, which is e634.
#e634:
#0x16, 0x56c, 0x56d on - 0x4e1 off. 0x29 also on, but is only used here.

#Cutscene removal for Hell Biker f004
f004_obj = get_script_obj_by_name(dds3, 'f004')
f004_biker_event = f004_obj.getProcIndexByLabel("001_01eve_03")
f004_biker_insts = [
    inst("PROC",f004_biker_event),
    inst("PUSHIS",0),
    inst("PUSHIS",0x754),#Didn't already run away.
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x10a),#Didn't already fight.
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("IF",0),#End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",5), #Do you want to stay here?
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",6), #Yes/no
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("COMM",2),
    inst("IF",1),
    inst("PUSHIS",0x10a), #turn on fought flag.
    inst("COMM",8),
    inst("PUSHIS",0x922), #turn on ???
    inst("COMM",8),
    inst("PUSHIS",0x3e8), #give candelabra
    inst("COMM",8),
    inst("PUSHIS",0x2e5),
    inst("PUSHIS",4),
    inst("PUSHIS",1),
    inst("COMM",0x97), #call next
    inst("PUSHIS",1029),
    inst("COMM",0x67), #fight biker
    inst("END"),
    inst("PUSHIS",0x754),
    inst("COMM",0x8),
    inst("COMM",0x61),
    inst("END")
]
f004_biker_labels = [
    assembler.label("BIKER_RAN",40),
    assembler.label("BIKER_FOUGHT",37)
]
f004_obj.changeProcByIndex(f004_biker_insts,f004_biker_labels,f004_biker_event)
f004_biker_callback_proc_str = "HBIKER_CB"
f004_biker_callback_msg = f004_obj.appendMessage("Hell Biker reward placeholder","HBIKER_REWARD")
f004_biker_callback_insts = [
    inst("PROC",len(f004_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f004_biker_callback_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f004_obj.appendProc(f004_biker_callback_insts,[],f004_biker_callback_proc_str)
insert_callback('f004', 0x540, f004_biker_callback_proc_str)
f004_lb = push_bf_into_lb(f004_obj, 'f004')
dds3.add_new_file(custom_vals.LB0_PATH['f004'], f004_lb)

#Cutscene removal in Kabukicho Prison f025
#Shorten forced Naga
#Shorten Mizuchi
#First Umugi stone usage flag
#Shorten Black Frost (low priority)
#set 0x583, 0x594
#change mizuchi intro to not set 0x59c. (Might as well also shorten it). It also sets 0x595
#Mizuchi is in 025_start
#0x589 is spoon cutscene.
f025_obj = get_script_obj_by_name(dds3, "f025")
f025_mizuchi_room = f025_obj.getProcIndexByLabel("025_start")
f025_mizuchi_room_insts, f025_mizuchi_room_labels = f025_obj.getProcInstructionsLabelsByIndex(f025_mizuchi_room)
#28 - 87 both inclusive. Insert 595 and 863.
#Probably don't need to change labels, but if you don't _443 is OoB, but it doesn't seem like it does anything since it was compiler made.
precut = 28
postcut = 88
f025_mizuchi_room_insert_insts = [
    inst("PUSHIS",0x595),
    inst("COMM",8),
    inst("PUSHIS",0x863),
    inst("COMM",8)
]
f025_mizuchi_room_labels[-1].label_offset = 0 #fixes _443 OoB warning.
f025_mizuchi_room_insts = f025_mizuchi_room_insts[:precut] + f025_mizuchi_room_insert_insts + f025_mizuchi_room_insts[postcut:]
f025_obj.changeProcByIndex(f025_mizuchi_room_insts, f025_mizuchi_room_labels, f025_mizuchi_room)
f025_obj.changeMessageByIndex(assembler.message("Mizuchi reward placeholder","MIZUCHI_REWARD"),0x62)

f025_021_05 = f025_obj.getProcIndexByLabel("021_01eve_05") #I don't think this gets executed, but I was frustrated when I chose the wrong LB file and this also has the Mizuchi text.
f025_021_insts = [
    inst("PROC",f025_021_05),
    inst("END")
]
f025_obj.changeProcByIndex(f025_021_insts,[],f025_021_05)

f025_lb = push_bf_into_lb(f025_obj, 'f025b')
dds3.add_new_file(custom_vals.LB0_PATH['f025b'], f025_lb)
#dds3.add_new_file("/fld/f/f025.bf",BytesIO(bytes(f025_obj.toBytes())))
#f025_bfasm = open("piped_scripts/f025.bfasm",'w')
#f025_bfasm.write(f025_obj.exportASM())
#f025_bfasm.close()

#Cutscene removal in Ikebukuro Tunnel (anything at all?) f026

#Cutscene removal in Asakusa (Hijiri?) f027
#Shorten Pale Rider

#Hijiri is e646_trm and trm_1st
#1st message is: "It's up to you to stop whatever's^ngoing on inside the Obelisk"

#Cutscene removal in Mifunashiro f035
#Shorten and add decision on boss
#6e2,6e3,6e7 - Mifunashiro splash/entrance
#6e5 - Angels asking for opinion

#Cutscene removal in Obelisk f031
#Anything? Could probably do everything with flags.
#000_dh_plus is sisters callback. Any added flags can be put there.
f031_obj = get_script_obj_by_name(dds3,"f031")
f031_obj.changeMessageByIndex(assembler.message("Sisters reward placeholder","SIS_REWARD"),0x2d)
f031_lb = push_bf_into_lb(f031_obj,'f031')
dds3.add_new_file(custom_vals.LB0_PATH['f031'],f031_lb)
#relevant story flags:
#Obelisk Yuko turns on: 0x46, 0x4e, 0x4c3. Turns off 0x48f.
#0x50 is the cutscene with Hijiri after Obelisk.

#Cutscene removal in Amala Network 2 f028
#Shorten Specter 2 and add reward message
#Remove waits on that dude?
#Flag ending cutscene with Isamu as already viewed.

#Cutscene removal in Asakusa Tunnel (anything at all?) f029
#Trumpeter

#Cutscene removal in Yoyogi Park f016
#TODO: Shorten Pixie stay/part scene to not have splash: Low Priority
#Shorten Girimekhala and Sakahagi
#Shorten Mother Harlot

#Cutscene removal in Amala Network 3 f030
#Shorten the one thing - if even because it's tiny. Add reward message

#Cutscene removal in Amala Temple f034
#Remove Intro and Fix Red Temple.
#Shorten pre and post cutscenes. Make sure there are reward messages and a separate message for defeating all 3 that brings down the central pyramid.
#Shorten ToK cutscene.
#Look into for future versions: Have doors to temples locked by particular flags.
#f034_obj = get_script_obj_by_name(iso,'f034')
#In the procedure that sets the flag 6a0 and displays messages 1f - 25
#002_start is outside.
#lots of comm 104 and 103
#002 -> 001 is entrance
#002 -> 012 is red entrance
#002 -> 004 is black entrance
#002 -> 021 is white entrance
f034_obj = get_script_obj_by_name(dds3,"f034")
a_msg = f034_obj.appendMessage("a_lb","A_LB")
b_msg = f034_obj.appendMessage("b_lb","B_LB")
c_msg = f034_obj.appendMessage("c_lb","C_LB")
d_msg = f034_obj.appendMessage("d_lb","D_LB")

bfcheck_insts = [
    inst("PROC",len(f034_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",a_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

proc_index = f034_obj.appendProc(bfcheck_insts,[],"001_start")
f034a_lb = push_bf_into_lb(f034_obj, 'f034')
dds3.add_new_file(custom_vals.LB0_PATH['f034'], f034a_lb)

bfcheck_insts[3] = inst("PUSHIS",b_msg)
f034_obj.changeProcByIndex(bfcheck_insts,[],proc_index)
f034b_lb = push_bf_into_lb(f034_obj, 'f034b')
dds3.add_new_file(custom_vals.LB0_PATH['f034b'], f034b_lb)

bfcheck_insts[3] = inst("PUSHIS",c_msg)
f034_obj.changeProcByIndex(bfcheck_insts,[],proc_index)
f034c_lb = push_bf_into_lb(f034_obj, 'f034c')
dds3.add_new_file(custom_vals.LB0_PATH['f034c'], f034c_lb)

bfcheck_insts[3] = inst("PUSHIS",d_msg)
f034_obj.changeProcByIndex(bfcheck_insts,[],proc_index)
f034d_lb = push_bf_into_lb(f034_obj, 'f034d')
dds3.add_new_file(custom_vals.LB0_PATH['f034d'], f034d_lb)


#Cutscene removal in Yurakucho Tunnel f021
#Shorten Trumpeter

#Cutscene removal in Diet Building f033
#Shorten Mada and Mithra. Add reward messages for all bosses.
#Shorten Samael cutscene, as well as force Samael.

#Cutscene removal in ToK1 f032
#Shorten Ahriman
#If possible, have block puzzle already solved

#Cutscene removal in ToK2 f036
#Shorten Noah

#Cutscene removal in ToK3 f037
#Shorten Thor 2
#Shorten Baal
#Shorten Kagutsuchi and Lucifer
#If possible, have block puzzle after Thor 2 already solved

#Cutscene removal in LoA Lobby f040
#If possible, have each hole with 3 options. Jump, Skip, Cancel
#Don't get put in LoA Lobby after Network 1. Have door always open.

#Cutscene removal in LoA K1 f041
#Candelabra door, tunnel door.

#Cutscene removal in LoA K2 f042
#Candelabra door, tunnel door.
#If possible, have an NPC that is easy to access unlock White Rider

#Cutscene removal in LoA K3 f043
#SHORTEN DANTE
#Candelabra door, tunnel door.

#Cutscene removal in LoA K4 f044
#Shorten Beelzebub. Look into the door unlocking cutscene.
#Candelabra door, tunnel door.

#Cutscene removal in LoA K5 f045
#Intro
#Look into stat requirements.
#Dante hire - have flags set as if you already said no to him. Shorten the yes.
#Metatron

#Hint message testing
''' Commented out, but still works. Mostly here to show how modifying text works.
script_objs = {}
for i,hint_msg in enumerate(custom_vals.hint_msgs):
    script_name = hint_msg[0]
    message_label = hint_msg[1]
    #print "Parsing",message_label
    if script_name not in script_objs:
        s_o = get_script_obj_by_name(iso,script_name)
        script_objs[script_name] = (s_o,len(s_o.toBytes())) #Using a tuple for a size check. Otherwise don't need it.
    index = script_objs[script_name][0].getMessageIndexByLabel(message_label)
    if index != -1:
        new_message_str = "Label: "+message_label+"^nHint index: "+str(i)+"^x2nd text box because ^bwhy not?^p"
        script_objs[script_name][0].changeMessageByIndex(assembler.message(new_message_str,message_label),index)
    else:
        print "ERROR: Message not found. Message label:",message_label
        
for s_name,s_obj in script_objs.iteritems():
    iso.seek(custom_vals.customizer_offsets[s_name])
    print "Packing script:",s_name
    #if s_name == 'f024':
    #    print s_obj.toBytes()
    ba = bytearray(s_obj[0].toBytes())
    
    if len(ba) > custom_vals.stack_sizes + s_obj[1]:
        print "ERROR: New script for",s_name,"is too big"
    else:
        iso.write(ba)
        open("piped_scripts/"+s_name+".bf","wb").write(ba)
iso.close()
'''

#Clean up
print("Writing new ISO")
# export the new DDS3 FS
dds3.export_dds3('rom/DDS3.DDT', 'rom/DDS3.IMG')

# remove the DUMMY file to save disk space and write back the iso
iso.rm_file("DUMMY.DAT;1")
with open('rom/DDS3.DDT', 'rb') as ddt, open('rom/DDS3.IMG', 'rb') as img:
    iso.export_iso('rom/modified_scripts.iso', {'DDS3.DDT;1': ddt, 'DDS3.IMG;1': img})

# remove the temp DDS3 files
#os.remove('rom/old_DDS3.DDT')
#os.remove('rom/old_DDS3.IMG')
#os.remove('rom/DDS3.DDT')
#os.remove('rom/DDS3.IMG')