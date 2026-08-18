# TÀI LIỆU TOÀN TẬP KỸ THUẬT & GIẢI MÃ MINI WORLD (RAINBOW ENGINE)

> **Tài liệu nghiên cứu kiến trúc hệ thống, định dạng tệp tin, cơ chế nén, mã hóa và công cụ chuyển đổi dữ liệu của game Mini World: CREATA.**

---

## 📑 MỤC LỤC

1. [Tổng Quan Kiến Trúc Engine (Rainbow Engine)](#1-tổng-quan-kiến-trúc-engine-rainbow-engine)
2. [Chi Tiết Cấu Trúc Định Dạng Tệp Tin Game](#2-chi-tiết-cấu-trúc-định-dạng-tệp-tin-game)
   - [2.1. Gói Dữ Liệu Lưu Trữ (.pkg)](#21-gói-dữ-liệu-lưu-trữ-pkg)
   - [2.2. Bản Đồ Thế Giới & Region (.r)](#22-bản-đồ-thế-giới--region-r)
   - [2.3. Kịch Bản Script Lua (.lua & .wsc)](#23-kịch-bản-script-lua-lua--wsc)
   - [2.4. Hình Ảnh & Texture Đồ Họa (.png / .tex)](#24-hình-ảnh--texture-đồ-họa-png--tex)
   - [2.5. Bảng Dữ Liệu & Cấu Hình (.csv, .xml, .json)](#25-bảng-dữ-liệu--cấu-hình-csv-xml-json)
   - [2.6. Mô Hình 3D & Khung Xương (.mesh, .skanim, .omod)](#26-mô-hình-3d--khung-xương-mesh-skanim-omod)
3. [Phân Tích Các Thư Viện C++ Cốt Lõi (DLL Binaries)](#3-phân-tích-các-thư-viện-c-cốt-lõi-dll-binaries)
4. [Cơ Chế Chuyển Đổi Map Minecraft (.mca) Sang Mini World (.r)](#4-cơ-chế-chuyển-đổi-map-minecraft-mca-sang-mini-world-r)
5. [Cây Thư Mục Toàn Bộ Dữ Liệu Đã Giải Mã (D:\DecodeFullMW)](#5-cây-thư-mục-toàn-bộ-dữ-liệu-đã-giải-mã-ddecodefullmw)
6. [Hướng Dẫn Sử Dụng Bộ Công Cụ (Tools & Decoders)](#6-hướng-dẫn-sử-dụng-bộ-công-cụ-tools--decoders)

---

## 1. TỔNG QUAN KIẾN TRÚC ENGINE (RAINBOW ENGINE)

Mini World được phát triển trên nền tảng **Rainbow Engine** (Engine độc quyền của Miniwan Technology):
* **Kiến trúc nhị phân**: 32-bit (x86 PE) tối ưu hóa cho đa nền tảng (PC Windows, Android, iOS).
* **Đồ họa Render**: Hỗ trợ đồng thời DirectX 11 (`D3D11`), OpenGL ES 2.0/3.0 và Vulkan.
* **Hệ thống nén dữ liệu**: Sử dụng kết hợp **LZ4 Block** (giải nén tốc độ cao trên RAM) và **LZMA** (nén stream dung lượng lớn khi tải gói tài nguyên).
* **Hệ thống kịch bản**: Tích hợp máy ảo **Lua 5.1** kết hợp hệ thống Trigger Event C++.

---

## 2. CHI TIẾT CẤU TRÚC ĐỊNH DẠNG TỆP TIN GAME

```
+-------------------------------------------------------------------------------+
|                       HỆ THỐNG ĐỊNH DẠNG TỆP TIN MINI WORLD                   |
+-------------------+-----------------------------------------------------------+
| Đuôi Tệp (.ext)   | Bản Chất & Thuật Toán Xử Lý                              |
+-------------------+-----------------------------------------------------------+
| .pkg              | Archive độc quyền Rainbow Engine (Nén LZ4 Block / LZMA)   |
| .r                | Bản đồ Region (32x32 Chunks, 512x512 Blocks, BitStorage) |
| .lua              | Bytecode Lua 5.1 đã biên dịch (Format 0, Little-Endian)   |
| .wsc / .lua mã hóa| Mã hóa XXTEA + Base64 (Tiền tố 'a0817i')                  |
| .png              | Texture GPU nén Crunch / DXT5 / BC3 (Header Texture2D)    |
| .ogg              | Âm thanh chuẩn Ogg Vorbis (SFX, BGM)                      |
| .csv / .xml       | Bảng dữ liệu thuần UTF-8 (itemdef.csv, monster.csv, v.v.) |
+-------------------+-----------------------------------------------------------+
```

### 2.1. Gói Dữ Liệu Lưu Trữ (`.pkg`)
Định dạng đóng gói tài nguyên chính của game:
* **Header (16 bytes)**:
  * `v1` (4 bytes uint32): Phiên bản cấu trúc gói.
  * `v2` (4 bytes uint32): Cờ mở rộng.
  * `Data Size` (4 bytes uint32): Kích thước toàn bộ khối dữ liệu payloads.
  * `Header Size` (4 bytes uint32): Kích thước của bảng mục lục Footer Table.
* **Footer File Index Table** (Nằm tại offset `Data Size`):
  * Được nén khối bằng **LZ4 Block** (4 byte đầu là kích thước sau giải nén).
  * Danh sách Entry: Mỗi file gồm `Hash128 (16B)`, `Offset (4B)`, `Size (4B)`, `Flag (4B)`, và `Hash2 (16B nếu flag & 0x20)`.
  * Bảng String Table: Chuỗi UTF-8 đường dẫn phân cấp của từng file.
* **Payloads**: Nếu `(flag & 1) != 0`, file con được nén LZ4 độc lập với 4-byte uncompressed size prefix.

---

### 2.2. Bản Đồ Thế Giới & Region (`.r`)
Nằm trong thư mục `data/w{WorldID}/m0/x{X}z{Z}.r`:
* **Kích thước vùng**: Mỗi file `.r` chứa chính xác **32 × 32 = 1.024 Chunks** (tương đương diện tích 512 × 512 blocks).
* **Header (8.192 bytes = 2 Sectors)**:
  * `Sector 0 (0..4095)`: Bảng Offset của 1.024 Chunks (`uint32: (sector_span << 24) | sector_offset`).
  * `Sector 1 (4096..8191)`: Bảng Unix Timestamp của 1.024 Chunks (`uint32`).
* **Sectors (Từ offset 8.192 trở đi)**:
  * Mỗi khối Chunk được căn chỉnh theo block 4.096 bytes.
  * Cấu trúc Chunk: `uint32 PayloadLength` + Khối dữ liệu Native Chunk (Lưu trữ bằng `PalettedTable` và `CompressBitStorage` tương tự Minecraft Palette).

---

### 2.3. Kịch Bản Script Lua (`.lua` & `.wsc`)
* **Bytecode Lua 5.1**:
  * Chữ ký Magic: `1B 4C 75 61` (`\x1bLua`).
  * Version: `0x51` (Lua 5.1.4 / 5.1.5 standard).
  * Chứa đầy đủ thông tin Debug Info (tên hàm, dòng lệnh, đường dẫn file nguồn `@F:/RainbowMiniw/...`).
  * Có thể dịch ngược bằng `unluac` hoặc `luadec`.
* **Script mã hóa XXTEA (`.wsc` / `.lua`)**:
  * Dữ liệu bắt đầu bằng tiền tố `a0817i` kèm chuỗi Base64.
  * Giải mã bằng thuật toán XXTEA 128-bit với Delta `0x9E3779B9`.

---

### 2.4. Hình Ảnh & Texture Đồ Họa (`.png` / `.tex`)
* **Bản chất**: Không phải ảnh PNG nén chuẩn, mà là **`Rainbow::Texture2D`** tối ưu nạp trực tiếp vào GPU VRAM (Direct3D 11).
* **Cấu trúc tệp**:
  * **Header (108 bytes)**: Chứa thông tin `Width` (offset 20), `Height` (offset 24), `Data Size` (offset 28), định dạng màu `DXGI_FORMAT` (offset 32), số tầng Mipmaps.
  * **Payload**: Dữ liệu nén đồ họa **Crunch (`crnlib` / DXT5 / BC3)**.
* **Cách mở xem**: Sử dụng phần mềm phân tích đồ họa **RenderDoc**, **Noesis** hoặc **TextureViewer**.

---

### 2.5. Bảng Dữ Liệu & Cấu Hình (`.csv`, `.xml`, `.json`)
* **`itemdef.csv`**: Bảng từ điển toàn bộ vật phẩm, block, ID và tên gọi tiếng Việt/tiếng Anh.
* **`monster.csv`**, **`skill.csv`**, **`enchant.csv`**: Bảng thông số quái vật, thuộc tính kỹ năng, bùa chú.
* Toàn bộ là văn bản thuần UTF-8, mở và chỉnh sửa trực tiếp bằng **Excel, Notepad, VS Code**.

---

## 3. PHÂN TÍCH CÁC THƯ VIỆN C++ CỐT LÕI (DLL BINARIES)

| Thư viện DLL | Dung lượng | Số Hàm C++ | Số Lớp RTTI | Chức Năng Chính Trong Game |
| :--- | :---: | :---: | :---: | :--- |
| **`libEngine.dll`** | 17.97 MB | 8.192 | 78 | Đồ họa DirectX, âm thanh FMOD, vật lý Bullet/PhysX, Scene Graph. |
| **`libframework.dll`** | 2.27 MB | 3.239 | 6 | Quản lý gói `.pkg`, giải nén LZ4/LZMA, hệ thống File System. |
| **`libMiniBlock.dll`** | 1.15 MB | 2.329 | 125 | Xử lý khối Voxel, ChunkSection, BitStorage, Palette, Biomes. |
| **`libiworld.dll`** | 16.38 MB | 3.860 | 1.157 | Quản lý bản đồ thế giới, Region `.r`, phòng chơi mạng, đồng bộ Actor. |
| **`libSandBoxEngine.dll`** | 40.46 MB | 8.192 | 4.247 | Cơ chế tạo map Sandbox, hệ thống Triggers, logic Custom Game. |
| **`libSandboxEngineDriver.dll`**| 3.85 MB | 4.415 | 145 | Trình điều khiển kịch bản Sandbox. |
| **`libMiniBaseEngine.dll`** | 9.81 MB | 8.192 | 263 | Thuật toán toán học ma trận 3D, mạng Socket TCP/UDP. |
| **`liblua.dll`** | 0.14 MB | 126 | 0 | Máy ảo thực thi mã kịch bản Lua 5.1. |

---

## 4. CƠ CHẾ CHUYỂN ĐỔI MAP MINECRAFT (.MCA) SANG MINI WORLD (.R)

```
[ Minecraft .mca ]                 [ Module Chuyển Đổi ]                 [ Mini World .r ]
+-------------------+             +-----------------------+             +-------------------+
| 32x32 Chunks      |             | 1. Đọc NBT Stream     |             | 32x32 Chunks      |
| 16x16x16 Sections | ----------> | 2. Ánh Xạ Block ID    | ----------> | Tọa độ (rx, rz)   |
| Palette / BitPack |             | 3. Chuẩn hóa độ cao Y |             | Cấu trúc m0/x*z*.r|
| Y: -64 .. 320     |             | 4. Ghi Native Sector  |             | Y: 0 .. 256       |
+-------------------+             +-----------------------+             +-------------------+
```

### Bảng đối soát Block Mapping:
* **Đất / Cỏ**: `minecraft:grass_block` -> `Khối Đất Mọc Cỏ (100)`, `minecraft:dirt` -> `Khối Đất (101)`.
* **Đá / Cuội**: `minecraft:stone` -> `Đá (103)`, `minecraft:cobblestone` -> `Đá Cuội (104)`.
* **Gỗ & Ván**: `minecraft:oak_log` -> `Gỗ Thông (201)`, `minecraft:oak_planks` -> `Ván Gỗ (207)`.
* **Quặng**: `minecraft:diamond_ore` -> `Mỏ Kim Cương (303)`, `minecraft:iron_ore` -> `Mỏ Sắt (301)`.
* **Chất lỏng**: `minecraft:water` -> `Nước (4)`, `minecraft:lava` -> `Dung Nham (6)`.

---

## 5. CÂY THƯ MỤC TOÀN BỘ DỮ LIỆU ĐÃ GIẢI MÃ (`D:\DecodeFullMW`)

```text
D:\DecodeFullMW\
├── 📁 01_Ma_Nguon_API_Ham_C++_DLL/              -> Báo cáo hàm & Class C++ của 9 DLLs
├── 📁 02_Kich_Ban_Lua_va_Cau_Hinh_CSV/
│   ├── 📁 01_Ngon_Ngu_Giao_Dien_Tieng_Viet/     -> Dữ liệu bản dịch ngôn ngữ game
│   └── 📁 02_Code_Lua_Scripts_va_Bang_CSV/      -> 6.900+ Lua scripts & 1.100+ CSVs
├── 📁 03_Tai_Nguyen_Do_Hoa_Am_Thanh_3D/
│   ├── 📁 01_Hinh_Anh_Textures_va_Am_Thanh_OGG/ -> Textures PNG & Âm thanh OGG
│   ├── 📁 02_Giao_Dien_UI_FairyGUI_Icon/        -> Giao diện đồ họa FairyGUI (.fui)
│   ├── 📁 03_Mo_Hinh_3D_Meshes_va_Khung_Xuong/  -> 3D Meshes (.mesh) & Skeletons (.skanim)
│   ├── 📁 04_DirectX_Shaders/                   -> Shaders đồ họa DirectX
│   └── 📁 05_Vat_Lieu_Do_Hoa_D3D11/             -> Định nghĩa vật liệu D3D11
├── 📁 04_Du_Lieu_Ban_Do_Va_Save_Game/
│   ├── 📁 01_Cac_The_Gioi_Map_Saves_w/          -> Các bản đồ thế giới (m0/*.r, map.ini)
│   ├── 📁 02_Model_Skin_va_UI_Tuy_Chinh/        -> Mô hình & Skin tự tạo
│   └── 📁 03_Mods_va_UGC_Plugins/               -> Plugins mod & UGC assets
└── 📁 05_Bo_Cong_Cu_Va_Tool_Giai_Ma/
    ├── 📁 Tool_Chuyen_Map_Minecraft_Sang_MiniWorld/
    │   ├── 📄 MC_to_MiniWorld_Converter.exe     -> Tool GUI chuyển map 1-click
    │   └── 📄 KEO_THA_MAP_MC_VAO_DAY.bat        -> Kéo thả file .mca để chuyển đổi
    ├── 📄 MiniWorld_PkgExtractor.exe            -> Tool giải nén file .pkg độc lập
    └── 📄 KEO_THA_FILE_PKG_VAO_DAY.bat          -> Kéo thả file .pkg để giải nén
```

---

## 6. HƯỚNG DẪN SỬ DỤNG BỘ CÔNG CỤ (TOOLS & DECODERS)

### 1. Giải mã file `.pkg` bất kỳ:
* **Cách 1**: Kéo file `.pkg` thả đè lên file `MiniWorld_PkgExtractor.exe` hoặc `KEO_THA_FILE_PKG_VAO_DAY.bat`.
* **Cách 2**: Nhấp đúp vào file `.exe` để tool tự động quét và giải nén toàn bộ tài nguyên game.

### 2. Chuyển đổi bản đồ Minecraft sang Mini World:
1. Mở file **`MC_to_MiniWorld_Converter.exe`** trong thư mục `05_Bo_Cong_Cu_Va_Tool_Giai_Ma\Tool_Chuyen_Map_Minecraft_Sang_MiniWorld`.
2. Chọn thư mục lưu Map Minecraft (`.minecraft/saves/TênMap`) hoặc file `.mca`.
3. Chọn xuất trực tiếp vào Mini World (`%APPDATA%/miniworddata410/data/`).
4. Nhấn **"BẮT ĐẦU CHUYỂN ĐỔI NGAY"** -> Mở game Mini World lên và vào chơi map vừa chuyển đổi!

---
*Tài liệu được tổng hợp tự động hoàn chỉnh cho hệ thống Mini World: CREATA.*
