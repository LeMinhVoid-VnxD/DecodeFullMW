import os
import struct
import time
import lz4.block

ORIG_PKG = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\pkg_assets\dx_res.pkg.original_backup"
TARGET_PKG = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\pkg_assets\dx_res.pkg"
EXTRACTED_MAT_DIR = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\pkg_assets\extracted_pkg\dx_res\materials"

def repack_dx_res():
    print("\n" + "=" * 70)
    print("      DANG DONG GOI SHADER ULTRA RTX TRUC TIEP VAO DX_RES.PKG")
    print("=" * 70)
    
    if not os.path.exists(ORIG_PKG):
        print(f"[!] Khong tim thay file goc: {ORIG_PKG}")
        return False
        
    t0 = time.time()
    
    # 1. Read original PKG
    print("[1/4] Dang doc cau truc header va bang chu ky tu dx_res.pkg...")
    with open(ORIG_PKG, 'rb') as f_orig:
        v1, v2, data_size, header_size = struct.unpack('<IIII', f_orig.read(16))
        f_orig.seek(data_size)
        table_comp = f_orig.read(header_size)
        uncomp_len = struct.unpack('<I', table_comp[:4])[0]
        table = lz4.block.decompress(table_comp[4:], uncompressed_size=uncomp_len)
        
        num_entries = struct.unpack('<I', table[:4])[0]
        pos = 4
        orig_entries = []
        for i in range(num_entries):
            h1 = table[pos:pos+16]
            offset, size, flag = struct.unpack('<III', table[pos+16:pos+28])
            pos += 28
            h2 = b''
            if (flag & 0x20) != 0:
                h2 = table[pos:pos+16]
                pos += 16
            orig_entries.append({
                'offset': offset,
                'size': size,
                'flag': flag,
                'h1': h1,
                'h2': h2
            })
            
        pos = (pos + 3) & ~3
        num_strings = struct.unpack('<I', table[pos:pos+4])[0]
        pos += 4
        
        file_list = []
        name_to_idx = {}
        for i in range(num_strings):
            str_len = struct.unpack('<I', table[pos:pos+4])[0]
            pos += 4
            name = table[pos:pos+str_len].decode('utf-8', errors='ignore')
            pos += str_len
            idx = struct.unpack('<I', table[pos:pos+4])[0]
            pos += 4
            file_list.append((name, idx))
            name_to_idx[name] = idx
            
        # Read all payload buffers
        print(f"[2/4] Dang nap {len(orig_entries)} files shader vao bo nho...")
        payload_data = []
        for idx, ent in enumerate(orig_entries):
            f_orig.seek(ent['offset'])
            data = f_orig.read(ent['size'])
            payload_data.append(data)

    # 2. Prepare modified shaders from EXTRACTED_MAT_DIR
    print("[3/4] Dang nap cac Shaders moi (Song nuoc 3D, May bieu cam, La rung rinh, Caustics)...")
    injected = 0
    for root, _, files in os.walk(EXTRACTED_MAT_DIR):
        for fname in files:
            if fname.endswith('.xml'):
                full_p = os.path.join(root, fname)
                rel_p = 'materials/' + os.path.relpath(full_p, EXTRACTED_MAT_DIR).replace('\\', '/')
                if rel_p in name_to_idx:
                    entry_idx = name_to_idx[rel_p]
                    with open(full_p, 'rb') as f_mat:
                        raw_mat = f_mat.read()
                    # Recompress with LZ4
                    comp_mat = lz4.block.compress(raw_mat, store_size=False)
                    payload_data[entry_idx] = comp_mat
                    orig_entries[entry_idx]['flag'] = 0x01 # compressed
                    orig_entries[entry_idx]['size'] = len(comp_mat)
                    injected += 1

    print(f"  -> Da tich hop {injected} Shader XML cao cap vao goi!")

    # 3. Write new PKG
    print(f"[4/4] Dang ghi de goi {os.path.basename(TARGET_PKG)}...")
    tmp_pkg = TARGET_PKG + ".tmp"
    with open(tmp_pkg, 'wb') as f_out:
        # Write 16-byte header placeholder
        f_out.write(b'\x00' * 16)
        
        # Write all data entries
        current_offset = 16
        new_entries = []
        for idx, data in enumerate(payload_data):
            ent = orig_entries[idx]
            f_out.write(data)
            new_entries.append({
                'offset': current_offset,
                'size': len(data),
                'flag': ent['flag'],
                'h1': ent['h1'],
                'h2': ent['h2']
            })
            current_offset += len(data)
            
        new_data_size = current_offset
        
        # Build decompressed table
        tbl_data = bytearray()
        tbl_data.extend(struct.pack('<I', len(new_entries)))
        for ent in new_entries:
            tbl_data.extend(ent['h1'])
            tbl_data.extend(struct.pack('<III', ent['offset'], ent['size'], ent['flag']))
            if (ent['flag'] & 0x20) != 0:
                tbl_data.extend(ent['h2'])
                
        # Align to 4 bytes
        pad = (4 - (len(tbl_data) % 4)) % 4
        tbl_data.extend(b'\x00' * pad)
        
        # String table
        tbl_data.extend(struct.pack('<I', len(file_list)))
        for name, idx in file_list:
            name_bytes = name.encode('utf-8')
            tbl_data.extend(struct.pack('<I', len(name_bytes)))
            tbl_data.extend(name_bytes)
            tbl_data.extend(struct.pack('<I', idx))
            
        # Compress table with LZ4
        comp_tbl = lz4.block.compress(bytes(tbl_data), store_size=False)
        comp_tbl_with_len = struct.pack('<I', len(tbl_data)) + comp_tbl
        new_header_size = len(comp_tbl_with_len)
        
        # Write compressed table to end of file
        f_out.write(comp_tbl_with_len)
        
        # Seek back and write header
        f_out.seek(0)
        f_out.write(struct.pack('<IIII', v1, v2, new_data_size, new_header_size))

    # Replace target
    if os.path.exists(TARGET_PKG):
        os.remove(TARGET_PKG)
    os.rename(tmp_pkg, TARGET_PKG)
    
    elapsed = time.time() - t0
    final_sz = os.path.getsize(TARGET_PKG) / (1024*1024)
    print("\n" + "=" * 70)
    print(f" [V] DONG GOI SHADER TRUC TIEP VAO GAME THANH CONG 100%! ({elapsed:.2f}s)")
    print(f" • Vi tri file da nap: {TARGET_PKG} ({final_sz:.2f} MB)")
    print("👉 Bay gio ban chi can thoat ra Menu hoac vao lai Map trong game")
    print("   la toan bo Song Nuoc, Anh Sang, La Cay se hien thi ngay lap tuc!")
    print("=" * 70 + "\n")
    return True

if __name__ == "__main__":
    repack_dx_res()
