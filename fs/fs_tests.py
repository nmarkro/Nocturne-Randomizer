import os
from Iso_FS import *
from DDS3_FS import *
from LB_FS import *

# Field LB decompression example

# open the iso and parse it
print("opening iso")
iso = IsoFS('../rom/input.iso')
iso.read_iso()

# get the ddt and write it out to disk
print("exporting old DDS3 fs")
ddt_file = iso.get_file_from_path('DDS3.DDT;1')
with open('old_DDS3.DDT', 'wb') as file:
    file.write(ddt_file.read())

# get the img and write it out to disk in chucks due to size
with open('old_DDS3.IMG', 'wb') as file:
    for chunk in iso.read_file_in_chunks('DDS3.IMG;1'):
        file.write(chunk)

# open the dds3 fs and parse it
print("opening DDS3 fs")
dds3 = DDS3FS('old_DDS3.DDT', 'old_DDS3.IMG')
dds3.read_dds3()

print("uncompressing field lb files")
# go through the /fld/f folder looking for files that end in '_000.LB'
fld_lbs = []
for name, entry in dds3.find_by_path('/fld/f').children.items():
    if entry.is_dir:
        for subname, subentry in entry.children.items():
            if subname.endswith('_000.LB'):
                fld_lbs.append(subentry)

# decompress those files and add them to a dict to write back later
uncompressed_lb = {}
for entry in fld_lbs:
    lb_file_data = dds3.get_file_from_path(entry.path)
    lb = LBFS(lb_file_data)
    lb.read_lb()

    lb = lb.export_decompressed_lb()
    uncompressed_lb[entry.path] = lb

# write the new dds3 fs out to disk
print("exporting new DDS3 fs")
dds3.export_dds3('DDS3.DDT', 'DDS3.IMG', uncompressed_lb)

# remove the DUMMY file to save space and export the iso with the changed dds3 fs
# should probably figure out a way to do this in chunks
# currently it loads the entire 2gb img file into RAM lmao
print("exporting new iso")
iso.rm_file("DUMMY.DAT;1")
with open('DDS3.DDT', 'rb') as ddt, open('DDS3.IMG', 'rb') as img:
    changes = {
        'DDS3.DDT;1': ddt,
        'DDS3.IMG;1': img
    }

    iso.export_iso('../rom/test.iso', {'DDS3.DDT;1': ddt, 'DDS3.IMG;1': img})

# delete the temp files for the user
print("cleaning up files")
os.remove('old_DDS3.DDT')
os.remove('old_DDS3.IMG')
os.remove('DDS3.DDT')
os.remove('DDS3.IMG')