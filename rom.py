import struct

# Location and size of SLUS_209.11 in the ISO 
BINARY_ADDR = 0xFD009000
BINARY_SIZE = 0x457410

# Wrapper class around low level reads/writes
# code modified from https://github.com/samfin/mmbn3-random/tree/cleanup
class Rom(object):
	def __init__(self, rom_path):
		with open(rom_path, 'rb') as file:
			file.seek(BINARY_ADDR)
			self.rom_data = file.read(BINARY_SIZE)
		self.buffer = bytearray(self.rom_data)
		self.w_offset = 0
		self.r_offset = 0
		self.stack = []

	def seekr(self, offset):
		self.r_offset = offset
	def seekw(self, offset):
		self.w_offset = offset
	def seek(self, offset):
		self.seekr(offset)
		self.seekw(offset)
	def save_offsets(self):
		self.stack.append((self.r_offset, self.w_offset))
	def load_offsets(self):
		self.r_offset, self.w_offset = self.stack.pop()

	# Generally, providing an offset = don't change the state
	# Not providing an offset = use the stored offset and increment it
	# Also changes the write offset, careful!!
	def read(self, n, offset = -1):
		if offset == -1:
			offset = self.r_offset
			self.w_offset = self.r_offset
			self.r_offset += n
		assert(offset >= 0)
		assert(offset + n <= len(self.rom_data))
		return self.rom_data[offset : offset + n]

	def read_byte(self, offset = -1):
		return ord(self.read(1, offset))
	def read_halfword(self, offset = -1):
		return struct.unpack('<H', self.read(2, offset))[0]
	def read_word(self, offset = -1):
		return struct.unpack('<I', self.read(4, offset))[0]
	def read_dblword(self, offset = -1):
		return struct.unpack('<Q', self.read(8, offset))[0]

	def write(self, data, offset = -1):
		if offset == -1:
			offset = self.w_offset
			self.w_offset += len(data)
		assert(offset >= 0)
		assert(offset + len(data) <= len(self.rom_data))
		for i in range(len(data)):
			self.buffer[offset + i] = data[i]

	def write_byte(self, x, offset = -1):
		return self.write(struct.pack('<B', x), offset)
	def write_halfword(self, x, offset = -1):
		return self.write(struct.pack('<H', x), offset)
	def write_word(self, x, offset = -1):
		return self.write(struct.pack('<I', x), offset)
	def write_dblword(self, x, offset = -1):
		return self.write(struct.pack('<Q', x), offset)