#Nocturne script file (*.bf) assembler and disassembler
#In a disassembled state, there is an API in the bf_script class that lets you modify the script programatically.
#Currently the API is not implemented and this entire piece is a messy WIP, but is useful to see to be able to understand how to interface with bf files.
import math
OPCODES = {
    "PUSHI":0,
    "PUSHF":1,
    "PUSHIX":2,
    "PUSHIF":3,
    "PUSHREG":4,
    "POPIX":5,
    "POPFX":6,
    "PROC":7,
    "COMM":8,
    "END":9,
    "JUMP":10,
    "CALL":11,
    "RUN":12,
    "GOTO":13,
    "ADD":14,
    "SUB":15,
    "MUL":16,
    "DIV":17,
    "MINUS":18,
    "NOT":19,
    "OR":20,
    "AND":21,
    "EQ":22,
    "NEQ":23,
    "S":24,
    "L":25,
    "SE":26,
    "LE":27,
    "IF":28,
    "PUSHIS":29,
    "PUSHLIX":30,
    "PUSHLFX":31,
    "POPLIX":32,
    "POPLFX":33,
    "PUSHSTR":34
}
OPCODES_0_OPERAND = ["PUSHI", "PUSHF", "PUSHIX", "PUSHIF", "PUSHREG", "POPIX", "POPFX",  "END", "ADD", "SUB", "MUL", "DIV", "MINUS", "NOT", "OR", "AND", "EQ", "NEQ", "S", "L", "SE", "LE"]
OPCODES_LABEL_OPERAND = ["JUMP", "GOTO", "IF","PROC"] #Proc specifically marks the beginning of a function and uses different labels
OPCODES_1_OPERAND = ["POPLFX", "POPLIX", "PUSHLFX", "PUSHLIX", "PUSHIS", "CALL", "COMM", "PUSHSTR"]
#PUSHSTR is a special code
BF_MAGIC = "FLW0"
MSG_MAGIC = "MSG1"

PROC_LABELS = 0
BR_LABELS = 1
BYTECODE = 2
MESSAGES = 3
STRINGS = 4

NULL_NAME_ID = 0xFFFF #name id is two bytes so this is -1

