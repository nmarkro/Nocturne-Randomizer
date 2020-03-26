import nocturne_script_assembler as assembler
import customizer_values as custom_vals

from io import BytesIO

from fs.Iso_FS import *
from fs.DDS3_FS import *
from fs.LB_FS import *

# gets the script object from dds3 fs by provided path
def get_script_obj_by_path(dds3, script_path):
    script = bytearray(dds3.get_file_from_path(script_path).read())
    return assembler.parse_binary_script(script)

# open the ISO and parse it
iso = IsoFS('rom/input.iso')
iso.read_iso()
'''
# get the ddt and write it out to disk
ddt_file = iso.get_file_from_path('DDS3.DDT;1')
with open('rom/old_DDS3.DDT', 'wb') as file:
    file.write(ddt_file.read())

# get the img and write it out to disk in chucks due to size
with open('rom/old_DDS3.IMG', 'wb') as file:
    for chunk in iso.read_file_in_chunks('DDS3.IMG;1'):
        file.write(chunk)
'''
# parse the dds3 fs
dds3 = DDS3FS('rom/old_DDS3.DDT', 'rom/old_DDS3.IMG')
dds3.read_dds3()

credit_str = "#ASM file of a SMT:Nocturne script\n#Generated using Nocturne Script Assembler by PinkPajamas and DDS3 FileSystem by NMarkro. Special thanks to TGEnigma.\n#COMM descriptions are made in func_descs.py\n#Send any requests or bugs to PinkPajamas\n\n"

for script_name,script_path in custom_vals.SCRIPT_OBJ_PATH.items():
    print ("Creating ASM for",script_name)
    if script_name != "e810":
        bf_obj = get_script_obj_by_path(dds3,script_path)
        out_str = credit_str + bf_obj.exportASM()
        outfile = open("scripts/"+script_name+".bfasm",'w')
        outfile.write(out_str)
        outfile.close()