# SPEC — Tool video vẽ bằng code "PIXEL STUDIO" (phong cách PIXEL 16-BIT)

> Tài liệu mô tả bằng lời để Minh cầm đi dùng với bất kỳ AI nào khác.
> Trạng thái: MOCKUP — chưa build tool thật. Chờ Minh duyệt mockup này mới build.
> **Dự án RIÊNG cho kênh mới — tách biệt hẳn tool videos hiện tại, không
> tích hợp, không dùng chung code với tool cũ.**

## 1. Tool này là gì

Tool làm video giải thích vẽ hoàn toàn bằng code, phong cách **PIXEL 16-BIT**
đã khóa cứng (Minh chốt 22/10/2026 sau khi xem bảng mẫu 8-bit vs 16-bit),
dành cho người KHÔNG biết code.

Luồng sử dụng:

1. Dán kịch bản vào ô text.
2. Tool tự cắt kịch bản thành từng câu.
3. Mỗi câu, người dùng chọn 1 MẪU CẢNH trong thư viện vẽ sẵn bằng code
   + 1 hiệu ứng (hiện dần, phóng to...).
4. Giọng đọc cố định của kênh: Kokoro `am_adam` (qua sherpa-onnx/VoiceStudio).
5. Chọn định dạng (ngang 16:9 cho Long / dọc 9:16 cho Shorts), nhạc nền có/không.
6. Bấm RENDER → tool tự khớp thời lượng từng cảnh theo độ dài giọng đọc,
   gắn phụ đề, xuất video.

KHÔNG có nhân vật chính cố định / mascot khóa cứng. Nhân vật nếu xuất hiện
chỉ là một phần tử bên trong cảnh (ví dụ mẫu 08), thay đổi theo từng câu.

## 2. Chuẩn phong cách PIXEL 16-BIT (ĐÃ KHÓA — không đổi giữa các video)

- **Lưới vẽ: 320×180.** Mọi cảnh đều vẽ trên lưới này rồi phóng lên
  960×540 (hoặc 1920×1080 khi render thật) bằng `Image.NEAREST` → mỗi ô
  pixel thành khối vuông 3×3 sắc nét, tuyệt đối không làm mờ/khử răng cưa.
- **Bảng màu cố định** (khai báo 1 chỗ duy nhất trong code — biến `PAL`):
  nền trời tím than 3 tông (26,21,58) / (20,16,46) / (17,14,41), đất
  (13,11,34), quả cầu đen (6,6,14) viền tím (88,76,168), cam (246,174,32),
  cyan (46,224,255), xanh lá (52,245,165), hồng (255,93,115),
  đỏ (255,77,94), tím (124,58,237)... Thêm màu mới phải thêm vào bảng này,
  không rải rác trong từng cảnh.
- **Đổ bóng 2–3 tông** cho từng vật: mỗi màu chính có tông sáng (mặt trên)
  và tông tối (mặt phải/dưới) đi kèm — ví dụ khối hộp luôn vẽ 3 mặt:
  trên sáng, trước giữa, phải tối.
- **Dithering** (chấm xen kẽ kiểu bàn cờ) ở rìa chuyển giữa các dải màu
  nền trời và rìa mặt đất — dấu hiệu nhận biết chất SNES/16-bit.
- **Chữ trong video: font pixel VT323** (có tiếng Việt) cho phụ đề/chữ
  trong cảnh, **PressStart2P** cho tiêu đề ngắn tiếng Anh/số (font này
  KHÔNG có dấu tiếng Việt — đã kiểm chứng). Cả 2 font ở `~/workspace/fonts/`.
- **Nền chung 1 thế giới:** trời sao tím than + dải đất tối ở chân cảnh
  cho mọi mẫu — video nào cũng nhận ra cùng 1 "vũ trụ pixel".

## 3. Thư viện 8 mẫu cảnh (đợt 1)

Mỗi mẫu = 1 hàm vẽ bằng code (Python/PIL) trên lưới 320×180, có thông số
chuyển động riêng khi render thật. Ảnh tĩnh đính kèm là khoảnh khắc đại
diện của mẫu.

| # | Mẫu cảnh | Dùng khi câu thoại nói về... | Chuyển động chính khi render |
|---|----------|------------------------------------------------|-------------------------------|
| 01 | Quả cầu nuốt cảnh (`scene-01.png`) | tăng trưởng, nguy cơ phình to, thứ gì đó lớn dần và đe dọa | quả cầu đen lớn dần theo thời gian, nuốt dần cảnh vật xung quanh |
| 02 | Cân so sánh A vs B (`scene-02.png`) | so sánh 2 lựa chọn, bên nào nặng/nhẹ hơn, đánh đổi | cán cân nghiêng dần về bên nặng hơn |
| 03 | Mạng lưới node (`scene-03.png`) | hệ thống, kết nối, lan truyền, nhiều thứ liên quan nhau | các node sáng lên lần lượt, xung chạy dọc đường nối |
| 04 | Dòng thời gian (`scene-04.png`) | lịch sử, tiến trình, các mốc phát triển | mốc hiện lần lượt từ trái sang phải, mốc sau to hơn mốc trước |
| 05 | Rơi & xếp chồng (`scene-05.png`) | tích lũy, số lượng tăng dần, chất đống theo thời gian | các khối rơi xuống xếp thành đống ngày càng cao |
| 06 | Bản đồ hành trình (`scene-06.png`) | quá trình từng bước, lộ trình, cách làm theo bước | đường đứt nét vẽ dần, các chặng sáng lên, ghim đích nhấp nháy |
| 07 | Cỗ máy vận hành (`scene-07.png`) | cơ chế hoạt động, bên trong nó chạy thế nào, quy trình sản xuất | bánh răng quay ăn khớp, băng chuyền chạy, thành phẩm ra lò |
| 08 | Người trong cảnh (`scene-08.png`) | con người bị công nghệ tác động, trải nghiệm người dùng | nhân vật ngồi làm việc, bong bóng suy nghĩ hiện vật thể tượng trưng |

