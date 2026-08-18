import os
import sys
import time
import struct
import lz4.block

def sanitize_path(path_str):
    clean = path_str.replace('\\', '/')
    while clean.startswith('../') or clean.startswith('./') or clean.startswith('/'):
        if clean.startswith('../'):
            clean = clean[3:]
        elif clean.startswith('./'):
            clean = clean[2:]
        elif clean.startswith('/'):
            clean = clean[1:]
    
    parts = clean.split('/')
    safe_parts = []
    for part in parts:
        part = part.strip()
        if not part or part == '.':
            continue
        if part == '..':
            continue
        for ch in '<>:"|?*':
            part = part.replace(ch, '_')
        safe_parts.append(part)
    
    if not safe_parts:
        return 'unnamed_file'
    return os.path.join(*safe_parts)

def unpack_pkg(pkg_path, output_dir=None):
    pkg_name = os.path.basename(pkg_path)
    pkg_stem = os.path.splitext(pkg_name)[0]
    
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(pkg_path)), pkg_stem + "_extracted")
    else:
        output_dir = os.path.join(output_dir, pkg_stem)
        
    os.makedirs(output_dir, exist_ok=True)
    file_size = os.path.getsize(pkg_path)
    print(f"\n[*] Dang giai ma: {pkg_name} ({file_size / (1024*1024):.2f} MB)...")
    
    t0 = time.time()
    try:
        with open(pkg_path, 'rb') as f:
            header_raw = f.read(16)
            if len(header_raw) < 16:
                print(f"[!] Loi: File {pkg_name} qua nho hoac khong hop le.")
                return False
            
            v1, v2, data_size, header_size = struct.unpack('<IIII', header_raw)
            if data_size + header_size != file_size:
                print(f"[!] Canh bao: data_size({data_size}) + header_size({header_size}) != file_size({file_size})")
            
            f.seek(data_size)
            table_compressed = f.read(header_size)
            uncomp_table_len = struct.unpack('<I', table_compressed[:4])[0]
            table_decomp = lz4.block.decompress(table_compressed[4:], uncompressed_size=uncomp_table_len)
            
            num_entries = struct.unpack('<I', table_decomp[:4])[0]
            pos = 4
            entries = []
            for i in range(num_entries):
                h1 = table_decomp[pos:pos+16]
                offset, size, flag = struct.unpack('<III', table_decomp[pos+16:pos+28])
                pos += 28
                h2 = None
                if (flag & 0x20) != 0:
                    h2 = table_decomp[pos:pos+16]
                    pos += 16
                entries.append({
                    'idx': i,
                    'hash1': h1.hex(),
                    'offset': offset,
                    'size': size,
                    'flag': flag,
                    'hash2': h2.hex() if h2 else None
                })
            
            pos = (pos + 3) & ~3
            num_strings = struct.unpack('<I', table_decomp[pos:pos+4])[0]
            pos += 4
            
            for i in range(num_strings):
                str_len = struct.unpack('<I', table_decomp[pos:pos+4])[0]
                pos += 4
                name = table_decomp[pos:pos+str_len].decode('utf-8', errors='ignore')
                pos += str_len
                entry_idx = struct.unpack('<I', table_decomp[pos:pos+4])[0]
                pos += 4
                if entry_idx < len(entries):
                    entries[entry_idx]['name'] = name
            
            print(f"    - Tim thay {len(entries)} file ben trong (so luong ten: {num_strings})")
            
            extracted_count = 0
            total_extracted_bytes = 0
            
            for idx, entry in enumerate(entries):
                f.seek(entry['offset'])
                raw_data = f.read(entry['size'])
                flag = entry['flag']
                
                if (flag & 1) != 0 and len(raw_data) >= 4:
                    try:
                        uncomp_sz = struct.unpack('<I', raw_data[:4])[0]
                        file_content = lz4.block.decompress(raw_data[4:], uncompressed_size=uncomp_sz)
                    except Exception:
                        file_content = raw_data
                else:
                    file_content = raw_data
                
                raw_name = entry.get('name', f"unnamed_{entry['idx']:06d}.bin")
                safe_rel_path = sanitize_path(raw_name)
                out_file_path = os.path.join(output_dir, safe_rel_path)
                
                os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
                with open(out_file_path, 'wb') as out_f:
                    out_f.write(file_content)
                
                extracted_count += 1
                total_extracted_bytes += len(file_content)
                
                if (idx + 1) % 5000 == 0 or idx + 1 == len(entries):
                    pct = (idx + 1) / len(entries) * 100
                    print(f"    - Tien do: {idx + 1}/{len(entries)} ({pct:.1f}%)")
            
            elapsed = time.time() - t0
            print(f"[+] Hoan tat: {extracted_count} file ({total_extracted_bytes / (1024*1024):.2f} MB) -> {output_dir} ({elapsed:.2f}s)")
            return True
    except Exception as ex:
        print(f"[!] Loi khi giai ma {pkg_name}: {ex}")
        return False

