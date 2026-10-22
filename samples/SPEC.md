# SPEC — Bảng mẫu pixel 8-bit vs 16-bit

Mục đích: cùng 2 cảnh vẽ bằng code (Python PIL) ở 2 phong cách pixel để
chọn 1 phong cách cố định cho tool video vẽ bằng code.

**Phạm vi dự án:** đây là tool RIÊNG cho kênh mới — KHÔNG tích hợp vào
tool videos cũ, không dùng chung code với tool cũ.

## Kỹ thuật chung

- Vẽ toàn bộ trên lưới pixel THẤP, rồi phóng lên 960×540 bằng
  `Image.NEAREST` → từng ô pixel vuông, sắc nét, không mờ.
- Cả 2 bản của 1 cảnh dùng CHUNG bố cục (tọa độ chuẩn hóa 0..1, cùng vị
  trí sao) — chỉ khác độ mịn lưới và độ giàu màu/bóng, để so sánh công bằng.
- Không AI sinh ảnh, không icon emoji. Nhân vật (cảnh B) chỉ là 1 phần tử
  trong cảnh, không phải mascot cố định.

## Khác nhau 8-bit vs 16-bit

| Tiêu chí | 8-bit | 16-bit |
|---|---|---|
| Lưới vẽ | 160×90 (phóng ×6) | 320×180 (phóng ×3) |
| Cỡ 1 pixel khi xuất | 6×6 px | 3×3 px |
| Số màu | Ít, kiểu NES (~12–23 màu/cảnh tùy cảnh) | Nhiều hơn (~18–32 màu/cảnh) |
| Đổ bóng | Không — màu phẳng hoàn toàn | 2–3 tông cho từng vật (áo, bàn, nhà, cầu...) |
| Chuyển màu nền | Nền 1 màu phẳng + dải đất phẳng | Trời chia 3 dải tông + **dithering** (chấm xen kẽ kiểu bàn cờ ở rìa chuyển) tạo cảm giác chuyển màu kiểu game SNES |
| Cảm giác | Thô, gắt, hài/game đời đầu | Mịn hơn, "xịn" hơn, vẫn rõ chất pixel |
| Chi tiết nhỏ | Cửa sổ 2×2 px, mặt nhân vật tối giản | Cửa sổ 3×3 px, vẽ được quầng sáng đèn, bóng cằm |

## 2 cảnh mẫu

- **Cảnh A — Quả cầu nuốt cảnh:** quả cầu đen lớn viền tím bên trái, mũi
  tên cong cam phía trên (gợi ý "đang lớn dần"), 2 quả cầu nhỏ + cụm nhà
  cửa sổ vàng bên phải, nền sao tím than.
- **Cảnh B — Người ngồi máy tính:** nhân vật ngồi bàn có laptop + đèn
  bàn cam, bong bóng suy nghĩ chứa quả cầu nhỏ, cửa sổ có trăng khuyết
  và sao bên phải.

## File

- `build_pixel_samples.py` — code vẽ toàn bộ (chạy: `python3 build_pixel_samples.py`)
- `scene-a-8bit.png`, `scene-a-16bit.png`, `scene-b-8bit.png`, `scene-b-16bit.png` — 4 panel 960×540
- `board.png` — bảng tổng 2000×1388 để chọn phong cách
