"""
Mini World Region (.r) File Writer & World Structure Generator
Creates standard Mini World map folders (data/w{id}/m0/*.r) and map.ini metadata.
"""

import os
import time
import struct
import random

class MWChunkData:
    def __init__(self, cx, cz):
        self.cx = cx
        self.cz = cz
        self.blocks = {} # (lx, y, lz) -> mw_block_id

class MWRegionWriter:
    def __init__(self, rx, rz):
        self.rx = rx
        self.rz = rz
        # 1024 slots for chunks (32x32)
        self.chunks = [None] * 1024

    def add_chunk(self, chunk):
        rel_cx = chunk.cx - (self.rx * 32)
        rel_cz = chunk.cz - (self.rz * 32)
        if 0 <= rel_cx < 32 and 0 <= rel_cz < 32:
            idx = rel_cz * 32 + rel_cx
            self.chunks[idx] = chunk

    def build_chunk_payload(self, chunk):
        """
        Encodes a chunk's blocks into Mini World chunk payload format.
        """
        if not chunk or not chunk.blocks:
            return b''

        # Filter blocks to positive Y heights (0 to 255)
        valid_blocks = {}
        for (lx, y, lz), bid in chunk.blocks.items():
            if 0 <= lx < 16 and 0 <= lz < 16 and 0 <= y < 256 and bid > 0:
                valid_blocks[(lx, y, lz)] = bid

        if not valid_blocks:
            return b''

        # Collect unique block palette
        palette = sorted(list(set(valid_blocks.values())))
        # Chunk header: uncompressed size, chunk flags, section count
        raw_sections = bytearray()
        
        # Write compact block list
        # Format: Count (uint16), then for each block: lx (1B), ly (1B), lz (1B), bid (uint16)
        block_records = bytearray()
        for (lx, y, lz), bid in valid_blocks.items():
            block_records.extend(struct.pack('<BBBH', lx, y, lz, bid))

        # Chunk payload:
        # Header (16B) + Palette Info + Block Data
        payload = bytearray()
        uncomp_len = len(block_records) + 32
        payload.extend(struct.pack('<H', min(65535, uncomp_len)))
        payload.extend(b'\x00\x20\x5d\x00\x40\x00\x00\x00\x14\x00\x30\x04')
        payload.extend(b'\x00' * 16) # Hash placeholder
        payload.extend(struct.pack('<I', len(valid_blocks)))
        payload.extend(block_records)
        
        return bytes(payload)

    def write_to_file(self, output_path):
        """
        Writes the .r file to output_path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        now_ts = int(time.time())
        sector_size = 4096
        
        offset_table = [0] * 1024
        timestamp_table = [now_ts] * 1024
        
        chunk_buffers = []
        curr_sector = 2 # Sectors 0 and 1 are header tables
        
        for i in range(1024):
            chunk = self.chunks[i]
            if chunk:
                payload = self.build_chunk_payload(chunk)
                if payload:
                    chunk_len = len(payload)
                    chunk_buf = struct.pack('<I', chunk_len) + payload
                    
                    # Pad to 4096-byte sector boundary
                    pad_len = (sector_size - (len(chunk_buf) % sector_size)) % sector_size
                    chunk_buf += b'\x00' * pad_len
                    
                    sector_span = len(chunk_buf) // sector_size
                    # Write offset entry: (sector_span << 24) | sector_index
                    offset_table[i] = (sector_span << 24) | (curr_sector & 0x00ffffff)
                    chunk_buffers.append(chunk_buf)
                    curr_sector += sector_span

        with open(output_path, 'wb') as f:
            # Sector 0: Offset Table (4096 bytes)
            for val in offset_table:
                f.write(struct.pack('<I', val))
            # Sector 1: Timestamp Table (4096 bytes)
            for ts in timestamp_table:
                f.write(struct.pack('<I', ts))
            # Sector 2+: Chunk Data Blocks
            for buf in chunk_buffers:
                f.write(buf)

        return len(chunk_buffers)

class MWWorldGenerator:
    @staticmethod
    def create_world(world_id, world_name, output_base_dir):
        """
        Creates a complete Mini World map folder structure: data/w{id}/...
        """
        world_dir = os.path.join(output_base_dir, f"w{world_id}")
        m0_dir = os.path.join(world_dir, "m0")
        sandbox_dir = os.path.join(world_dir, "sandbox")
        data_dir = os.path.join(world_dir, "data")
        
        os.makedirs(m0_dir, exist_ok=True)
        os.makedirs(sandbox_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # Create map.ini
        map_ini_content = f"""[Map]
name={world_name}
game_mode=1
seed={random.randint(10000000, 99999999)}
world_width=10000
world_height=256
world_depth=10000
version=410
create_time={int(time.time())}
last_save_time={int(time.time())}
is_custom_mode=1
"""
        with open(os.path.join(world_dir, "map.ini"), "w", encoding="utf-8") as f:
            f.write(map_ini_content)

        return world_dir, m0_dir
