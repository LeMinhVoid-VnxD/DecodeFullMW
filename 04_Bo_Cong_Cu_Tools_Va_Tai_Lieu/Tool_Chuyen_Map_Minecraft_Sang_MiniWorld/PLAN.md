# Kế hoạch phát triển: Tool chuyển đổi Map Minecraft (.mca) sang Mini World (.r)

## Mục tiêu
Xây dựng bộ công cụ chuyển đổi toàn diện cho phép người dùng chuyển bất kỳ bản đồ Minecraft (định dạng Region `.mca` từ Minecraft 1.12 đến 1.20+) sang bản đồ Mini World: CREATA (định dạng Region `.r` trong thư mục `m0/`).

---

## Các thành phần chính

### 1. Module đọc và phân tích Minecraft MCA (`mc_region_parser.py`)
- Đọc bảng sector header (1024 chunks / file).
- Giải nén NBT Chunk Payload (Zlib / Deflate).
- Hỗ trợ cả 2 chuẩn:
  - **Modern NBT (1.13 - 1.20+)**: Palette + Packed BitStorage `BlockStates`.
  - **Legacy NBT (1.12-)**: Mảng byte `Blocks` + `Data`.
- Trích xuất tọa độ 3D `(X, Y, Z)` và loại block Minecraft.

### 2. Từ điển ánh xạ Block (Minecraft -> Mini World Block Mapping)
- Ánh xạ đầy đủ các loại khối phổ biến:
  - Địa hình: Grass Block -> Khối Đất Mọc Cỏ (100), Dirt -> Khối Đất (101), Stone -> Đá (103), Cobblestone -> Đá Cuội (104), Sand -> Cát (29), Gravel -> Sỏi (107), Bedrock -> Đá Nền (1).
  - Gỗ & Cây cối: Oak/Birch/Spruce Logs -> Gỗ Thông/Cherry/Bạch Dương (200-204), Planks -> Ván Gỗ (207-212), Leaves -> Lá Cây (218-222).
  - Quặng: Coal Ore -> Mỏ Than (300), Iron Ore -> Mỏ Sắt (301), Gold Ore -> Mỏ Vàng (302), Diamond Ore -> Mỏ Kim Cương (303), v.v.
  - Chất lỏng: Water -> Nước (3/4), Lava -> Dung Nham (5/6).
  - Kiến trúc & Kính: Glass -> Thủy Tinh (140), Bricks -> Gạch (108), Wool / Concrete -> Các khối màu sắc Mini World.

### 3. Module ghi Mini World Region & World Generator (`mw_region_writer.py`)
- Tạo các file Region `.r` chuẩn (`m0/x{X}z{Z}.r`).
- Xây dựng cấu trúc thư mục Map Mini World hoàn chỉnh:
  - `data/w{WorldID}/`
    - `m0/` (chứa các file `.r`)
    - `map.ini` (cấu hình tên map, chế độ chơi, phiên bản)
    - `sandbox/` & `data/`
- Tự động copy thẳng vào thư mục game Mini World nếu người dùng chọn để vào game chơi được ngay!

### 4. Giao diện người dùng & Đóng gói (`mc2mw_gui.py` & Standalone `.exe`)
- Giao diện đồ họa (GUI) dễ dùng: Nút chọn file/thư mục map Minecraft, chọn thư mục xuất, thanh tiến trình (Progress Bar), nút "Chuyển Đổi Ngay".
- Hỗ trợ kéo thả (Drag & Drop) file `.mca` vào file `.bat`.
- Đóng gói thành file `.exe` độc lập không cần cài Python.

---

## Vị trí lưu trữ
Thư mục: `C:\Users\Le Minh\OneDrive\Desktop\decodepkg\mc2mw_converter`
