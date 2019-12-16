import struct
import os
from io import BytesIO

from fs_utils import *

SECTOR_SIZE = 2048
SYSTEM_HEADER_SIZE = 32768

class IsoFileEntry(object):
    def __init__(self):
        self.parent = None
        self.is_dir = False

    def read(self, entry_offset, data):
        self.entry_offset = entry_offset
        self.entry_length = len(data)
        self.location = int(struct.unpack('<I', data[2:6])[0])
        self.size = int(struct.unpack('<I', data[10:14])[0])
        self.flags = int(data[25])
        self.volume = int(struct.unpack('<H', data[28:30])[0])

        name_length = int(data[32])

        if name_length == 1:
            c = chr(data[33])
            if c == '\u0000':
                self.name = "."
            elif c == '\u0001':
                self.name = ".."
            else:
                self.name = c.decode()
        else:
            self.name = data[33:33+name_length].decode()

        if self.flags == 2:
            self.is_dir = True
            self.children = {}

class IsoFS(object):
    def __init__(self, iso_path):
        self.iso_path = iso_path
        self.changes = {}

    def read_iso(self):
        self.iso_file = open(self.iso_path, "rb")

        # test if first volume is primary (should be for nocturne)
        assert read_byte(self.iso_file, SYSTEM_HEADER_SIZE) == 1 
        assert read_bytes(self.iso_file, SYSTEM_HEADER_SIZE + 1, 5).decode() == "CD001"

        self.file_entries = {}

        root_file_entry_length = read_byte(self.iso_file, SYSTEM_HEADER_SIZE + 156)
        root_file_entry_data = read_bytes(self.iso_file, SYSTEM_HEADER_SIZE + 156, root_file_entry_length)

        self.root = IsoFileEntry()
        self.root.read(SYSTEM_HEADER_SIZE + 156, root_file_entry_data)
        self.root.name = ""
        self.root.file_path = ""
        self.file_entries[self.root.file_path] = self.root

        self.read_directory(self.root, None)

        self.iso_file.close()
        self.iso_file = None

    # parses each entry in the directory
    def read_directory(self, directory_entry, path):
        directory_offset = directory_entry.location * SECTOR_SIZE
        current_offset = directory_offset

        remaining_size = directory_entry.size

        while remaining_size > 0:
            entry_length = read_byte(self.iso_file, current_offset)
            if entry_length == 0:
                break
            remaining_size -= entry_length

            data = read_bytes(self.iso_file, current_offset, entry_length)

            entry = IsoFileEntry()
            entry.read(current_offset, data)

            entry.parent = directory_entry
            directory_entry.children[entry.name] = entry

            current_offset += entry_length
            if entry.name == "." or entry.name == "..":
                continue

            if path:
                file_path = '/'.join([path, entry.name])
            else:
                file_path = entry.name
            entry.file_path = file_path

            if entry.is_dir:
                self.read_directory(entry, file_path)
                
            self.file_entries[entry.file_path] = entry

    # return the entry object for provided path
    def find_by_path(self, path):
        entry = self.file_entries.get(path)
        return entry

    # delete a file entry from it's parent directory
    def rm_file(self, path):
        entry = self.find_by_path(path)
        assert entry is not None
        del self.file_entries[entry.name]
        del entry.parent.children[entry.name]

    # writes back a directory entry
    def write_directory(self, directory_entry):
        for entry in directory_entry.children.values():
            # update each entries' offset used in the parent directory table here
            offset = self.output_iso.tell()
            entry.entry_offset = offset

            write_byte(self.output_iso, offset, entry.entry_length)
            # padding
            write_byte(self.output_iso, offset + 1, 0)

            # we are going to rewrite the new location and size later
            write_word_le(self.output_iso, offset + 2, entry.location)
            write_word_be(self.output_iso, offset + 6, entry.location)
            if entry.is_dir:
                # I'm too lazy to actually calculate this
                # so write the max sector size back to every directory entries' size
                # this really shouldn't matter, ultraiso does this anyways lmao
                write_word_le(self.output_iso, offset + 10, SECTOR_SIZE)
                write_word_be(self.output_iso, offset + 14, SECTOR_SIZE)
            else:
                write_word_le(self.output_iso, offset + 10, entry.size)
                write_word_be(self.output_iso, offset + 14, entry.size)

            # padding 
            write_bytes(self.output_iso, offset + 18, b"\0\0\0\0\0\0\0")
            write_byte(self.output_iso, offset + 25, entry.flags)
            # more padding 
            write_bytes(self.output_iso, offset + 26, b"\0\0")
            write_halfword_le(self.output_iso, offset + 28, entry.volume)
            write_halfword_be(self.output_iso, offset + 30, entry.volume)

            # reconvert back the "." and ".." names
            name = entry.name
            if name == '.':
                name = '\u0000'
            elif name == '..':
                name = '\u0001'
            write_byte(self.output_iso, offset + 32, len(name))

            # each entry should start on an even offset
            padding_length = (entry.entry_length - 33) - len(name)
            padding = b"\0"*padding_length
            write_bytes(self.output_iso, offset + 33, name.encode() + padding)

    def pad_iso_by(self, amount):
        self.output_iso.write(b"\0"*amount)

    def align_iso_to(self, size):
        offset = self.output_iso.tell()
        if offset % size != 0:
            padding_needed = size - (offset % size)
            self.pad_iso_by(padding_needed)

    # copy 1:1 from the original iso in chunks to save on memory usage
    def copy_from_input(self, offset, size, chunk_size=1024*1024):
        size_remaining = size
        input_offset = 0
        while size_remaining > 0:
            size_to_read = min(size_remaining, chunk_size)

            with open(self.iso_path, 'rb') as iso_file:
                data = read_bytes(iso_file, offset + input_offset, size_to_read)
            self.output_iso.write(data)

            size_remaining -= size_to_read
            input_offset += size_to_read

    def update_entry_info(self, entry, new_location, new_size):
        # save the current position in the file because align_iso_to() gets called after this
        saved_pos = self.output_iso.tell()
        offset = entry.entry_offset
        # update the directory entry for the file with it's new location and size
        write_word_le(self.output_iso, offset + 2, new_location)
        write_word_be(self.output_iso, offset + 6, new_location)
        write_word_le(self.output_iso, offset + 10, new_size)
        write_word_be(self.output_iso, offset + 14, new_size)
        # re-seek to original position
        self.output_iso.seek(saved_pos)

    # used to read full files from the iso
    def get_file_from_path(self, path):
        entry = self.find_by_path(path)
        assert entry is not None

        offset = entry.location * SECTOR_SIZE
        size_to_read = entry.size

        with open(self.iso_path, 'rb') as iso_file:
            iso_file.seek(offset)
            data = BytesIO(iso_file.read(size_to_read))
        return data

    # used to read very large files from the iso in chunks
    def read_file_in_chunks(self, path, chunk_size=1024*1024):
        entry = self.find_by_path(path)
        assert entry is not None

        base_offset = entry.location * SECTOR_SIZE
        size_remaining = entry.size
        current_offset = 0

        while size_remaining > 0:
            size_to_read = min(size_remaining, chunk_size)

            with open(self.iso_path, 'rb') as iso_file:
                data = read_bytes(iso_file, base_offset + current_offset, size_to_read)

            size_remaining -= size_to_read
            current_offset += size_to_read

            yield data

    # make new entries and add them to the correct directory entry
    def add_new_file(self, path, data):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        new_entry = IsoFileEntry()
        new_entry.name = basename
        # entry_offset gets updated later so we don't need to calculate it here
        new_entry.entry_offset = None
        new_entry.size = file_len(data)
        new_entry.flags = 0
        # nocturne only uses 1 volume (I think)
        new_entry.volume = 1
        # set location to max word so that new files will always be written after everything else
        new_entry.location = 0xFFFFFFFF
        # each entry should start on an even offset
        new_entry.entry_length = len(new_entry.name) + 33
        new_entry.entry_length += new_entry.entry_length % 2
        new_entry.file_path = path

        parent = self.find_by_path(dirname)
        new_entry.parent = parent
        parent.children[new_entry.name] = new_entry
        self.file_entries[path] = new_entry
        self.changes[path] = data

    def export_iso(self, output_path, changes):
        self.changes.update(changes)
        # make sure any new/changed files get correctly added to each directory's table
        for path in self.changes:
            if not self.find_by_path(path):
                self.add_new_file(path, self.changes[path])

        self.output_iso = open(output_path, 'wb')

        # write back files in the order they were original in
        file_entries_in_order = [entry for path, entry in self.file_entries.items()]
        file_entries_in_order.sort(key=lambda e: e.location)

        # copy the input iso 1:1 until the root entry
        # I don't want to update each path table because adding directories isn't going to be done
        # I'm assuming the ps2 uses the system header for some stuff so write it 1:1
        size_until_root = self.root.location * SECTOR_SIZE
        self.copy_from_input(0, size_until_root)

        for entry in file_entries_in_order:
            new_location = int(self.output_iso.tell() / SECTOR_SIZE)
            size = entry.size

            if entry.file_path in self.changes:
                data = self.changes[entry.file_path]
                data.seek(0)
                self.output_iso.write(data.read())
                size = file_len(data)
            else:
                # unchanged files should just be copied 1:1 from the input iso
                if entry.is_dir:
                    self.write_directory(entry)
                else:
                    offset = entry.location * SECTOR_SIZE
                    self.copy_from_input(offset, size)

            if not entry.is_dir:
                self.update_entry_info(entry, new_location, size)
            self.align_iso_to(SECTOR_SIZE)

        # update a few parts of the primary volume
        end_size = int(self.output_iso.tell() / SECTOR_SIZE)
        write_word_le(self.output_iso, SYSTEM_HEADER_SIZE + 80, end_size)
        write_word_be(self.output_iso, SYSTEM_HEADER_SIZE + 84, end_size)

        write_word_le(self.output_iso, SYSTEM_HEADER_SIZE + 166, SECTOR_SIZE)
        write_word_be(self.output_iso, SYSTEM_HEADER_SIZE + 170, SECTOR_SIZE)

        self.output_iso.close()
        self.output_iso = None

