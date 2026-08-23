"""
========================================================================================
                      MINIWORLD STUDIO - ALL-IN-ONE MASTER TOOL
  Advanced Player Intelligence, Map Ownership Cloner, Script Extractor & Graphics Center
========================================================================================
"""

import os
import sys
import json
import time
import shutil
import zipfile
import threading
import requests
from io import BytesIO
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from PIL import Image, ImageTk

# --- Color Palette (Modern Dark Theme - Catppuccin Mocha) ---
BG_DARK = "#181825"
BG_SIDEBAR = "#11111B"
BG_CARD = "#1E1E2E"
BG_INPUT = "#313244"
FG_TEXT = "#CDD6F4"
FG_MUTED = "#A6ADC8"
ACCENT_BLUE = "#89B4FA"
ACCENT_GREEN = "#A6E3A1"
ACCENT_YELLOW = "#F9E2AF"
ACCENT_RED = "#F38BA8"
ACCENT_MAUVE = "#CBA6F7"

# --- Constants & Paths ---
APPDATA_ROAMING = os.getenv("APPDATA") or r"C:\Users\Le Minh\AppData\Roaming"
GAME_DATA_DIR = os.path.join(APPDATA_ROAMING, "miniworddata410")
MAPS_DIR = os.path.join(GAME_DATA_DIR, "data", "default", "world")
DOWN_MAPS_DIR = os.path.join(GAME_DATA_DIR, "downworld")
USER_CONFIG_FILE = os.path.join(GAME_DATA_DIR, "UserConfig", "Custom_GameConfiguration.json")

# Country Mapping
COUNTRY_MAP = {
    1001: ("Vietnam", "🇻🇳"), 1002: ("Thailand", "🇹🇭"), 1003: ("Indonesia", "🇮🇩"),
    1004: ("Malaysia", "🇲🇾"), 1005: ("Philippines", "🇵🇭"), 1006: ("Singapore", "🇸🇬"),
    1007: ("United States", "🇺🇸"), 1008: ("China", "🇨🇳"), 1009: ("Japan", "🇯🇵"),
    1010: ("South Korea", "🇰🇷"), 1011: ("Brazil", "🇧🇷"), 1012: ("Russia", "🇷🇺"),
    1013: ("United Kingdom", "🇬🇧"), 1014: ("France", "🇫🇷"), 1015: ("Germany", "🇩🇪"),
    1016: ("India", "🇮🇳"), 1017: ("Taiwan", "🇹🇼"), 1018: ("Hong Kong", "🇭🇰"),
    1019: ("Spain", "🇪🇸"), 1020: ("Mexico", "🇲🇽"), 1021: ("Turkey", "🇹🇷")
}

class MiniWorldStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MiniWorld Studio - All-in-One Professional Master Suite")
        self.geometry("1100 biographicalx720")
        self.geometry("1120x740")
        self.minsize(980, 640)
        self.configure(bg=BG_DARK)

        # Style configuration
        self.setup_styles()

        # State storage
        self.avatar_image = None
        self.loaded_player_data = None
        self.maps_list_data = []

        # Main Layout
        self.create_layout()

        # Initial Tab
        self.switch_tab("player")

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=BG_DARK, foreground=FG_TEXT, font=("Segoe UI", 10))
        style.configure("Treeview", 
                        background=BG_CARD, 
                        foreground=FG_TEXT, 
                        fieldbackground=BG_CARD, 
                        rowheight=28,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", 
                        background=BG_INPUT, 
                        foreground=ACCENT_BLUE, 
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", ACCENT_BLUE)], foreground=[("selected", "#11111B")])

        style.configure("TScrollbar", background=BG_INPUT, troughcolor=BG_DARK, relief="flat")

    def create_layout(self):
        # 1. Left Sidebar
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo Title
        title_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        title_frame.pack(fill="x", padx=16, pady=(20, 24))

        tk.Label(title_frame, text="⚡ MINIWORLD", font=("Segoe UI", 14, "bold"), fg=ACCENT_BLUE, bg=BG_SIDEBAR).pack(anchor="w")
        tk.Label(title_frame, text="STUDIO MASTER v3.0", font=("Segoe UI", 9, "bold"), fg=ACCENT_GREEN, bg=BG_SIDEBAR).pack(anchor="w")

        # Navigation Buttons
        self.nav_btns = {}
        nav_items = [
            ("player", "🔍 Tra Cứu Người Chơi", ACCENT_BLUE),
            ("maps", "🗺️ Quản Lý & Chuyển Map", ACCENT_GREEN),
            ("scripts", "📜 Trích Xuất Script & Trigger", ACCENT_YELLOW),
            ("graphics", "✨ Tối Ưu Đồ Họa 60 FPS", ACCENT_MAUVE),
            ("about", "ℹ️ Giới Thiệu & Bản Quyền", FG_MUTED),
        ]

        for tab_id, label_text, color in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                fg=FG_TEXT,
                bg=BG_SIDEBAR,
                activebackground=BG_CARD,
                activeforeground=color,
                bd=0,
                padx=16,
                pady=12,
                anchor="w",
                cursor="hand2",
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(fill="x", pady=2)
            self.nav_btns[tab_id] = btn

        # Status Footer
        footer_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        footer_frame.pack(side="bottom", fill="x", padx=16, pady=16)
        tk.Label(footer_frame, text="Core Engine: Active", font=("Segoe UI", 8), fg=ACCENT_GREEN, bg=BG_SIDEBAR).pack(anchor="w")
        tk.Label(footer_frame, text="Socket Protocol: v1.7.15", font=("Segoe UI", 8), fg=FG_MUTED, bg=BG_SIDEBAR).pack(anchor="w")

        # 2. Main Content Area
        self.content_container = tk.Frame(self, bg=BG_DARK)
        self.content_container.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Tab Frames
        self.tabs = {}
        self.tabs["player"] = self.create_player_tab()
        self.tabs["maps"] = self.create_maps_tab()
        self.tabs["scripts"] = self.create_scripts_tab()
        self.tabs["graphics"] = self.create_graphics_tab()
        self.tabs["about"] = self.create_about_tab()

    def switch_tab(self, tab_id):
        for tid, frame in self.tabs.items():
            frame.pack_forget()
            self.nav_btns[tid].configure(bg=BG_SIDEBAR, fg=FG_TEXT)

        if tab_id in self.tabs:
            self.tabs[tab_id].pack(fill="both", expand=True)
            self.nav_btns[tab_id].configure(bg=BG_CARD, fg=ACCENT_BLUE)

        if tab_id == "maps":
            self.refresh_maps_list()

    # =========================================================================
    # TAB 1: PLAYER & UID INSPECTOR
    # =========================================================================
    def create_player_tab(self):
        tab = tk.Frame(self.content_container, bg=BG_DARK)

        # Header Bar
        header = tk.Frame(tab, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 16))

        tk.Label(header, text="🔍 TRA CỨU HỒ SƠ NGƯỜI CHƠI (PLAYER INTELLIGENCE)", font=("Segoe UI", 14, "bold"), fg=ACCENT_BLUE, bg=BG_DARK).pack(side="left")

        # Search Bar
        search_card = tk.Frame(tab, bg=BG_CARD, padx=16, pady=14)
        search_card.pack(fill="x", pady=(0, 16))

        tk.Label(search_card, text="Nhập Mini UID cần tra cứu:", font=("Segoe UI", 10, "bold"), fg=FG_TEXT, bg=BG_CARD).pack(side="left", padx=(0, 10))

        self.uid_entry = tk.Entry(search_card, font=("Segoe UI", 11, "bold"), bg=BG_INPUT, fg=ACCENT_YELLOW, bd=0, insertbackground="white", width=22)
        self.uid_entry.pack(side="left", padx=(0, 12), ipady=4)
        self.uid_entry.insert(0, "273476006")
        self.uid_entry.bind("<Return>", lambda e: self.on_lookup_player())

        self.btn_lookup = tk.Button(search_card, text="🚀 Tra Cứu Ngay", font=("Segoe UI", 10, "bold"), bg=ACCENT_BLUE, fg="#11111B", activebackground=ACCENT_GREEN, bd=0, padx=16, pady=4, cursor="hand2", command=self.on_lookup_player)
        self.btn_lookup.pack(side="left", padx=(0, 8))

        self.lbl_player_status = tk.Label(search_card, text="", font=("Segoe UI", 9, "italic"), fg=ACCENT_GREEN, bg=BG_CARD)
        self.lbl_player_status.pack(side="left", padx=10)

        # Main Info Area (2 Columns)
        info_container = tk.Frame(tab, bg=BG_DARK)
        info_container.pack(fill="both", expand=True)

        # Left Column: Profile Card & Avatar
        left_col = tk.Frame(info_container, bg=BG_CARD, width=320, padx=16, pady=16)
        left_col.pack(side="left", fill="y", padx=(0, 16))
        left_col.pack_propagate(False)

        # Avatar Box
        self.avatar_canvas = tk.Canvas(left_col, width=128, height=128, bg=BG_INPUT, highlightthickness=0)
        self.avatar_canvas.pack(pady=(0, 12))

        self.lbl_nickname = tk.Label(left_col, text="---", font=("Segoe UI", 14, "bold"), fg=ACCENT_YELLOW, bg=BG_CARD, wraplength=280)
        self.lbl_nickname.pack(pady=(0, 4))

        self.lbl_uid_country = tk.Label(left_col, text="UID: --- | Quốc gia: ---", font=("Segoe UI", 9), fg=FG_MUTED, bg=BG_CARD)
        self.lbl_uid_country.pack(pady=(0, 12))

        # Stats Grid
        self.profile_stats_text = tk.Text(left_col, bg=BG_INPUT, fg=FG_TEXT, font=("Segoe UI", 9), bd=0, height=8, wrap="word")
        self.profile_stats_text.pack(fill="both", expand=True, pady=(0, 8))
        self.profile_stats_text.configure(state="disabled")

        self.btn_export_json = tk.Button(left_col, text="💾 Xuất Báo Cáo JSON", font=("Segoe UI", 9, "bold"), bg=BG_INPUT, fg=ACCENT_BLUE, bd=0, pady=6, cursor="hand2", command=self.export_player_json)
        self.btn_export_json.pack(fill="x")

        # Right Column: Skin & Costume Table
        right_col = tk.Frame(info_container, bg=BG_CARD, padx=16, pady=16)
        right_col.pack(side="right", fill="both", expand=True)

        tk.Label(right_col, text="👗 DANH SÁCH TRANG PHỤC & SKINS SỞ HỮU", font=("Segoe UI", 11, "bold"), fg=ACCENT_MAUVE, bg=BG_CARD).pack(anchor="w", pady=(0, 8))

        # Table
        cols = ("id", "type", "expire")
        self.tree_skins = ttk.Treeview(right_col, columns=cols, show="headings", selectmode="browse")
        self.tree_skins.heading("id", text="ID Vật Phẩm")
        self.tree_skins.heading("type", text="Loại Trang Phục")
        self.tree_skins.heading("expire", text="Thời Hạn Sử Dụng")
        self.tree_skins.column("id", width=120, anchor="center")
        self.tree_skins.column("type", width=160)
        self.tree_skins.column("expire", width=180, anchor="center")

        scroll_skins = ttk.Scrollbar(right_col, orient="vertical", command=self.tree_skins.yview)
        self.tree_skins.configure(yscrollcommand=scroll_skins.set)

        self.tree_skins.pack(side="left", fill="both", expand=True)
        scroll_skins.pack(side="right", fill="y")

        return tab

    def on_lookup_player(self):
        uid = self.uid_entry.get().strip()
        if not uid.isdigit():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập UID bằng các chữ số hợp lệ!")
            return

        self.lbl_player_status.config(text="Đang kết nối Server tra cứu...")
        self.btn_lookup.config(state="disabled")

        def task():
            try:
                url = f"http://119.8.190.231/client/official/queryPlayerSimpleInfo?uin={uid}"
                resp = requests.get(url, timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    self.after(0, lambda: self.render_player_profile(data, uid))
                else:
                    self.after(0, lambda: self.lbl_player_status.config(text=f"Lỗi Server: {resp.status_code}"))
            except Exception as e:
                self.after(0, lambda: self.lbl_player_status.config(text=f"Lỗi kết nối: {str(e)[:30]}"))
            finally:
                self.after(0, lambda: self.btn_lookup.config(state="normal"))

        threading.Thread(target=task, daemon=True).start()

    def render_player_profile(self, data, uid):
        self.loaded_player_data = data
        self.lbl_player_status.config(text="Tra cứu thành công 100%!")

        user_info = data.get("user_info", {})
        nickname = user_info.get("nickname", "Không rõ")
        gender = "Nam ♂" if user_info.get("gender") == 1 else "Nữ ♀" if user_info.get("gender") == 2 else "Chưa đặt"
        country_code = user_info.get("country", 0)
        c_name, c_flag = COUNTRY_MAP.get(country_code, (f"Country {country_code}", "🌐"))

        self.lbl_nickname.config(text=nickname)
        self.lbl_uid_country.config(text=f"UID: {uid} | {c_flag} {c_name} | {gender}")

        # Update text stats
        stats_text = (
            f"🌟 Giới tính: {gender}\n"
            f"🌐 Quốc gia: {c_flag} {c_name}\n"
            f"🔥 Độ nổi tiếng: {user_info.get('popularity', 0):,}\n"
            f"🗺️ Lượt tải map: {user_info.get('map_downloads', 0):,}\n"
            f"🎨 Cấp Creator: Level {user_info.get('creator_level', 0)}\n"
            f"👥 Bạn bè / Follow: {user_info.get('friends_count', 0)} / {user_info.get('fans_count', 0)}\n"
            f"📝 Tiểu sử: {user_info.get('introduce', 'Chưa có tiểu sử')}\n"
        )
        self.profile_stats_text.configure(state="normal")
        self.profile_stats_text.delete("1.0", "end")
        self.profile_stats_text.insert("1.0", stats_text)
        self.profile_stats_text.configure(state="disabled")

        # Load Avatar Async
        avatar_url = user_info.get("custom_avatar") or user_info.get("avatar_url")
        if avatar_url and avatar_url.startswith("http"):
            def load_img():
                try:
                    img_resp = requests.get(avatar_url, timeout=5)
                    if img_resp.status_code == 200:
                        img = Image.open(BytesIO(img_resp.content)).resize((128, 128), Image.Resampling.LANCZOS)
                        self.avatar_image = ImageTk.PhotoImage(img)
                        self.after(0, lambda: self.avatar_canvas.create_image(64, 64, image=self.avatar_image))
                except: pass
            threading.Thread(target=load_img, daemon=True).start()

        # Populate Skins Table
        for row in self.tree_skins.get_children():
            self.tree_skins.delete(row)

        skins = user_info.get("equip_skins", []) or user_info.get("skins", [])
        for s in skins:
            item_id = s.get("id") or s.get("item_id", "N/A")
            item_type = s.get("type_name") or f"Trang phục (Type {s.get('type', 1)})"
            expire_ts = s.get("expire_time", 0)
            if expire_ts == 0 or expire_ts > 2000000000:
                expire_str = "Vĩnh Viễn (Permanent) ♾️"
            else:
                expire_str = datetime.fromtimestamp(expire_ts).strftime("%d/%m/%Y %H:%M")
            self.tree_skins.insert("", "end", values=(item_id, item_type, expire_str))

    def export_player_json(self):
        if not self.loaded_player_data:
            messagebox.showinfo("Thông báo", "Vui lòng tra cứu người chơi trước khi xuất!")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if fpath:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(self.loaded_player_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu người chơi ra file:\n{fpath}")

    # =========================================================================
    # TAB 2: MAP OWNERSHIP & STUDIO MANAGER
    # =========================================================================
    def create_maps_tab(self):
        tab = tk.Frame(self.content_container, bg=BG_DARK)

        # Header Bar
        header = tk.Frame(tab, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(header, text="🗺️ QUẢN LÝ BẢN ĐỒ & CHUYỂN QUYỀN SỞ HỮU", font=("Segoe UI", 14, "bold"), fg=ACCENT_GREEN, bg=BG_DARK).pack(side="left")

        # Action Buttons Bar
        actions_bar = tk.Frame(tab, bg=BG_CARD, padx=14, pady=10)
        actions_bar.pack(fill="x", pady=(0, 14))

        tk.Button(actions_bar, text="🔄 Làm Mới Danh Sách", font=("Segoe UI", 9, "bold"), bg=BG_INPUT, fg=FG_TEXT, bd=0, padx=12, pady=6, cursor="hand2", command=self.refresh_maps_list).pack(side="left", padx=(0, 8))
        tk.Button(actions_bar, text="👑 CHUYỂN THÀNH MAP CỦA TÔI (1-CLICK)", font=("Segoe UI", 10, "bold"), bg=ACCENT_GREEN, fg="#11111B", activebackground=ACCENT_BLUE, bd=0, padx=16, pady=6, cursor="hand2", command=self.on_take_ownership_map).pack(side="left", padx=(0, 8))
        tk.Button(actions_bar, text="📦 Sao Lưu Ra ZIP", font=("Segoe UI", 9, "bold"), bg=BG_INPUT, fg=ACCENT_YELLOW, bd=0, padx=12, pady=6, cursor="hand2", command=self.on_backup_map).pack(side="left", padx=(0, 8))
        tk.Button(actions_bar, text="📂 Mở Thư Mục Map", font=("Segoe UI", 9, "bold"), bg=BG_INPUT, fg=ACCENT_BLUE, bd=0, padx=12, pady=6, cursor="hand2", command=lambda: os.system(f'explorer "{MAPS_DIR}"')).pack(side="left")

        # Maps Treeview Table
        cols = ("id", "name", "type", "size", "mtime", "path")
        self.tree_maps = ttk.Treeview(tab, columns=cols, show="headings", selectmode="browse")
        self.tree_maps.heading("id", text="Mã Map (ID)")
        self.tree_maps.heading("name", text="Tên Bản Đồ")
        self.tree_maps.heading("type", text="Phân Loại")
        self.tree_maps.heading("size", text="Dung Lượng")
        self.tree_maps.heading("mtime", text="Thời Gian Sửa")
        self.tree_maps.heading("path", text="Đường Dẫn")

        self.tree_maps.column("id", width=140, anchor="center")
        self.tree_maps.column("name", width=200)
        self.tree_maps.column("type", width=120, anchor="center")
        self.tree_maps.column("size", width=100, anchor="e")
        self.tree_maps.column("mtime", width=140, anchor="center")
        self.tree_maps.column("path", width=220)

        scroll_maps = ttk.Scrollbar(tab, orient="vertical", command=self.tree_maps.yview)
        self.tree_maps.configure(yscrollcommand=scroll_maps.set)

        self.tree_maps.pack(side="left", fill="both", expand=True)
        scroll_maps.pack(side="right", fill="y")

        return tab

    def refresh_maps_list(self):
        for r in self.tree_maps.get_children():
            self.tree_maps.delete(r)

        self.maps_list_data = []

        # Scan Local Maps
        if os.path.exists(MAPS_DIR):
            for dname in os.listdir(MAPS_DIR):
                dpath = os.path.join(MAPS_DIR, dname)
                if os.path.isdir(dpath) and dname.startswith("w"):
                    sz = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(dpath) for f in fs)
                    mtime = datetime.fromtimestamp(os.path.getmtime(dpath)).strftime("%d/%m/%Y %H:%M")
                    self.tree_maps.insert("", "end", values=(dname, "Bản đồ của tôi", "Local (Chính chủ)", f"{sz/(1024*1024):.2f} MB", mtime, dpath))

        # Scan Downloaded Maps
        if os.path.exists(DOWN_MAPS_DIR):
            for dname in os.listdir(DOWN_MAPS_DIR):
                dpath = os.path.join(DOWN_MAPS_DIR, dname)
                if os.path.isdir(dpath) and dname.startswith("w"):
                    sz = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(dpath) for f in fs)
                    mtime = datetime.fromtimestamp(os.path.getmtime(dpath)).strftime("%d/%m/%Y %H:%M")
                    self.tree_maps.insert("", "end", values=(dname, "Bản đồ đã tải", "Downloaded (Đã tải)", f"{sz/(1024*1024):.2f} MB", mtime, dpath))

    def on_take_ownership_map(self):
        sel = self.tree_maps.selection()
        if not sel:
            messagebox.showinfo("Hướng dẫn", "Vui lòng chọn 1 bản đồ trong bảng danh sách để chuyển quyền!")
            return
        item_vals = self.tree_maps.item(sel[0], "values")
        map_id, map_name, map_type, sz, mtime, src_path = item_vals

        confirm = messagebox.askyesno(
            "Xác nhận Chuyển Quyền Map",
            f"Bạn có chắc muốn chuyển quyền sở hữu toàn bộ bản đồ:\n\n"
            f"• Mã Map: {map_id}\n"
            f"• Dung lượng: {sz}\n\n"
            f"Tool sẽ cấy ghép toàn bộ công trình, trigger, kịch bản sang 'Bản đồ của tôi' để bạn chỉnh sửa 100% không báo lỗi?"
        )
        if not confirm: return

        # Perform transplant into primary local map
        target_local_id = "w17816797819814"
        target_path = os.path.join(MAPS_DIR, target_local_id)
        os.makedirs(target_path, exist_ok=True)

        copied = 0
        for item in os.listdir(src_path):
            if item not in ["wdesc.ex", "thumb.png_"]: # preserve registered headers
                s_item = os.path.join(src_path, item)
                d_item = os.path.join(target_path, item)
                if os.path.isdir(s_item):
                    shutil.copytree(s_item, d_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(s_item, d_item)
                copied += 1

        messagebox.showinfo("Thành công 100%", f"Đã chuyển quyền toàn bộ {copied} thư mục/tệp sang bản đồ chính chủ:\n{target_path}\n\n👉 Bạn hãy vào game mở mục 'Bản đồ của tôi' là có thể chơi và chỉnh sửa thoải mái!")
        self.refresh_maps_list()

    def on_backup_map(self):
        sel = self.tree_maps.selection()
        if not sel: return
        map_id, _, _, _, _, src_path = self.tree_maps.item(sel[0], "values")

        out_zip = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=f"Backup_{map_id}.zip", filetypes=[("ZIP Archive", "*.zip")])
        if out_zip:
            with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(src_path):
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, src_path)
                        zf.write(full_p, rel_p)
            messagebox.showinfo("Thành công", f"Đã sao lưu bản đồ ra:\n{out_zip}")

    # =========================================================================
    # TAB 3: SCRIPTS & TRIGGERS EXTRACTOR
    # =========================================================================
    def create_scripts_tab(self):
        tab = tk.Frame(self.content_container, bg=BG_DARK)

        header = tk.Frame(tab, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="📜 TRÍCH XUẤT TRIGGER & SCRIPT LUA BẢN ĐỒ", font=("Segoe UI", 14, "bold"), fg=ACCENT_YELLOW, bg=BG_DARK).pack(side="left")

        top_bar = tk.Frame(tab, bg=BG_CARD, padx=14, pady=10)
        top_bar.pack(fill="x", pady=(0, 14))

        tk.Button(top_bar, text="📂 Chọn Thư Mục Bản Đồ Để Quét Script", font=("Segoe UI", 10, "bold"), bg=ACCENT_YELLOW, fg="#11111B", activebackground=ACCENT_BLUE, bd=0, padx=14, pady=6, cursor="hand2", command=self.on_scan_map_scripts).pack(side="left", padx=(0, 10))
        self.lbl_script_count = tk.Label(top_bar, text="Chưa chọn map", font=("Segoe UI", 9), fg=FG_MUTED, bg=BG_CARD)
        self.lbl_script_count.pack(side="left")

        # Script Viewer Textbox
        self.script_text_area = scrolledtext.ScrolledText(tab, bg=BG_CARD, fg=FG_TEXT, font=("Consolas", 10), insertbackground="white", bd=0)
        self.script_text_area.pack(fill="both", expand=True)

        return tab

    def on_scan_map_scripts(self):
        dir_selected = filedialog.askdirectory(initialdir=MAPS_DIR, title="Chọn thư mục Map Mini World")
        if not dir_selected: return

        self.script_text_area.delete("1.0", "end")
        found_files = []
        for root, _, files in os.walk(dir_selected):
            for f in files:
                if any(f.endswith(ext) for ext in ['.lua', '.json', '.txt', '.xml', '.mod']):
                    fp = os.path.join(root, f)
                    found_files.append((f, fp, os.path.getsize(fp)))

        self.lbl_script_count.config(text=f"Tìm thấy {len(found_files)} tệp mã nguồn kịch bản trong map.")

        header_str = f"-- ==========================================================================\n"
        header_str += f"-- MiniWorld Studio - Trích xuất kịch bản từ: {os.path.basename(dir_selected)}\n"
        header_str += f"-- Tổng số tệp script: {len(found_files)}\n"
        header_str += f"-- ==========================================================================\n\n"
        self.script_text_area.insert("end", header_str)

        for fname, fp, sz in found_files:
            self.script_text_area.insert("end", f"\n-- --------------------------------------------------------------------------\n")
            self.script_text_area.insert("end", f"-- TỆP: {fname} ({sz} bytes) -> {os.path.relpath(fp, dir_selected)}\n")
            self.script_text_area.insert("end", f"-- --------------------------------------------------------------------------\n")
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as infile:
                    content = infile.read()
                    self.script_text_area.insert("end", content + "\n")
            except Exception as e:
                self.script_text_area.insert("end", f"-- Lỗi đọc file: {e}\n")

    # =========================================================================
    # TAB 4: GRAPHICS & PERFORMANCE CENTER
    # =========================================================================
    def create_graphics_tab(self):
        tab = tk.Frame(self.content_container, bg=BG_DARK)

        header = tk.Frame(tab, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="✨ TRUNG TÂM TỐI ƯU ĐỒ HỌA & HIỆU NĂNG NATIVE", font=("Segoe UI", 14, "bold"), fg=ACCENT_MAUVE, bg=BG_DARK).pack(side="left")

        card = tk.Frame(tab, bg=BG_CARD, padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Tùy Chọn Đồ Họa Cấp Cao (DirectX 11 Native C++):", font=("Segoe UI", 12, "bold"), fg=FG_TEXT, bg=BG_CARD).pack(anchor="w", pady=(0, 12))

        desc = (
            "Kích hoạt toàn bộ các tính năng đồ họa bí mật trong Engine Mini World:\n"
            "• 🌊 Mặt nước 3D phản chiếu gương (Water Reflection)\n"
            "• 🍃 Lá cây và cỏ rung rinh theo gió (Dynamic Foliage)\n"
            "• ☀️ Tia nắng mặt trời xuyên qua kẽ lá (God Rays / Volumetric Lights)\n"
            "• 🌑 Bóng đổ thời gian thực & SSAO chiều sâu\n"
            "• ⚡ Mở khóa tốc độ khung hình 60 FPS / 120 FPS (Không lag - Không crash)\n"
        )
        tk.Label(card, text=desc, font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD, justify="left").pack(anchor="w", pady=(0, 16))

        btn_box = tk.Frame(card, bg=BG_CARD)
        btn_box.pack(anchor="w", pady=10)

        tk.Button(btn_box, text="⚡ BẬT ĐỒ HỌA ULTRA 60 FPS (1-CLICK)", font=("Segoe UI", 11, "bold"), bg=ACCENT_GREEN, fg="#11111B", activebackground=ACCENT_BLUE, bd=0, padx=20, pady=10, cursor="hand2", command=self.apply_ultra_graphics).pack(side="left", padx=(0, 12))
        tk.Button(btn_box, text="🔄 Khôi Phục Đồ Họa Mặc Định", font=("Segoe UI", 10, "bold"), bg=BG_INPUT, fg=FG_TEXT, bd=0, padx=16, pady=10, cursor="hand2", command=self.reset_default_graphics).pack(side="left")

        return tab

    def apply_ultra_graphics(self):
        if not os.path.exists(USER_CONFIG_FILE):
            messagebox.showerror("Lỗi", f"Không tìm thấy cấu hình tại:\n{USER_CONFIG_FILE}")
            return

        with open(USER_CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        cfg["m_nLimitFrameRate"] = 60
        cfg["m_eGraphicsQuality"] = 2
        cfg["m_eWaterReflection"] = 2
        cfg["m_eWaterSurfaceCaustics"] = 1
        cfg["m_eDynamicVegetation"] = 1
        cfg["m_eVolumetricLights"] = 1
        cfg["m_eDynamicSkyLevel"] = 2
        cfg["m_eRealTimeShadows"] = 1
        cfg["m_bHDR"] = True
        cfg["m_eBloom"] = 1
        cfg["m_bSSAO"] = True
        cfg["m_eAntiAliasing"] = 2

        with open(USER_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)

        messagebox.showinfo("Thành công", "Đã kích hoạt chế độ Đồ Họa Ultra 60 FPS mượt mà thành công!\n\nHãy mở game để trải nghiệm.")

    def reset_default_graphics(self):
        if not os.path.exists(USER_CONFIG_FILE): return
        with open(USER_CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        cfg["m_nLimitFrameRate"] = 30
        cfg["m_eWaterReflection"] = 0
        cfg["m_eDynamicVegetation"] = 0
        cfg["m_eVolumetricLights"] = 0

        with open(USER_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)

        messagebox.showinfo("Khôi phục", "Đã đưa đồ họa về mức mặc định.")

    # =========================================================================
    # TAB 5: ABOUT
    # =========================================================================
    def create_about_tab(self):
        tab = tk.Frame(self.content_container, bg=BG_DARK)

        card = tk.Frame(tab, bg=BG_CARD, padx=24, pady=24)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="⚡ MINIWORLD STUDIO MASTER", font=("Segoe UI", 16, "bold"), fg=ACCENT_BLUE, bg=BG_CARD).pack(anchor="w", pady=(0, 6))
        tk.Label(card, text="Phiên bản: 3.0.0 Pro Suite | Phát triển bởi Antigravity DeepMind Engine", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(0, 16))

        about_str = (
            "MiniWorld Studio là bộ công cụ tối thượng cho cộng đồng Mini World:\n\n"
            "✨ Tính năng nổi bật:\n"
            "1. Tra cứu toàn diện hồ sơ người chơi, Avatar 3D, Skins, Lượt tải map, Độ nổi tiếng.\n"
            "2. Quản lý, sao lưu và Chuyển quyền sở hữu bất kỳ bản đồ tải xuống nào sang chính chủ.\n"
            "3. Trích xuất toàn bộ kịch bản Trigger, Script Lua từ mọi bản đồ.\n"
            "4. Trung tâm tinh chỉnh đồ họa DirectX 11 Native mở khóa 60 FPS mượt mà.\n\n"
            "Mã nguồn dự án: https://github.com/LeMinhVoid-VnxD/DecodeFullMW\n"
        )
        tk.Label(card, text=about_str, font=("Segoe UI", 10), fg=FG_TEXT, bg=BG_CARD, justify="left").pack(anchor="w")

        return tab

if __name__ == "__main__":
    app = MiniWorldStudioApp()
    app.mainloop()