class bf_script:
    def __init__(self):
        self.size = 0
        self.magic = ""
        self.section_count = 0
        self.sections_size = 0 #Not sure what this value is
        self.sections = [] #In a hard typed language this would be a relocated_class pointer
    def toBytes(self):
        retbytes = [0]*4
        retbytes.extend(itobb(self.size,4)) #possibly needs to change?
        retbytes.extend(ctobb(self.magic,4))
        retbytes.extend([0]*4)
        retbytes.extend(itobb(self.section_count,4))
        retbytes.extend(itobb(self.sections_size,4))
        retbytes.extend([0]*8)
        for header in self.sections:
            retbytes.extend(header.headerBytes())
        for base in self.sections:
            retbytes.extend(base.toBytes())
        return retbytes

    def changeProcByIndex(self, instructions, relative_labels, index):
        #Integrity checks:
        #   Check that index is not OoB
        #   Check that instructions is a valid list of instruction objects
        #   Check that relative_labels is a valid list of label objects
        #   Check that the label strs in relative_labels have not been used
        #   Check that the index of the labels are within the length of instructions
        #   Check that the first instruction is PROC. Perhaps add it and add the relative label indices by 1?
        #   Check any other instructions for invalid logic:
        #       Make sure last instruction is END. Perhaps add it?
        #       Make sure instructions with a label operand have a given relative_label
        #       Make sure PUSHSTR instructions are not OoB with the STRINGS section
        
        #Optional things:
        #   Remove replaced labels
        
        #Pointer cleanup
        #Get the relative change in bytes (positive or negative) and instruction count
        #   All PROC labels past this one are added by instruction count delta
        #   All BR labels past current proc instruction offset + count are added by instruction count delta
        #   Add the offset of the bf script headers past this one with delta byte count
        #   Add the count of the instruction bf script header with delta instruction count
                
        #Append added labels (maybe its own function?):
        #   Add relative_labels indices by current label count (in label header)
        #   Add relative_labels to BR_LABELS
        #   Add count in bf script to added labels
        #   Add label count*0x20 bytes to offset of sections past BR_LABELS
        
        #Cut out old instructions
        #Insert new instructions
        
        #No return value
        pass
    def changeMessageByIndex(self, byte_text):
        
        #No return value
        pass
    def appendProc(self, instructions, relative_labels, proc_label):
    
        #Return proc index
        pass
    def appendMessage(self, message_label, byte_text, is_decision = False, speaker_id = 0):
        #NOTE: byte_text is as it has gone through space_text() and str_to_bytes() in message.py
    
        #Find textbox count
        #Construct relative pointers to the textboxes
        #That should be enough to construct a valid mesage as well as the extra bytes added.
        #Added bytes = message pointer length + message length (added to offset of PUSHSTRS)
        #Add bf section header count to length of added bytes
        #Every message pointer offset is added by the length of a message pointer
        
        #Add names_obj offset by added bytes
        #Add unknown_pointer offset by added bytes
        
        #Return message index
        pass
    def appendPUSHSTR(self,str):
    
        #Return str index
        pass
    def getMessageIndexByLabel(self, label_str):
    
        #Return message index
        pass
    def getPUSHSTRIndexByStr(self, str):
    
        #Return pushstr index
        pass
    def getProcIndexByLabel(self, label_str):
    
        #Return proc index
        pass
    def getProcInstructionsByIndex(self, proc_index):
    
        #Return a list of instructions
        pass
    def exportASM(self, asmFilename):
        pass
    def importASM(self, asmFilename):
        pass
        
class relocated_class: #aka section. Is an abstract base class
    def __init__(self):
        self.index = 0
        self.size = 0
        self.count = 0
        self.offset = 0
    def toBytes(self):
        raise NotImplementedError() #needs to be implemented in child classes
    def toString(self):
        raise NotImplementedError() 
    def headerBytes(self):
        bytes = []
        bytes.extend(itobb(self.index,4))
        bytes.extend(itobb(self.size,4))
        bytes.extend(itobb(self.count,4))
        bytes.extend(itobb(self.offset,4)) #need to change based off of the total size of other sections
        #possibly call self.getSize to change the size...
        return bytes
        
class label:
    def __init__(self,str,offset):
        self.label_str = str
        self.label_offset = offset

#used twice with both procedure and branch labels
class label_obj(relocated_class):
    def __init__(self):
        self.labels = []
    def toBytes(self):
        bytes = []
        for l in self.labels:        
            bytes.extend(ctobb(l.label_str,0x18))
            bytes.extend(itobb(l.label_offset,8))
        return bytes
    def toString(self):
        pass
    def getSize(self):
        return len(self.labels) * 0x20
        
class instruction:
    def __init__(self, opcode, operand):
        self.opcode = opcode
        self.operand = operand

class instruction_obj(relocated_class):
    def __init__(self):
        self.instructions=[]
    def toBytes(self):
        bytes = []
        for ins in self.instructions:
            bytes.extend(itobb(ins.opcode,2))
            bytes.extend(itobb(ins.operand,2))
        return bytes
    def toString(self):
        pass
    def getSize(self):
        return len(self.instructions) * 4
        
