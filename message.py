'''
Message injector that spaces the text out and generates the textbox pointers.
Easiest usage:
injected_str = "Hi! :)"
m = message(injected_str)
#original message read as bytes, result is also as bytes.
finished_message = m.change_message(original_message_bytes) #will print a warning if resulting injected bytes are larger in size than the original

Needs a customizer (decompressed field scripts) to actually be able to do the injection in the first place.

Escape codes: 
	^p - Plain text F2 02 01 FF
	^r - Red text F2 02 02 FF
	^b - Blue text F2 02 03 FF
	^y - Yellow text F2 02 04 FF
	^g - Green text F2 02 05 FF
	^n - New line 0A
	^x - End text box 0a F1 04 F2 08 FF FF
	^m - End message 0a f1 04 00
If you're using any color other than plain text, it's best to start the next text with ^p as a sort of ending tag. Use a period if you need to.

Note: Hasn't been super extensively tested. Let PinkPajamas know if there are any bugs with this.
'''
pixels_per_line = 420
kerning = {" ": 8,"!": 9,'"': 8,'#': 13,'$': 12,'%': 19,'&': 13,"'": 4,'(': 11,')': 11,'*': 11,'+': 14,',': 6,'-': 13,'.': 6,'/': 13,'0': 13,'1': 11,'2': 12,'3': 13,'4': 12,'5': 13,'6': 12,'7': 12,'8': 13,'9': 13,':': 9,';': 9,'<': 14,'=': 14,'>': 14,'?': 13,'@': 17,'A': 13,'B': 14,'C': 17,'D': 14,'E': 14,'F': 14,'G': 17,'H': 14,'I': 6,'J': 11,'K': 14,'L': 13,'M': 16,'N': 14,'O': 17,'P': 12,'Q': 17,'R': 12,'S': 13,'T': 12,'U': 13,'V': 15,'W': 20,'X': 14,'Y': 12,'Z': 15,'[': 11,'\\': 17,']': 12,'_': 13,'`': 15,'a': 12,'b': 11,'c': 11,'d': 12,'e': 12,'f': 8,'g': 12,'h': 13,'i': 7,'j': 7,'k': 10,'l': 6,'m': 19,'n': 13,'o': 14,'p': 14,'q': 14,'r': 7,'s': 13,'t': 7,'u': 13,'v': 12,'w': 16,'x': 12,'y': 13,'z': 11,'{': 11,'|': 9,'}': 11,'~': 15}
#escape codes
ep = [0xF2, 0x02, 0x01, 0xFF]
er = [0xF2, 0x02, 0x02, 0xFF]
eb = [0xF2, 0x02, 0x03, 0xFF]
ey = [0xF2, 0x02, 0x04, 0xFF]
eg = [0xF2, 0x02, 0x05, 0xFF]
en = [0x0A]
ex = [0x0A, 0xF1, 0x04, 0xF2, 0x08, 0xFF, 0xFF]
em = [0x0A, 0xF1, 0x04, 0x00]

def byte_str_to_bytes(s):
    bytes_str = s.split(' ')
    bytes = []
    for b in bytes_str:
        bytes.append(int(b,base=16))
    return bytes
def bytes_to_byte_str(b):
    return ' '.join('%02x'%i for i in b)

#adding only - least significant left side
def multi_byte_add(ls,rs):
    if len(ls) < len(rs):
        return multi_byte_add(rs,ls)
    rs_mod = rs
    while len(ls) > len(rs_mod):
        rs_mod = rs_mod + [0]
    ret = [0]*len(ls)
    carry=0
    for i in range(len(ls)):
        sum = ls[i] + rs_mod[i] + carry
        carry=0
        while sum > 255:
            sum -= 256
            carry += 1
        ret[i] = sum
    return ret

#subtraction only - least significant left side
def multi_byte_sub(ls,rs):
    if len(ls) < len(rs):
        print "Error in multi_byte_sub. Subtracting a smaller byte range to a larger byte range."
        return [0]
    rs_mod = rs
    while len(ls) > len(rs_mod):
        rs_mod = rs_mod + [0]
    ret = [0]*len(ls)
    carry = 0
    for i in range(len(ls)):
        sum = ls[i] - rs_mod[i] - carry
        carry = 0
        while sum < 0:
            sum+=256
            carry += 1
        ret[i] = sum
    return ret
        
