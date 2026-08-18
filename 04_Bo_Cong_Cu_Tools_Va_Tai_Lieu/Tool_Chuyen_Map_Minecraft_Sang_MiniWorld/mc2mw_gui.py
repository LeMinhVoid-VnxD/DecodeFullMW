"""
Mini World - Minecraft Map Converter GUI
Converts Minecraft Region files (.mca) to Mini World Region files (.r) & Full World Saves.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from converter_core import convert_minecraft_world, convert_single_mca

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft (.mca) -> Mini World (.r) Map Converter")
        self.root.geometry("780x640")
        self.root.minsize(700, 550)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.last_output_dir = None
        self._build_ui()
        self._auto_detect_defaults()

    def _build_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Title Banner
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        lbl_title = tk.Label(
            title_frame,
            text="MINECRAFT (.MCA) -> MINI WORLD (.R) CONVERTER",
            font=("Segoe UI", 13, "bold"),
            fg="#1a5fb4"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            title_frame,
            text="Chuyen doi ban do Minecraft sang ban do Mini World: CREATA tu dong va nhanh chong",
            font=("Segoe UI", 9),
            fg="#555555"
        )
        lbl_sub.pack(anchor="w")

        # 2. Input Section
        in_group = ttk.LabelFrame(main_frame, text=" 1. Chon Ban Do Minecraft Nguon ", padding="10")
        in_group.pack(fill=tk.X, pady=(0, 10))

        # Radio mode: Full World vs Single File
        self.mode_var = tk.StringVar(value="world")
        r_frame = ttk.Frame(in_group)
        r_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Radiobutton(r_frame, text="Chuyen doi ca Thu muc Map (World / Saves)", variable=self.mode_var, value="world", command=self._on_mode_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(r_frame, text="Chuyen doi 1 File .mca don le", variable=self.mode_var, value="file", command=self._on_mode_change).pack(side=tk.LEFT)

        in_input_frame = ttk.Frame(in_group)
        in_input_frame.pack(fill=tk.X, pady=5)
        
        self.input_path_var = tk.StringVar()
        self.txt_input = ttk.Entry(in_input_frame, textvariable=self.input_path_var, font=("Segoe UI", 9))
        self.txt_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.btn_browse_in = ttk.Button(in_input_frame, text="Duyet...", command=self._browse_input)
        self.btn_browse_in.pack(side=tk.RIGHT)

        # 3. Output Section
        out_group = ttk.LabelFrame(main_frame, text=" 2. Thu Muc Xuat Mini World ", padding="10")
        out_group.pack(fill=tk.X, pady=(0, 10))

        self.out_target_var = tk.StringVar(value="game")
        out_r_frame = ttk.Frame(out_group)
        out_r_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Radiobutton(out_r_frame, text="Xuat truc tiep vao Game Mini World (Vao choi duoc ngay)", variable=self.out_target_var, value="game", command=self._on_out_target_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(out_r_frame, text="Xuat ra Thu muc tuy chon tren may", variable=self.out_target_var, value="custom", command=self._on_out_target_change).pack(side=tk.LEFT)

        out_input_frame = ttk.Frame(out_group)
        out_input_frame.pack(fill=tk.X, pady=5)

        self.output_path_var = tk.StringVar()
        self.txt_output = ttk.Entry(out_input_frame, textvariable=self.output_path_var, font=("Segoe UI", 9))
        self.txt_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.btn_browse_out = ttk.Button(out_input_frame, text="Duyet...", command=self._browse_output)
        self.btn_browse_out.pack(side=tk.RIGHT)

        # World Name option
        name_frame = ttk.Frame(out_group)
        name_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(name_frame, text="Ten Map hien thi trong Mini World:").pack(side=tk.LEFT, padx=(0, 8))
        self.world_name_var = tk.StringVar(value="MC_Converted_World")
        ttk.Entry(name_frame, textvariable=self.world_name_var, width=30).pack(side=tk.LEFT)

        # 4. Action Section & Progress
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(5, 10))

        self.btn_convert = tk.Button(
            action_frame,
            text=" BẮT ĐẦU CHUYỂN ĐỔI NGAY ",
            font=("Segoe UI", 10, "bold"),
            bg="#2ec27e",
            fg="white",
            activebackground="#26a269",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._start_conversion
        )
        self.btn_convert.pack(side=tk.LEFT)

        self.btn_open_folder = ttk.Button(
            action_frame,
            text="Mo Thu Muc Xuat",
            state=tk.DISABLED,
            command=self._open_output_folder
        )
        self.btn_open_folder.pack(side=tk.RIGHT, pady=5)

        # 5. Log & Console Output
        log_group = ttk.LabelFrame(main_frame, text=" Nhat Ky Tien Do (Log) ", padding="5")
        log_group.pack(fill=tk.BOTH, expand=True)

        self.txt_log = tk.Text(log_group, wrap=tk.WORD, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_group, orient=tk.VERTICAL, command=self.txt_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log.config(yscrollcommand=scrollbar.set)

    def _auto_detect_defaults(self):
        # Auto detect Mini World game save dir
        appdata = os.environ.get("APPDATA", "")
        mw_save_dir = os.path.join(appdata, "miniworddata410", "data")
        if not os.path.exists(mw_save_dir):
            for d in os.listdir(appdata) if appdata and os.path.exists(appdata) else []:
                if "miniword" in d.lower() or "miniworld" in d.lower():
                    cand = os.path.join(appdata, d, "data")
                    if os.path.exists(cand):
                        mw_save_dir = cand
                        break
        self.mw_default_dir = mw_save_dir
        self.output_path_var.set(self.mw_default_dir)

        # Auto detect Minecraft saves dir
        mc_saves_dir = os.path.join(appdata, ".minecraft", "saves")
        if os.path.exists(mc_saves_dir):
            saves = [os.path.join(mc_saves_dir, s) for s in os.listdir(mc_saves_dir) if os.path.isdir(os.path.join(mc_saves_dir, s))]
            if saves:
                self.input_path_var.set(saves[0])
                self.world_name_var.set(os.path.basename(saves[0]))

    def _on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "file":
            self.input_path_var.set("")
        else:
            self._auto_detect_defaults()

    def _on_out_target_change(self):
        target = self.out_target_var.get()
        if target == "game":
            self.output_path_var.set(self.mw_default_dir)
            self.txt_output.config(state="disabled")
            self.btn_browse_out.config(state="disabled")
        else:
            self.txt_output.config(state="normal")
            self.btn_browse_out.config(state="normal")
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            self.output_path_var.set(os.path.join(desktop, "Converted_MW_Maps"))

    def _browse_input(self):
        mode = self.mode_var.get()
        if mode == "world":
            selected = filedialog.askdirectory(title="Chon Thu Muc Map Minecraft (chua thu muc region)")
            if selected:
                self.input_path_var.set(selected)
                self.world_name_var.set(os.path.basename(selected))
        else:
            selected = filedialog.askopenfilename(
                title="Chon File .mca",
                filetypes=[("Minecraft Region File", "*.mca"), ("All files", "*.*")]
            )
            if selected:
                self.input_path_var.set(selected)

    def _browse_output(self):
        selected = filedialog.askdirectory(title="Chon Thu Muc Luu Ban Do Mini World")
        if selected:
            self.output_path_var.set(selected)

    def _log(self, text):
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)

    def _start_conversion(self):
        in_path = self.input_path_var.get().strip()
        out_path = self.output_path_var.get().strip()
        wname = self.world_name_var.get().strip() or "Converted_World"

        if not in_path or not os.path.exists(in_path):
            messagebox.showerror("Lỗi", "Vui lòng chọn đường dẫn bản đồ Minecraft hợp lệ!")
            return

        if not out_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục xuất Mini World hợp lệ!")
            return

        self.btn_convert.config(state=tk.DISABLED, text=" ĐANG CHUYỂN ĐỔI... ", bg="#888888")
        self.btn_open_folder.config(state=tk.DISABLED)
        self.txt_log.delete("1.0", tk.END)

        def run_thread():
            try:
                mode = self.mode_var.get()
                if mode == "file" or in_path.endswith(".mca"):
                    self._log(f"[*] Bat dau chuyen file don le: {in_path}")
                    out_r = os.path.join(out_path, os.path.splitext(os.path.basename(in_path))[0] + ".r")
                    success = convert_single_mca(in_path, out_r, progress_cb=self._log)
                    self.last_output_dir = out_path
                else:
                    self._log(f"[*] Bat dau chuyen doi thu muc Map: {in_path}")
                    res = convert_minecraft_world(in_path, out_path, world_name=wname, progress_cb=self._log)
                    self.last_output_dir = res if res else out_path

                self.root.after(0, self._on_conversion_done, True)
            except Exception as e:
                self._log(f"[!] LOI TRONG QUA TRINH CHUYEN DOI: {e}")
                self.root.after(0, self._on_conversion_done, False)

        threading.Thread(target=run_thread, daemon=True).start()

    def _on_conversion_done(self, success):
        self.btn_convert.config(state=tk.NORMAL, text=" BẮT ĐẦU CHUYỂN ĐỔI NGAY ", bg="#2ec27e")
        if success:
            self.btn_open_folder.config(state=tk.NORMAL)
            messagebox.showinfo("Hoàn Tất", "Bản đồ đã được chuyển đổi thành công sang Mini World!")

    def _open_output_folder(self):
        target = self.last_output_dir or self.output_path_var.get()
        if target and os.path.exists(target):
            os.startfile(target)

def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