class message_script(relocated_class):
    #all pointers in the message script are relative to the message script itself
    def __init__(self):
        self.m_size = 0 #Should be the same as relocated_class.size
        self.magic = ""
        self.type = 0 #Should always end up being 7
        self.unknown_pointer = 0
        self.unknown_size = 0
        self.pointers_count = 0
        self.unknown_value = 0
        self.m_offset = 0
        self.message_pointers = []
        self.names = None #spot for names_obj
        self.messages = []
        self.unknown_bytes = []
    def toBytes(self):
        retbytes = []
        retbytes.extend(itobb(self.type,4))
        retbytes.extend(itobb(self.m_size,4)) #or self.getSize()
        retbytes.extend(ctobb(self.magic,4))
        retbytes.extend([0]*4)
        retbytes.extend(itobb(self.unknown_pointer,4)) #pointer to update
        retbytes.extend(itobb(self.unknown_size,4))
        retbytes.extend(itobb(self.pointers_count,4))
        retbytes.extend(itobb(self.unknown_value,4))
        
        for mp in self.message_pointers:
            retbytes.extend(itobb(mp.bool_val,4))
            retbytes.extend(itobb(mp.pointer,4)) #pointer to update
        
        retbytes.extend(itobb(self.names.offset,4)) #pointer to update
        retbytes.extend(itobb(self.names.names_count,4))
        retbytes.extend([0]*8)
        
        #this part is disgusting since every message is variable length, and there are 2 types of messages
        for mo in self.messages:
            #pointer spot of message_pointers[i]
            retbytes.extend(ctobb(mo.label_str,0x18))
            if mo.is_decision:
                retbytes.extend([0]*2)
                retbytes.extend(itobb(mo.textbox_count,2))
                retbytes.extend([0]*4)
            else:
                retbytes.extend(itobb(mo.textbox_count,2))
                retbytes.extend(itobb(mo.name_id,2))
            #check if c == len(mo.text_pointers)?
            for tp in mo.text_pointers:
                retbytes.extend(itobb(tp,4))
            retbytes.extend(itobb(mo.text_size,4))
            extra_extend = (4-(len(mo.text_bytes)%4))%4 #2nd mod 4 is in case it ends up being 4, which doesn't extend.
            retbytes.extend(mo.text_bytes)
            if extra_extend > 0:
                retbytes.extend([0]*extra_extend)
        
        #names.offset pointer spot
        for np in self.names.names_pointers:
            retbytes.extend(itobb(np,4)) #pointers to update
        full_len=0
        for n in self.names.names:
            retbytes.extend(ctobb(n,len(n)+1))
            full_len+=len(n)+1
        extra_extend = (4-(full_len%4))%4
        if extra_extend > 0:
            retbytes.extend([0]*extra_extend)
        
        #unknown_bytes pointer spot
        retbytes.extend(self.unknown_bytes)
        return retbytes
            
    def toString(self):
        pass
    def getSize(self):
        pass
        #0x20 for header
        #8 for each message pointer
        #0x10 for name header
        #message: go through each one
        #   0x18 for label
        #   4 bytes for two values
        #   4 * textbox_count (pointers)
        #   4 bytes for text_size
        #   text_size bytes ceilinged by 4
        #add size of names_obj
        #add len of unknown_bytes

class message_pointer:
    def __init__(self, bool_val, pointer):
        self.bool_val = bool_val
        self.pointer = pointer

class message:
    def __init__(self):
        self.label_str = ""
        self.textbox_count = 0
        self.name_id = 0
        self.text_pointers = []
        self.text_size = 0
        self.text_bytes = [] #message in text as bytes because of escape codes
        self.is_decision = False #decision text (like yes/no) is structured differently than other text
        
class names_obj:
    def __init__(self, offset, names_count):
        self.offset = offset
        self.names_count = names_count
        self.names_pointers = []
        self.names = []
    def getSize(self):
        #4 bytes * names_count
        #sum of lengths of names + names_count (representing 00 delimiters)
        #ceiling by 4 (the 00 at the end can ceiling into 4 bytes of 00)
        pass

class pushstrs(relocated_class):
    def __init__(self):
        self.strings = []
    def toBytes(self):
        bytes = []
        for s in self.strings:
            bytes.extend(ctobb(s,len(s)+1))
        return bytes
    def toString(self):
        pass
    def getSize(self):
        #sum of lengths of strings + len(strings) (representing 00 delimiters)
        #do not need to ceiling since it is the end of the file
        pass
        
