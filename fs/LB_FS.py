import struct
import re
from io import BytesIO

from fs.fs_utils import *

SECTOR_SIZE = 2048

# Code based off of https://github.com/TGEnigma/AtlusFileSystemLibrary
class LBFileEntry(object):
    def __init__(self):
        self.user_id = None 
        # self.handle = None

    def read(self, offset, data):
        # self.handle = handle
        self.entry_type = int(data[0])
        self.compressed = int(data[1])
        self.user_id = int(struct.unpack('<H', data[2:4])[0])
        self.size = int(struct.unpack('<I', data[4:8])[0]) - 16
        self.extension = data[8:12].decode().replace('\0', '')
        self.decompressed_size = int(struct.unpack('<I', data[12:16])[0])
        self.offset = offset
        # self.name = ''.join([str(handle), '_', str(self.user_id), ".", self.extension.replace('\0', '')])
        self.name = ''.join([str(self.user_id), ".", self.extension])

    def decompress(self, lb_file):
        self.decompressed = []

        lb_file.seek(self.offset)
        while len(self.decompressed) < self.decompressed_size:
            op = read_byte(lb_file)
            
            count = op & 0x1F
            if count == 0:
                count = read_halfword(lb_file)

            opcode = (op >> 4) & 0xE
            # CopyBytes
            if opcode == 0x0:
                for i in range(count):
                    self.decompressed.append(read_byte(lb_file))
            # RepeatZero
            elif opcode == 0x2:
                for i in range(count):
                    self.decompressed.append(0)
            # RepeatByte
            elif opcode == 0x4:
                b = read_byte(lb_file)
                for i in range(count):
                    self.decompressed.append(b)
            # CopyBytesFromOffset
            elif opcode == 0x6:
                offset = read_byte(lb_file)
                for i in range(count):
                    b = self.decompressed[(len(self.decompressed) - 1) + -offset + 1]
                    self.decompressed.append(b)
            # CopyBytesFromLargeOffset
            elif opcode == 0x8:
                offset = read_halfword(lb_file)
                for i in range(count):
                    b = self.decompressed[(len(self.decompressed) - 1) + -offset + 1]
                    self.decompressed.append(b)
            # CopyBytesZeroInterleaved
            elif opcode == 0xA:
                for i in range(count):
                    self.decompressed.append(read_byte(lb_file))
                    self.decompressed.append(0)
            else:
                print("Error at " + hex(lb_file.tell()) + " with unknown opcode " + hex(opcode))
                return

        return BytesIO(bytes(self.decompressed))

class LB_FS(object):
    def __init__(self, lb_file):
        self.lb_file = lb_file
        self.changes = {}

    def read_lb(self):
        self.file_entries = {}

        current_offset = 0
        file_size = file_len(self.lb_file)
        self.lb_file.seek(0)

        while current_offset < file_size:
            entry_data = read_bytes(self.lb_file, current_offset, 16)
            if entry_data[0] == 0xFF:
                break

            entry = LBFileEntry()
            entry_offset = self.lb_file.tell()
            # entry_handle = len(self.file_entries)
            entry.read(entry_offset, entry_data)

            self.file_entries[entry.extension] = entry
            current_offset += (entry.size + 16)
            if current_offset % 64 != 0:
                current_offset += 64 - (current_offset % 64)

    def pad_lb_by(self, amount):
        self.output_lb.write(b"\0"*amount)

    def align_lb_to(self, size):
        offset = self.output_lb.tell()
        if offset % size != 0:
            padding_needed = size - (offset % size)
            self.pad_lb_by(padding_needed)

    def get_file_by_entry(self, entry):
        data = read_bytes(self.lb_file, entry.offset, entry.size)

        return data

    def get_file_by_extension(self, extension):
        entry = self.file_entries[extension]
        assert entry is not None

        return self.get_file_by_entry(entry)

    def add_new_file(self, extension, data):
        new_entry = LBFileEntry()        
        new_entry.entry_type = 1
        new_entry.compressed = 0
        if self.file_entries.get(extension):
            new_entry.user_id = self.file_entries[extension].user_id
        else:
            new_entry.user_id = len(self.file_entries) + 1
        new_entry.size = file_len(data)
        new_entry.extension = extension
        new_entry.decompressed_size = new_entry.size
        new_entry.name = ''.join([str(new_entry.user_id), ".", extension])

        self.file_entries[extension] = new_entry
        self.changes[extension] = data

    def export_lb(self, changes={}):
        self.changes.update(changes)
        self.output_lb = BytesIO()

        for extension in self.changes:
            #if not self.get_file_by_extension(extension):
            self.add_new_file(extension, self.changes[extension])

        file_entries_in_order = [entry for name, entry in self.file_entries.items()]
        file_entries_in_order.sort(key=lambda e: e.user_id)

        for e in file_entries_in_order:
            current_offset = self.output_lb.tell()
            write_byte(self.output_lb, current_offset, e.entry_type)
            write_byte(self.output_lb, current_offset + 1, e.compressed)
            write_halfword(self.output_lb, current_offset + 2, e.user_id)
            extension = e.extension.upper().ljust(4, '\0')
            write_word(self.output_lb, current_offset + 4, e.size + 16)
            write_bytes(self.output_lb, current_offset + 8, extension.encode())
            write_word(self.output_lb, current_offset + 12, e.decompressed_size)

            if e.extension in self.changes:
                data = self.changes[e.extension]
                data.seek(0)
                self.output_lb.write(data.read())
            else:
                self.output_lb.write(self.get_file_by_entry(e))

            self.align_lb_to(64)

        # write end entry
        current_offset = self.output_lb.tell()
        end = bytes([0xFF, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x45, 0x4E, 0x44, 0x30, 0x00, 0x00, 0x00, 0x00])
        write_bytes(self.output_lb, current_offset, end)
        self.align_lb_to(64)

        return self.output_lb

    def export_decompressed_lb(self):
        changes = self.decompress_files()
        return self.export_lb(changes)

    def decompress_files(self):
        decompressed_entries = {}
        for e in self.file_entries.values():
            if e.compressed == 1:
                decompressed_entries[e.extension] = e.decompress(self.lb_file)
            else:
                decompressed_entries[e.extension] = self.get_file_by_entry(e)

        return decompressed_entries