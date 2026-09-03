"""
Tool Chuyen Quyen So Huu Map Mini World (Map Ownership Transfer Tool)
Cho phep nhap duong dan (Path) thu muc Map hoac keo tha folder map vao de chuyen toan bo quyen so huu thanh Map cua ban.
"""

import os
import sys
import json
import time
import shutil
import struct
import re

DATA_DIR = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\data"
ACCOUNT_DIR = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\data\account\http___hwacchm.mini1.cn_4000"

def get_current_user_uin():
    curr_file = os.path.join(ACCOUNT_DIR, "currentv2.data2tmp.bak")
    if os.path.exists(curr_file):
        with open(curr_file, "r", encoding="utf-8", errors="ignore") as f:
            c = f.read()
            m = re.search(r'Uin\s*=\s*(\d+)', c)
            if m:
                return int(m.group(1))
    return 1273476006 # Fallback UIN

def get_map_title(map_path):
    wdesc_p = os.path.join(map_path, "wdesc.fb")
    if os.path.exists(wdesc_p):
        with open(wdesc_p, "rb") as f:
            data = f.read()
            strs = [m.group().decode('utf-8', 'ignore') for m in re.finditer(rb'[\x20-\x7e\xc0-\xff]{3,}', data)]
            for s in strs:
                if len(s) > 2 and not s.startswith("http") and "{" not in s:
                    return s[:30]
    return os.path.basename(map_path)

