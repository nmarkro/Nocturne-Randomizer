import nocturne_script_assembler as assembler
import customizer_values as custom_vals
import copy

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
    inst("PUSHIS",0x9), #Shibuya Chiaki cutscene
    inst("COMM",8),
    inst("PUSHIS",0xa), #Initial Cathedral cutscene
    inst("COMM",8),
    inst("PUSHIS",0xb), #Hijiri Shibuya cutscene
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
    #inst("PUSHIS",0x5e0), #Amala Network 2 Splash
    #inst("COMM",8), #Turned off because it's short and has a bunch of necessary code so I'm not going to bother with it yet. If I get to it I'll probably want to keep this off anyway.
    inst("PUSHIS",0x5eb), #Amala Network 2 Cutscene
    inst("COMM",8),
    inst("PUSHIS",0x43), #Amala Network 2 Cutscene 2
    inst("COMM",8),
    inst("PUSHIS",0x5ed), #Amala Network 2 Cutscene 3
    inst("COMM",8),
    inst("PUSHIS",0x600), #Asakusa Tunnel Splash
    inst("COMM",8),
    inst("PUSHIS",0x640), #Obelisk Splash
    inst("COMM",8),
    inst("PUSHIS",0x650), #Sisters Talk at entrance (Consider to keep on, but change their models to the randomized boss)
    inst("COMM",8),
    inst("PUSHIS",0x46), #Obelisk flag 1
    inst("COMM",8),
    inst("PUSHIS",0x4e), #Obelisk flag 2
    inst("COMM",8),
    inst("PUSHIS",0x4c3), #Obelisk flag 3 (possibly Mara flag?)
    inst("COMM",8),
    inst("PUSHIS",0x50), #Hijiri cutscene post Obelisk
    inst("COMM",8),
    inst("PUSHIS",0x464), #Yoyogi Park 1
    inst("COMM",8),
    inst("PUSHIS",0x465), #Yoyogi Park 2
    inst("COMM",8),
    inst("PUSHIS",0x466), #Yoyogi Park 3
    inst("COMM",8),
    inst("PUSHIS",0x467), #Yoyogi Park 4
    inst("COMM",8),
    inst("PUSHIS",0x474), #Yoyogi Park 5
    inst("COMM",8),
    inst("PUSHIS",0x4b),  #Yuko in Yoyogi (no cutscene possible)
    inst("COMM",8),
    inst("PUSHIS",0x3dd), #Yoyogi Key
    inst("COMM",8),
    inst("PUSHIS",0x51), #Amala Temple dropping Hijiri cutscene
    inst("COMM",8),
    inst("PUSHIS",0x500), #Yurakucho Splash
    inst("COMM",8),
    inst("PUSHIS",0x506), #Auto-Shige (Kimon Stone location)
    inst("COMM",8),
    inst("PUSHIS",0x680), #Diet Building Splash
    inst("COMM",8),
    inst("PUSHIS",0x69E), #Diet Building Message 1
    inst("COMM",8),
    inst("PUSHIS",0x688), #Diet Building Message 2
    inst("COMM",8),
    inst("PUSHIS",0x689), #Diet Building Message 3
    inst("COMM",8),
    inst("PUSHIS",0x660), #ToK entrance cutscene
    inst("COMM",8),
    inst("PUSHIS",0x95), #Neutral reason
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
    inst("PUSHIS",0x3c0), #Black Key (testing purposes)
    inst("COMM",8),
    inst("PUSHIS",0x3c1), #White Key (testing purposes)
    inst("COMM",8),
    inst("PUSHIS",0x3c2), #Red Key (testing purposes)
    inst("COMM",8),
    inst("PUSHIS",0x3c3), #Apocalypse Stone (unlocks white rider check - testing purposes)
    inst("COMM",8),
    inst("PUSHIS",0x3c4), #Golden Goblet (unlocks mother harlot check - testing purposes)
    inst("COMM",8),
    inst("PUSHIS",0x3c5), #Eggplant (unlocks mara check - testing purposes)
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

#Black Rider
f015_br_proc = f015_obj.getProcIndexByLabel('014_b_rider')
f015_br_insts, f015_br_labels = f015_obj.getProcInstructionsLabelsByIndex(f015_br_proc)
f015_br_insts[4] = inst("PUSHIS",0x3c3) #Change rider trigger check from 7b8 to key item
f015_br_insts[7] = inst("PUSHIS",0x3c3) #"Remove" story trigger check. (Yuko in Obelisk cutscene)
f015_obj.changeProcByIndex(f015_br_insts, f015_br_labels, f015_br_proc)

f015_14_proc = f015_obj.getProcIndexByLabel('014_01eve_01')
f015_14_insts = [
    inst("PROC",f015_14_proc),
    inst("PUSHIS",0x106), #Red Rider dead
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x3c3), #Key item to enable Riders
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x757), #Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x109), #Didn't already beat him
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("AND"), 
    inst("AND"),
    inst("IF",0), #End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x6f), #"Stay here?"
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x70), #">Yes/no"
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #Not quite end label
    inst("PUSHIS",0x109), #Fought flag
    inst("COMM",8),
    inst("PUSHIS",0x3e2), #Candelabra
    inst("COMM",8),
    inst("PUSHIS",0x920), #Fusion flag
    inst("COMM",8),
    inst("PUSHIS",0x2e9),
    inst("PUSHIS",0xf),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x403),
    inst("COMM",0x67), #Fight Black Rider
    inst("END"),
    inst("PUSHIS",0x757),
    inst("COMM",8),
    inst("COMM",0x61),
    inst("END")
]
f015_14_labels = [
    assembler.label("BRIDER_FOUGHT",47),
    assembler.label("BRIDER_RAN",44)
]
f015_obj.changeProcByIndex(f015_14_insts, f015_14_labels, f015_14_proc)