Nguyên tắc thêm mẫu mới: mỗi mẫu phải là 1 ẨN DỤ HÌNH ẢNH dùng lại được
cho nhiều chủ đề, không vẽ riêng cho 1 video. Rio nạp thêm mẫu → thư viện
trong tool tự hiện thêm, người dùng không phải làm gì.

## 4. Giao diện (theo ảnh `tool-mockup-pixel.png`, 2000×1280, 3 cột)

- Header: logo pixel + tên "PIXEL STUDIO — MOCKUP (chưa phải tool thật)",
  dòng mô tả luồng, và **băng khóa phong cách** ghi rõ chuẩn 16-bit đã
  khóa + dự án riêng kênh mới.
- Cột trái — KỊCH BẢN: ô dán text (ví dụ trong hình: mở đầu Long #5);
  ghi chú tool tự cắt câu; chip đếm số câu và số câu đã gán cảnh;
  danh sách thư viện mẫu cảnh hiện có.
- Cột giữa — TỪNG CÂU: mỗi câu 1 thẻ gồm ảnh thu nhỏ của mẫu cảnh pixel
  đã chọn, câu thoại, mốc thời gian tự khớp giọng đọc, ô chọn "MẪU CẢNH"
  và "Hiệu ứng".
- Cột phải — XEM TRƯỚC + RENDER: khung xem trước 16:9 (cảnh quả cầu
  pixel) có thanh phụ đề, ô chọn giọng cố định `am_adam`, định dạng +
  nhạc nền, nút RENDER VIDEO, thanh tiến trình dạng ô pixel.
- Chất pixel trong giao diện mockup: khung vuông góc (không bo tròn),
  ô vuông trang trí ở 4 góc panel, tiêu đề cột bằng font VT323,
  tên tool và nút Render bằng font PressStart2P, chữ nội dung giữ font
  thường dễ đọc.

## 5. Kỹ thuật (cho AI/dev đọc khi build)

- Vẽ cảnh: Python + PIL, mỗi frame vẽ bằng code trên lưới 320×180 rồi
  phóng NEAREST. Kế thừa kỹ thuật từ
  `~/workspace/pixel-studio-sample/build_pixel_samples.py` (Painter theo
  tọa độ chuẩn hóa, quả cầu viền tím, nền sao + dithering) và bố cục 8
  mẫu từ `~/workspace/kurzgesagt-tool-mockup/`. Cấm zoompan trên ảnh
  tĩnh — chuyển động phải đến từ chính các vật thể trong cảnh.
- Giọng: Kokoro `am_adam` qua sherpa-onnx (chạy local, miễn phí);
  khi viết script, thuật ngữ cần đánh vần thì ghi dạng "R.A.G.".
- Ráp video: ffmpeg, loudnorm về −16 LUFS, phụ đề cháy theo câu
  (font VT323).
- File trong thư mục này: `scene-01.png` … `scene-08.png` (8 mẫu cảnh
  pixel, 960×540, có thanh nhãn), `tool-mockup-pixel.png` (mockup tool),
  `build_pixel_tool_mockup.py` (toàn bộ code vẽ). Tất cả 100% code,
  không AI sinh ảnh, không icon emoji.

## 6. Điểm yếu đã biết (ghi trung thực, sau 3 vòng eye-check)

- Các mẫu mới ở mức "đọc được ý" — khi build bản thật, mỗi mẫu cần 1
  vòng tinh chỉnh chuyển động riêng sau khi Minh duyệt hướng.
- Mẫu 02 (cân): dây treo đĩa trái bị chồng khối che khuất (thanh cân
  nhìn như chạm vào khối — đúng bố cục tham chiếu nhưng dây không thấy);
  chữ "B" hơi đè lên quầng sáng của quả cầu cyan.
- Mẫu 04 (dòng thời gian): số thứ tự 2 và 4 nằm khá sát biểu tượng phía
  dưới trục; node mốc 5 chạm nhẹ đầu mũi tên cuối trục.
- Mẫu 08 (người trong cảnh): tay nhân vật còn là 1 thanh thẳng dài,
  chao đèn hơi giống lá cờ — giữ nguyên từ bảng mẫu pixel đã được duyệt
  trước đó; chấp nhận được vì nhân vật chỉ là phần tử cảnh.
- Font VT323 ở cỡ nhỏ: các dấu xếp chồng (kiểu "Ẫ", "Ệ") hơi chật nhưng
  vẫn đọc được — chỉ dùng cho tiêu đề ngắn, không dùng cho đoạn dài.
- Mockup là ảnh tĩnh dựng bằng code: vị trí/kích thước các nút là đề
  xuất, khi build web thật có thể lệch nhẹ nhưng phải giữ đúng 3 cột,
  luồng trên và chuẩn pixel đã khóa.
