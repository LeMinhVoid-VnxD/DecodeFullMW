"""
Minecraft Region (.mca) File Parser
Reads 32x32 chunks, parses sections, decodes palette and packed BlockStates.
"""

import os
import struct
import zlib
from mc_nbt import parse_nbt_buffer
from block_mapping import map_mc_block_to_mw

class MCChunk:
    def __init__(self, cx, cz):
        self.cx = cx
        self.cz = cz
        # Map of (x, y, z) in local chunk [0..15, 0..319, 0..15] -> Mini World Block ID
        self.blocks = {} # (lx, y, lz) -> mw_block_id
        self.min_y = 0
        self.max_y = 255

class MCAReader:
    def __init__(self, mca_path):
        self.mca_path = mca_path
        self.rx, self.rz = self._parse_region_coords(mca_path)

    @staticmethod
    def _parse_region_coords(path):
        fname = os.path.basename(path).lower()
        parts = fname.split('.')
        try:
            if len(parts) >= 4 and parts[0] == 'r':
                return int(parts[1]), int(parts[2])
            elif len(parts) >= 3 and parts[0] == 'r':
                return int(parts[1]), int(parts[2])
        except Exception:
            pass
        return 0, 0

    def read_all_chunks(self):
        """
        Yields all MCChunk instances present in the .mca file.
        """
        if not os.path.exists(self.mca_path):
            return

        file_size = os.path.getsize(self.mca_path)
        if file_size < 8192:
            return

        with open(self.mca_path, 'rb') as f:
            header = f.read(4096)
            for i in range(1024):
                rel_cx = i % 32
                rel_cz = i // 32
                entry_offset = i * 4
                b0, b1, b2, b3 = header[entry_offset:entry_offset+4]
                sector_offset = (b0 << 16) | (b1 << 8) | b2
                sector_count = b3

                if sector_offset > 0 and sector_count > 0:
                    byte_offset = sector_offset * 4096
                    if byte_offset + 5 <= file_size:
                        f.seek(byte_offset)
                        chunk_len_raw = f.read(4)
                        if len(chunk_len_raw) < 4:
                            continue
                        chunk_len = struct.unpack('>I', chunk_len_raw)[0]
                        comp_type = f.read(1)
                        if chunk_len <= 1:
                            continue
                        raw_payload = f.read(chunk_len - 1)
                        try:
                            nbt_data = parse_nbt_buffer(raw_payload)
                            if nbt_data:
                                chunk = self._parse_chunk_nbt(nbt_data, rel_cx, rel_cz)
                                if chunk:
                                    yield chunk
                        except Exception:
                            continue

    def _parse_chunk_nbt(self, nbt, rel_cx, rel_cz):
        level = nbt.get('Level', nbt)
        cx = level.get('xPos', self.rx * 32 + rel_cx)
        cz = level.get('zPos', self.rz * 32 + rel_cz)
        
        chunk = MCChunk(cx, cz)
        
        sections = level.get('sections', level.get('Sections', []))
        if not sections or not isinstance(sections, list):
            return chunk

        for sec in sections:
            sec_y = sec.get('Y', sec.get('y', 0))
            # Support modern 1.18+ (block_states compound)
            block_states = sec.get('block_states', {})
            palette = None
            data_array = None

            if isinstance(block_states, dict):
                palette = block_states.get('palette', None)
                data_array = block_states.get('data', None)

            # Support 1.13-1.17 (Palette & BlockStates directly in section)
            if palette is None:
                palette = sec.get('Palette', None)
            if data_array is None:
                data_array = sec.get('BlockStates', None)

            # Modern Palette unpacking (4096 blocks per section)
            if palette and isinstance(palette, list):
                mw_palette = []
                for p in palette:
                    bname = p.get('Name', 'minecraft:air') if isinstance(p, dict) else str(p)
                    mw_palette.append(map_mc_block_to_mw(bname))

                if len(mw_palette) == 1:
                    # Entire 16x16x16 section is 1 single block type
                    single_id = mw_palette[0]
                    if single_id != 0:
                        for ly in range(16):
                            world_y = sec_y * 16 + ly
                            for lz in range(16):
                                for lx in range(16):
                                    chunk.blocks[(lx, world_y, lz)] = single_id
                elif data_array:
                    # Unpack bitstream
                    self._unpack_palette_bits(chunk, mw_palette, data_array, sec_y)

            # Legacy 1.12- Blocks array (4096 bytes)
            elif 'Blocks' in sec:
                raw_blocks = sec['Blocks']
                if len(raw_blocks) >= 4096:
                    for i in range(4096):
                        bid = raw_blocks[i]
                        if bid != 0:
                            lx = i & 0x0f
                            lz = (i >> 4) & 0x0f
                            ly = (i >> 8) & 0x0f
                            world_y = sec_y * 16 + ly
                            chunk.blocks[(lx, world_y, lz)] = map_mc_block_to_mw(bid)

        return chunk

    def _unpack_palette_bits(self, chunk, mw_palette, data_array, sec_y):
        palette_len = len(mw_palette)
        if palette_len <= 1:
            return

        # Calculate bits per block (minimum 4 bits in MC)
        bits_per_block = max(4, (palette_len - 1).bit_length())
        blocks_per_long = 64 // bits_per_block
        mask = (1 << bits_per_block) - 1

        block_idx = 0
        for val in data_array:
            uval = val if val >= 0 else (val + (1 << 64))
            for b in range(blocks_per_long):
                if block_idx >= 4096:
                    break
                p_idx = (uval >> (b * bits_per_block)) & mask
                if p_idx < len(mw_palette):
                    mw_id = mw_palette[p_idx]
                    if mw_id != 0:
                        lx = block_idx & 0x0f
                        lz = (block_idx >> 4) & 0x0f
                        ly = (block_idx >> 8) & 0x0f
                        world_y = sec_y * 16 + ly
                        chunk.blocks[(lx, world_y, lz)] = mw_id
                block_idx += 1
