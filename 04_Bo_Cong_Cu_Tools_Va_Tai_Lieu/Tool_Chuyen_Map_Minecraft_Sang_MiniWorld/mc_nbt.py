"""
Fast pure-Python NBT (Named Binary Tag) parser for Minecraft Chunk Data
Supports TAG_End, TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float,
TAG_Double, TAG_Byte_Array, TAG_String, TAG_List, TAG_Compound, TAG_Int_Array, TAG_Long_Array.
"""

import struct
import io
import zlib
import gzip

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

class NBTReader:
    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def read_byte(self):
        return struct.unpack('>b', self.stream.read(1))[0]

    def read_ubyte(self):
        return struct.unpack('>B', self.stream.read(1))[0]

    def read_short(self):
        return struct.unpack('>h', self.stream.read(2))[0]

    def read_int(self):
        return struct.unpack('>i', self.stream.read(4))[0]

    def read_long(self):
        return struct.unpack('>q', self.stream.read(8))[0]

    def read_float(self):
        return struct.unpack('>f', self.stream.read(4))[0]

    def read_double(self):
        return struct.unpack('>d', self.stream.read(8))[0]

    def read_string(self):
        length = struct.unpack('>H', self.stream.read(2))[0]
        return self.stream.read(length).decode('utf-8', errors='replace')

    def read_payload(self, tag_type):
        if tag_type == TAG_BYTE:
            return self.read_byte()
        elif tag_type == TAG_SHORT:
            return self.read_short()
        elif tag_type == TAG_INT:
            return self.read_int()
        elif tag_type == TAG_LONG:
            return self.read_long()
        elif tag_type == TAG_FLOAT:
            return self.read_float()
        elif tag_type == TAG_DOUBLE:
            return self.read_double()
        elif tag_type == TAG_BYTE_ARRAY:
            length = self.read_int()
            return self.stream.read(length)
        elif tag_type == TAG_STRING:
            return self.read_string()
        elif tag_type == TAG_LIST:
            item_type = self.read_ubyte()
            length = self.read_int()
            return [self.read_payload(item_type) for _ in range(length)]
        elif tag_type == TAG_COMPOUND:
            compound = {}
            while True:
                child_type = self.read_ubyte()
                if child_type == TAG_END:
                    break
                child_name = self.read_string()
                compound[child_name] = self.read_payload(child_type)
            return compound
        elif tag_type == TAG_INT_ARRAY:
            length = self.read_int()
            return list(struct.unpack(f'>{length}i', self.stream.read(length * 4)))
        elif tag_type == TAG_LONG_ARRAY:
            length = self.read_int()
            return list(struct.unpack(f'>{length}q', self.stream.read(length * 8)))
        else:
            raise ValueError(f"Unknown NBT Tag Type: {tag_type}")

    def parse(self):
        tag_type = self.read_ubyte()
        if tag_type == TAG_END:
            return None
        root_name = self.read_string()
        payload = self.read_payload(tag_type)
        return payload

def parse_nbt_buffer(raw_data):
    """
    Decompresses and parses NBT buffer from gzip, zlib, or uncompressed stream.
    """
    if len(raw_data) < 2:
        return None
    # Check Gzip (1f 8b)
    if raw_data[:2] == b'\x1f\x8b':
        data = gzip.decompress(raw_data)
    # Check Zlib / Deflate (78 01, 78 9c, 78 da)
    elif raw_data[0] == 0x78:
        try:
            data = zlib.decompress(raw_data)
        except Exception:
            data = zlib.decompress(raw_data, -15)
    else:
        data = raw_data

    reader = NBTReader(data)
    return reader.parse()