f015_brider_callback_str = "BR_CB"
f015_brider_rwms_index = f015_obj.appendMessage("Black Rider reward placeholder", "BR_REWARD")
f015_br_rwms_insts = [
    inst("PROC",len(f015_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f015_brider_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f015_obj.appendProc(f015_br_rwms_insts, [], f015_brider_callback_str)
insert_callback('f015',0x3b0,f015_brider_callback_str)


f015_lb = push_bf_into_lb(f015_obj, 'f015')
dds3.add_new_file(custom_vals.LB0_PATH['f015'], f015_lb)

#Cutscene removal in Shibuya f017
#TODO: Shorten Mara
f017_obj = get_script_obj_by_name(dds3,'f017')
#001_01eve_01 -> 009_start
#normal bit check line of 001_01eve_01 is 0x483 on line 20. We want it to be a key item instead.
#cut out 24-29 inclusive for FULL check. put in an AND instead
f017_01_proc = f017_obj.getProcIndexByLabel('001_01eve_01')
f017_01_insts, f017_01_labels = f017_obj.getProcInstructionsLabelsByIndex(f017_01_proc)
#f017_01_insts[16] = inst("PUSHIS",0x3c5)
#Fails if: 0x3c5 is not set. Also fails if 0x482 is set.
#I need the negation of that though.
f017_01_insert_insts = [
    inst("PUSHIS",0),
    inst("PUSHIS",0x3c5),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("OR")
]
precut = 19
postcut = 30
diff = postcut - precut
f017_01_insts = f017_01_insts[:precut] + f017_01_insert_insts + f017_01_insts[postcut:]
for l in f017_01_labels:
    if l.label_offset > precut:
        l.label_offset -= diff
        l.label_offset += len(f017_01_insert_insts)
f017_obj.changeProcByIndex(f017_01_insts, f017_01_labels, f017_01_proc)

#009_start also takes care of callback
#check 0x488 to make sure mara wasn't already fought
#cut out 10 - 420 inclusive
#callback text id is 0x19
#can hint about location of item with text id 0x1. "It seems fishy..."
f017_09_proc = f017_obj.getProcIndexByLabel('009_start')
f017_09_insts, f017_09_labels = f017_obj.getProcInstructionsLabelsByIndex(f017_09_proc)
precut = 10
postcut = 421
diff = postcut - precut
f017_09_insts = f017_09_insts[:precut] + f017_09_insts[postcut:]
for l in f017_09_labels:
    if l.label_offset > precut:
        if l.label_offset < postcut:
            l.label_offset=0
        else:
            l.label_offset-=diff
f017_obj.changeProcByIndex(f017_09_insts, f017_09_labels, f017_09_proc)

#001_w_rider for warning.
#bit checks: 5c0, 7b8, 112 unset. Turns off 0x755.
#7b8 is riders flag. We want that as a key item (3c3). 112 is defeating white rider.
#5c0 is a flag that gets set when going into Shibuya. It is also the Asakusa entrance cutscene splash that we've set to be always on. Do we replicate this effect or ignore it? Ignoring it for now.
f017_wr_proc = f017_obj.getProcIndexByLabel("001_w_rider")
f017_wr_insts, f017_wr_labels = f017_obj.getProcInstructionsLabelsByIndex(f017_wr_proc)
f017_wr_insts[4] = inst("PUSHIS",0x3c3)
f017_obj.changeProcByIndex(f017_wr_insts, f017_wr_labels, f017_wr_proc)
#003_01eve_01
#bit checks: 5c0, 7b8, 755 off, 112 off.
#Run away: 755 on.
#003_01eve_02 and 03 is dupe.
f017_03_1_proc = f017_obj.getProcIndexByLabel("003_01eve_01")
f017_03_2_proc = f017_obj.getProcIndexByLabel("003_01eve_02")
f017_03_3_proc = f017_obj.getProcIndexByLabel("003_01eve_03")
f017_03_insts = [ #See Daisoujou proc for more detailed comments on this proc
    inst("PROC",f017_03_1_proc),
    inst("PUSHIS",0x5c0), #"Story trigger" to enable Riders
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x3c3), #Key item to enable Riders
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x755), #Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x112), #Didn't already beat him
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("AND"), 
    inst("AND"),
    inst("IF",0), #End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x35), #"Stay here?"
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x36), #">Yes/no"
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #Not quite end label
    inst("PUSHIS",0x112), #Fought flag
    inst("COMM",8),
    inst("PUSHIS",0x3e4), #Candelabra
    inst("COMM",8),
    inst("PUSHIS",0x91e), #Fusion flag
    inst("COMM",8),
    inst("PUSHIS",0x2e7),
    inst("PUSHIS",0x11),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x401),
    inst("COMM",0x67), #Fight White Rider
    inst("END"),
    inst("PUSHIS",0x755),
    inst("COMM",8),
    inst("COMM",0x61),
    inst("END")
]
f017_03_labels = [
    assembler.label("WRIDER_FOUGHT",47),
    assembler.label("WRIDER_RAN",44)
]

f017_03_2_insts = [
    inst("PROC",f017_03_2_proc),
    inst("CALL",f017_03_1_proc),
    inst("END"),
]
f017_03_3_insts = [
    inst("PROC",f017_03_3_proc),
    inst("CALL",f017_03_1_proc),
    inst("END"),
]
f017_obj.changeProcByIndex(f017_03_insts, f017_03_labels, f017_03_1_proc)
f017_obj.changeProcByIndex(f017_03_2_insts, [], f017_03_2_proc)
f017_obj.changeProcByIndex(f017_03_3_insts, [], f017_03_3_proc)
f017_wr_rwms_index = f017_obj.appendMessage("White Rider reward placeholder","WR_RWMS")
f017_wr_callback_str = "WR_CB"
f017_wr_callback_insts = [
    inst("PROC",len(f017_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f017_wr_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f017_obj.appendProc(f017_wr_callback_insts, [], f017_wr_callback_str)
insert_callback('f017', 0x34c, f017_wr_callback_str)

f017_lb = push_bf_into_lb(f017_obj, 'f017')
dds3.add_new_file(custom_vals.LB0_PATH['f017'], f017_lb)

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
e623_obj = get_script_obj_by_name(dds3, 'e623')
e623_trm_proc = e623_obj.getProcIndexByLabel('e623_trm')
e623_insts, e623_labels = e623_obj.getProcInstructionsLabelsByIndex(e623_trm_proc)
#Turning the cutscene into a noop
e623_insts[84] = inst("PUSHIS",0)
e623_insts[85] = inst("COMM",0xe)
e623_obj.changeProcByIndex(e623_insts, e623_labels, e623_trm_proc)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e623'],BytesIO(bytes(e623_obj.toBytes())))

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
    inst("COMM",1),
    inst("PUSHIS",f019_troll_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
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

f022_rr_proc = f022_obj.getProcIndexByLabel('010_r_rider')
f022_rr_insts, f022_rr_labels = f022_obj.getProcInstructionsLabelsByIndex(f022_rr_proc)
f022_rr_insts[4] = inst("PUSHIS",0x3c3) #Change rider trigger check from 7b8 to key item
f022_obj.changeProcByIndex(f022_rr_insts, f022_rr_labels, f022_rr_proc)

f022_10_proc = f022_obj.getProcIndexByLabel('010_01eve_01')
f022_10_insts = [
    inst("PROC",f022_10_proc),
    inst("PUSHIS",0x112), #White Rider dead
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x3c3), #Key item to enable Riders
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x756), #Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x106), #Didn't already beat him
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("AND"), 
    inst("AND"),
    inst("IF",0), #End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x5a), #"Stay here?"
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x5b), #">Yes/no"
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #Not quite end label
    inst("PUSHIS",0x106), #Fought flag
    inst("COMM",8),
    inst("PUSHIS",0x3e3), #Candelabra
    inst("COMM",8),
    inst("PUSHIS",0x91f), #Fusion flag
    inst("COMM",8),
    inst("PUSHIS",0x2e8),
    inst("PUSHIS",0x16),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x402),
    inst("COMM",0x67), #Fight Red Rider
    inst("END"),
    inst("PUSHIS",0x756),
    inst("COMM",8),
    inst("COMM",0x61),
    inst("END")
]
f022_10_labels = [
    assembler.label("RRIDER_FOUGHT",47),
    assembler.label("RRIDER_RAN",44)
]
f022_obj.changeProcByIndex(f022_10_insts, f022_10_labels, f022_10_proc)

