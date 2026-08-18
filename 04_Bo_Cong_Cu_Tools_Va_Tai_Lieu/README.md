# Mini World `.pkg` Extractor & Decoder (Rainbow Engine)

Bộ công cụ giải mã và trích xuất toàn diện định dạng archive `.pkg` độc quyền của game **Mini World: CREATA** (Rainbow Engine).

---

## 📦 Danh mục tệp tin trong bộ công cụ:

| Tên file | Loại | Mô tả |
| :--- | :---: | :--- |
| **`MiniWorld_PkgExtractor.exe`** | Ứng dụng | File `.exe` độc lập (Portable), chạy ngay trên mọi máy Windows mà **không cần cài Python**. |
| **`KEO_THA_FILE_PKG_VAO_DAY.bat`** | Batch script | File chạy nhanh 1-Click hoặc hỗ trợ kéo thả file `.pkg` đè lên. |
| **`extract_all_pkg.py`** | Python script | Mã nguồn Python gốc với đầy đủ thuật toán LZ4 Block và Struct Parser. |
| **`HUONG_DAN_SU_DUNG.txt`** | Tài liệu | Hướng dẫn sử dụng nhanh bằng Tiếng Việt. |

---

## 🚀 Hướng dẫn sử dụng:

### Cách 1: Chạy tự động (Khuyên dùng)
* Nhấp đúp (double-click) vào file **`MiniWorld_PkgExtractor.exe`** (hoặc `KEO_THA_FILE_PKG_VAO_DAY.bat`).
* Tool sẽ **tự động quét** toàn bộ thư mục dữ liệu Mini World (`%APPDATA%`, `pkg_assets`, v.v.) trên máy người dùng và tiến hành giải mã toàn bộ.

### Cách 2: Kéo thả (Drag & Drop)
* Nắm kéo bất kỳ file `.pkg` hoặc thư mục chứa file `.pkg` nào rồi **thả đè lên** file `MiniWorld_PkgExtractor.exe`.
* Dữ liệu giải nén sẽ được tự động tạo ngay bên cạnh file gốc.

### Cách 3: Chạy dòng lệnh (CLI)
```bash
# Giải mã 1 file cụ thể:
MiniWorld_PkgExtractor.exe "C:\Path\To\file.pkg"

# Giải mã toàn bộ thư mục và chỉ định thư mục xuất:
MiniWorld_PkgExtractor.exe "C:\Path\To\Folder" -o="C:\OutputFolder"
```

---

## 🛠️ Chi tiết kỹ thuật định dạng `.pkg` (Rainbow Engine):
* **Header (16 bytes)**: Gồm `v1` (4B), `v2` (4B), `data_size` (4B), `header_size` (4B).
* **Footer File Table**: Nằm tại vị trí `data_size` với dung lượng `header_size`, được nén khối bằng **LZ4 Block**.
* **File Entries**: Mỗi bản ghi chứa `Hash128` (16B), `Offset` (4B), `Size` (4B), `Flag` (4B), và `Hash2` (16B nếu `flag & 0x20 != 0`).
* **String Table**: Bảng chuỗi ánh xạ `entry_index` với toàn bộ đường dẫn phân cấp gốc.
* **Payload**: Các file nén LZ4 nếu `flag & 1 != 0` (4 byte đầu là kích thước sau giải nén, tiếp theo là LZ4 data stream).