#big endian bytes to integer
def bbtoi(byte_array):
    retint = 0
    current_power = 0
    for byte in byte_array:
        retint += byte * math.pow(256,current_power)
        current_power +=1
    return int(retint)

def itobb(int_p,length):
    byte_array = [0]*length
    resultint = int_p
    i=0
    while resultint > 0 and i < length:
        byte_array[i] = resultint%256
        resultint = resultint//256
        i+=1
    return byte_array

def ctobb(str, length):
    retbytes = [0]*length
    for i in range(min(len(str),length)):
        retbytes[i] = ord(str[i])
    return retbytes
    
def parse_binary_script(byte_array):
    s = bf_script()
    #0x00:
    #first 4 bytes are nothing. It involves compression and user_id both which are irrelevant here
    #4 byte value that is file size. Doesn't quite fit exactly. Roughly 0x500 short?
    #4 bytes known as "magic". For this purpose it's "FLW0"
    #4 bytes of nothing. 
    #0x10:
    #1 byte (technically 4) that indicates the number of sections (items in relocation table). Each section will cover 0x10 bytes in the header. With every script I've seen this value is 5.
    #Unknown value. According to TGE's code it's the size of the sections (relocation table size), but it doesn't seem to match.
    #8 bytes of 0
    #0x20+: repeats every 0x10 bytes for section count
    #1 byte (technically 4) - section number index
    #1 byte (technically 4) - size of each object in the section in bytes. A size of 1 means it's variable.
    #4 bytes - number of objects in the section
    #4 bytes - offset to the section
    
    s.size = bbtoi(byte_array[4:8])
    s.magic = [chr(x) for x in byte_array[8:12]]
    if s.magic != BF_MAGIC:
        print "Wrong file type detected. Should be FLW0, found:",s.magic
    s.section_count = bbtoi(byte_array[16:20])
    if s.section_count != 5:
        print "Possible warning? Section count not 5"
    s.sections_size = bbtoi(byte_array[20:24])
    
    s.sections_offset = 32
    s.sections.append(label_obj()) #Procedure Labels
    s.sections.append(label_obj()) #Branch Labels
    s.sections.append(instruction_obj()) #Bytecode instructions
    s.sections.append(message_script()) #Message binary script
    s.sections.append(pushstrs()) #PUSHSTR strings
    for i in range(s.section_count):
        c_off = s.sections_offset+(i*16) #current offset
        s.sections[i].index = bbtoi(byte_array[c_off:c_off+4])
        s.sections[i].size = bbtoi(byte_array[c_off+4:c_off+8])
        s.sections[i].count = bbtoi(byte_array[c_off+8:c_off+12])
        s.sections[i].offset = bbtoi(byte_array[c_off+12:c_off+16])

    #Section 00 - Procedure Labels
    #   Size: 0x20 (of all that I've seen)
    #0x18 of label string
    #4 bytes (or 8?) of index to labeled operation. It's always a PROC command (from what I've seen)
    
    
    
    c_off = s.sections[PROC_LABELS].offset
    for i in range(s.sections[PROC_LABELS].count):
        c_str = ""
        for j in range(0x18):
            c = byte_array[c_off+j]
            if c==0:
                break
            c_str+=chr(c)
        c_pointer = bbtoi(byte_array[c_off+0x18:c_off+0x20])
        s.sections[PROC_LABELS].labels.append(label(c_str,c_pointer))
        c_off+=s.sections[PROC_LABELS].size
    
    #Section 01 - Branch Labels
    #   Size: 0x20 (of all that I've seen)
    #literally the same format as procedure labels
    #0x18 of label string
    #4 bytes (or 8?) of index to labeled operation.
    
    c_off = s.sections[BR_LABELS].offset
    for i in range(s.sections[BR_LABELS].count):
        c_str = ""
        for j in range(0x18):
            c = byte_array[c_off+j]
            if c==0:
                break
            c_str+=chr(c)
        c_pointer = bbtoi(byte_array[c_off+0x18:c_off+0x20])
        s.sections[BR_LABELS].labels.append(label(c_str,c_pointer))
        c_off+=s.sections[BR_LABELS].size
    
    #Section 02 - Bytecode
    #   Size: 0x04
    #0x02 - Opcode
    #0x02 - Operand
    
    c_off = s.sections[BYTECODE].offset
    for i in range(s.sections[BYTECODE].count):
        c_opcode = bbtoi(byte_array[c_off:c_off+2])
        c_operand = bbtoi(byte_array[c_off+2:c_off+4])
        s.sections[BYTECODE].instructions.append(instruction(c_opcode,c_operand))
        c_off+=s.sections[BYTECODE].size
    
    
    #Section 03 - Messages
    #   In essence its own file type.
    #1 byte (technically 4): Always 07. Indicates MSG file type?
    #4 bytes of file size. Should match value at 0x58
    #4 bytes of "magic". "MSG1"
    #4 bytes of 00
    #4 bytes of ??
    #4 bytes of ??
    #4 bytes - entry count of pointers
    #Maybe something after? 00 00 02 00.

    c_off = s.sections[MESSAGES].offset
    s.sections[MESSAGES].type = bbtoi(byte_array[c_off:c_off+4])
    if s.sections[MESSAGES].type != 7:
        print "Warning? Message file type not 7. Type:",s.sections[MESSAGES].type
    s.sections[MESSAGES].m_size = bbtoi(byte_array[c_off+4:c_off+8])
    if s.sections[MESSAGES].m_size != s.sections[MESSAGES].count:
        print "Warning. Message file size from relocation / section table (",s.sections[MESSAGES].count,") and message script (",s.sections[MESSAGES].m_size,") do not match."
    s.sections[MESSAGES].magic = [chr(x) for x in byte_array[c_off+8:c_off+12]]
    if s.sections[MESSAGES].magic != "MSG1":
        print "Warning. Message file signature not 'MSG1'"
    #12:16 is 0's
    s.sections[MESSAGES].unknown_pointer = bbtoi(byte_array[c_off+16:c_off+20]) #pointer to gibberish section
    s.sections[MESSAGES].unknown_size = bbtoi(byte_array[c_off+20:c_off+24]) #size of gibberish section
    s.sections[MESSAGES].pointers_count = bbtoi(byte_array[c_off+24:c_off+28])
    s.sections[MESSAGES].unknown_value = bbtoi(byte_array[c_off+28:c_off+32]) #0x20000 (?)
    
    #Pointer entry start.
    #   Size: 0x08   
    #4 bytes of 00 00 00 00 or 01 00 00 00. Boolean value?
    #4 bytes of offset (relative to section start)
    
    c_off += 32
    m_off = c_off #save the message offset used for later
    for i in range(s.sections[MESSAGES].pointers_count):
        bval = bbtoi(byte_array[c_off:c_off+4])
        mpointer = bbtoi(byte_array[c_off+4:c_off+8])
        s.sections[MESSAGES].message_pointers.append(message_pointer(bval,mpointer))
        c_off+=8
    
    #Names in script - header
    #   Size: 0x10
    #4 bytes of offset
    #4 bytes of name count
    #8 bytes of 00
    
    n_off = bbtoi(byte_array[c_off:c_off+4])
    n_count = bbtoi(byte_array[c_off+4:c_off+8])
    s.sections[MESSAGES].names = names_obj(n_off,n_count)
    #8 0's #c_off+=16
    
    #Names in script - NC = Name Count
    #Pointers(?) - 4 bytes * NC
    #Names delimited by 00
    
    c_off = m_off + n_off
    n_pointers = []
    for i in range(n_count):
        n_pointers.append(bbtoi(byte_array[c_off:c_off+4]))
        c_off+=4
    n_strings = []
    for p in n_pointers:
        c_off = m_off + p
        c = byte_array[c_off]
        n_str = ""
        while c != 0:
            n_str+=chr(c)
            c_off+=1
            c = byte_array[c_off]
        n_strings.append(n_str)
    s.sections[MESSAGES].names.names_pointers = n_pointers
    s.sections[MESSAGES].names.names = n_strings
    
    #Messages
    #   Size: Variable
    #0x18 bytes of label string
    #2 bytes of textbox count
    #   if textbox count > 0 - Is not a decision text
    #2 bytes of speaker name ID. Note: -1 (FFFF) is viable.
    #4 bytes of text pointer * textbox count
    #4 bytes of text length in bytes (starting right after this)
    #text length bytes of text string
    #   if textbox count == 0 - Is a decision text
    #2 bytes of actual textbox count
    #4 bytes of 0 (I think?)
    #4 bytes of text pointer * textbox count
    #4 bytes of text length in bytes (starting right after this)
    #use the pointers get to the message objects
    for mp_obj in s.sections[MESSAGES].message_pointers:
        p = mp_obj.pointer
        c_off = m_off + p
        m = message()
        l_str = ""
        for j in range(0x18):
            c = byte_array[c_off+j]
            if c==0:
                break
            l_str+=chr(c)
        m.label_str = l_str
        c_off+=0x18
        m.textbox_count = bbtoi(byte_array[c_off:c_off+2])
        if m.textbox_count == 0: #structured differently for decision text
            m.textbox_count = bbtoi(byte_array[c_off+2:c_off+4])
            m.is_decision = True
            m.name_id = 0 #isn't going to be stored but just setting it
            c_off+=4 #4 bytes of 0
        else:
            m.name_id = bbtoi(byte_array[c_off+2:c_off+4])
        c_off+=4
        for i in range(m.textbox_count):
            m.text_pointers.append(bbtoi(byte_array[c_off:c_off+4]))
            c_off+=4
        m.text_size = bbtoi(byte_array[c_off:c_off+4])
        c_off+=4
        m.text_bytes = byte_array[c_off:c_off+m.text_size]
        s.sections[MESSAGES].messages.append(m)
            
    #A bunch of data that looks like gibberish. No idea how to parse it
    u_p = s.sections[MESSAGES].unknown_pointer
    u_s = s.sections[MESSAGES].unknown_size
    s.sections[MESSAGES].unknown_bytes = byte_array[m_off+u_p-0x20:m_off+u_p+u_s-0x20] #for some reason the pointer offset is before the message header instead of after like the other instances?
    
    #Section 04 - PUSHSTR strings
    #   Size: Variable
    #Strings delimited by 0x00. Referred to by index.
    c_off = s.sections[STRINGS].offset
    #for i in range(s.sections[STRINGS].count): #It turns out the count is completely irrelevant!
    while c_off < len(byte_array): #Possibly better to go until the size of the section but whatever
        p_str = ""
        c = byte_array[c_off]
        while c != 0:
            p_str+=chr(c)
            c_off+=1
            c=byte_array[c_off]
        s.sections[STRINGS].strings.append(p_str)
        c_off+=1
    return s
    
#possible states:
#assembled into a binary
#disassembled into memory
#disassembled from memory into a text file (like .asm)
#parsed from text file into memory

def filenameToBytes(fname):
    return bytearray(open(fname,'rb').read())

def bytesToFile(bytes,fname):
    f = open(fname,'wb')
    f.write(bytearray(bytes))

#push a file through the whole pipeline
def test_file(fname):
    bytes = filenameToBytes(fname)
    obj = parse_binary_script(bytes)
    piped_bytes = obj.toBytes()
    bytesToFile(piped_bytes,"piped_"+fname)
    #Success! The piped version is equal!
    
#test_file("scripts/f016.bf")