f022_rrider_callback_str = "RR_CB"
f022_rrider_rwms_index = f022_obj.appendMessage("Red Rider reward placeholder", "RR_REWARD")
f022_rr_rwms_insts = [
    inst("PROC",len(f022_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f022_rrider_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f022_obj.appendProc(f022_rr_rwms_insts, [], f022_rrider_callback_str)
insert_callback('f022',0x1bc,f022_rrider_callback_str)

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
#TODO: Change it so you can't fight Ose multiple times.
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
#Move Black Frost to Sakahagi room.
f027_obj = get_script_obj_by_name(dds3,'f027')

#Pale Rider
f027_pr_proc = f027_obj.getProcIndexByLabel('016_p_rider')
f027_pr_insts, f027_pr_labels = f027_obj.getProcInstructionsLabelsByIndex(f027_pr_proc)
f027_pr_insts[12] = inst("PUSHIS",0x3c3) #Change rider trigger check from 7b8 to key item
f027_obj.changeProcByIndex(f027_pr_insts, f027_pr_labels, f027_pr_proc)

f027_16_proc = f027_obj.getProcIndexByLabel('016_01eve_01')
f027_16_insts = [
    inst("PROC",f027_16_proc),
    inst("PUSHIS",0x109), #Black Rider dead
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x3c3), #Key item to enable Riders
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x758), #Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x113), #Didn't already beat him
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("AND"), 
    inst("AND"),
    inst("IF",0), #End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x14), #"Stay here?"
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x15), #">Yes/no"
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #Not quite end label
    inst("PUSHIS",0x113), #Fought flag
    inst("COMM",8),
    inst("PUSHIS",0x3e1), #Candelabra
    inst("COMM",8),
    inst("PUSHIS",0x91d), #Fusion flag
    inst("COMM",8),
    inst("PUSHIS",0x2ea),
    inst("PUSHIS",0x1b),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x400),
    inst("COMM",0x67), #Fight Pale Rider
    inst("END"),
    inst("PUSHIS",0x758),
    inst("COMM",8),
    inst("COMM",0x61),
    inst("END")
]
f027_16_labels = [
    assembler.label("PRIDER_FOUGHT",47),
    assembler.label("PRIDER_RAN",44)
]
f027_obj.changeProcByIndex(f027_16_insts, f027_16_labels, f027_16_proc)