class message:
    def __init__(self):
        self.str = ""
        self.relative_pointers = []
        self.bytes = None
    def __init__(self,str):
        self.space_text(str) #sets self.str to spaced correctly text
        self.str_to_bytes()
    ''' 0x17 - Label
        0x02 - # of text boxes
        0x02 - Speaker name index (05 is "Soul", 00 is nothing)
        0x04 - 1st text box pointer
        0x04 - 2nd text box pointer
    '''
    #Take the message of the object and inject it into given message bytes. 
    #Returns injected message and does not change the message object.
    def change_message(self, original_bytes):
        #don't change the label
        retbytes = original_bytes[:24]
        #change number of text boxes
        #print "original_bytes", original_bytes
        original_text_box_count = original_bytes[24]
        #print "original text box count", original_text_box_count
        #print "relative pointers", self.relative_pointers
        delta_text_boxes = len(self.relative_pointers) - original_text_box_count
        #print "delta_text_boxes",delta_text_boxes
        retbytes.append(len(self.relative_pointers))
        #don't change the speaker name
        retbytes.extend(original_bytes[25:28])
        #change each pointer, keep in mind there is an offset with delta text boxes *4
        #absolute_pointer = original_bytes[29:33] + delta_text_boxes * 4
        if delta_text_boxes < 0:
            absolute_pointer = multi_byte_sub(original_bytes[28:32], [delta_text_boxes * -4])
        else:
            absolute_pointer = multi_byte_add(original_bytes[28:32], [delta_text_boxes * 4])
        #print "absolute_pointer", absolute_pointer
        #write the pointers
        for p in self.relative_pointers:
            if p!=0:
                retbytes.extend(multi_byte_add([p+4],absolute_pointer))#+4 for some reason fixes it??? I think it's because the first 4 bytes is displayed for what I thought was the header and it does something that you can't normally see.
            else:
                retbytes.extend(multi_byte_add([p],absolute_pointer))
        #keep message header
        retbytes.extend(original_bytes[28 + (original_text_box_count * 4): 40 + (original_text_box_count * 4)])
        #write shit in
        for b in self.bytes:
            retbytes.append(b)
        #note if you go over. That is a whole can of worms right there.
        if len(retbytes) > len(original_bytes):
            print "BIG WARNING: New byte count exceeds old byte count. This will break something else."
        return retbytes
    '''
    ^p - Plain text F2 02 01 FF
	^r - Red text F2 02 02 FF
	^b - Blue text F2 02 03 FF
	^y - Yellow text F2 02 04 FF
	^g - Green text F2 02 05 FF
	^n - New line 0A
	^x - End text box 0a F1 04 F2 08 FF FF
	^m - End message 0a f1 04 00
    '''
    #use self.str to fill in self.bytes and self.relative_pointers
    def str_to_bytes(self):
        #print "spaced str:",self.str
        byte_count = 0
        in_escape = False
        bytes_by_int = []
        relative_pointers = [0]
        for c in self.str:
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
                    relative_pointers.append(byte_count)
                elif c == "m":
                    bytes_by_int.extend(em)
                    byte_count +=len(em)
                in_escape=False
            elif c == "^":
                in_escape = True
            else:
                bytes_by_int.append(ord(c))
                byte_count+=1
        self.relative_pointers = relative_pointers
        self.bytes = bytes_by_int
    #Append the message word by word and determine what the whitespace is.
    def space_text(self,str):
        lines = []
        word = ""
        processed_str = str
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
                    print "WARNING: Escape character as last character. Ignoring."
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
                    print "WARNING: Unknown escape character: '",esc_ch,"'. Ignoring."
            elif ch not in kerning:
                print "WARNING: Kerning of ",ch," is unknown. Removing character"
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
        #Cleanup: Append the last word and add ^m. Also check if there needs to be a textbox for the last word.
#In these examples, "the_dude" is the guy near the shibuya terminal that says how everything revolves around Macca.
#example using a large amount of text
def large_text_test():
    the_dude_original_byte_string = '46 30 31 37 5F 53 49 4E 45 4E 5F 30 33 00 00 00 00 00 00 00 00 00 00 00 03 00 05 00 FC 9C 44 01 38 9D 44 01 88 9D 44 01 B4 00 00 00 F2 08 FF FF F2 07 07 FF 54 68 65 20 6F 6D 6C 79 20 63 75 72 72 65 6E 63 79 20 69 6E 20 74 68 69 73 20 77 6F 72 6C 64 20 69 73 0A F2 02 02 FF 4D 61 63 63 61 F2 02 01 FF 2E 0A F1 04 F2 08 FF FF 44 65 6D 6F 6E 73 20 61 6E 64 20 73 68 61 64 79 20 73 74 6F 72 65 73 20 6D 61 79 20 61 73 6B 0A 66 6F 72 20 67 65 6D 73 2C 20 62 75 74 20 69 74 20 61 6C 6C 20 63 6F 6D 65 73 20 64 6F 77 6E 20 74 6F 0A 4D 61 63 63 61 2E 0A F1 04 F2 08 FF FF 59 6F 75 20 63 61 6E 20 62 75 79 20 61 6E 79 74 68 69 6E 67 20 77 69 74 68 20 4D 61 63 63 61 21 0A F1 04 00'
    the_dude_original_bytes = byte_str_to_bytes(the_dude_original_byte_string)
    test_str = 'So basically, whenever a demon has been fully analyzed, it will give you its source the next time it gains a level. A demon source contains a maximum of three fixed skills and one bonus skill, which is drawn from the current skill pool (moveset) of that demon. This guide\'s purpose is not to provide an in-depth explanation of the demon source mechanics, so if you\'re looking for those, I refer you to Zeruel\'s "Game Mechanics / Demon Database" guide. Shin Megami Tensei: Strange Journey is a pretty easy game until you encounter a sector\'s boss and need to access certain skills that can help you out to hit its weakness or a specific skill to buff your team/debuff the boss. Since there\'s no list of the best sources and passwords to summon their demons I decided to create this guide. What makes this demon source compendium special is the demons\' experience. These aren\'t just the base passwords for the demons listed, the demons have all been levelled to the point where one battle should level them up (xperience needed for the next level varies from 16 to 250). With that in mind, you can summon any of these demons, go back to sector Antlia, enter a random battle and defend for about 40 turns. That should bring its analysis level to the maximum. After that, save the game, enter one of the later sectors and do some random battles (one should be enough though) to level up the demon and obtain its source. If the source contains the bonus skills you wanted, save the game. If it didn\'t, you can keep resetting and doing some quick battles until you obtain the source you were after. The next section contains all the demons whose source I considered useful. All of these demons only contain their innate skills, so you don\'t need to worry about having access to an overpowered skill way before you normally are able to. If you want early access to sources with the better skills and combo sources (like a magic skill + its amp, or luster candy/debilitate) you should read the section thereafter. That section is still under construction though.'
    m = message(test_str)
    finished_message = m.change_message(the_dude_original_bytes)
    print "Resulting bytes:"
    print bytes_to_byte_str(finished_message)
