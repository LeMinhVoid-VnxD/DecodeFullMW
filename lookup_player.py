import os
import sys
import json
import time
import urllib.request
import re

COUNTRY_NAMES = {
    "VN": "Việt Nam 🇻🇳",
    "TH": "Thái Lan 🇹🇭",
    "ID": "Indonesia 🇮🇩",
    "MY": "Malaysia 🇲🇾",
    "PH": "Philippines 🇵🇭",
    "SG": "Singapore 🇸🇬",
    "US": "Hoa Kỳ 🇺🇸",
    "BR": "Brazil 🇧🇷",
    "RU": "Nga 🇷🇺",
    "JP": "Nhật Bản 🇯🇵",
    "KR": "Hàn Quốc 🇰🇷",
    "CN": "Trung Quốc 🇨🇳",
    "TW": "Đài Loan 🇹🇼",
    "HK": "Hồng Kông 🇭🇰",
    "IN": "Ấn Độ 🇮🇳",
    "DE": "Đức 🇩🇪",
    "FR": "Pháp 🇫🇷",
    "GB": "Vương Quốc Anh 🇬🇧",
    "CA": "Canada 🇨🇦",
    "AU": "Úc 🇦🇺",
    "ES": "Tây Ban Nha 🇪🇸",
    "IT": "Ý 🇮🇹",
    "MX": "Mexico 🇲🇽",
    "TR": "Thổ Nhĩ Kỳ 🇹🇷"
}

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
    if country: 
        c_code = country.group(1).upper()
        data['Country'] = COUNTRY_NAMES.get(c_code, f"{c_code}")
        data['CountryCode'] = c_code
        
    pop = re.search(r'\["popularity"\]=(\d+)', text)
    if pop: data['Popularity'] = pop.group(1)
    
    dl = re.search(r'\["all_download_count"\]=(\d+)', text)
    if dl: data['Downloads'] = dl.group(1)
    
    gender = re.search(r'\["gender"\]=(\d+)', text)
    if gender: 
        g_val = gender.group(1)
        if g_val == "1":
            data['Gender'] = "Nam ♂️"
        elif g_val == "2":
            data['Gender'] = "Nữ ♀️"
        else:
            data['Gender'] = "Không công khai Ẩn"
            
    frame = re.search(r'\["head_frame_id"\]=(\d+)', text)
    if frame: data['Frame'] = frame.group(1)
    
    avatar_url = re.search(r'\["header"\]=\{[^}]*\["url"\]="([^"]+)"', text)
    if avatar_url: data['AvatarURL'] = avatar_url.group(1)
    
    creator_lvl = re.search(r'\["creator"\]=\{[^}]*\["level"\]=(\d+)', text)
    if creator_lvl: data['CreatorLevel'] = f"Level {creator_lvl.group(1)}"
    
    following = re.search(r'\["friend_attention"\]=(\d+)', text)
    followers = re.search(r'\["friend_beattention"\]=(\d+)', text)
    mutual = re.search(r'\["friend_eachother"\]=(\d+)', text)
    if following and followers and mutual:
        data['Social'] = f"Đang theo dõi: {following.group(1)} | Người theo dõi: {followers.group(1)} | Bạn bè: {mutual.group(1)}"

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

    print("\n" + "=" * 70)
    print(f"      TRÌNH TRA CỨU ĐẦY ĐỦ THÔNG TIN ID: {target_id}")
    print("=" * 70)
    
    t0 = time.time()
    
    local_info = search_local_cache(target_id)
    server_uin, server_items, api_url = query_live_server(target_id)
    
    elapsed = time.time() - t0
    
    if not local_info and not server_items:
        print(f"\n[!] Không tìm thấy dữ liệu cho ID: {target_id}")
        print("    (Hãy kiểm tra lại xem bạn đã nhập đúng số ID chưa)")
        return

    print(f"\n[+] KẾT QUẢ TRA CỨU CHI TIẾT (Tốc độ phản hồi: {elapsed:.2f}s):\n")
    
    print("┌" + "─" * 68 + "┐")
    print("│                    1. HỒ SƠ CÁ NHÂN (PROFILE)                      │")
    print("├" + "─" * 68 + "┤")
    
    if local_info:
        print(f"│  • Tên nhân vật:        {local_info.get('NickName', 'Chưa xác định'):<41}│")
        print(f"│  • Giới tính:           {local_info.get('Gender', 'Chưa rõ'):<41}│")
        print(f"│  • Quốc gia / Khu vực:  {local_info.get('Country', 'Việt Nam 🇻🇳'):<41}│")
        print(f"│  • Độ nổi tiếng:        {local_info.get('Popularity', '0') + ' điểm':<41}│")
        print(f"│  • Tổng lượt tải map:   {local_info.get('Downloads', '0') + ' lượt':<41}│")
        if local_info.get('CreatorLevel'):
            print(f"│  • Cấp Nhà sáng tạo:    {local_info.get('CreatorLevel'):<41}│")
        if local_info.get('Frame'):
            print(f"│  • Khung Avatar ID:     {local_info.get('Frame'):<41}│")
        if local_info.get('Social'):
            print(f"│  • Mạng xã hội:         {local_info.get('Social'):<41}│")
        if local_info.get('Bio'):
            print(f"│  • Chữ ký Bio:          \"{local_info.get('Bio')}\"")
        if local_info.get('AvatarURL'):
            print(f"│  • Ảnh Avatar tùy chọn: {local_info.get('AvatarURL')}")
    else:
        print(f"│  • UID Hiển thị:        {target_id:<41}│")
        print(f"│  • Server UIN Máy chủ:  {server_uin if server_uin else target_id:<41}│")
        print(f"│  • Máy chủ hoạt động:   Máy chủ Quốc Tế (Mini World Overseas)      │")
        print(f"│  • Trạng thái hồ sơ:    Tài khoản tồn tại và đang hoạt động          │")
    print("└" + "─" * 68 + "┘")

    if server_items:
        perm_items = [i for i in server_items if i.get("ExpireTime") == -1]
        temp_items = [i for i in server_items if i.get("ExpireTime") != -1]
        
        print(f"\n--- 2. DANH SÁCH TRANG PHỤC, SKIN & PHỤ KIỆN ({len(server_items)} MÓN) ---")
        print(f"  [★ Đồ Vĩnh Viễn: {len(perm_items)} món | ⏳ Đồ Có Thời Hạn: {len(temp_items)} món]\n")
        
        print(f"  {'STT':<4} | {'Vị Trí / Bộ Phận':<26} | {'Model ID':<10} | {'Hạn Sử Dụng'}")
        print("  " + "-" * 66)
        
        for idx, item in enumerate(server_items[:30], 1):
            p_name = get_part_name(item.get("Part", 0))
            m_id = item.get("ModelID", 0)
            exp = format_timestamp(item.get("ExpireTime"))
            print(f"  {idx:<4} | {p_name:<26} | Model {m_id:<4} | {exp}")
            
        if len(server_items) > 30:
            print(f"  ... Và còn {len(server_items) - 30} món đồ khác nữa.")

    if api_url:
        print(f"\n--- 3. LINK API TRUY VẤN MÁY CHỦ TRỰC TIẾP ---")
        print(f"  URL: {api_url}")

    print("\n" + "=" * 70)

def main():
    if len(sys.argv) > 1:
        lookup(sys.argv[1])
    else:
        while True:
            try:
                val = input("\nNhập ID Mini World cần tra cứu (hoặc gõ 'exit' để thoát): ").strip()
                if val.lower() in ['exit', 'quit', 'q']:
                    break
                if val:
                    lookup(val)
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    main()
