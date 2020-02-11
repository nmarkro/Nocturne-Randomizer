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
def appendMessage(self, message_label_str, message_str, is_decision = False, name_id = 0):
def appendPUSHSTR(self,str):
def getMessageIndexByLabel(self, label_str):
def getPUSHSTRIndexByStr(self, str):
def getProcIndexByLabel(self, label_str):
def getProcInstructionsLabelsByIndex(self, proc_index):
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

# get the 601 event script and add our hook
e601_obj = get_script_obj_by_name(dds3, 'e601')
e601_insts = [
    inst("PROC",0), 
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

#TODO: Remove SMC splash with a flag.
#TODO: Remove SMC exit cutscene with a flag: Set 0x404

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

#TODO: Shorten Black Rider
f015_lb = push_bf_into_lb(f015_obj, 'f015')
dds3.add_new_file(custom_vals.LB0_PATH['f015'], f015_lb)

#Cutscene removal in Shibuya f017
#SMC Splash removal: 0x440
#Splash removal: Set 0x480
#Chiaki removal or shortening: Removal is set 0x9
#Initial Cathedral cutscene - Remove with 0xA
#Hijiri Shibuya removal: 0xB
#Fountain cutscene removal: 0xa2
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
#Add setting E. PUSHIS 0xe, COMM 8
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
    #Can also put in a reward message
]
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
#open("scripts/f018_test.bfasm",'w').write(f018_obj.exportASM())

dds3.add_new_file(custom_vals.LB0_PATH['f018'], f018_lb)

#75E gets set going into LoA Lobby.
#4C2 gets set leaving LoA Lobby.
#4C0 is Ginza splash

#Cutscene removal in Ginza (Hijiri mostly) f019
#Optional: Shorten Troll (already short)

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

f022_obj.changeProcByIndex(f022_013_e1_insts, f022_013_e1_labels, f022_mata_room)
f022_lb = push_bf_into_lb(f022_obj, 'f022')
dds3.add_new_file(custom_vals.LB0_PATH['f022'], f022_lb)

#Cutscene removal in Ikebukuro f023
#913 set in Ikebukuro. 54b 54c 54d - 540, 549, 56C, 931, 75E
#Shorten Daisoujou

#Cutscene removal in Mantra HQ f024
#Shorten Thor Gauntlet

#Cutscene removal in East Nihilo f020
#Shorten Koppa & Incubus encounter
#Fix visual puzzle bug
#Shorten Berith cutscene - Add text box for Berith reward.
#How to do Kaiwans??? - Automatically have all switches already hit?
#Shorten spiral staircase down cutscene
#Shorten Ose

#Cutscene removal in Kabukicho Prison f025
#Shorten forced Naga
#Shorten Mizuchi
#First Umugi stone usage flag
#Shorten Black Frost (low priority)

#Cutscene removal in Ikebukuro Tunnel (anything at all?) f026

#Cutscene removal in Asakusa (Hijiri mostly) f027
#Shorten Pale Rider

#Cutscene removal in Mifunashiro f035
#Shorten and add decision on boss

#Cutscene removal in Obelisk f031
#Anything? Could probably do everything with flags.

#Cutscene removal in Amala Network 2 f028
#Shorten Specter 2 and add reward message

#Cutscene removal in Asakusa Tunnel (anything at all?) f029

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
#002_start
#lots of comm 104 and 103

#Cutscene removal in Yurakucho Tunnel f021
#Shorten Trumpeter

#Cutscene removal in Diet Building f033
#Shorten Mada and Mithra. Add reward messages for all bosses.
#Shorten Samael cutscene.

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