# various tests/examples of how the api will be used
# the actual functionally the randomizer will use is:
# 1. parsing the DDS3 file systems (DDS3.IMG, DDS3.DDT)
# 2. rewriting changed versions of the DDS3 file systems with uncompressed scripts
# 3. getting the game binary for randomization
# things the api cannot/won't currently do:
# 1. create new directories
# 2. update path tables
# and probably some other stuff I'm forgetting

# iso = IsoFS('../rom/input.iso')
# iso.read_iso()

# for path, e in iso.file_entries.items():
#     print(e.name + " - " + str(e.location))
# print()

# iso.rm_file("DUMMY.DAT;1")

# test_file = BytesIO(b"New test file has been written (and to a sub directory!)")
# test_file_path = "IRX/TEST.TXT;1"

# iso.add_new_file(test_file_path, test_file)

# for path, e in iso.file_entries.items():
#     print(e.name + " - " + str(e.location) + " - " + e.file_path)
# print()

# system_cnf_file_path = "SYSTEM.CNF;1"
# system_cnf_file = iso.get_file_from_path(system_cnf_file_path)
# print(system_cnf_file.read().decode())
# new_system_cnf_file = BytesIO(b"File has been updated")
# changes = {
#     system_cnf_file_path: new_system_cnf_file,
# }

# iso.export_iso('../rom/test.iso', changes)

# output_iso = IsoFS('../rom/test.iso')
# output_iso.read_iso()

# output_test_file = output_iso.get_file_from_path(test_file_path)
# print(output_test_file.read().decode())

# output_system_cnf_file = output_iso.get_file_from_path(system_cnf_file_path)
# print(output_system_cnf_file.read().decode())