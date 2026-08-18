import os
import sys
import json
import time
import urllib.request
import re

def format_timestamp(ts):
    if not ts or ts == -1:
        return "Vĩnh viễn"
    try:
        return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(ts))
    except Exception:
        return str(ts)

def get_part_name(part_id):
    parts = {
        1: "Mũ / Tóc (Part 1)",
        2: "Khuôn mặt (Part 2)",
        3: "Áo / Thân trên (Part 3)",
        4: "Quần / Thân dưới (Part 4)",
        7: "Lưng / Cánh (Part 7)",
        8: "Hiệu ứng / Chân (Part 8)",
        9: "Phụ kiện đi kèm (Part 9)"
    }
    return parts.get(part_id, f"Phụ kiện (Part {part_id})")

def search_local_cache(input_id):
    cache_dirs = [
        r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\data\http\photo",
        r"D:\DecodeFullMW\01_Nguon_MiniWorld_Data410\07_Du_Lieu_Ban_Do_Saves_w\04_Cache_va_Du_Lieu_He_Thong\http\photo",
        r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\data\account\http___hwacchm.mini1.cn_4000",
    ]
    
    targets = [input_id, f"1{input_id}", f"10{input_id}", f"11{input_id}", f"100{input_id}"]
    
    for d in cache_dirs:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            for t in targets:
                if t in f and f.endswith(".list"):
                    fp = os.path.join(d, f)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f_in:
                            content = f_in.read()
                            return parse_lua_profile(content)
                    except Exception:
                        pass
    return None

def parse_lua_profile(text):
    data = {}
    nick = re.search(r'\["NickName"\]="([^"]+)"', text)
    if nick: data['NickName'] = nick.group(1)
    
    mood = re.search(r'\["mood_text"\]="([^"]+)"', text)
    if mood: data['Bio'] = mood.group(1).replace('\\n', ' ').strip()
    
    country = re.search(r'\["country"\]="([^"]+)"', text)
    if country: data['Country'] = country.group(1)
    
    pop = re.search(r'\["popularity"\]=(\d+)', text)
    if pop: data['Popularity'] = pop.group(1)
    
    dl = re.search(r'\["all_download_count"\]=(\d+)', text)
    if dl: data['Downloads'] = dl.group(1)
    
    gender = re.search(r'\["gender"\]=(\d+)', text)
    if gender: data['Gender'] = "Nam" if gender.group(1) == "1" else "Nữ"
    
    frame = re.search(r'\["head_frame_id"\]=(\d+)', text)
    if frame: data['Frame'] = frame.group(1)
    
    return data if data else None

def query_live_server(input_id):
    candidates = [
        input_id,
        f"1{input_id}",
        f"10{input_id}",
        f"11{input_id}",
        f"100{input_id}"
    ]
    
    headers = {"User-Agent": "MiniWorldClient/0.46.0"}
    
    for uin in candidates:
        url = f"http://update.miniworldgame.com:6000/miscquery/query_avatar_list_by_uin/?uin={uin}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as resp:
                res = json.loads(resp.read().decode('utf-8', errors='ignore'))
                if res.get("code") == 0 and res.get("msg"):
                    return uin, res["msg"], url
        except Exception:
            pass
            
    return None, None, None

def lookup(target_id):
    target_id = target_id.strip()
    if not target_id:
        return

    print("\n" + "=" * 65)
    print(f"      DANG TRA CUU THONG TIN ID: {target_id}")
    print("=" * 65)
    
    t0 = time.time()
    
    local_info = search_local_cache(target_id)
    server_uin, server_items, api_url = query_live_server(target_id)
    
    elapsed = time.time() - t0
    
    if not local_info and not server_items:
        print(f"\n[!] Khong tim thay du lieu cho ID: {target_id}")
        print("    (Hay kiem tra lai xem ban da nhap dung so ID chua)")
        return

    print(f"\n[+] KET QUA TRA CUU (Thoi gian phan hoi: {elapsed:.2f}s):\n")
    
    print("--- 1. THONG TIN NGUOI CHOI ---")
    if local_info:
        print(f"  - Ten nhan vat:     {local_info.get('NickName', 'Chua xac dinh')}")
        print(f"  - Quoc gia:         {local_info.get('Country', 'VN')}")
        print(f"  - Gioi tinh:        {local_info.get('Gender', 'Nam')}")
        print(f"  - Do noi tieng:     {local_info.get('Popularity', '0')} diem")
        print(f"  - Luot tai map:     {local_info.get('Downloads', '0')} luot")
        print(f"  - Khung Avatar ID:  {local_info.get('Frame', 'Khong')}")
        if local_info.get('Bio'):
            print(f"  - Chu ky ca nhan:   \"{local_info.get('Bio')}\"")
    else:
        print(f"  - UID Game:         {target_id}")
        print(f"  - Server UIN:       {server_uin if server_uin else target_id}")
        print(f"  - Trang thai:       Dang hoat dong tren May chu Quoc te (Overseas)")

    if server_items:
        print(f"\n--- 2. DANH SACH TRANG PHUC & SKIN ({len(server_items)} MON) ---")
        perm_items = [i for i in server_items if i.get("ExpireTime") == -1]
        temp_items = [i for i in server_items if i.get("ExpireTime") != -1]
        
        print(f"  [Vinh vien: {len(perm_items)} mon | Co han su dung: {len(temp_items)} mon]\n")
        
        print(f"  {'STT':<4} | {'Vi Tri / Bo Phan':<25} | {'Model ID':<10} | {'Han Su Dung'}")
        print("  " + "-" * 62)
        
        for idx, item in enumerate(server_items[:25], 1):
            p_name = get_part_name(item.get("Part", 0))
            m_id = item.get("ModelID", 0)
            exp = format_timestamp(item.get("ExpireTime"))
            print(f"  {idx:<4} | {p_name:<25} | Model {m_id:<4} | {exp}")
            
        if len(server_items) > 25:
            print(f"  ... Va con {len(server_items) - 25} mon do khac nua.")

    if api_url:
        print(f"\n--- 3. LINK API MAY CHU TRUC TIEP ---")
        print(f"  URL: {api_url}")

    print("\n" + "=" * 65)

def main():
    if len(sys.argv) > 1:
        lookup(sys.argv[1])
    else:
        while True:
            try:
                val = input("\nNhap ID Mini World can tra cuu (hoac go 'exit' de thoat): ").strip()
                if val.lower() in ['exit', 'quit', 'q']:
                    break
                if val:
                    lookup(val)
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    main()