f027_prider_callback_str = "PR_CB"
f027_prider_rwms_index = f027_obj.appendMessage("Pale Rider reward placeholder", "PR_REWARD")
f027_pr_rwms_insts = [
    inst("PROC",len(f027_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f027_prider_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f027_obj.appendProc(f027_pr_rwms_insts, [], f027_prider_callback_str)
insert_callback('f027',0xf4,f027_prider_callback_str)

f027_bfrost_callback_str = "BFROST_CB"
f027_bfrost_rwms_index = f027_obj.appendMessage("Black Frost reward placeholder", "BFROST_REWARD")
f027_bfrost_rwms_insts = [
    inst("PROC",len(f027_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f027_bfrost_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f027_obj.appendProc(f027_bfrost_rwms_insts, [], f027_bfrost_callback_str)
insert_callback('f027',0x1ddc,f027_bfrost_callback_str)

f027_lb = push_bf_into_lb(f027_obj,'f027')
dds3.add_new_file(custom_vals.LB0_PATH['f027'],f027_lb)

#Change e644 to fight Black Frost. Normally it's the Sakahagi cutscene in Asakusa, but we're repurposing it so no two bosses are in the same location.
#Flag is 2e
#Callback is 0x1ddc in f027
e644_obj = get_script_obj_by_name(dds3,'e644')
e644_insts = [
    inst("PROC",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x2e),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0),
    inst("PUSHIS",0x2e),
    inst("COMM",8),
    inst("PUSHIS",644),#Should work???
    inst("PUSHIS",0x2ca),#Black Frost battle ID
    inst("COMM",0x28),
    inst("END"),
    inst("PUSHIS",644),
    inst("PUSHIS",27),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("COMM",0x23),
    inst("COMM",0x2e),
    inst("END")
]
e644_labels = [
    assembler.label("BFROST_FOUGHT",13)
]
e644_obj.changeProcByIndex(e644_insts, e644_labels, 0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e644'],BytesIO(bytes(e644_obj.toBytes())))

#Cutscene removal in Mifunashiro f035
#Shorten and add decision on boss
#6e2,6e3,6e7 - Mifunashiro splash/entrance
#6e5 - Angels asking for opinion
#009_01eve_01 is platform that takes you to boss decision.
#156-157 inclusive is removed. Put in setting 0x56 then calling Futomimi fight. Return is already included.
#Insert callback for reward message. 0xf68
#Fight Futomimi always.
f035_obj = get_script_obj_by_name(dds3,'f035')
f035_futomimi_insert_insts = [
    inst("PUSHIS",0x56),
    inst("COMM",8),
    inst("PUSHIS",0x2a2), #0x2a1 is archangels
    inst("COMM",0x67)
]
f035_09_index = f035_obj.getProcIndexByLabel('009_01eve_01')
f035_09_insts, f035_09_labels = f035_obj.getProcInstructionsLabelsByIndex(f035_09_index)
precut = 156
postcut = 158
diff = postcut-precut
for l in f035_09_labels:
    if l.label_offset > precut:
        l.label_offset -= diff
        l.label_offset += len(f035_futomimi_insert_insts)
f035_09_insts = f035_09_insts[:precut] + f035_futomimi_insert_insts + f035_09_insts[postcut:]
f035_obj.changeProcByIndex(f035_09_insts, f035_09_labels, f035_09_index)
f035_futomimi_rwms_index = f035_obj.appendMessage("Futomimi reward placeholder","FUTO_RWMS")
f035_futomimi_callback_insts = [
    inst("PROC",len(f035_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f035_futomimi_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f035_futomimi_callback_str = "FUTO_CB"
f035_obj.appendProc(f035_futomimi_callback_insts,[],f035_futomimi_callback_str)
f035_lb = push_bf_into_lb(f035_obj, 'f035')
dds3.add_new_file(custom_vals.LB0_PATH['f035'], f035_lb)
insert_callback('f035',0xf68,f035_futomimi_callback_str)

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
#0x5eb
#001_start has code for 
#011_01eve_02 is specter 2. remove 7 - 162 inclusive
f028_obj = get_script_obj_by_name(dds3,"f028")
f028_011_index = f028_obj.getProcIndexByLabel("011_01eve_02")
f028_011_insts, f028_011_labels = f028_obj.getProcInstructionsLabelsByIndex(f028_011_index)
precut = 7
postcut = 163
diff = postcut - precut
#nothing to insert.
f028_011_insts = f028_011_insts[:precut] + f028_011_insts[postcut:]
#only one label.
f028_011_labels[0].label_offset -= diff
f028_obj.changeProcByIndex(f028_011_insts, f028_011_labels, f028_011_index)
f028_specter2_rwms_index = f028_obj.appendMessage("Specter 2 placeholder","SPEC2_RWMS")
f028_specter2_callback_insts = [
    inst("PROC",len(f028_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f028_specter2_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    #inst("PUSHIS",0x44), #Needs to be set at some time so why not now? Flag for Hijiri to not take you back into Network 2.
    #inst("COMM",8),
    inst("END")
]
f028_specter2_callback_str = "SPEC2_CB"
f028_obj.appendProc(f028_specter2_callback_insts,[],f028_specter2_callback_str)
f028_lb = push_bf_into_lb(f028_obj, 'f028')
dds3.add_new_file(custom_vals.LB0_PATH['f028'], f028_lb)
insert_callback('f028',0xf4,f028_specter2_callback_str)
#set 0x43, 0x5ed
#0x5f9 gets set on finish of network 2.

#e652 - e652_trm
#0-30 init
#{
#   Transfer to Network 2? 32-64
#   {
#       Go into Network 2. Set bit 0x41. 66-90
#       return
#   }{
#       Say no. 92-122
#   }{
#       blah blah blah 123-152
#   }
#}
#155-156 end

#Write as:
#0-30 init
#   Check 0x5f9.
#   Unset {
#       Transfer to Network 2?
#       Yes {
#           Go into Network 2. Set bit 0x41. Return.
#       }
#   }Set{
#       Check 0x4a.
#       Unset {
#           "Come back after you've completed yoyogi park."
#       } Set {
#           Transfer to Network 3?
#           Yes {
#               Go into Network 3. Set 0x53 to make Hikawa in Asakusa disappear.
#           }
#       }
#   }
#   Go to TERMINAL

e652_obj = get_script_obj_by_name(dds3,'e652')
e652_proc = e652_obj.getProcIndexByLabel('e652_trm')
e652_insts, e652_labels = e652_obj.getProcInstructionsLabelsByIndex(e652_proc)
e652_terminal_label_index = 0 #relative index for TERMINAL label. Absolute is 13
e652_kept_insts = e652_insts[:52] #0-31 is terminal code. 32-51 has camera to hijiri code.
e652_network2_msg = e652_obj.appendMessage("Would you like me to take you to Amala Network 2?","NETWORK2_MSG")
e652_network3_msg = e652_obj.appendMessage("Would you like me to take you to Amala Network 3, leading to Amala Temple?","NETWORK3_MSG")
e652_locked_msg = e652_obj.appendMessage("Come back after you've completed Yoyogi Park and I will take you to Amala Network 3.","LOCKED_MSG")
e652_gl_msg = e652_obj.appendMessage("Good luck!","GL_MSG")
e652_insert_insts = [
    inst("PUSHIS",0),
    inst("PUSHIS",0x5f9), #Check if gone in Network 2
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #0x5f9 check (Network 2) scope
    inst("COMM",1),
    inst("PUSHIS",e652_network2_msg),
    inst("COMM",0),
    inst("PUSHIS",7), #Sure/No thanks
    inst("COMM",3), #MSG_DEC
    inst("PUSHREG"),
    inst("POPIX"),
    inst("COMM",2),
    inst("PUSHIS",0),
    inst("PUSHIX"),
    inst("EQ"),
    inst("IF",3), #Go to Network 2 scope. If not return to terminal.
    inst("COMM",1),
    inst("PUSHIS",e652_gl_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("PUSHIS",0x41), #turn on flag 0x41. Not sure why but eh.
    inst("COMM",8),
    inst("COMM",0x45),
    inst("COMM",0x23),
    inst("PUSHIS",0x28c),
    inst("PUSHIS",0x1c),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("END"), #End go to Network 2 scope
    inst("PUSHIS",0),#Start Network 3 locked check scope.
    inst("PUSHIS",0x4a), 
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",2), #Network 3 Locked scope
    inst("COMM",1),
    inst("PUSHIS",e652_locked_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("GOTO",0),
    inst("COMM",1), #Network 3 Unlocked scope
    inst("PUSHIS",e652_network3_msg),
    inst("COMM",0),
    inst("PUSHIS",7),
    inst("COMM",3),
    inst("PUSHREG"),
    inst("POPIX"),
    inst("COMM",2),
    inst("PUSHIS",0),
    inst("PUSHIX"),
    inst("EQ"),
    inst("IF",3),
    inst("COMM",1),
    inst("PUSHIS",e652_gl_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("PUSHIS",0x53), #Change Asakusa terminal to not have Hijiri.
    inst("COMM",8),
    inst("COMM",0x45),
    inst("COMM",0x23),
    inst("PUSHIS",0x296),
    inst("PUSHIS",0x1e),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("END"),
    inst("PUSHIS",8),#Returning to beginning code. Resetting camera.
    inst("PUSHIX"),
    inst("COMM",0x4b),
    inst("PUSHIS",0),
    inst("PUSHIS",0xa),
    inst("PUSHIS",0),
    inst("PUSHIS",0xb),
    inst("PUSHIX"),
    inst("COMM",0x73),
    inst("PUSHSTR",344),
    inst("COMM",0x94),
    inst("PUSHREG"),
    inst("COMM",0x12),
    inst("PUSHSTR",356),
    inst("COMM",0x94),
    inst("PUSHREG"),
    inst("PUSHSTR",350),
    inst("COMM",0x94),
    inst("PUSHREG"),
    inst("COMM",0x13),
    inst("GOTO",0),
    inst("END") #end label location. Also here to not trip off a warning in the assembler.
]
e652_kept_insts[31] = inst("IF",4) #END label for the kept portion.
e652_labels = [
    e652_labels[e652_terminal_label_index], #TERMINAL label.
    assembler.label("NETWORK2_SCOPE",len(e652_kept_insts) + 31),
    assembler.label("NETWORK3_SCOPE",len(e652_kept_insts) + 42),
    assembler.label("NETWORK3_SCOPE",len(e652_kept_insts) + 67),
    assembler.label("END_LABEL",len(e652_kept_insts) + 88)
]
e652_obj.changeProcByIndex(e652_kept_insts + e652_insert_insts, e652_labels, e652_proc)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e652'],BytesIO(bytes(e652_obj.toBytes())))
#file = open("piped_scripts/e652.bfasm",'w')
#file.write(e652_obj.exportASM())
#file.close()

#Cutscene removal in Asakusa Tunnel (anything at all?) f029

#Cutscene removal in Yoyogi Park f016
#TODO: Shorten Pixie stay/part scene to not have splash: Low Priority
#Shorten Girimekhala and Sakahagi
#Shorten Mother Harlot
#Flags for each short cutscene in the area
#set: 0x464, 0x465, 0x466, 0x467, 0x474
#set: 0x4b. 0x3dd is yoyogi key.
#0x4a is gary fight. e658. Door is 01d_10
#wap entry of 0x1b94 in 
#e701_main is Yuko differentiator in Yoyogi park. 
e658_obj = get_script_obj_by_name(dds3,"e658")
e658_insts = [
    inst("PROC",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x4a),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0),
    inst("PUSHIS",0x4a),
    inst("COMM",8),
    inst("PUSHIS",658),
    inst("PUSHIS",0x133),
    inst("COMM",0x28),#CALL_EVENT_BATTLE
    inst("END"),
    inst("PUSHIS",658),
    inst("PUSHIS",16),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("COMM",0x23),
    inst("COMM",0x2e),
    inst("END")
]
e658_labels = [
    assembler.label("GARY_FOUGHT",13)
]
e658_obj.changeProcByIndex(e658_insts,e658_labels,0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e658'],BytesIO(bytes(e658_obj.toBytes())))

f016_obj = get_script_obj_by_name(dds3,"f016")
f016_gary_reward_msg = f016_obj.appendMessage("Gary reward placeholder","GARY_MSG")
f016_gary_reward_insts = [
    inst("PROC",len(f016_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f016_gary_reward_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f016_gary_reward_proc_str = "GARY_CB"
f016_obj.appendProc(f016_gary_reward_insts, [], f016_gary_reward_proc_str)

f016_mh_proc = f016_obj.getProcIndexByLabel('019_mother')
f016_mh_insts, f016_mh_labels = f016_obj.getProcInstructionsLabelsByIndex(f016_mh_proc)
f016_mh_insts[1] = inst("PUSHIS",0x3c4) #Change Harlot trigger from a story trigger to a key item
f016_obj.changeProcByIndex(f016_mh_insts, f016_mh_labels, f016_mh_proc)

f016_19_proc = f016_obj.getProcIndexByLabel('019_01eve_01')

f016_19_insts = [
    inst("PROC",f016_19_proc),
    inst("PUSHIS",0x3c4), #Key item to enable Harlot
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x759), #Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x116), #Didn't already beat her
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("AND"),
    inst("IF",0), #End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x4b), #"Stay here?"
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x4c), #">Yes/no"
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",1), #Not quite end label
    inst("PUSHIS",0x116), #Fought flag
    inst("COMM",8),
    inst("PUSHIS",0x3e6), #Candelabra
    inst("COMM",8),
    inst("PUSHIS",0x924), #Fusion flag
    inst("COMM",8),
    inst("PUSHIS",0x2eb),
    inst("PUSHIS",0x10),
    inst("PUSHIS",1),
    inst("COMM",0x97), #Call next
    inst("PUSHIS",0x407),
    inst("COMM",0x67), #Fight Harlot
    inst("END"),
    inst("PUSHIS",0x759),
    inst("COMM",8),
    inst("COMM",0x61),
    inst("END")
]
f016_19_labels = [
    assembler.label("HARLOT_FOUGHT",43),
    assembler.label("HARLOT_RAN",40)
]
f016_obj.changeProcByIndex(f016_19_insts, f016_19_labels, f016_19_proc)

f016_harlot_callback_str = "HARLOT_CB"
f016_harlot_rwms_index = f016_obj.appendMessage("Harlot reward placeholder", "HARLOT_REWARD")
f016_harlot_rwms_insts = [
    inst("PROC",len(f016_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f016_harlot_rwms_index),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f016_obj.appendProc(f016_harlot_rwms_insts, [], f016_harlot_callback_str)
insert_callback('f016',0xf4,f016_harlot_callback_str)

f016_lb = push_bf_into_lb(f016_obj,'f016')
dds3.add_new_file(custom_vals.LB0_PATH['f016'],f016_lb)
insert_callback('f016', 0x1b84, f016_gary_reward_proc_str)
#file = open('piped_scripts/f016.bfasm','w')
#file.write(f016_obj.exportASM())
#file.close()

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
#Bit checks in 001_start:
#6ac, 6ae, 6ad, 6a0, 63. 6a7 off.
#possibly cut 202-298 inclusive
f034_02_proc = f034_obj.getProcIndexByLabel("002_start")
f034_02_insts, f034_02_labels = f034_obj.getProcInstructionsLabelsByIndex(f034_02_proc)
precut = 151
postcut = 299
diff = postcut - precut
f034_02_insert_insts = [
    inst("PUSHIS",0x4a0),
    inst("COMM",8)
]
f034_02_insts = f034_02_insts[:precut] + f034_02_insert_insts + f034_02_insts[postcut:]
for l in f034_02_labels:
    if l.label_offset > precut:
        if l.label_offset < postcut:
            l.label_offset = 0
        else:
            l.label_offset -= diff
            l.label_offset += len(f034_02_insert_insts)
f034_obj.changeProcByIndex(f034_02_insts, f034_02_labels, f034_02_proc)

#Plan: Completely gut the 002_01 events. The underground magatsuhi flows into the center won't show, but who gives a shit.
#6aX:
#   9 - Aciel spawn
#   a - Skadi spawn
#   b - Albion spawn
#   c - Aciel callback (defeat confirmed)
#   d - Skadi callback (defeat confirmed)
#   e - Albion callback (defeat confirmed)
#   f - Gets set after all 3 defeats are confirmed (cde), then enables 003_start in the center instead of 002_start.

#Temp plan. Gut out 002_01 events and see what happens.
f034_02_1_proc = f034_obj.getProcIndexByLabel('002_01eve_01')
f034_02_2_proc = f034_obj.getProcIndexByLabel('002_01eve_02')
f034_02_3_proc = f034_obj.getProcIndexByLabel('002_01eve_03')
f034_obj.changeProcByIndex([inst("PROC",f034_02_1_proc),inst("END")], [], f034_02_1_proc)
f034_obj.changeProcByIndex([inst("PROC",f034_02_2_proc),inst("END")], [], f034_02_2_proc)
f034_obj.changeProcByIndex([inst("PROC",f034_02_3_proc),inst("END")], [], f034_02_3_proc)

f034_wap_file_path = custom_vals.WAP_PATH['f034']
f034_wap_file = bytes(dds3.get_file_from_path(f034_wap_file_path).read())
wap_empty_entry = bytes([0]*0x38) + bytes(assembler.ctobb("01pos_01",8)) + bytes([0]*6) + bytes(assembler.ctobb("01cam_01",8)) + bytes([0,0,0,0,1,1]) + bytes([0]*0x10)

#"Deleting" 2nd, 4th and 6th wap entries.
f034_wap_file = f034_wap_file[:0xa0 + 0x64] + wap_empty_entry + f034_wap_file[0xa0 + (0x64*2):0xa0 + (0x64*3)] + wap_empty_entry + f034_wap_file[0xa0 + (0x64*4):0xa0 + (0x64*5)] + wap_empty_entry + f034_wap_file[0xa0 + (0x64*6):]
#Thankfully there aren't any callbacks that need to be inserted.

dds3.add_new_file(f034_wap_file_path,BytesIO(f034_wap_file)) #Write in normal WAP spot, but this isn't what we 'really' need.
#What we really need to do is to write the WAP into all 4 LB files.
f034a_lb_data = dds3.get_file_from_path(custom_vals.LB0_PATH['f034'])
f034b_lb_data = dds3.get_file_from_path(custom_vals.LB0_PATH['f034b'])
f034c_lb_data = dds3.get_file_from_path(custom_vals.LB0_PATH['f034c'])
f034d_lb_data = dds3.get_file_from_path(custom_vals.LB0_PATH['f034d'])
f034a_lb = LB_FS(f034a_lb_data)
f034b_lb = LB_FS(f034b_lb_data)
f034c_lb = LB_FS(f034c_lb_data)
f034d_lb = LB_FS(f034d_lb_data)
f034a_lb.read_lb()
f034b_lb.read_lb()
f034c_lb.read_lb()
f034d_lb.read_lb()
#f034a_lb = f034a_lb.export_lb({'WAP': BytesIO(f034_wap_file)})
#f034b_lb = f034b_lb.export_lb({'WAP': BytesIO(f034_wap_file)})
#f034c_lb = f034c_lb.export_lb({'WAP': BytesIO(f034_wap_file)})
#f034d_lb = f034d_lb.export_lb({'WAP': BytesIO(f034_wap_file)})
#dds3.add_new_file(custom_vals.LB0_PATH['f034'], f034a_lb)
#dds3.add_new_file(custom_vals.LB0_PATH['f034b'], f034b_lb)
#dds3.add_new_file(custom_vals.LB0_PATH['f034c'], f034c_lb)
#dds3.add_new_file(custom_vals.LB0_PATH['f034d'], f034d_lb)

#6aX:
#   9 - Aciel spawn
#   a - Skadi spawn
#   b - Albion spawn
#   c - Aciel callback (defeat confirmed)
#   d - Skadi callback (defeat confirmed)
#   e - Albion callback (defeat confirmed)
#   f - Gets set after all 3 defeats are confirmed (cde), then enables 

f034_temple_bosses_done_msg = f034_obj.appendMessage("All temple bosses defeated.^nThe central temple is now open.","CENTER_TEMPLE_MSG")

#Albion callback
f034_25_2_proc = f034_obj.getProcIndexByLabel('025_01eve_02')
#Set 6ae, check 6ac and 6ad. If both are set then set 6af
f034_albion_rwms = f034_obj.appendMessage("Albion reward placeholder","ALBION_RWMS") #Could change a message, but this is just easier.
f034_25_2_insts = [
    inst("PROC",f034_25_2_proc),
    inst("PUSHIS",0x6ae),
    inst("COMM",8),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f034_albion_rwms),
    inst("COMM",0),
    inst("PUSHIS",0x6ac),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x6ad),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("AND"),
    inst("IF",0),#Check if other two bosses defeated.
    inst("PUSHIS",f034_temple_bosses_done_msg),
    inst("COMM",0),
    inst("PUSHIS",0x6af),
    inst("COMM",8),
    inst("COMM",2),#Label here. 19
    inst("COMM",0x61),
    inst("END")
]
f034_25_2_labels = [
    assembler.label("ALBION_TO_CENTER",19)
]
f034_obj.changeProcByIndex(f034_25_2_insts, f034_25_2_labels, f034_25_2_proc)

#Skadi callback
#Set 6ad, check 6ac and 6ae. If both are set then set 6af
f034_18_2_proc = f034_obj.getProcIndexByLabel('018_01eve_02')
f034_skadi_rwms = f034_obj.appendMessage("Skadi reward placeholder", "SKADI_RWMS")
f034_18_2_insts = [
    inst("PROC",f034_18_2_proc),
    inst("PUSHIS",0x6ad),
    inst("COMM",8),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f034_skadi_rwms),
    inst("COMM",0),
    inst("PUSHIS",0x6ac),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x6ae),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("AND"),
    inst("IF",0),#Check if other two bosses defeated.
    inst("PUSHIS",f034_temple_bosses_done_msg),
    inst("COMM",0),
    inst("PUSHIS",0x6af),
    inst("COMM",8),
    inst("COMM",2),#Label here. 19
    inst("COMM",0x61),
    inst("END")
]
f034_18_2_labels = [
    assembler.label("SKADI_TO_CENTER",19)
]
f034_obj.changeProcByIndex(f034_18_2_insts, f034_18_2_labels, f034_18_2_proc)

#Aciel callback
f034_10_2_proc = f034_obj.getProcIndexByLabel('010_01eve_02')
#Set 6ac, check 6ae and 6ad. If both are set then set 6af
f034_aciel_rwms = f034_obj.appendMessage("Aciel reward placeholder","ACIEL_RWMS")
f034_10_2_insts = [
    inst("PROC",f034_10_2_proc),
    inst("PUSHIS",0x6ac),
    inst("COMM",8),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f034_aciel_rwms),
    inst("COMM",0),
    inst("PUSHIS",0x6ad),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("PUSHIS",0x6ae),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("AND"),
    inst("IF",0),#Check if other two bosses defeated.
    inst("PUSHIS",f034_temple_bosses_done_msg),
    inst("COMM",0),
    inst("PUSHIS",0x6af),
    inst("COMM",8),
    inst("COMM",2),#Label here. 19
    inst("COMM",0x61),
    inst("END")
]
f034_10_2_labels = [
    assembler.label("ACIEL_TO_CENTER",19)
]
f034_obj.changeProcByIndex(f034_10_2_insts, f034_10_2_labels, f034_10_2_proc)

#Center temple: 1st scene sets 0x864 and 0x52. 0x51 is the check. Keeping 0x51 set is probably safe.
#   2nd scene checks 0x73. We want it to check Pyramidion instead.
f034_03_01_proc = f034_obj.getProcIndexByLabel('003_01eve_01')
f034_03_01_insts, f034_03_01_labels = f034_obj.getProcInstructionsLabelsByIndex(f034_03_01_proc)
f034_03_01_insts[61] = inst("PUSHIS",0x3da) #Change flag check to key item (Himorogi)
f034_obj.changeProcByIndex(f034_03_01_insts, f034_03_01_labels, f034_03_01_proc)

#Swap out Markro's INF.
#Black Temple - Checks flag 0x03C0
#    MSG 1 - 0x10
#    MSG 2 - 0x13
#White Temple - Checks flag 0x03C1
#    MSG 1 - 0x11
#    MSG 2 - 0x13
#Red Temple - Checks flag 0x03C2
#    MSG 1 - 0x12
#    MSG 2 - 0x13
f034_inf_patched = BytesIO(bytes(open('patches/Doors_F034.INF','rb').read()))
dds3.add_new_file('/fld/f/f034/F034.INF', f034_inf_patched)
f034_obj.changeMessageByIndex(assembler.message("This door is locked by the^n^bblack temple key^p,^nwhich is held by ^gsome dude^p.","BLACK_LOCK"),0x10)
f034_obj.changeMessageByIndex(assembler.message("This door is locked by the^n^ywhite temple key^p,^nwhich is held by ^gsome dude^p.","WHITE_LOCK"),0x11)
f034_obj.changeMessageByIndex(assembler.message("This door is locked by the^n^rred temple key^p,^nwhich is held by ^gsome dude^p.","RED_LOCK"),0x12)
f034_obj.changeMessageByIndex(assembler.message("You have opened the locked door.","DOOR_OPEN"),0x13)
#f034_lb = push_bf_into_lb(f034_obj, 'f034')
#f034b_lb = push_bf_into_lb(f034_obj, 'f034b')
#f034c_lb = push_bf_into_lb(f034_obj, 'f034c')
#f034d_lb = push_bf_into_lb(f034_obj, 'f034d')

f034_amb_a = dds3.get_file_from_path('/fld/f/f034/f034.amb')
f034_amb_b = dds3.get_file_from_path('/fld/f/f034/f034b.amb')
f034_amb_c = dds3.get_file_from_path('/fld/f/f034/f034c.amb')
f034_amb_d = dds3.get_file_from_path('/fld/f/f034/f034d.amb')

f034a_lb = f034a_lb.export_lb({'WAP': BytesIO(f034_wap_file), 'BF': BytesIO(bytes(f034_obj.toBytes())), 'ATMP': f034_amb_a, 'INF': f034_inf_patched})
f034b_lb = f034b_lb.export_lb({'WAP': BytesIO(f034_wap_file), 'BF': BytesIO(bytes(f034_obj.toBytes())), 'ATMP': f034_amb_b, 'INF': f034_inf_patched})
f034c_lb = f034c_lb.export_lb({'WAP': BytesIO(f034_wap_file), 'BF': BytesIO(bytes(f034_obj.toBytes())), 'ATMP': f034_amb_c, 'INF': f034_inf_patched})
f034d_lb = f034d_lb.export_lb({'WAP': BytesIO(f034_wap_file), 'BF': BytesIO(bytes(f034_obj.toBytes())), 'ATMP': f034_amb_d, 'INF': f034_inf_patched})
#Modified WAP is to remove the warping outside when you defeat one of the bosses (because internally you get warped outside, view the cutscene, then warped back in).
#Modified BF as usual.
#Modified ATMP/AMB because if I don't the map stays on the outside one whenever you go into a temple.
#Modified INF for locked doors (though probably fine as just a_lb).

dds3.add_new_file(custom_vals.LB0_PATH['f034'], f034a_lb)
dds3.add_new_file(custom_vals.LB0_PATH['f034b'], f034b_lb)
dds3.add_new_file(custom_vals.LB0_PATH['f034c'], f034c_lb)
dds3.add_new_file(custom_vals.LB0_PATH['f034d'], f034d_lb)
#set 0x51

e703_obj = get_script_obj_by_name(dds3,'e703')
e703_msg = e703_obj.appendMessage("The Tower of Kagutsuchi has been lowered onto the Obelisk.^nFinish it at the Tower of Kagutsuchi!","TOK_LOWERED")
e703_insts = [
    inst("PROC",0),
    inst("PUSHIS",0x10),
    inst("PUSHIS",1),
    inst("COMM",0xf),
    inst("COMM",1),
    inst("PUSHIS",e703_msg),
    inst("COMM",0),
    inst("COMM",2),
    inst("PUSHIS",0x96),
    inst("COMM",8),
    inst("COMM",0x23),#FLD_EVENT_END2
    inst("COMM",0x2e),
    inst("END")
]
e703_obj.changeProcByIndex(e703_insts,[],0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e703'], BytesIO(bytes(e703_obj.toBytes())))

#file = open("piped_scripts/f034.bfasm",'w')
#file.write(f034_obj.exportASM())
#file.close()

#Cutscene removal in Yurakucho Tunnel f021
#Shorten Trumpeter
#add archangels to room north of bead of life chest
f021_obj = get_script_obj_by_name(dds3,"f021")
#Trumpeter is 001_01eve_04
f021_toot_proc = f021_obj.getProcIndexByLabel("001_01eve_04")
f021_toot_insts = [
    inst("PROC",f021_toot_proc),
    inst("PUSHIS",0),
    inst("PUSHIS",0x75a),#Didn't already run away
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0),
    inst("PUSHIS",0x118),#Didn't already fight
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("AND"),
    inst("IF",0),#End label
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",0x39),#Do you want to stay here?
    inst("COMM",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x3a),#Yes/no
    inst("COMM",3),
    inst("PUSHREG"),
    inst("EQ"),
    inst("COMM",2),
    inst("IF",1),
    inst("PUSHIS",0x118), #turn on fought flag.
    inst("COMM",8),
    inst("PUSHIS",0x3e5), #give candelabra
    inst("COMM",8),
    inst("PUSHIS",0x925), #Fusion flag???
    inst("COMM",8),
    inst("PUSHIS",0x2ec),
    inst("PUSHIS",0x15),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("PUSHIS",0x408),
    inst("COMM",0x67),
    inst("END"),
    inst("PUSHIS",0x75a),
    inst("COMM",0x8),
    inst("COMM",0x61),
    inst("END")
]
f021_toot_labels = [
    assembler.label("TOOT_RAN",40),
    assembler.label("TOOT_FOUGHT",37)
]
f021_obj.changeProcByIndex(f021_toot_insts,f021_toot_labels,f021_toot_proc)

f021_toot_rwms = f021_obj.appendMessage("Trumpeter reward placeholder","TOOT_RWMS")
f021_toot_rwms_insts = [
    inst("PROC",len(f021_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f021_toot_rwms),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]
f021_toot_reward_proc_str = "TOOT_CB"
f021_obj.appendProc(f021_toot_rwms_insts,[],f021_toot_reward_proc_str)
insert_callback('f021', 0xf4, f021_toot_reward_proc_str)

f021_lb = push_bf_into_lb(f021_obj, 'f021')
dds3.add_new_file(custom_vals.LB0_PATH['f021'], f021_lb)
#Insert archangels in the same room that has "009_01eve_08"
#Plan: Move 009_01eve_08 over to the door, and have the normal door opening moved OoB. At that point we have BF control.

#Cutscene removal in Diet Building f033
#Shorten Mada and Mithra. Add reward messages for all bosses.
#Shorten Samael cutscene, as well as force Samael.
#001_01eve_01 is Surt cutscene. No shortnening needed, but a callback is needed.
#   Location value is: 0x226
#0x694 set going into 007_start is Mada. No shortening needed, but a callback is needed.
#   Location value is: 0x227
#024_01eve_01 - 08 is Mot. "> Mot's magic is coming undone." can be used as reward message in 018_start.
#   Message ID is: 0xd
#029_01eve_01 is Mithra. Shortening possibly needed, but pretty low priority. 029_start has callback on the text: "O Kagutsuchi... Hath the destroyer (ry"
#   Message ID is: 0x2d
#e674_main is event with Samael. Shorten like Gary.
f033_obj = get_script_obj_by_name(dds3,"f033")

f033_surt_rwms = f033_obj.appendMessage("Surt reward message","SURT_RWMS")
f033_surt_rwms_insts = [
    inst("PROC",len(f033_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f033_surt_rwms),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f033_surt_reward_proc_str = "SURT_CB"
f033_obj.appendProc(f033_surt_rwms_insts,[],f033_surt_reward_proc_str)
insert_callback('f033', 0x37a4, f033_surt_reward_proc_str)

f033_mada_rwms = f033_obj.appendMessage("Mada reward message","MADA_RWMS")
f033_mada_rwms_insts = [
    inst("PROC",len(f033_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f033_mada_rwms),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f033_mada_reward_proc_str = "MADA_CB"
f033_obj.appendProc(f033_mada_rwms_insts,[],f033_mada_reward_proc_str)
insert_callback('f033', 0x3808, f033_mada_reward_proc_str)


f033_obj.changeMessageByIndex(assembler.message("Mot reward placeholder","MOT_REWARD"),0xd)

f033_29_proc = f033_obj.getProcIndexByLabel('029_01eve_01') #Mithra
f033_29_insts = [
    inst("PROC",f033_29_proc),
    inst("PUSHIS",0),
    inst("PUSHIS",0x691),
    inst("COMM",0x7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0),
    inst("PUSHIS",0x691),
    inst("COMM",0x8),
    inst("PUSHIS",0x919), #Fusion flag I think. Probably not necessary
    inst("COMM",0x8),
    inst("PUSHIS",0x22a),
    inst("PUSHIS",0x21),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("PUSHIS",0x3ca),
    inst("COMM",0x67),
    inst("END")
]
f033_29_labels = [
    assembler.label("MITHRA_FOUGHT",17)
]
f033_obj.changeProcByIndex(f033_29_insts, f033_29_labels, f033_29_proc)
f033_obj.changeMessageByIndex(assembler.message("Mithra Reward Placeholder","MITHRA_REWARD"),0x2d)

f033_samael_rwms = f033_obj.appendMessage("Samael reward message","MADA_RWMS")
f033_samael_rwms_insts = [
    inst("PROC",len(f033_obj.p_lbls().labels)),
    inst("COMM",0x60),
    inst("COMM",1),
    inst("PUSHIS",f033_samael_rwms),
    inst("COMM",0),
    inst("COMM",2),
    inst("COMM",0x61),
    inst("END")
]

f033_samael_reward_proc_str = "SAMAEL_CB"
f033_obj.appendProc(f033_samael_rwms_insts,[],f033_samael_reward_proc_str)
insert_callback('f033', 0x3998, f033_samael_reward_proc_str)

f033_lb = push_bf_into_lb(f033_obj, 'f033')
dds3.add_new_file(custom_vals.LB0_PATH['f033'], f033_lb)

#e674_main
#set bits: 0x904, 0x72 (then calls battle 0x2a0). 0x73 (closes door), 0x3da, 0x870, 0x6b7 (off), 0x76, 0x70, 0x71, 
e674_obj = get_script_obj_by_name(dds3,'e674')
e674_insts = [
    inst("PROC",0),
    inst("PUSHIS",0),
    inst("PUSHIS",0x73),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("IF",0),
    inst("PUSHIS",0x73),
    inst("COMM",8),
    inst("PUSHIS",0x3da),
    inst("COMM",8),
    inst("PUSHIS",0x2a2),
    inst("PUSHIS",0x2a0),
    inst("COMM",0x28),
    inst("END"),
    inst("PUSHIS",0x2a2),#guess
    inst("PUSHIS",33),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("COMM",0x23),#FLD_EVENT_END2
    inst("COMM",0x2e),
    inst("END")
]
e674_labels = [
    assembler.label("SAMAEL_DEFEATED",15)
]
e674_obj.changeProcByIndex(e674_insts,e674_labels,0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e674'], BytesIO(bytes(e674_obj.toBytes())))

#Going into ToK is 015_01eve_02 of Obelisk
#With 0x660 set it's super quick.

#Cutscene removal in ToK1 f032
#Shorten Ahriman
#If possible, have block puzzle already solved
#Block puzzle to ahriman is in 017. Probably initialized with 017_start.
#9&10 is middle block. 5&7 is front block. 6&8 is far block.
#e681 is Ahriman. e678 is Ahriman dead.
e681_obj = get_script_obj_by_name(dds3,'e681')
e681_insts = [
    inst("PROC",0),
    inst("PUSHIS",0x75),
    inst("COMM",8),
    inst("PUSHIS",0x74),
    inst("COMM",8),
    inst("PUSHIS",0x2a6),
    inst("PUSHIS",0x14e),
    inst("COMM",0x28),
    inst("PUSHIS",0x3df),
    inst("COMM",8),
    inst("PUSHIS",0x2a9),
    inst("PUSHIS",32),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("COMM",0x23),#FLD_EVENT_END2
    inst("COMM",0x2e),
    inst("END")
]
e681_obj.changeProcByIndex(e681_insts,[],0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e681'], BytesIO(bytes(e681_obj.toBytes())))
#Could probably blank out e678

#Cutscene removal in ToK2 f036
#Shorten Noah
#013_01eve_09 is block. (inverse is 10)
#e680 is noah. e677 is noah dead.
e680_obj = get_script_obj_by_name(dds3,'e680')
e680_insts = [
    inst("PROC",0),
    inst("PUSHIS",0x62),
    inst("COMM",8),
    inst("PUSHIS",0x61),
    inst("COMM",8),
    inst("PUSHIS",0x2a5),
    inst("PUSHIS",0x1d8),
    inst("COMM",0x28),
    inst("PUSHIS",0x3e0),
    inst("COMM",8),
    inst("PUSHIS",680),
    inst("PUSHIS",36),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("COMM",0x23),#FLD_EVENT_END2
    inst("COMM",0x2e),
    inst("END")
]
e680_obj.changeProcByIndex(e680_insts,[],0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e680'], BytesIO(bytes(e680_obj.toBytes())))
#By setting 0x660, some stuff doesn't properly work. We'd like to keep 0x660 on, so we'll change the flag (using new flags, a30 and a31). This also allows direct ToK2 and ToK3 to work properly.
#Change 012_start to use the 0xa30 flag and 013_start to be a duplicate (013 doesn't exist as a proc, but it's still referenced, and it's exactly where we want it).
#There's a super duper corner-case scenario where you unlock ToK2 terminal externally, warp directly to ToK2, which doesn't trigger 012_start, then you go into 014 or 015 and it'll look weird. You still can't progress or lock yourself, and going back into 012 will call 012_start and fix it, so as far as I'm concerned there is no issue whatsoever. If someone submits a bug report for this situation, point them to this comment and say it is known and does not need to be fixed.
f036_obj = get_script_obj_by_name(dds3,'f036')
f036_12_proc = f036_obj.getProcIndexByLabel('012_start')
f036_12_insts, f036_12_labels = f036_obj.getProcInstructionsLabelsByIndex(f036_12_proc)
f036_12_insts[2] = inst("PUSHIS",0xa30)
f036_12_insts[227] = inst("PUSHIS",0xa30)

f036_13_insts = copy.deepcopy(f036_12_insts)
f036_13_labels = copy.deepcopy(f036_12_labels) #Need to deepcopy the labels because changeProcByIndex changes the label offsets from relative to absolute, and I didn't think of this situation when I wrote the assembler.

f036_obj.changeProcByIndex(f036_12_insts, f036_12_labels, f036_12_proc)

#Repurpose for 013, then append it.
f036_13_labels[0].label_str = "_13_START_LABEL"
f036_13_insts[0] = inst("PROC",len(f036_obj.p_lbls().labels))
f036_obj.appendProc(f036_13_insts, f036_13_labels, "013_start")

f036_lb = push_bf_into_lb(f036_obj, 'f036')
dds3.add_new_file(custom_vals.LB0_PATH['f036'], f036_lb)

#Cutscene removal in ToK3 f037
#Shorten Thor 2
#Shorten Baal
#Shorten Kagutsuchi and Lucifer
#If possible, have block puzzle after Thor 2 already solved
#Thor 2 is 007_01eve_05. 007_THOR_AFTER exists.
#007_01eve_03 is center block. (inverse is 04)
#Baal is e682. e679 is baal dead.
#0x665 is ToK3 top splash.
#027_01eve_04 is left pillar, 05 is middle, 06 is right. 07 is central pillar to Kagutsuchi.
#e705?
e682_obj = get_script_obj_by_name(dds3,'e682')
e682_insts = [
    inst("PROC",0),
    inst("PUSHIS",0x83),
    inst("COMM",8),
    inst("PUSHIS",0x84),
    inst("COMM",8),
    inst("PUSHIS",0x2a7),
    inst("PUSHIS",0x14d),
    inst("COMM",0x28),
    inst("PUSHIS",0x3d3),
    inst("COMM",8),
    inst("PUSHIS",682),
    inst("PUSHIS",37),
    inst("PUSHIS",1),
    inst("COMM",0x97),
    inst("COMM",0x23),#FLD_EVENT_END2
    inst("COMM",0x2e),
    inst("END")
]
e682_obj.changeProcByIndex(e682_insts,[],0)
dds3.add_new_file(custom_vals.SCRIPT_OBJ_PATH['e682'], BytesIO(bytes(e682_obj.toBytes())))

f037_obj = get_script_obj_by_name(dds3,'f037')
#Same 0x660 problem as ToK2. Use 0xa31, a32, a33, a34 instead.
f037_19_proc = f037_obj.getProcIndexByLabel('019_start')
f037_19_insts, f037_19_labels = f037_obj.getProcInstructionsLabelsByIndex(f037_19_proc)
f037_19_insts[2] = inst("PUSHIS",0xa31)
f037_19_insts[67] = inst("PUSHIS",0xa31)
f037_obj.changeProcByIndex(f037_19_insts, f037_19_labels, f037_19_proc)

f037_20_proc = f037_obj.getProcIndexByLabel('020_start')
f037_20_insts, f037_20_labels = f037_obj.getProcInstructionsLabelsByIndex(f037_20_proc)
f037_20_insts[2] = inst("PUSHIS",0xa32)
f037_20_insts[27] = inst("PUSHIS",0xa32)
f037_obj.changeProcByIndex(f037_20_insts, f037_20_labels, f037_20_proc)

#37 for 21
f037_21_proc = f037_obj.getProcIndexByLabel('021_start')
f037_21_insts, f037_21_labels = f037_obj.getProcInstructionsLabelsByIndex(f037_21_proc)
f037_21_insts[2] = inst("PUSHIS",0xa33)
f037_21_insts[37] = inst("PUSHIS",0xa33)
f037_obj.changeProcByIndex(f037_21_insts, f037_21_labels, f037_21_proc)

#47 for 23
f037_23_proc = f037_obj.getProcIndexByLabel('023_start')
f037_23_insts, f037_23_labels = f037_obj.getProcInstructionsLabelsByIndex(f037_23_proc)
f037_23_insts[2] = inst("PUSHIS",0xa34)
f037_23_insts[47] = inst("PUSHIS",0xa34)
f037_obj.changeProcByIndex(f037_23_insts, f037_23_labels, f037_23_proc)

f037_lb = push_bf_into_lb(f037_obj, 'f037')
dds3.add_new_file(custom_vals.LB0_PATH['f037'], f037_lb)

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