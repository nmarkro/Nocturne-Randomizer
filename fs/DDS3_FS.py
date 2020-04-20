import struct
import os
from io import BytesIO

from fs.fs_utils import *

SECTOR_SIZE = 2048

# Code based off of https://github.com/TGEnigma/AtlusFileSystemLibrary/
class DDS3FileEntry(object):
    def __init__(self):
        self.parent = None
        self.is_dir = False

    def read(self, ddt_file, data):
        self.name_offset = int(struct.unpack('<I', data[0:4])[0])
        # location is sector in IMG file not actual offset
        self.location = int(struct.unpack('<I', data[4:8])[0])
        self.size = int(struct.unpack('<i', data[8:12])[0])

        self.name = ""
        saved_pos = ddt_file.tell()
        if self.name_offset != 0:
            ddt_file.seek(self.name_offset)

            while True:
                c = ord(ddt_file.read(1))
                if c == 0:
                    break
                self.name += chr(c)
            ddt_file.seek(saved_pos)

        if self.size < 0:
            self.is_dir = True
            self.size = -self.size
            self.children = {}

class DDS3FS(object):
    def __init__(self, ddt_path, img_path):
        self.ddt_path = ddt_path
        self.img_path = img_path
        self.changes = {}

    def read_dds3(self):
        self.ddt_file = open(self.ddt_path, "rb")

        self.file_entries = {}
        self.root = self.read_entry(None)

        self.ddt_file.close()
        self.ddt_file = None

    def read_entry(self, parent):
        entry = DDS3FileEntry()
        # save the entry offset
        entry.offset = self.ddt_file.tell()
        entry.read(self.ddt_file, self.ddt_file.read(12))
        entry.parent = parent

        if parent:
            path = "/".join([parent.path, entry.name])
        else:
            path = entry.name
        entry.path = path

        if entry.is_dir:
            self.ddt_file.seek(entry.location)

            for i in range(entry.size):
                child_entry = self.read_entry(entry)
                entry.children[child_entry.name] = child_entry
                child_entry.parent = entry

            self.ddt_file.seek(entry.offset + 12)

        self.file_entries[entry.path] = entry
        return entry

    def find_by_path(self, path):
        entry = self.file_entries.get(path)
        return entry

    # used to read full files from the .img file
    def get_file_from_path(self, path, access_changes=True):
        if access_changes:
            if path in self.changes:
                data = self.changes[path]
                data.seek(0)
                return data

        entry = self.find_by_path(path)
        assert entry is not None

        offset = entry.location * SECTOR_SIZE
        size_to_read = entry.size

        with open(self.img_path, 'rb') as img_path:
            img_path.seek(offset)
            data = BytesIO(img_path.read(size_to_read))
        return data

    # make new entries and add them to the correct directory entry
    def add_new_file(self, path, data):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        new_entry = DDS3FileEntry()
        new_entry.name = basename
        # entry_offset gets updated later so we don't need to calculate it here
        new_entry.size = file_len(data)
        new_entry.location = 0xFFFFFFFF
        new_entry.path = path

        parent = self.find_by_path(dirname)
        new_entry.parent = parent
        parent.children[new_entry.name] = new_entry
        self.file_entries[path] = new_entry
        self.changes[path] = data

    def pad_file_by(self, file, amount):
        file.write(b"\0"*amount)

    def align_file_to(self, file, size):
        offset = file.tell()
        if offset % size != 0:
            padding_needed = size - (offset % size)
            self.pad_file_by(file, padding_needed)

    # copy 1:1 from the original img in chunks to save on memory usage
    def copy_from_input(self, offset, size, chunk_size=1024*1024):
        size_remaining = size
        input_offset = 0
        while size_remaining > 0:
            size_to_read = min(size_remaining, chunk_size)

            with open(self.img_path, 'rb') as img_file:
                data = read_bytes(img_file, offset + input_offset, size_to_read)
            self.output_img.write(data)

            size_remaining -= size_to_read
            input_offset += size_to_read

    def write_name_and_offset(self, entry):
        new_offset = self.output_ddt.tell()
        
        self.output_ddt.write(entry.name.encode() + b"\0")
        self.align_file_to(self.output_ddt, 4)
        saved_offset = self.output_ddt.tell()

        write_word(self.output_ddt, entry.offset, new_offset)

        self.output_ddt.seek(saved_offset)

    def write_offset(self, entry):
        saved_offset = self.output_ddt.tell()

        write_word(self.output_ddt, entry.offset + 4, saved_offset)

        self.output_ddt.seek(saved_offset)

    def write_entry(self, entry):
        # fill in the name_offset location later
        entry.offset = self.output_ddt.tell()
        self.output_ddt.write(b'\0'*4)

        if entry.name != "":
            self.post_writes.append((self.write_name_and_offset, entry))

        if entry.is_dir:
            self.output_ddt.write(b'\0'*4)
            self.post_writes.append((self.write_offset, entry))

            for child_entry in entry.children.values():
                self.post_writes.append((self.write_entry, child_entry))

            write_signed_word(self.output_ddt, entry.offset + 8, -len(entry.children))
        else:
            write_word(self.output_ddt, entry.offset + 4, entry.location)
            write_word(self.output_ddt, entry.offset + 8, entry.size)  


    def export_dds3(self, output_ddt_path, output_img_path, changes={}):
        self.changes.update(changes)
        self.post_writes = []

        for path in self.changes:
            if not self.find_by_path(path):
                self.add_new_file(path, self.changes[path])

        self.output_ddt = open(output_ddt_path, 'wb')
        self.output_img = open(output_img_path, 'wb')

        for entry in self.file_entries.values():
            if not entry.is_dir:
                new_location = int(self.output_img.tell() / SECTOR_SIZE)
                size = entry.size

                if entry.path in self.changes:
                    data = self.changes[entry.path]
                    data.seek(0)
                    self.output_img.write(data.read())
                    size = file_len(data)
                else:
                    offset = entry.location * SECTOR_SIZE
                    self.copy_from_input(offset, size)
                    
                entry.location = new_location
                entry.size = size

                self.align_file_to(self.output_img, SECTOR_SIZE)

        self.write_entry(self.root)
        for (f, entry) in self.post_writes:
            f(entry)

        self.output_ddt.close()
        self.output_img.close()  
        self.output_ddt = None
        self.output_img = None      

    def export_entry(self, entry, output_path):
        if entry.is_dir:
            if not os.path.exists(output_path):
                os.mkdir(output_path)

            for child_entry in entry.children.values():
                child_path = '/'.join([output_path, child_entry.name])
                self.export_entry(child_entry, child_path)
        else:
            with open(output_path, 'wb') as f:
                f.write(self.get_file_from_path(entry.path).read())

    def export_dds3_to_folder(self, output_path, changes={}):
        self.changes.update(changes)
        for path in self.changes:
            if not self.find_by_path(path):
                self.add_new_file(path, self.changes[path])

        self.export_entry(self.root, output_path)