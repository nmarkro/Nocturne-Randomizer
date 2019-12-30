#Currently uses a customizer, which is a modification of the iso that has the scripts decompressed.
#There shouldn't be too much modification needed when an ISO builder is completed.
import nocturne_script_assembler as assembler
import customizer_values as custom_vals

from io import BytesIO

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

'''def get_script_obj_by_name(iso,script_name):
    file_offset = custom_vals.customizer_offsets[script_name]
    iso.seek(file_offset + 4)
    #Get script size, but script size only goes to the end of the message script. If you have the actual size then you don't need to do this nasty calculation.
    fsize = assembler.bbtoi(bytearray(iso.read(4))) 
    iso.seek(file_offset + fsize)
    is0 = False
    c = ord(iso.read(1))
    #Calculate the size of the final strings section by manually going through it until it stops.
    while not is0 or c != 0:
        fsize += 1
        if c == 0:
            is0 = True
        else:
            is0 = False
        c = ord(iso.read(1))
    #Now that we have the right size, read the file.
    iso.seek(file_offset)
    script_iso = bytearray(iso.read(fsize))
    return assembler.parse_binary_script(script_iso)
'''
# open the ISO and parse it
iso = IsoFS('rom/input.iso')
iso.read_iso()

# get the ddt and write it out to disk
ddt_file = iso.get_file_from_path('DDS3.DDT;1')
with open('rom/old_DDS3.DDT', 'wb') as file:
    file.write(ddt_file.read())

# get the img and write it out to disk in chucks due to size
with open('rom/old_DDS3.IMG', 'wb') as file:
    for chunk in iso.read_file_in_chunks('DDS3.IMG;1'):
        file.write(chunk)

# parse the dds3 fs
dds3 = DDS3FS('rom/old_DDS3.DDT', 'rom/old_DDS3.IMG')
dds3.read_dds3()

# Replace e506.bf (intro) with a custom one to set a bunch of initial values.
with open('patches/e506.bf','rb') as file:
    e506 = BytesIO(file.read())
dds3.add_new_file('/event/e500/e506/scr/e506.bf', e506)

# get the 601 event script and add our hook
e601_obj = get_script_obj_by_path(dds3, '/event/e600/e601/scr/e601.bf')
e601_insts = [
    inst("PROC",0), 
    inst("PUSHIS",506), 
    inst("COMM",0x66), 
    inst("END",0)
]
e601_obj.changeProcByIndex(e601_insts,[],0) #empty list is relative branch labels
# convert the script object to a filelike object and add it to the dds3 file system
e601_data = BytesIO(bytearray(e601_obj.toBytes()))
dds3.add_new_file('/event/e600/e601/scr/e601.bf', e601_data)

# Shorten 618 (intro)
# Cutscene removal in SMC f015

# SMC area flag
# ">You find yourself in a strange place" - "...Show me... the strength...^nof a demon..." - "> The old man and the woman^ndisappeared..."
# ">A voice echoes in your head..." - "> The old man and the woman^ndisappeared..."
# "...We shall meet again... soon..."
# "I've never seen a demon like you"
# "They fell for it. Are you ready?"
# "..........Blarg?" PROC: 012_start
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
    inst("PUSHIS",0), #Label: _366 - Line number 20 (21st) 
    inst("PUSHIS",0x453),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("EQ"),
    inst("PUSHIS",0x452),
    inst("COMM",7),
    inst("PUSHREG"),
    inst("AND"),
    inst("IF",1), #Branch to END if (flag 0x453 is unset) is true
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

# get the field lb and parse it
f015_lb_data = dds3.get_file_from_path('/fld/f/f015/f015_000.LB')
f015_lb = LB_FS(f015_lb_data)
f015_lb.read_lb()
# add the uncompressed, modified BF file to the LB and add it to the dds3 fs
f015_lb_data = f015_lb.export_lb({'BF': BytesIO(bytearray(f015_obj.toBytes()))})
dds3.add_new_file('/fld/f/f015/f015_000.LB', f015_lb_data)

# export the new DDS3 FS
dds3.export_dds3('rom/DDS3.DDT', 'rom/DDS3.IMG')

# remove the DUMMY file to save disk space and write back the iso
iso.rm_file("DUMMY.DAT;1")
with open('rom/DDS3.DDT', 'rb') as ddt, open('rom/DDS3.IMG', 'rb') as img:
    iso.export_iso('rom/modified_scripts.iso', {'DDS3.DDT;1': ddt, 'DDS3.IMG;1': img})

# remove the temp DDS3 files
os.remove('rom/old_DDS3.DDT')
os.remove('rom/old_DDS3.IMG')
os.remove('rom/DDS3.DDT')
os.remove('rom/DDS3.IMG')

#">You obtained an ^rAnnex Gate Pass^p." - Also part of 012_start, but may not be worth the effort to shorten
#"You used the Annex Gate Pass"
#"Hey, punk! I've never seen you^naround, and I don't like your face!"
#"> You feel the presence^nof something...
#"That old guy... what a client.^nThis is gonna be one tough job." - "Oh well time to get to work" - Maybe skip with a flag?

#Cutscene removal in Shibuya f017

#Cutscene removal in Amala Network 1 f018

#Cutscene removal in Ginza (Hijiri mostly) f019

#Cutscene removal in Ginza Underpass f022

#Cutscene removal in Ikebukuro f023

#Cutscene removal in Mantra HQ f024

#Cutscene removal in East Nihilo f020

#Cutscene removal in Kabukicho Prison f025

#Cutscene removal in Ikebukuro Tunnel (anything at all?) f026

#Cutscene removal in Asakusa (Hijiri mostly) f027

#Cutscene removal in Mifunashiro f035

#Cutscene removal in Obelisk f031

#Cutscene removal in Amala Network 2 f028

#Cutscene removal in Asakusa Tunnel (anything at all?) f029

#Cutscene removal in Yoyogi Park f016

#Cutscene removal in Amala Netowrk 3 f030

#Cutscene removal in Amala Temple f034
#f034_obj = get_script_obj_by_name(iso,'f034')
#In the procedure that sets the flag 6a0 and displays messages 1f - 25
#002_start
#lots of comm 104 and 103
#Cutscene removal in Yurakucho Tunnel f021

#Cutscene removal in Diet Building f033

#Cutscene removal in ToK1 f032

#Cutscene removal in ToK2 f036

#Cutscene removal in ToK3 f037

#Cutscene removal in LoA Lobby f040

#Cutscene removal in LoA K1 f041

#Cutscene removal in LoA K2 f042

#Cutscene removal in LoA K3 f043

#Cutscene removal in LoA K4 f044

#Cutscene removal in LoA K5 f045

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