def transfer_ownership(src_map_path, target_uin=None):
    # Clean quotes if dragged
    src_map_path = src_map_path.strip().strip('"').strip("'")
    
    if not os.path.exists(src_map_path):
        # Try checking in DATA_DIR
        alt_p = os.path.join(DATA_DIR, src_map_path)
        if os.path.exists(alt_p):
            src_map_path = alt_p
        else:
            print(f"\n[!] KHONG TIM THAY THU MUC MAP: {src_map_path}")
            return False

    if not os.path.isdir(src_map_path):
        print(f"\n[!] Duong dan khong phai la mot thu muc map: {src_map_path}")
        return False

    if target_uin is None:
        target_uin = get_current_user_uin()

    map_name = get_map_title(src_map_path)
    new_world_id = f"w{int(time.time() * 1000)}"
    dest_map_path = os.path.join(DATA_DIR, new_world_id)

    print("\n" + "=" * 70)
    print("      TIEN TRINH CHUYEN QUYEN SO HUU MAP MINI WORLD")
    print("=" * 70)
    print(f"[*] Map goc can chuyen:    {src_map_path}")
    print(f"[*] Ten Map nhan dien:     {map_name}")
    print(f"[*] Map moi tao ra:        {new_world_id}")
    print(f"[*] UIN chu so huu moi:    {target_uin}")
    print("-" * 70)

    # 1. Copy Map
    print("\n[1/5] Dang sao chep toan bo khoi Voxel, cong trinh, trigger va tai nguyen...")
    try:
        shutil.copytree(src_map_path, dest_map_path, dirs_exist_ok=True)
    except Exception as e:
        print(f"[!] Loi khi copy map: {e}")
        return False

    # 2. Find Old Author UIN
    old_author_uin = None
    modinfo_p = os.path.join(dest_map_path, "mods", "modinfo.json")
    if os.path.exists(modinfo_p):
        try:
            with open(modinfo_p, "r", encoding="utf-8") as f:
                minfo = json.load(f)
                if minfo.get("mods") and len(minfo["mods"]) > 0:
                    old_author_uin = minfo["mods"][0].get("authoruin")
        except Exception: pass

    roles_dir = os.path.join(dest_map_path, "roles")
    if not old_author_uin and os.path.exists(roles_dir):
        for rf in os.listdir(roles_dir):
            if rf.startswith("u") and rf.endswith(".p"):
                try:
                    old_author_uin = int(rf[1:-2])
                    break
                except Exception: pass

    print(f"[2/5] Phat hien UIN tac gia goc: {old_author_uin if old_author_uin else 'Khong ro (Se tu dong gan UIN moi)'}")

    # 3. Patch JSON & Mods (open_edit = true, authoruin = target_uin)
    print("[3/5] Mo khoa toan bo Plugins, Blocks, Quai vat custom (open_edit = true)...")
    mods_dir = os.path.join(dest_map_path, "mods")
    if os.path.exists(mods_dir):
        for root, _, files in os.walk(mods_dir):
            for f in files:
                if f.endswith(".json"):
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, "r", encoding="utf-8") as jf:
                            content = jf.read()
                        if old_author_uin:
                            content = content.replace(str(old_author_uin), str(target_uin))
                        content = re.sub(r'"open_edit"\s*:\s*false', '"open_edit": true', content)
                        with open(fp, "w", encoding="utf-8") as jf:
                            jf.write(content)
                    except Exception: pass

    # 4. Patch Roles & Permissions (Grant Full Host & Edit Rights)
    print("[4/5] Cap toan quyen Admin / Host cho tai khoan cua ban...")
    if os.path.exists(roles_dir):
        target_role_file = os.path.join(roles_dir, f"u{target_uin}.p")
        if old_author_uin and os.path.exists(os.path.join(roles_dir, f"u{old_author_uin}.p")):
            shutil.copy2(os.path.join(roles_dir, f"u{old_author_uin}.p"), target_role_file)
        elif not os.path.exists(target_role_file):
            with open(target_role_file, "wb") as rf:
                rf.write(b"\x00" * 32)

    # 5. Remove Cloud Lock & Patch wdesc.fb
    print("[5/5] Xoa bo khoa Cloud va bo sung chu quyen Map...")
    for lock_file in ["upload.rec", "mapmd5", "cover.data"]:
        lp = os.path.join(dest_map_path, lock_file)
        if os.path.exists(lp):
            try: os.remove(lp)
            except Exception: pass

    wdesc_p = os.path.join(dest_map_path, "wdesc.fb")
    if os.path.exists(wdesc_p) and old_author_uin:
        try:
            with open(wdesc_p, "rb") as f:
                wdesc_raw = f.read()
            old_bytes = struct.pack("<I", old_author_uin)
            new_bytes = struct.pack("<I", target_uin)
            wdesc_patched = wdesc_raw.replace(old_bytes, new_bytes)
            with open(wdesc_p, "wb") as f:
                f.write(wdesc_patched)
        except Exception: pass

    print("\n" + "=" * 70)
    print(" [V] CHUYEN QUYEN SO HUU THANH CONG 100%!")
    print("=" * 70)
    print(f" • Ten Map:             {map_name}")
    print(f" • Thu muc map moi:     {new_world_id}")
    print(f" • Duong dan luu tru:   {dest_map_path}")
    print(f" • Chu so huu hien tai: UID {target_uin}")
    print("\n👉 Bay gio ban co the vao game Mini World, mo muc 'Ban do cua toi'")
    print("   se thay map xuat hien ngay voi toan quyen Chinh sua, Trigger & Build!")
    print("=" * 70 + "\n")
    return True

def main():
    print("=" * 70)
    print("   CONG CU CHUYEN QUYEN SO HUU MAP MINI WORLD - NHAP PATH HOAC KEO THA")
    print("=" * 70)

    my_uin = get_current_user_uin()
    print(f"[*] Tai khoan dang dang nhap (UIN): {my_uin}\n")

    if len(sys.argv) > 1:
        path_input = sys.argv[1]
        transfer_ownership(path_input, my_uin)
    else:
        while True:
            try:
                print("Nhap duong dan (Path) thu muc Map can chuyen quyen")
                print("(Hoac keo tha folder map vao day, go 'exit' de thoat):")
                path_input = input(">> ").strip()
                if path_input.lower() in ['exit', 'quit', 'q']:
                    break
                if path_input:
                    transfer_ownership(path_input, my_uin)
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    main()
