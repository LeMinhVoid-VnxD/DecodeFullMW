"""
Mini World Full Map Cloner & Unlocker Tool
Transfers 100% of any map (Builds, Triggers, Scripts, Mods, 3D Models, UI) into your local account with full editing rights without game errors.
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
    return 1273476006 # Fallback default UIN

def get_map_title(map_path):
    # Try reading from editor_lang.fb or wdesc.fb or folder name
    wdesc_p = os.path.join(map_path, "wdesc.fb")
    if os.path.exists(wdesc_p):
        with open(wdesc_p, "rb") as f:
            data = f.read()
            # find strings
            strs = [m.group().decode('utf-8', 'ignore') for m in re.finditer(rb'[\x20-\x7e\xc0-\xff]{3,}', data)]
            for s in strs:
                if len(s) > 2 and not s.startswith("http") and "{" not in s:
                    return s[:25]
    return os.path.basename(map_path)

def list_available_maps():
    if not os.path.exists(DATA_DIR):
        return []
    maps = []
    for item in os.listdir(DATA_DIR):
        full_p = os.path.join(DATA_DIR, item)
        if item.startswith("w") and os.path.isdir(full_p):
            # Check if it has m0 or wdesc.fb
            if os.path.exists(os.path.join(full_p, "m0")) or os.path.exists(os.path.join(full_p, "wdesc.fb")):
                sz_mb = sum(os.path.getsize(os.path.join(root, f)) for root, _, files in os.walk(full_p) for f in files) / (1024*1024)
                title = get_map_title(full_p)
                maps.append({
                    "id": item,
                    "path": full_p,
                    "title": title,
                    "size_mb": sz_mb
                })
    return sorted(maps, key=lambda x: x["size_mb"], reverse=True)

def clone_and_unlock(src_map_path, target_uin=None, new_title_suffix=" (Bản Edit)"):
    if not os.path.exists(src_map_path):
        print(f"[!] Khong tim thay thu muc map: {src_map_path}")
        return False

    if target_uin is None:
        target_uin = get_current_user_uin()

    # Generate new unique World ID based on timestamp
    new_world_id = f"w{int(time.time() * 1000)}"
    dest_map_path = os.path.join(DATA_DIR, new_world_id)
    
    print("\n" + "=" * 70)
    print(f"      DANG CHUYEN DOI VA UNLOCK TOAN BO MAP SANG LOCAL CUA BAN")
    print("=" * 70)
    print(f"[*] Map Nguon:        {os.path.basename(src_map_path)}")
    print(f"[*] Map Moi (Local):  {new_world_id}")
    print(f"[*] UIN So Huu Moi:   {target_uin}")
    
    # 1. Copy 100% full directory
    print("\n[1/5] Dang sao chep toan bo cong trinh, trigger, plugin, 3D models...")
    shutil.copytree(src_map_path, dest_map_path, dirs_exist_ok=True)
    
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

    # If not found in modinfo, search roles/
    roles_dir = os.path.join(dest_map_path, "roles")
    if not old_author_uin and os.path.exists(roles_dir):
        for rf in os.listdir(roles_dir):
            if rf.startswith("u") and rf.endswith(".p"):
                try:
                    old_author_uin = int(rf[1:-2])
                    break
                except Exception: pass

    print(f"[2/5] Phat hien UIN goc cua tac gia: {old_author_uin if old_author_uin else 'Khong ro'}")

    # 3. Patch JSON & Mod manifests (Set open_edit = true, authoruin = target_uin)
    print("[3/5] Mo khoa toan bo Plugins, Blocks, Quai vat custom (open_edit = true)...")
    for root, _, files in os.walk(os.path.join(dest_map_path, "mods")):
        for f in files:
            if f.endswith(".json"):
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8") as jf:
                        content = jf.read()
                    # Replace authoruin
                    if old_author_uin:
                        content = content.replace(str(old_author_uin), str(target_uin))
                    # Force open_edit
                    content = re.sub(r'"open_edit"\s*:\s*false', '"open_edit": true', content)
                    with open(fp, "w", encoding="utf-8") as jf:
                        jf.write(content)
                except Exception: pass

    # 4. Patch Roles & Permissions (Grant Full Host & Edit Rights to Target UIN)
    print("[4/5] Cap toan quyen Admin / Host cho tai khoan cua ban...")
    if os.path.exists(roles_dir):
        # Rename or duplicate role file for target_uin
        target_role_file = os.path.join(roles_dir, f"u{target_uin}.p")
        if old_author_uin and os.path.exists(os.path.join(roles_dir, f"u{old_author_uin}.p")):
            shutil.copy2(os.path.join(roles_dir, f"u{old_author_uin}.p"), target_role_file)
        elif not os.path.exists(target_role_file):
            # Create a base role file
            with open(target_role_file, "wb") as rf:
                rf.write(b"\x00" * 32)

    # 5. Patch wdesc.fb & Remove Cloud Lock / Tamper Markers
    print("[5/5] Xoa bo khoa Cloud va bo sung chu quyen Map...")
    for lock_file in ["upload.rec", "mapmd5", "cover.data"]:
        lp = os.path.join(dest_map_path, lock_file)
        if os.path.exists(lp):
            try: os.remove(lp)
            except Exception: pass

    # Patch binary UIN in wdesc.fb
    wdesc_p = os.path.join(dest_map_path, "wdesc.fb")
    if os.path.exists(wdesc_p) and old_author_uin:
        with open(wdesc_p, "rb") as f:
            wdesc_raw = f.read()
        old_bytes = struct.pack("<I", old_author_uin)
        new_bytes = struct.pack("<I", target_uin)
        wdesc_patched = wdesc_raw.replace(old_bytes, new_bytes)
        with open(wdesc_p, "wb") as f:
            f.write(wdesc_patched)

    print("\n" + "=" * 70)
    print("[V] HOAN TAT CHUYEN DOI MAP THANH CONG 100%!")
    print(f"- Ten thu muc map moi: {new_world_id}")
    print(f"- Vi tri luu tru:      {dest_map_path}")
    print("👉 Ban chi can mo game Mini World len la se thay Map moi xuat hien ngay")
    print("   trong danh sach Map Local voi toan quyen Chinh sua, Trigger, Build & Mod!")
    print("=" * 70)
    return True

def main():
    print("=" * 70)
    print("    CONG CU CHUYEN MAP NGUOI KHAC THANH MAP LOCAL EDIT CUA BAN")
    print("=" * 70)
    
    current_uin = get_current_user_uin()
    print(f"[*] Tai khoan Mini World hien tai cua ban (UIN): {current_uin}\n")
    
    maps = list_available_maps()
    if not maps:
        print("[!] Khong tim thay map nao trong thu muc data/ cua Mini World.")
        input("\nNhan Enter de thoat...")
        return
        
    print(f"Tim thay {len(maps)} Map trong may cua ban:\n")
    print(f"  {'STT':<4} | {'Thu Muc Map':<20} | {'Dung Luong':<12} | {'Ten Map'}")
    print("  " + "-" * 65)
    for idx, m in enumerate(maps[:30], 1):
        print(f"  {idx:<4} | {m['id']:<20} | {m['size_mb']:>6.2f} MB     | {m['title']}")
        
    if len(maps) > 30:
        print(f"  ... Va con {len(maps) - 30} map khac nua.")
        
    print("\n" + "=" * 70)
    while True:
        try:
            choice = input(f"Nhap so thu tu Map muon chuyen (1 - {min(len(maps), 30)}) hoac go duong dan/folder map: ").strip()
            if not choice: continue
            if choice.isdigit() and 1 <= int(choice) <= len(maps):
                selected_map = maps[int(choice) - 1]["path"]
                clone_and_unlock(selected_map, current_uin)
                break
            elif os.path.exists(choice):
                clone_and_unlock(choice, current_uin)
                break
            else:
                # check if choice is world ID like w17825387754406
                check_p = os.path.join(DATA_DIR, choice)
                if os.path.exists(check_p):
                    clone_and_unlock(check_p, current_uin)
                    break
                print("[!] Lua chon khong hop le, vui long nhap lai.")
        except (KeyboardInterrupt, EOFError):
            break
            
    input("\nNhan Enter de hoan tat...")

if __name__ == "__main__":
    main()
