#Nocturne script file (*.bf) assembler and disassembler
#In a disassembled state, there is an API in the bf_script class that lets you modify the script programatically.
#Currently the API is not implemented and this entire piece is a messy WIP, but is useful to see to be able to understand how to interface with bf files.
import math
import copy

#Values for the message class
pixels_per_line = 420
kerning = {" ": 8,"!": 9,'"': 8,'#': 13,'$': 12,'%': 19,'&': 13,"'": 4,'(': 11,')': 11,'*': 11,'+': 14,',': 6,'-': 13,'.': 6,'/': 13,'0': 13,'1': 11,'2': 12,'3': 13,'4': 12,'5': 13,'6': 12,'7': 12,'8': 13,'9': 13,':': 9,';': 9,'<': 14,'=': 14,'>': 14,'?': 13,'@': 17,'A': 13,'B': 14,'C': 17,'D': 14,'E': 14,'F': 14,'G': 17,'H': 14,'I': 6,'J': 11,'K': 14,'L': 13,'M': 16,'N': 14,'O': 17,'P': 12,'Q': 17,'R': 12,'S': 13,'T': 12,'U': 13,'V': 15,'W': 20,'X': 14,'Y': 12,'Z': 15,'[': 11,'\\': 17,']': 12,'_': 13,'`': 15,'a': 12,'b': 11,'c': 11,'d': 12,'e': 12,'f': 8,'g': 12,'h': 13,'i': 7,'j': 7,'k': 10,'l': 6,'m': 19,'n': 13,'o': 14,'p': 14,'q': 14,'r': 7,'s': 13,'t': 7,'u': 13,'v': 12,'w': 16,'x': 12,'y': 13,'z': 11,'{': 11,'|': 9,'}': 11,'~': 15}

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
OPCODE_STR = ["PUSHI","PUSHF","PUSHIX","PUSHIF","PUSHREG","POPIX","POPFX", "PROC","COMM","END","JUMP","CALL","RUN","GOTO","ADD","SUB","MUL","DIV","MINUS","NOT","OR","AND","EQ","NEQ","S","L","SE","LE","IF","PUSHIS","PUSHLIX","PUSHLFX","POPLIX","POPLFX","PUSHSTR"]
OPCODES_0_OPERAND = ["PUSHI", "PUSHF", "PUSHIX", "PUSHIF", "PUSHREG", "POPIX", "POPFX",  "END", "ADD", "SUB", "MUL", "DIV", "MINUS", "NOT", "OR", "AND", "EQ", "NEQ", "S", "L", "SE", "LE"]
OPCODES_0_OPERAND_BYNUM = [0,1,2,3,4,5,6,9,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
OPCODES_LABEL_OPERAND = ["JUMP", "GOTO", "IF","PROC"] #Proc specifically marks the beginning of a function and uses different labels
OPCODES_LABEL_OPERAND_BRANCH_BYNUM = [10,13,28]
OPCODES_1_OPERAND = ["POPLFX", "POPLIX", "PUSHLFX", "PUSHLIX", "PUSHIS", "CALL", "COMM", "PUSHSTR"]
#PUSHSTR is a special code
OPCODES_1_OPERAND_BYNUM = [33,32,31,30,29,11,8,34]
BF_MAGIC = "FLW0"
MSG_MAGIC = "MSG1"

MESSAGE_POINTER_SIZE = 8

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
    #Shortcuts
    def p_lbls(self):
        return self.sections[PROC_LABELS]
    def b_lbls(self):
        return self.sections[BR_LABELS]
    def code(self):
        return self.sections[BYTECODE]
    def msgs(self):
        return self.sections[MESSAGES]
    def p_strs(self):
        return self.sections[STRINGS]
    def toBytes(self):
        #Update rolling offsets before outputting the bytes.
        delta_bytes = self.sections[MESSAGES].updateRollingOffsets()
        self.size += delta_bytes
        self.sections[MESSAGES].count += delta_bytes
        self.sections[STRINGS].offset += delta_bytes
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

    #Potential problem with this proc handling: Assumes proc list will be in order.
    def changeProcByIndex(self, instructions, relative_labels, index):
        #Integrity checks:
        #   Check that index is not OoB
        proclen = len(self.sections[PROC_LABELS].labels)
        if index >= proclen:
            print("ERROR: In changeProcByIndex(), given index is out of bounds.")
            return -1
        #   Check that instructions is a valid list of instruction objects
        if not isinstance(instructions,list):
            print("ERROR: In changeProcByIndex(), parameter 'instructions' is not a list.")
            return -1
        if len(instructions) > 0 and not isinstance(instructions[0],instruction):
            print("ERROR: In changeProcByIndex(), parameter 'instructions' is not an instruction list.")
            return -1
        #   Check that relative_labels is a valid list of label objects
        if relative_labels and not isinstance(relative_labels,list):
            print("ERROR: In changeProcByIndex(), parameter 'relative_labels' is not a list.")
            return -1
        if not relative_labels:
            relative_labels = []
        if len(relative_labels) > 0 and not isinstance(relative_labels[0],label):
            print("ERROR: In changeProcByIndex(), parameter 'relative_labels' is not a label list.")
            return -1
        #   Check that the index of the labels are within the length of instructions
        proclabel = self.sections[PROC_LABELS].labels[index]
        if index == proclen - 1:
            procsize = len(self.sections[BYTECODE].instructions) - proclabel.label_offset #minus 1?
        else:
            procsize = self.sections[PROC_LABELS].labels[index+1].label_offset - proclabel.label_offset
        proc_instructions = self.sections[BYTECODE].instructions[proclabel.label_offset:proclabel.label_offset+procsize]
        
        #Pointer cleanup
        #Get the relative change in bytes (positive or negative) and instruction count
        delta_instructions = len(instructions) - len(proc_instructions) 
        delta_bytes = delta_instructions * 4
        removed_branch_indices = []
        labels_to_remove = []
        for r_lab in relative_labels:
            if r_lab.label_offset > len(instructions) or r_lab.label_offset < 0:
                print("ERROR: In changeProcByIndex(), given label",r_lab.label_str,"is out of bounds.")
                return -1
            for br_index,br_lab in enumerate(self.sections[BR_LABELS].labels):
                #Remove overwritten labels
                if br_lab.label_offset >= proclabel.label_offset and br_lab.label_offset <= proclabel.label_offset + procsize and br_lab not in labels_to_remove:
                    removed_branch_indices.append(br_index)
                    #self.sections[BR_LABELS].labels.remove(br_lab) #remove overwritten labels
                    labels_to_remove.append(br_lab)
                    self.sections[BR_LABELS].count -= 1
                    self.sections[BYTECODE].offset -= 0x20 # could use size instead of hardcoding 0x20 but eh
                    self.sections[MESSAGES].offset -= 0x20
                    self.sections[STRINGS].offset -= 0x20
                    #print "+DEBUG: removing label. Name:",br_lab.label_str,"Offset:",br_lab.label_offset, "0x:",hex(br_lab.label_offset)
                elif r_lab.label_str == br_lab.label_str and br_lab not in labels_to_remove:
                    print("ERROR: Label string",r_lab.label_str,"is the same name as an already existing branch string")
                    #print "-DEBUG: relative offset:",r_lab.label_offset,"0x:",hex(r_lab.label_offset),"absolute proc offset:",proclabel.label_offset,"procsize:",procsize
                    #print "--DEBUG: br absolute offset:",br_lab.label_offset
                    return -1
            for pr_lab in self.sections[PROC_LABELS].labels:
                if r_lab.label_str == pr_lab.label_str:
                    print("ERROR: Label string",r_lab.label_str,"is the same name as an already existing procedure string")
                    return -1
        for l in labels_to_remove:
            self.sections[BR_LABELS].labels.remove(l)
        #   Check that the label strs in relative_labels have not been used
        #   Check that the first instruction is PROC. Perhaps add it and add the relative label indices by 1?
        if len(instructions) > 0 and instructions[0].opcode != OPCODES["PROC"]:
            print("WARNING: In changeProcByIndex(), given first instruction is not PROC. Instruction opcode is:",instructions[0].opcode)
        #   Check any other instructions for invalid logic:
        #       Make sure last instruction is END. Perhaps add it?
        if len(instructions) > 0 and instructions[-1].opcode != OPCODES["END"]:
            print("WARNING: In changeProcByIndex(), given last instruction is not END. Instruction opcode is:",instructions[-1].opcode)
        
        #       Make sure instructions with a label operand have a given relative_label or is in the current list of lables. Perhaps only give a warning?
        #TODO: This integrity check
        #       Make sure PUSHSTR instructions are not OoB with the STRINGS section
        #TODO: This integrity check
        
        #   All PROC labels past this one are added by instruction count delta
        if index < proclen - 1:
            for proc_l in self.sections[PROC_LABELS].labels[index+1:]:
                proc_l.label_offset += delta_instructions
                
        #   All BR labels past current proc instruction offset + count are added by instruction count delta
        for br_l in self.sections[BR_LABELS].labels:
            if br_l.label_offset > proclabel.label_offset + procsize:
                br_l.label_offset += delta_instructions
        
        #   Add the offset of the bf script headers past this one with delta byte count
        #In this case it's just messsages and strings
        self.sections[MESSAGES].offset += delta_bytes
        self.sections[STRINGS].offset += delta_bytes
        self.size += delta_bytes
        
        #   Add the count of the instruction bf script header with delta instruction count
        self.sections[BYTECODE].count += delta_instructions
                
        #Branch label indices have moved. Fix each instruction with a branch.
        def recalc_index(index,removed_indices):
            n=0
            #print removed_branch_indices
            for ind in removed_indices:
                if index>ind:
                    n+=1
                elif index == ind:
                    print("WARNING or internal logic error: Branch label used outside of procedure. Previous index:",index,"Removed_indices:",removed_indices)
            return index - n
        #recalculate branch indices before
        if len(removed_branch_indices)>0:
            #print "DEBUG: Fixing br labels of indices:",removed_branch_indices
            for l_inst in self.sections[BYTECODE].instructions[:proclabel.label_offset]:
                if l_inst.opcode in OPCODES_LABEL_OPERAND_BRANCH_BYNUM:
                    #r = recalc_index(l_inst.operand,removed_branch_indices)
                    #if r != l_inst.operand:
                    #    print "DEBUG: Rewriting previous branch instruction from",l_inst.operand,"to",r
                    l_inst.operand = recalc_index(l_inst.operand,removed_branch_indices)
            #recalculate branch indices after
            for l_inst in self.sections[BYTECODE].instructions[proclabel.label_offset + procsize:]:
                if l_inst.opcode in OPCODES_LABEL_OPERAND_BRANCH_BYNUM:
                    #r = recalc_index(l_inst.operand,removed_branch_indices)
                    #if r != l_inst.operand:
                    #    print "DEBUG: Rewriting later branch instruction from",l_inst.operand,"to",r
                    l_inst.operand = recalc_index(l_inst.operand,removed_branch_indices)
            #turn branch instruction indices from relative to absolute
            for inst in instructions:
                if inst.opcode in OPCODES_LABEL_OPERAND_BRANCH_BYNUM:
                    #print "DEBUG: Rewriting instruction from relative label to absolute.",inst.operand,"to",inst.operand + len(self.sections[BR_LABELS].labels) #- len(removed_branch_indices)
                    inst.operand += len(self.sections[BR_LABELS].labels) #- len(removed_branch_indices)
            #print "DEBUG: Done fixing"
        #Append added labels (maybe its own function?):
        #   Add relative_labels offset by current instruction count (in label header)
        #   Add relative_labels to BR_LABELS
        for relative_l in relative_labels:
            relative_l.label_offset += proclabel.label_offset
            self.sections[BR_LABELS].labels.append(relative_l)
        
        #   Add count in bf script to added labels
        self.sections[BR_LABELS].count += len(relative_labels)
        #   Add label count*0x20 bytes to offset of sections past BR_LABELS
        self.sections[BYTECODE].offset += len(relative_labels) * 0x20
        self.sections[MESSAGES].offset += len(relative_labels) * 0x20
        self.sections[STRINGS].offset += len(relative_labels) * 0x20
        
        #Cut out old instructions and insert new ones
        self.sections[BYTECODE].instructions = self.sections[BYTECODE].instructions[:proclabel.label_offset] + instructions + self.sections[BYTECODE].instructions[proclabel.label_offset + procsize:]
        
        #Integrity check to make sure length is correct?
        
        #Return 0 for success
        return 0
    def changeMessageByIndex(self, message_obj, index):
        if not message_obj.byte_formed and message_obj.text_formed:
            message_obj.message_str_to_bytes()
        elif not message_obj.byte_formed and not message_obj.text_formed:
            print("ERROR In changeMessageByIndex(). Given message object has no text formed in it!")
            return -1
        indexed_message = self.sections[MESSAGES].messages[index]
        absolute_pointer = self.sections[MESSAGES].message_pointers[index].pointer
        
        #Calculate header size
        if message_obj.is_decision:
            header_size = 0x18 + 12 + (len(message_obj.relative_pointers) * 4)
        else:
            header_size = 0x18 + 8 + (len(message_obj.relative_pointers) * 4)
        
        #Turn the relative pointers into fully functional pointers
        message_obj.text_pointers = []
        for rp in message_obj.relative_pointers:
            message_obj.text_pointers.append(rp + absolute_pointer + header_size)
        
        #Swap the object in
        self.sections[MESSAGES].messages[index] = message_obj
        
        #Change the offset of each of the next message pointers
        byte_len = len(message_obj.toBytes())
        delta_bytes = byte_len - len(indexed_message.toBytes())
        for mp in self.sections[MESSAGES].message_pointers:
            if mp.pointer > absolute_pointer: #+ byte_len?
                mp.pointer += delta_bytes
        
        #Update all text pointers past this since they're absolute
        for c,mobj in enumerate(self.sections[MESSAGES].messages):
            for i,tp in enumerate(mobj.text_pointers): #This is probably computationally bad but meh
                if index != c and tp > absolute_pointer:
                    mobj.text_pointers[i]+= delta_bytes 

        #Update section header for byte change
        self.sections[MESSAGES].count+=delta_bytes # * size which equals 1
        self.sections[MESSAGES].m_size+=delta_bytes
        self.sections[STRINGS].offset+=delta_bytes

        #Update other affected pointers
        self.sections[MESSAGES].names.names_pointers = [x+delta_bytes for x in self.sections[MESSAGES].names.names_pointers]
        self.sections[MESSAGES].names.offset += delta_bytes
        self.sections[MESSAGES].rolling_pointer += delta_bytes
        self.size += delta_bytes
        return 0
    def appendProc(self, instructions, relative_labels, proc_label_str):
        #TODO: integrity check of proc_label being a valid label
        self.sections[PROC_LABELS].labels.append(label(proc_label_str,len(self.sections[BYTECODE].instructions)))
        self.sections[BYTECODE].instructions.extend(instructions)
        self.sections[PROC_LABELS].count += 1
        self.sections[BR_LABELS].offset += 0x20
        self.sections[BYTECODE].offset += 0x20
        self.sections[BYTECODE].count += len(instructions)
        self.sections[MESSAGES].offset += 0x20 + (len(instructions)*4)
        self.sections[STRINGS].offset += 0x20 + (len(instructions)*4)
        self.size += 0x20 + (len(instructions)*4)
        retval = self.changeProcByIndex(instructions,relative_labels,len(self.sections[PROC_LABELS].labels)-1)
        if retval == -1:
            return -1
        return len(self.sections[PROC_LABELS].labels)-1 #return index of appended proc
    def appendMessage(self, message_str, message_label_str, is_decision = False, name_id = NULL_NAME_ID, auto_space = True):
        m = message()
        
        m.label_str = message_label_str
        m.name_id = name_id
        
        #Deal with the textbox and line spacing 
        if auto_space:
            m.space_text(message_str) 
        
        #Turn the message to a byte form
        m.message_str_to_bytes()
        
        #New pointer is going to be where the names_obj pointer is, and changed by the size of the pointer itself
        m_ptr = self.sections[MESSAGES].names.offset + MESSAGE_POINTER_SIZE
        
        #Calculate header size
        if is_decision:
            header_size = 0x18 + 12 + (len(m.relative_pointers) * 4)
        else:
            header_size = 0x18 + 8 + (len(m.relative_pointers) * 4)
        
        #Add in the text pointers relative to the message script
        for rp in m.relative_pointers:
            m.text_pointers.append(rp + m_ptr + header_size)
        
        byte_count = len(m.toBytes()) + MESSAGE_POINTER_SIZE
        
        #Every message pointer offset is added by the length of a message pointer
        for mp in self.sections[MESSAGES].message_pointers:
            mp.pointer+=8
        
        #Every text pointer is added by the length of a message pointer
        for mobj in self.sections[MESSAGES].messages:
            mobj.text_pointers = [x+MESSAGE_POINTER_SIZE for x in mobj.text_pointers]
        
        #Add the message pointer
        self.sections[MESSAGES].message_pointers.append(message_pointer(is_decision,m_ptr))
        self.sections[MESSAGES].pointers_count += 1
        
        #Add bf section header count to length of added bytes
        self.sections[MESSAGES].count+=byte_count
        self.sections[MESSAGES].m_size+=byte_count
        self.sections[STRINGS].offset+=byte_count
        self.size += byte_count

        #Update both names offset and names pointers
        self.sections[MESSAGES].names.names_pointers = [x+byte_count for x in self.sections[MESSAGES].names.names_pointers]
        self.sections[MESSAGES].names.offset += byte_count
        self.sections[MESSAGES].rolling_pointer += byte_count #rolling offsets are all recalculated during export, but the pointer to it needs to be updated

        #Put the message in
        self.sections[MESSAGES].messages.append(m)
        
        #Return message index
        return len(self.sections[MESSAGES].messages)-1
    def appendPUSHSTR(self,str):
        self.sections[STRINGS].count += len(str) + 1
        self.sections[STRINGS].strings.append(str)
        return len(self.sections[STRINGS].strings) - 1 #Return str index
    def getMessageIndexByLabel(self, label_str):
        for i in range (len(self.sections[MESSAGES].messages)):
            l_s = self.sections[MESSAGES].messages[i].label_str
            if label_str == l_s:
                return i
        return -1
    def getPUSHSTRIndexByStr(self, str):
        try:
            retval = self.sections[STRINGS].strings.index(str)
        except ValueError as e:
            return -1
        return retval
    def getProcIndexByLabel(self, label_str):
        for index,proc in enumerate(self.sections[PROC_LABELS].labels):
            if label_str == proc.label_str:
                return index
        return -1
    def getProcLocByLabel(self, label_str):
        for proc in self.sections[PROC_LABELS].labels:
            if label_str == proc.label_str:
                return proc.label_offset
        return -1
    #Returns a tuple of instructions and relative labels. Branches are all returned as relative labels. 
    #All values are returned as a deep copy as modifications can have huge ramifications elsewhere, which needs to be handled separately.
    def getProcInstructionsLabelsByIndex(self, proc_index):
        try:
            proc = self.sections[PROC_LABELS].labels[proc_index]
            if proc.label_str == self.sections[PROC_LABELS].labels[-1].label_str:#is last one
                islast = True
            else:
                islast = False
                next_proc = self.sections[PROC_LABELS].labels[proc_index+1]
        except IndexError as e:
            return ([],[])
        relative_labels = []
        relative_label_indices = []
        #print "DEBUG. Obtained: proc offset:",proc.label_offset," - Proc index:",proc_index
        for br_ind, br_lab in enumerate(self.sections[BR_LABELS].labels):
            if br_lab.label_offset > proc.label_offset:
                if islast or br_lab.label_offset < next_proc.label_offset:
                    lab = copy.deepcopy(br_lab)
                    lab.label_offset -= proc.label_offset
                    relative_labels.append(lab)
                    relative_label_indices.append(br_ind)
                    #print "DEBUG: Adding relative label:",lab.label_str,"Index:",br_ind
        #print "DEBUG: relative label indices:",relative_label_indices
        if islast:
            ret_instrucitons = copy.deepcopy(self.sections[BYTECODE].instructions[proc.label_offset:])
        ret_instructions = copy.deepcopy(self.sections[BYTECODE].instructions[proc.label_offset:next_proc.label_offset])
        for inst in ret_instructions:
            if inst.opcode in OPCODES_LABEL_OPERAND_BRANCH_BYNUM:
                inst.operand = relative_label_indices.index(inst.operand)
        return (ret_instructions, relative_labels)
 
    def exportASM(self):
        import func_descs
        ret_str = ".instructions\n"
        proc_ind = 0
        proc_count = 0
        #start with .instructions
        #iterate through instructions with index i.
        #   if there is a br label at that index, then put that string in.
        #   put in opcode string
        #   if opcode string is PROC, put in the proc label string
        #       verify that there is a proc label at current index. If not then the instructions are malformed. 
        #   if opcode string is a branch label operand, put the string of the indexed br label in with a colon
        #   if opcode string is PUSHSTR, put the string of the indexed pushstr in
        #   if opcode string has an operand, put in the operand number
        #   otherwise (opcode string with 0 operands) - Nothing!
        #print("PUSHSTRS: ",self.sections[STRINGS].strings,"\nLength:",len(self.sections[STRINGS].strings))
        for i, inst in enumerate(self.sections[BYTECODE].instructions):
            extra_comment = ""
            for br_lab in self.sections[BR_LABELS].labels:
                if i == br_lab.label_offset:
                    ret_str += br_lab.label_str + ":\n"
            if inst.opcode == OPCODES["PROC"]:
                if len(self.sections[PROC_LABELS].labels) > proc_count:
                    ret_str += "\nPROC\t" + self.sections[PROC_LABELS].labels[proc_count].label_str+ "\t"
                else:
                    ret_str += "\nPROC\tOut of Bounds!!!\t"
                extra_comment = "Proc index: "+str(proc_count)
                proc_count+=1
                proc_ind=0
            elif inst.opcode == OPCODES["COMM"]:
                ret_str += "COMM\t" + hex(inst.operand)+"\t"
                if inst.operand in func_descs.COMM_FUNS:
                    extra_comment = func_descs.COMM_FUNS[inst.operand].lineDesc()
            elif inst.opcode == OPCODES["PUSHSTR"]:
                #print("PUSHSTR operand:",inst.operand)
                ret_str += "PUSHSTR" + "\t" + self.sections[STRINGS].readStr(inst.operand) +"\t"
                extra_comment = "String index: "+str(inst.operand)
            elif inst.opcode in OPCODES_0_OPERAND_BYNUM:
                ret_str += OPCODE_STR[inst.opcode]+"\t\t"
            elif inst.opcode in OPCODES_1_OPERAND_BYNUM:
                ret_str += OPCODE_STR[inst.opcode]+"\t"+hex(inst.operand)+"\t"
            elif inst.opcode in OPCODES_LABEL_OPERAND_BRANCH_BYNUM:
                ret_str += OPCODE_STR[inst.opcode]+"\t"+self.sections[BR_LABELS].labels[inst.operand].label_str+"\t"
                extra_comment = "Label index: "+str(inst.operand)
            else:
                ret_str += "Unknown opcode " + str(inst.opcode)
            ret_str += "\t\t#"+str(proc_ind)+";"+str(i)+"\t"+extra_comment+"\n"
            proc_ind+=1
        #next is .messages
        #.sel or .msg space, [index], space, Message label, space, name or -1 or blank, colon. Perhaps have a way to ignore auto-spacing? Seems kind of bad.
        #String with escape codes. Message MUST end with ^m.
        ret_str += ".messages\n\n"
        for i, msg in enumerate(self.sections[MESSAGES].messages):
            if msg.is_decision:
                ret_str+="Sel "
            else:
                ret_str+="Msg "
            ret_str+=hex(i) + " " + msg.label_str + " Name:"
            if msg.name_id == NULL_NAME_ID:
                ret_str+="NO_NAME"
            else:
                if msg.name_id < len(self.sections[MESSAGES].names.names):
                    ret_str+=self.sections[MESSAGES].names.names[msg.name_id]
                else:
                    ret_str+="OoB Name"
            ret_str+="\n\t"
            if not msg.text_formed:
                msg.bytes_to_message_str()
                msg.space_text()
            ret_str+=msg.str
            ret_str+="\n"
        return ret_str
    def importASM(self, asmFilename):
        #first pass of .instructions used to create proc_labels, br_labels, and pushstrs
        #second pass of .instructions to create the bytecode
        #first pass of .messages to create name list
        #second pass of .messages to do everything else
        #third pass to create a list of rolling pointers
        #return -1 for failure, 0 for success
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
        self.rolling_pointer = 0
        self.rolling_size = 0
        self.pointers_count = 0
        self.unknown_value = 0
        self.m_offset = 0
        self.message_pointers = []
        self.names = None #spot for names_obj
        self.messages = []
        self.rolling_offsets = []
    def toBytes(self):
        retbytes = []
        retbytes.extend(itobb(self.type,4))
        retbytes.extend(itobb(self.m_size,4)) #or self.getSize()
        retbytes.extend(ctobb(self.magic,4))
        retbytes.extend([0]*4)
        retbytes.extend(itobb(self.rolling_pointer,4)) #pointer to update
        retbytes.extend(itobb(self.rolling_size,4))
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
            retbytes.extend(mo.toBytes())
        
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
        
        #rolling pointer offsets
        retbytes.extend(self.rolling_offsets)
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
        #add len of rolling_offsets
    #Regenerates the rolling offsets of the message script. Only needs to be ran once before turning into bytes.
    #Returns the delta bytes to update the bf script header with.
    def updateRollingOffsets(self):
        #Rolling numbers are in increments of 2 bytes, so a length of 8 bytes is a value of 4.
        #Offsets for the message pointers which are consistent
        #Some of this I understand, some if it makes no sense whatsoever.
        r_offs = [4] * len(self.message_pointers)
        r_offs[0] = 2
        r_offs.append(2)
        roll = 8
        for m_obj in self.messages:
            roll += 12 #label length
            if m_obj.is_decision:
                roll += 4
            else:
                roll += 2
            if roll > 255:
                roll*=2
                roll+=1
                r_offs.extend(itobb(roll,2)) #Just going to say 2 because there's no way it's going past that
            else:
                r_offs.append(roll)
            roll=4
            if m_obj.textbox_count == 2:
                r_offs.append(2)
            elif m_obj.textbox_count >=30:
                print("ERROR: Too many textboxes???", m_obj.label_str)
                
            elif m_obj.textbox_count > 2:
                r_offs.append(((m_obj.textbox_count-2) * 8)-1) #WHY???????????????????????
            #r_offs.extend([2]*(m_obj.textbox_count-1)) #This would actually make sense and be more intuitive. Gotta save those precious bytes I guess??? But this entire section isn't even necessary if you really want to save space. AAAAAAAAAAAAGHGHHGHGHHHHGHHHHHH!!!!!!!!!!!!!
            roll += (len(m_obj.text_bytes) + (4-(len(m_obj.text_bytes)%4))%4)//2
        r_offs.append(roll)
        n = self.names.names_count
        if n == 2:
            r_offs.append(2)
        elif n > 2:
            r_offs.append(((n-2) * 8)-1)
        delta_bytes =  len(r_offs) - len(self.rolling_offsets)
        self.m_size += delta_bytes
        self.rolling_size += delta_bytes
        self.rolling_offsets = r_offs
        return delta_bytes
            
class message_pointer:
    def __init__(self, bool_val, pointer):
        self.bool_val = bool_val
        self.pointer = pointer


#escape codes
ep = [0xF2, 0x02, 0x01, 0xFF]
er = [0xF2, 0x02, 0x02, 0xFF]
eb = [0xF2, 0x02, 0x03, 0xFF]
ey = [0xF2, 0x02, 0x04, 0xFF]
eg = [0xF2, 0x02, 0x05, 0xFF]
en = [0x0A]
ex = [0x0A, 0xF1, 0x04, 0xF2, 0x08, 0xFF, 0xFF]
exx = [0xF1, 0x04, 0xF2, 0x08, 0xFF, 0xFF] #alternate of ex
em = [0x0A, 0xF1, 0x04, 0x00]
es = [0xF2, 0x08, 0xFF, 0xFF, 0xF2, 0x07, 0x07, 0xFF] #bytes at the start. Not used as an escape but automatically added in.
class message:
    def __init__(self, str = "", label_str = ""):
        self.str = str #message in text as str
        self.label_str = label_str
        self.textbox_count = 0
        self.name_id = NULL_NAME_ID
        self.text_pointers = []
        self.relative_pointers = []
        self.text_size = 0
        self.text_bytes = [] #message in text as bytes because of escape codes
        self.is_decision = False #decision text (like yes/no) is structured differently than other text
        self.byte_formed = False #message is valid in byte form
        self.text_formed = False #message is valid in string form
        if str != "" and label_str != "":
            self.space_text()
            self.text_formed = True
    def getSize(self):
        #Label str 0x18
        #if msg
        #   4 bytes for textbox count and name id
        #   4 bytes * textbox_count
        #   4 bytes for text_size
        #
        pass
    #Fills in text_bytes and relative_pointers given self.str / givenstr (writes into self.str if givenstr is given)
    def message_str_to_bytes(self, givenstr = ""):
        if not self.text_formed and givenstr == "":
            print("ERROR: In message.message_str_to_bytes(). Message needs to be text formed to convert from string to bytes.")
            return -1
        in_escape = False
        byte_count = 8
        bytes_by_int = copy.deepcopy(es)
        self.relative_pointers = [0]
        if givenstr != "":
            self.str = givenstr
            self.text_formed = True
        for c in self.str: #self
            if in_escape:
                #e* are escape codes in bytes
                if c == "p":
                    bytes_by_int.extend(ep)
                    byte_count +=len(ep)
                elif c == "r":
                    bytes_by_int.extend(er)
                    byte_count +=len(er)
                elif c == "b":
                    bytes_by_int.extend(eb)
                    byte_count +=len(eb)
                elif c == "y":
                    bytes_by_int.extend(ey)
                    byte_count +=len(ey)
                elif c == "g":
                    bytes_by_int.extend(eg)
                    byte_count +=len(eg)
                elif c == "n":
                    bytes_by_int.extend(en)
                    byte_count +=len(en)
                elif c == "x":
                    bytes_by_int.extend(ex)
                    byte_count +=len(ex)
                    self.relative_pointers.append(byte_count)
                elif c == "m":
                    bytes_by_int.extend(em)
                    byte_count +=len(em)
                in_escape=False
            elif c == "^":
                in_escape = True
            else:
                bytes_by_int.append(ord(c))
                byte_count+=1
        self.byte_formed = True
        self.text_bytes = bytes_by_int #self
        self.text_size = len(self.text_bytes)
        self.textbox_count = len(self.relative_pointers)
        return 0
    #Fills in self.str from text_bytes / givenbytes. Writes into text_bytes from givenbytes if given.
    def bytes_to_message_str(self, givenbytes = []):
        #Note: Does not fill in relative_pointers
        if not self.byte_formed or givenbytes != []:
            print("ERROR: In message.bytes_to_message_str(), Message needs to be byte formed to convert from bytes to string")
            return -1
        if givenbytes !=[]:
            self.bytes = givenbytes
            self.byte_formed = True
        else:
            self.bytes = self.text_bytes
            print (self.bytes)
            print (len(self.bytes))
        bytelen = len(self.bytes)
        i=0
        m_str = ""
        if self.bytes[:8] == bytearray(es):
            i=8
        loopcheck = -1
        while i<bytelen:
            if loopcheck == i:
                i+=1
            loopcheck=i
            if self.bytes[i] == 0xF2:
                if i+3 < bytelen:
                    bc = self.bytes[i:i+4] #byte check
                    if bc == bytearray(ep):
                        m_str+="^p"
                    elif bc == bytearray(er):
                        m_str+="^r"
                    elif bc == bytearray(eb):
                        m_str+="^b"
                    elif bc == bytearray(ey):
                        m_str+="^y"
                    elif bc == bytearray(eg):
                        m_str+="^g"
                    else:
                        print("Warning: In message.bytes_to_str(). Unknown set of bytes:",bc)
                        m_str+="^u("+str(bc)+")"
                else:
                    print("ERROR: In message.bytes_to_str(). Invalid set of bytes")
                    return -1
                i+=4
            elif self.bytes[i] == 0x0A:
                checkdone = False
                if i+5 < bytelen: #check ^x first
                    if self.bytes[i:i+6] == bytearray(ex):
                        m_str+="^x"
                        i+=6
                        checkdone = True
                if i+3 < bytelen and not checkdone:
                    if self.bytes[i:i+4] == bytearray(em):
                        m_str+="^m"
                        i+=4
                        checkdone = True
                if not checkdone:
                    m_str+="^n"
                    i+=1
            elif self.bytes[i] == 0xf1:
                if i+4 < bytelen:
                    if self.bytes[i:i+5] == bytearray(exx):
                        m_str+="^x"
                        i+=5
                    else:
                        print("Warning: In message.bytes_to_str(). Unknown bytes from 0xF1")
                        m_str+="^u(f1)"
                        i+=1
            else:
                m_str+=chr(self.bytes[i])
                i+=1
        self.text_formed = True
        self.str = m_str
        return 0
    def space_text(self, givenstr = ""):
        if givenstr == "" and self.str == "":
            print("ERROR in message.space_text(). No text to space!")
            return -1
        if givenstr != "":
            self.str = givenstr
            self.text_formed = True
        lines = []
        word = ""
        processed_str = self.str
        line_pixels = 0
        index = 0
        pending_space = False
        #space_index = 0
        line_count = 0 #lines on the text box
        is_newline = False #lots of cases for newline so it's consolidated all in this flag
        text_boxes = 1
        while index < len(processed_str):
            ch = processed_str[index]
            #check for ^n, ^x, ^m, \r, \n and \r\n.
            if ch == '\n':
                is_newline = True
            elif ch == '\r':
                #watch out for \r\n
                if index+1 < len(processed_str) and processed_str[index+1] == '\n':
                    index+=1
                is_newline = True
            elif ch == "^" or ch == "\\":
                #check if the escape character is the last character
                if index+1 == len(processed_str):
                    print("WARNING: Escape character as last character. Ignoring.")
                    break
                esc_ch = processed_str[index+1]
                #Ignore text coloring. That's for byte conversion
                if ch == "^" and (esc_ch == 'p' or esc_ch == 'r' or esc_ch == 'b' or esc_ch == 'y' or esc_ch == 'g'):
                    index+=1 #skip an extra character
                    word = word + ch
                    word = word + esc_ch
                elif ch == "^" and esc_ch == 'n':
                    if pending_space and word != "":
                        lines.append(" ")
                        lines.append(word)
                        word = ""
                    elif word != "":
                        lines.append(word)
                        word = ""
                    is_newline = True
                    index+=1
                elif ch == "^" and esc_ch == 'x':
                    #Reset everything
                    line_pixels = 0
                    line_count = 0
                    if pending_space and word != "":
                        lines.append(" ")
                        lines.append(word)
                        word = ""
                    elif word != "":
                        lines.append(word)
                        word = ""
                    pending_space = False
                    lines.append("^x")
                    text_boxes += 1
                    index+=1
                elif ch == "^" and esc_ch == "m":
                    break #End of message. ^m is automatically added at the end.
                else:
                    print("WARNING: Unknown escape character: '",esc_ch,"'. Ignoring.")
            elif ch not in kerning:
                print("WARNING: Kerning of ",ch," is unknown. Removing character")
            elif ch == " ":
                if pending_space:
                    lines.append(" ")
                if line_pixels + kerning[" "] > pixels_per_line:
                    lines.append(word)
                    word = ""
                    is_newline = True
                    pending_space = False
                else:
                    line_pixels += kerning[" "]
                    lines.append(word)
                    word = ""
                    pending_space = True
            else:
                if line_pixels + kerning[ch] > pixels_per_line:
                    is_newline = True
                else:
                    line_pixels = line_pixels + kerning[ch]
                word = word + ch
                
            if is_newline:
                #append ^n or ^x depending on textbox length
                is_newline = False
                line_pixels = 0
                if line_count == 2:
                    line_count = 0
                    lines.append("^x")
                    text_boxes += 1
                else:
                    line_count += 1
                    lines.append("^n")
                pending_space = False
            index+=1
        if pending_space:
            lines.append(" ")
        if word != "":
            lines.append(word)
        lines.append("^m")
        self.str = ''.join(lines)
        return 0
    def toBytes(self):
        if self.byte_formed == False:
            self.message_str_to_bytes()
        retbytes = []
            #pointer spot of message_pointers[i]
        retbytes.extend(ctobb(self.label_str,0x18))
        if self.is_decision:
            retbytes.extend([0]*2)
            retbytes.extend(itobb(self.textbox_count,2))
            retbytes.extend([0]*4)
        else:
            retbytes.extend(itobb(self.textbox_count,2))
            retbytes.extend(itobb(self.name_id,2))
        #check if c == len(mo.text_pointers)?
        
        for tp in self.text_pointers:
            retbytes.extend(itobb(tp,4))
        retbytes.extend(itobb(self.text_size,4))
        extra_extend = (4-(len(self.text_bytes)%4))%4 #2nd mod 4 is in case it ends up being 4, which doesn't extend.
        retbytes.extend(self.text_bytes)
        if extra_extend > 0:
            retbytes.extend([0]*extra_extend)
        return retbytes
        
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
    #Given an offset of the entirety of the consecutive PUSHSTRs, return the given string.
    def readStr(self,offset):
        current_offset = offset
        for s in self.strings:
            if current_offset == 0:
                return s
            elif current_offset < len(s):
                return s[current_offset:]
            current_offset -= len(s)+1 #+1 is for \0
        print("WARNING: in readStr(). Given offset for PUSHSTRs is out of bounds. Returning empty string.")
        return ''
        
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
    #if s.magic != BF_MAGIC:
    #    print "Wrong file type detected. Should be FLW0, found:",s.magic #finds ['F','L','W','0'] instead so meh
    s.section_count = bbtoi(byte_array[16:20])
    if s.section_count != 5:
        print("Possible warning? Section count not 5")
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
        #print "Appending proc label. Str:",c_str,"Pointer:",c_pointer
    
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
        print("Warning? Message file type not 7. Type:",s.sections[MESSAGES].type)
    s.sections[MESSAGES].m_size = bbtoi(byte_array[c_off+4:c_off+8])
    if s.sections[MESSAGES].m_size != s.sections[MESSAGES].count:
        print("Warning. Message file size from relocation / section table (",s.sections[MESSAGES].count,") and message script (",s.sections[MESSAGES].m_size,") do not match.")
    s.sections[MESSAGES].magic = [chr(x) for x in byte_array[c_off+8:c_off+12]]
    #if s.sections[MESSAGES].magic != "MSG1":
    #    print "Warning. Message file signature not 'MSG1'" #Finds ['M','S','G','1'] instead.
    #12:16 is 0's
    s.sections[MESSAGES].rolling_pointer = bbtoi(byte_array[c_off+16:c_off+20]) #pointer to gibberish section
    s.sections[MESSAGES].rolling_size = bbtoi(byte_array[c_off+20:c_off+24]) #size of gibberish section
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
            m.name_id = NULL_NAME_ID #isn't going to be stored but just setting it
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
        m.byte_formed = True
        s.sections[MESSAGES].messages.append(m)
            
    #A list of rolling offsets to the pointers in the message script.
    #The values are the offset from the previous pointer by every other byte. It starts with 2 and a bunch of 4's because the first pointer is after the 4 byte boolean value, then each pointer object has a length of 8.
    #This is used to turn the pointers from pointers relative to the message script to pointers absolute in memory.
    #One last thing: W H Y ? ? ?
    r_p = s.sections[MESSAGES].rolling_pointer
    r_s = s.sections[MESSAGES].rolling_size
    s.sections[MESSAGES].rolling_offsets = byte_array[m_off+r_p-0x20:m_off+r_p+r_s-0x20] #for some reason the pointer offset is before the message header instead of after like the other instances?
    
    #Section 04 - PUSHSTR strings
    #   Size: Variable
    #Strings delimited by 0x00. Referred to by index.
    c_off = s.sections[STRINGS].offset
    #for i in range(s.sections[STRINGS].count): #It turns out the count is completely irrelevant!
    while c_off < len(byte_array): #Possibly better to go until the size of the section but whatever
        p_str = ""
        c = byte_array[c_off]
        while c != 0 and c_off+1 < len(byte_array):
            p_str+=chr(c)
            c_off+=1
            c=byte_array[c_off]
        if p_str != "":
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

def test_funs(fname):
    '''
    def changeProcByIndex(self, instructions, relative_labels, index):
        OK
    def changeMessageByIndex(self, message_obj, index):
        OK
    def appendProc(self, instructions, relative_labels, proc_label):
        OK
    def appendMessage(self, message_label_str, message_str, is_decision = False, name_id = 0):
        OK
    def appendPUSHSTR(self,str):
        Untested
    def getMessageIndexByLabel(self, label_str):
        Untested
    def getPUSHSTRIndexByStr(self, str):
        Untested
    def getProcIndexByLabel(self, label_str):
        OK
    def getProcInstructionsLabelsByIndex(self, proc_index):
        OK
        
    Untested functions don't add much value as of yet, and they're not even that hard.
    Next focus: ASM
    '''
    
    bytes = filenameToBytes(fname)
    obj = parse_binary_script(bytes)
    
    noop_inst1 = instruction(OPCODES["PUSHIS"],0)
    noop_inst2 = instruction(OPCODES["COMM"],0xe)
    m_index = obj.appendMessage("This is a totally new message!^xThat's incredible, isn't it!?^n^yIsn't^nIt!?^p","_new_msg_label")
    #m_index = 4
    #obj.changeMessageByIndex(message("Different message!^nOh^nBaby^xThis text box is for testing.^xWould a third box change things?","_new_msg_label"), m_index)
    message_proc = [
        instruction(OPCODES["PROC"],0),
        instruction(OPCODES["COMM"],1), 
        instruction(OPCODES["PUSHIS"], m_index), 
        instruction(OPCODES["COMM"],0), 
        instruction(OPCODES["COMM"],2),
        instruction(OPCODES["END"],0)
    ]
    newproc_index = obj.appendProc(message_proc, [], "extra_message_proc")
    if newproc_index == -1:
        print("Append failed")
        return
    yoyogi_east_intro_proc_index = obj.getProcIndexByLabel("006_01eve_01")
    #proc_labels = obj.sections[PROC_LABELS].labels
    #for i in range(len(proc_labels)):
    #for i in range(40,60): #only do first 30 because we don't have the room
    #if True:
#        i=0
    insts, r_labs = obj.getProcInstructionsLabelsByIndex(yoyogi_east_intro_proc_index)
    insts = insts[:-1] + [instruction(OPCODES["CALL"],newproc_index)] + [insts[-1]]
    obj.changeProcByIndex(insts,r_labs,yoyogi_east_intro_proc_index)
        #insts = insts[:-1] + [noop_inst1, noop_inst2] + [insts[-1]]
    #    insts = insts[:-1] + message_inst + [insts[-1]]
        
    #obj.changeProcByIndex(insts, r_labs, i)
    #print "Total added instructions:",hex(len(proc_labels) * 2)
    piped_bytes = obj.toBytes()
    #bytesToFile(piped_bytes,"piped_scripts/f016check.bf")
    bytesToFile(piped_bytes,"piped_scripts/f024.bf")


#piped_bytes = obj.toBytes()
#test_funs("piped_scripts/f016.bf")
#test_funs("scripts/f024.bf")