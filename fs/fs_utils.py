import struct

# calculate the size of a file
def file_len(data):
    data.seek(0, 2)
    return data.tell()

def read_bytes(data, offset, length):
    data.seek(offset)
    return data.read(length)

# there is no reason to read in "be" form
def read_byte(data, offset=None):
    if offset:
        data.seek(offset)
    return struct.unpack("<B", data.read(1))[0]

def read_halfword(data, offset=None):
    if offset:
        data.seek(offset)
    return struct.unpack("<H", data.read(2))[0]

def read_word(data, offset=None):
    if offset:
        data.seek(offset)
    return struct.unpack("<I", data.read(4))[0]

def read_signed_word(data, offset=None):
    if offset:
        data.seek(offset)
    return struct.unpack("<i", data.read(4))[0]

# by default write data in "le" form
def write_bytes(data, offset, bytes):
    data.seek(offset)
    data.write(bytes)

def write_byte(data, offset, value):
    write_byte_le(data, offset, value)

def write_halfword(data, offset, value):
    write_halfword_le(data, offset, value)

def write_word(data, offset, value):
    write_word_le(data, offset, value)

def write_byte_le(data, offset, value):
    value = struct.pack("<B", value)
    data.seek(offset)
    data.write(value)

def write_byte_be(data, offset, value):
    value = struct.pack(">B", value)
    data.seek(offset)
    data.write(value)

def write_halfword_le(data, offset, value):
    value = struct.pack("<H", value)
    data.seek(offset)
    data.write(value)

def write_halfword_be(data, offset, value):
    value = struct.pack(">H", value)
    data.seek(offset)
    data.write(value)

def write_word_le(data, offset, value):
    value = struct.pack("<I", value)
    data.seek(offset)
    data.write(value)

def write_word_be(data, offset, value):
    value = struct.pack(">I", value)
    data.seek(offset)
    data.write(value)

def write_signed_word(data, offset, value):
    value = struct.pack("<i", value)
    data.seek(offset)
    data.write(value)