'''
	^p - Plain text F2 02 01 FF
	^r - Red text F2 02 02 FF
	^b - Blue text F2 02 03 FF
	^y - Yellow text F2 02 04 FF
	^g - Green text F2 02 05 FF
	^n - New line 0A
	^x - End text box 0a F1 04 F2 08 FF FF
	^m - End message 0a f1 04 00
'''
#Example using escape codes
def color_text_test():
    the_dude_original_byte_string = '46 30 31 37 5F 53 49 4E 45 4E 5F 30 33 00 00 00 00 00 00 00 00 00 00 00 03 00 05 00 FC 9C 44 01 38 9D 44 01 88 9D 44 01 B4 00 00 00 F2 08 FF FF F2 07 07 FF 54 68 65 20 6F 6D 6C 79 20 63 75 72 72 65 6E 63 79 20 69 6E 20 74 68 69 73 20 77 6F 72 6C 64 20 69 73 0A F2 02 02 FF 4D 61 63 63 61 F2 02 01 FF 2E 0A F1 04 F2 08 FF FF 44 65 6D 6F 6E 73 20 61 6E 64 20 73 68 61 64 79 20 73 74 6F 72 65 73 20 6D 61 79 20 61 73 6B 0A 66 6F 72 20 67 65 6D 73 2C 20 62 75 74 20 69 74 20 61 6C 6C 20 63 6F 6D 65 73 20 64 6F 77 6E 20 74 6F 0A 4D 61 63 63 61 2E 0A F1 04 F2 08 FF FF 59 6F 75 20 63 61 6E 20 62 75 79 20 61 6E 79 74 68 69 6E 67 20 77 69 74 68 20 4D 61 63 63 61 21 0A F1 04 00'
    the_dude_original_bytes = byte_str_to_bytes(the_dude_original_byte_string)
    test_str = "Time^nfor^nsome^n^bC^ro^yl^go^rr^x^pHow was it?"
    m = message(test_str)
    finished_message = m.change_message(the_dude_original_bytes)
    print "Resulting bytes:"
    print bytes_to_byte_str(finished_message)
#Mostly here to make sure byte subtraction works
def small_text_test():
    the_dude_original_byte_string = '46 30 31 37 5F 53 49 4E 45 4E 5F 30 33 00 00 00 00 00 00 00 00 00 00 00 03 00 05 00 FC 9C 44 01 38 9D 44 01 88 9D 44 01 B4 00 00 00 F2 08 FF FF F2 07 07 FF 54 68 65 20 6F 6D 6C 79 20 63 75 72 72 65 6E 63 79 20 69 6E 20 74 68 69 73 20 77 6F 72 6C 64 20 69 73 0A F2 02 02 FF 4D 61 63 63 61 F2 02 01 FF 2E 0A F1 04 F2 08 FF FF 44 65 6D 6F 6E 73 20 61 6E 64 20 73 68 61 64 79 20 73 74 6F 72 65 73 20 6D 61 79 20 61 73 6B 0A 66 6F 72 20 67 65 6D 73 2C 20 62 75 74 20 69 74 20 61 6C 6C 20 63 6F 6D 65 73 20 64 6F 77 6E 20 74 6F 0A 4D 61 63 63 61 2E 0A F1 04 F2 08 FF FF 59 6F 75 20 63 61 6E 20 62 75 79 20 61 6E 79 74 68 69 6E 67 20 77 69 74 68 20 4D 61 63 63 61 21 0A F1 04 00'
    the_dude_original_bytes = byte_str_to_bytes(the_dude_original_byte_string)
    test_str = "Hi! :)"
    m = message(test_str)
    finished_message = m.change_message(the_dude_original_bytes)
    print "Resulting bytes:"
    print bytes_to_byte_str(finished_message)
#large_text_test()
#color_text_test()
#small_text_test()