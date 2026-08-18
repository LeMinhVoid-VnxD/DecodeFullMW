# MINI WORLD: CREATA - TOÀN BỘ DỮ LIỆU ĐÃ GIẢI MÃ THEO 3 NGUỒN FOLDER

Toàn bộ dữ liệu của Mini World đã được phân chia thành **3 nguồn thư mục riêng biệt** rõ ràng:

---

## 📂 1. `01_Nguon_MiniWorld_Data410` (Thư mục Client Dữ Liệu Chính)
Chứa toàn bộ 6 gói PKG giải mã và các map thế giới của người chơi:
* **`01_Ngon_Ngu_Giao_Dien_game_language`**: Bản dịch giao diện đa ngôn ngữ (Tiếng Việt, Anh, v.v.).
* **`02_Lua_Scripts_va_Bang_CSV_script_res`**: Hơn 6.000 file kịch bản Lua gameplay + hơn 1.100 file `.csv` thông số vật phẩm (`itemdef.csv`), quái vật, kỹ năng.
* **`03_Textures_va_Audio_common_res`**: 36.550 file textures PNG, âm thanh SFX/BGM `.ogg`, hiệu ứng `.emo`.
* **`04_Giao_Dien_UI_game_res`**: 3.517 file giao diện đồ họa FairyGUI (`.fui`) và icon UI.
* **`05_Mo_Hinh_3D_remote_res`**: 21.528 file mô hình 3D Meshes, Animation Skeletons (`.skanim`), Prefabs.
* **`06_DirectX_Shaders_dx_res`**: 15.464 file Shader đồ họa DirectX.
* **`07_Du_Lieu_Ban_Do_Saves_w`**: Toàn bộ các map thế giới của người chơi (`data/w*/`) gồm các file Region `.r` (`m0/x0z0.r`) và `map.ini`.

---

## 📂 2. `02_Nguon_MiniWorld_Data999` (Thư mục Dữ Liệu & Cache 999)
* Chứa toàn bộ cây thư mục asset cache, CloudAssets và dữ liệu lưu trữ từ `miniworddata999`.

---

## 📂 3. `03_Nguon_MiniWorld_OverseasGame` (Thư mục Bộ Cài Đặt Game Gốc)
Chứa toàn bộ mã máy nhị phân, thư viện DLL và tài nguyên engine gốc:
* **`01_Phan_Tich_84_DLL_C++_APIs`**: Báo cáo giải mã toàn bộ hàm C++ Demangled và cấu trúc Class RTTI của các file DLL (`libEngine`, `libframework`, `libMiniBlock`, `libiworld`, `libSandBoxEngine`, v.v.).
* **`02_Vat_Lieu_material_res`**: 15.423 file định nghĩa vật liệu đồ họa D3D11.
* **`03_Khoi_Dong_Engine_engine_res`**: 6.920 file tài nguyên cốt lõi khi khởi động engine.
* **`04_Tai_Nguyen_first_res`**: 3.221 file tài nguyên màn hình loading đầu game.
* **`05_Plugin_Resources_va_Skins`**: Toàn bộ font chữ và skin plugin.
* **`06_MainData_Configs`**: Dữ liệu cấu hình hệ thống game.
* **`07_Locales_CEF_UI`**: Gói ngôn ngữ trình duyệt nhúng CEF.

---

## 📂 4. `04_Bo_Cong_Cu_Tools_Va_Tai_Lieu` (Công Cụ & Hướng Dẫn)
* **`MiniWorld_PkgExtractor.exe`**: Tool giải mã file `.pkg` 1-click độc lập.
* **`Tool_Chuyen_Map_Minecraft_Sang_MiniWorld`**: Công cụ chuyển đổi map Minecraft (`.mca`) sang Mini World (`.r`) kèm giao diện GUI.
* **`TAI_LIEU_TOAN_TAP_MINI_WORLD.md`**: Tài liệu kỹ thuật toàn tập về kiến trúc Rainbow Engine.

---
*Thời gian cập nhật: 2026-08-18 10:25:18*