def auto_detect_pkg_sources():
    candidates = []
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(curr_dir)
    candidates.append(os.path.join(curr_dir, "pkg_assets"))
    
    appdata = os.environ.get("APPDATA", "")
    if appdata and os.path.exists(appdata):
        for d in os.listdir(appdata):
            dl = d.lower()
            if "miniword" in dl or "miniworld" in dl:
                full_d = os.path.join(appdata, d)
                if os.path.isdir(full_d):
                    candidates.append(full_d)
                    candidates.append(os.path.join(full_d, "pkg_assets"))
                    candidates.append(os.path.join(full_d, "AssetsCache"))
    
    found_pkgs = []
    seen = set()
    for cand in candidates:
        if os.path.exists(cand):
            for root, _, files in os.walk(cand):
                if root.count(os.sep) - cand.count(os.sep) <= 2:
                    for f in files:
                        if f.endswith('.pkg'):
                            full_pkg = os.path.join(root, f)
                            if full_pkg not in seen:
                                seen.add(full_pkg)
                                found_pkgs.append(full_pkg)
    return found_pkgs

def choose_with_gui():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        print("[*] Dang mo hop thoai chon file/thu muc...")
        selected = filedialog.askopenfilename(
            title="Chon file .pkg can giai ma (hoac Cancel de chon thu muc)",
            filetypes=[("Mini World PKG", "*.pkg"), ("All files", "*.*")]
        )
        if selected:
            return selected
            
        selected_dir = filedialog.askdirectory(title="Chon thu muc chua file .pkg")
        if selected_dir:
            return selected_dir
    except Exception:
        pass
    return None

def main():
    print("=" * 65)
    print("      MINI WORLD .PKG EXTRACTOR - TU DONG TIM DUONG DAN")
    print("=" * 65)
    
    input_items = []
    output_dir = None
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("-o="):
                output_dir = arg[3:]
            elif os.path.isfile(arg) and arg.endswith(".pkg"):
                input_items.append(arg)
            elif os.path.isdir(arg):
                for root, _, files in os.walk(arg):
                    for f in files:
                        if f.endswith('.pkg'):
                            input_items.append(os.path.join(root, f))
    
    if not input_items:
        print("[*] Khong co tham so truyen vao, dang tu dong quet %APPDATA%...")
        input_items = auto_detect_pkg_sources()
        
    if not input_items:
        print("[!] Khong tim thay file .pkg tu dong. Mo hop thoai chon file...")
        gui_path = choose_with_gui()
        if gui_path:
            if os.path.isfile(gui_path) and gui_path.endswith('.pkg'):
                input_items.append(gui_path)
            elif os.path.isdir(gui_path):
                for root, _, files in os.walk(gui_path):
                    for f in files:
                        if f.endswith('.pkg'):
                            input_items.append(os.path.join(root, f))
                            
    if not input_items:
        print("\n[!] Khong tim thay bat ky file .pkg nao tren he thong!")
        print("[*] Huong dan su dung:")
        print("    1. Keo tha truc tiep file .pkg vao file script nay hoac file .bat")
        print("    2. Hoac copy file script nay vao cung thu muc chua file .pkg roi chay")
        print("    3. Hoac chay lenh: python extract_all_pkg.py \"duong_dan_file.pkg\"")
        input("\nNhan Enter de thoat...")
        return
    
    print(f"\n[+] Tim thay tong cong {len(input_items)} file .pkg can xu ly:\n")
    for idx, fp in enumerate(input_items, 1):
        sz = os.path.getsize(fp) / (1024*1024)
        print(f"  {idx}. {os.path.basename(fp):<25} ({sz:>7.2f} MB) -> {fp}")
    print()
    
    t_start = time.time()
    success = 0
    for fp in input_items:
        if not output_dir:
            target_out = os.path.join(os.path.dirname(os.path.abspath(fp)), "extracted_pkg")
        else:
            target_out = output_dir
            
        if unpack_pkg(fp, target_out):
            success += 1
            
    t_total = time.time() - t_start
    print("\n" + "=" * 65)
    print(f"[V] DA GIAI MA THANH CONG {success}/{len(input_items)} FILE .PKG!")
    print(f"Tong thoi gian: {t_total:.2f} giay")
    print("=" * 65)
    print("\nNhan Enter de hoan tat...")
    try:
        input()
    except Exception:
        pass

if __name__ == "__main__":
    main()
