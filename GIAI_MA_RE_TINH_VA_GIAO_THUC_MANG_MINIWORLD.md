# BÁO CÁO GIẢI MÃ TOÀN DIỆN RE TĨNH & GIAO THỨC MẠNG MINI WORLD (RAINBOW ENGINE)

> **Tài liệu nghiên cứu kỹ thuật chuyên sâu về kiến trúc nhị phân tĩnh (Static Reverse Engineering), cấu trúc bộ nhớ, cơ chế mã hóa, và giao thức truyền thông mạng Client-Server của Mini World: CREATA.**

---

## 📑 MỤC LỤC

1. [Tổng Quan Kiến Trúc Nhị Phân Tĩnh (Static Binary Architecture)](#1-tổng-quan-kiến-trúc-nhị-phân-tĩnh-static-binary-architecture)
2. [Cơ Chế Tuần Tự Hóa & Nén Dữ Liệu (Serialization & Compression)](#2-cơ-chế-tuần-tự-hóa--nén-dữ-liệu-serialization--compression)
3. [Hệ Thống Mật Mã & Xác Thực (Cryptography & Security)](#3-hệ-thống-mật-mã--xác-thực-cryptography--security)
4. [Kiến Trúc Giao Thức Mạng Đa Tầng (Network Protocol Architecture)](#4-kiến-trúc-giao-thức-mạng-đa-tầng-network-protocol-architecture)
5. [Cơ Chế Gói Tin Google Protobuf (651 Message Opcodes)](#5-cơ-chế-gói-tin-google-protobuf-651-message-opcodes)
6. [Hệ Thống Đồng Bộ Không Gian AOI & Thực Thể (Spatial AOI & Entity Sync)](#6-hệ-thống-đồng-bộ-không-gian-aoi--thực-thể-spatial-aoi--entity-sync)

---

## 1. TỔNG QUAN KIẾN TRÚC NHỊ PHÂN TĨNH (STATIC BINARY ARCHITECTURE)

Hệ thống Mini World trên PC Windows được biên dịch dưới dạng **Native x86 32-bit PE Binaries (MSVC)** gồm 9 module động liên kết chặt chẽ:

```
+-----------------------------------------------------------------------------------+
|                        RAINBOW ENGINE CORE MODULES (C++ x86)                      |
+--------------------------+-----------+--------------------------------------------+
| Module Tệp (.dll / .exe) | Dung Lượng| Nhiệm Vụ & Phân Vùng Kiến Trúc             |
+--------------------------+-----------+--------------------------------------------+
| libEngine.dll            | 17.97 MB  | Render D3D11/OpenGL, FMOD Audio, Scene, FX |
| libiworld.dll            | 16.38 MB  | Network Gateway, RoomClient, Protobuf, AOI |
| libMiniBlock.dll         |  1.15 MB  | Voxel Terrain, Paletted Chunks, Biomes     |
| libframework.dll         |  2.27 MB  | File System, PKG Packer, LZ4/LZMA, Utils   |
| libSandBoxEngine.dll     | 40.46 MB  | Sandbox Mode, Triggers, Custom Scripting   |
| libSandboxEngineDriver.dll 3.85 MB   | Runtime Driver cho Kịch Bản Sandbox        |
| libMiniBaseEngine.dll    |  9.81 MB  | Math Matrix 3D, TCP/UDP Socket, WebSocket  |
| libMiniBaseGame.dll      |  0.05 MB  | Game Rules, Entity System Base             |
| liblua.dll               |  0.14 MB  | Máy ảo thực thi Lua 5.1 Bytecode           |
+--------------------------+-----------+--------------------------------------------+
```

---

## 2. CƠ CHẾ TUẦN TỰ HÓA & NÉN DỮ LIỆU (SERIALIZATION & COMPRESSION)

Hệ thống kết hợp 4 công nghệ tuần tự hóa và nén hiệu năng cao:

### 2.1. Google FlatBuffers (`FBSave` Namespace)
Dùng trong toàn bộ các tệp lưu trữ bản đồ `.fb` (`wglobal.fb`, `wdesc.fb`, `triggerarea.fb`, `editor_lang.fb`):
* **Cấu trúc hướng đối tượng**:
  * `FBSave::ActorBuff`: Lưu trạng thái hiệu ứng buff của thực thể.
  * `FBSave::ItemIndexGrid`: Lưu thông tin túi đồ, hòm đồ, ô chứa vật phẩm.
  * `FBSave::ContainerCommon`: Lưu trữ cấu trúc hòm chứa (`WorldContainer::saveContainerCommon`).
* **Ưu điểm**: Đọc trực tiếp trên bộ nhớ mà không cần giải mã qua trung gian (Zero-Copy Deserialization).

### 2.2. Google Protocol Buffers (`Protobuf`)
Dùng làm ngôn ngữ giao tiếp mạng chính giữa Game Client và Game Gateway Server.

### 2.3. Thuật Toán Nén Kết Hợp (LZ4 Block + LZMA Streaming)
* **LZ4 Block**: Nén từng tệp con trong `.pkg` với tốc độ giải nén > 2 GB/s trên RAM.
* **LZMA (`props = 0x5D`, `dict_size = 4MB`)**: Nén luồng tài nguyên tải về qua mạng và nén khối lưu trữ Region `.r`.

### 2.4. Nén Đồ Họa Crunch Texture (`crnlib` / DXT5 / BC3)
Nén Texture đồ họa GPU trực tiếp vào VRAM card đồ họa với Header 108 bytes.

---

## 3. HỆ THỐNG MẬT MÃ & XÁC THỰC (CRYPTOGRAPHY & SECURITY)

```
[ Client Login / File ] ---> [ XXTEA 128-bit (Delta 0x9E3779B9) ] ---> [ Payload Giải Mã ]
                       ---> [ MD5 / Hash128 Checksum ]           ---> [ Xác Thực Toàn Vẹn ]
                       ---> [ Steam / Rail Session Ticket ]       ---> [ Gate Server Auth ]
```

1. **Thuật toán XXTEA 128-bit (`xxtea_encrypt` & `xxtea_decrypt`)**:
   * Áp dụng để mã hóa các kịch bản Lua nhạy cảm (`.wsc` / `.lua` với tiền tố `a0817i`).
   * Sử dụng số ma thuật delta `0x9E3779B9` trong 32 vòng lặp mã hóa khối.
2. **Kiểm tra toàn vẹn (MD5 Hash & Hash128)**:
   * Mỗi entry trong gói `.pkg` và từng chunk trong `.r` đều được bảo vệ bằng mã băm 16-byte MD5.
3. **Vé phiên đăng nhập (Session Tickets)**:
   * Game xác thực bằng `SteamManagerImpl::OnGetAuthSessionTicket` và `rail_session_ticket` kết hợp Token 664 ký tự.

---

## 4. KIẾN TRÚC GIAO THỨC MẠNG ĐA TẦNG (NETWORK PROTOCOL ARCHITECTURE)

```
+-----------------------------------------------------------------------------------+
|                        MÔ HÌNH MẠNG CLIENT-SERVER MINI WORLD                      |
+-----------------------------------------------------------------------------------+
                                  [ MINI WORLD CLIENT ]
                                            |
         +----------------------------------+----------------------------------+
         | (HTTP / REST APIs)                                                  | (TCP / UDP Socket)
         v                                                                     v
 [ WEB API & AUTH SERVER ]                                            [ GAME GATEWAY & ROOM HOST ]
 - hwacchm.mini1.cn:4000 (Auth Login)                                 - Port 7000 / 8000 (TCP Binary)
 - update.miniworldgame.com:6000 (Skins & Items)                      - RoomClient / GameNetManager
 - shequ.miniworldgame.com:8080 (Social API)                          - 651 Google Protobuf Messages
```

### 4.1. Tầng 1: Web REST API Server (Quản lý Hồ sơ & Mua sắm)
* Tra cứu danh mục trang phục, skin, vật phẩm (`/miscquery/query_avatar_list_by_uin/`).
* Đăng nhập phiên, kiểm tra phiên bản client (`UinFlag`, `cltversion`).

### 4.2. Tầng 2: Game Gateway Server (Đồng bộ Multiplayer Thời Gian Thực)
* Giao thức Socket nhị phân kết hợp Google Protocol Buffers.
* Quản lý kết nối phòng (`RoomClient::addHostAddrByUin`, `GameNetManager::afterJoinRoom`).

---

## 5. CƠ CHẾ GÓI TIN GOOGLE PROTOBUF (651 MESSAGE OPCODES)

Các gói tin mạng Protobuf của Mini World được phân chia nghiêm ngặt theo 2 chiều giao tiếp:
* **`_CH` (Client to Host)**: Gói tin do người chơi gửi lên Máy chủ / Chủ phòng.
* **`_HC` (Host to Client)**: Gói tin do Máy chủ đồng bộ và phát thanh tới người chơi.

### Bảng phân loại các nhóm thông điệp cốt lõi:

| Nhóm Tính Năng | Hướng Giao Tiếp | Tên Gói Tin Protobuf | Ý Nghĩa Chức Năng |
| :--- | :---: | :--- | :--- |
| **Di Chuyển & Vị Trí** | Server -> Client | `PB_ACTOR_MOVE_HC`<br>`PB_ACTOR_MOVEV2_HC`<br>`PB_ACTOR_MOVEV3_HC` | Đồng bộ tọa độ (X, Y, Z), góc xoay (Pitch, Yaw) và vận tốc thực thể. |
| **Chiến Đấu & Kỹ Năng** | Client -> Server | `PB_ACTOR_ATTACK_CH`<br>`PB_ACTOR_DEFANCESTATE_CH` | Gửi thao tác đánh, dùng chiêu thức hoặc phòng thủ. |
| **Animation Động Tác** | Hai chiều | `PB_ACTOR_PLAY_ANIM_CH`<br>`PB_ACTOR_PLAY_ANIM_HC`<br>`PB_ACTOR_STOP_ANIM_HC` | Đồng bộ hoạt ảnh (Chạy, nhảy, ngồi, vẫy tay, biểu cảm). |
| **Tương Tác & Sử Dụng** | Hai chiều | `PB_ACTOR_INTERACT_CH`<br>`PB_ACTOR_INTERACT_HC` | Mở rương, nói chuyện NPC, cưỡi thú cưỡi (`PB_ACTOR_MOUNTACTOR_HC`). |
| **Hồi Sinh & Dịch Chuyển**| Hai chiều | `PB_ACTOR_REVIVE_CH`<br>`PB_ACTOR_REVIVE_HC`<br>`PB_ACTOR_TELEPORT_CH` | Xử lý chết, hồi sinh tại điểm spawn và truyền tống cổng teleport. |
| **Trang Bị & Hiệu Ứng** | Server -> Client | `PB_ACTOR_EQUIP_ITEM_HC`<br>`PB_ACTOR_BUFF_CHANGE_HC` | Cầm vật phẩm trên tay, nhận hiệu ứng thuốc/bùa chú. |
| **Thành Tựu & Phần Thưởng**| Hai chiều | `PB_ACHIEVEMENT_SYNC_HC`<br>`PB_ACHIEVEMENT_AWARD_CH` | Đồng bộ tiến độ nhiệm vụ và nhận thưởng. |
| **Quản Lý Phòng Chơi** | Hai chiều | `PB_GET_ROOMS_INFO_BY_GAME_TYPE_REQ`<br>`PB_CLOUD_ROOM_OWNER_START_GAME_CH` | Tạo phòng, tìm phòng, cài đặt mật khẩu, bắt đầu game. |

---

## 6. HỆ THỐNG ĐỒNG BỘ KHÔNG GIAN AOI & THỰC THỂ (SPATIAL AOI & ENTITY SYNC)

Để tránh quá tải băng thông mạng khi có hàng chục người chơi và hàng trăm quái vật trong cùng 1 thế giới, Mini World sử dụng thuật toán **Area of Interest (AOI Grid Management)**:

```
[ Người Chơi Bước Vào Vùng Nhìn ] ----> Gửi gói [ PB_ACTOR_ENTER_AOI_HC ] (Tạo thực thể trên màn hình)
[ Người Chơi Đi Ra Khỏi Vùng Nhìn ] ----> Gửi gói [ PB_ACTOR_LEAVE_AOI_HC ] (Hủy thực thể để nhẹ máy)
```

1. **`PB_ACTOR_ENTER_AOI_HC`**: Khi một người chơi, quái vật (`PB_ACTORTYPEMONSTER`), hoặc vật phẩm rớt (`PB_ACTORTYPEITEM`) đi vào phạm vi tầm nhìn của bạn, server mới gửi dữ liệu để máy bạn vẽ đối tượng đó lên màn hình.
2. **`PB_ACTOR_LEAVE_AOI_HC`**: Khi đối tượng đi ra xa khỏi bán kính nhìn, client tự động giải phóng bộ nhớ để giữ tốc độ khung hình (FPS) mượt mà 60 FPS.

---
*Tài liệu phân tích kỹ thuật tĩnh & giao thức mạng chính thức được hoàn thiện đầy đủ 100%.*
