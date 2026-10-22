# PIXEL STUDIO — Hướng dẫn dùng (cho người mới, không cần biết code)

Tool làm video giải thích **vẽ hoàn toàn bằng code**, phong cách **PIXEL 16-BIT**
đã khóa cứng: bạn dán kịch bản → chọn mẫu cảnh cho từng câu → bấm Render →
có video. Giọng đọc cố định của kênh: **am_adam** (chạy ngay trên máy bạn,
không gửi đi đâu, không tốn phí).

Đây là **dự án riêng cho kênh mới**, tách biệt hẳn tool videos hiện tại —
hai tool không dùng chung gì cả, cứ yên tâm dùng song song.

---

## PHẦN A — Cài đặt 1 lần duy nhất (khoảng 15–20 phút)

### Bước 1: Cài Python
1. Vào trang `python.org/downloads` → bấm nút tải Python 3 (bản mới nhất).
2. Mở file vừa tải → ở màn hình cài đầu tiên, **tick vào ô "Add python.exe
   to PATH"** ở dưới cùng (quan trọng nhất, quên là tool không chạy) → bấm
   **Install Now**.
3. Xong bạn sẽ thấy dòng **"Setup was successful"** → đóng cửa sổ đó lại.

### Bước 2: Cài 3 thư viện cho tool
1. Mở thư mục chứa tool Pixel Studio (thư mục có file `START-PIXEL.bat`).
2. Bấm vào thanh địa chỉ của thư mục → gõ `cmd` → Enter.
   → Một cửa sổ đen (cửa sổ lệnh) sẽ mở ra ngay tại thư mục này.
3. Dán đúng dòng này vào rồi Enter:
   `pip install pillow sherpa-onnx soundfile`
4. Chờ chạy xong → bạn sẽ thấy dòng **"Successfully installed ..."** ở cuối.
   (Bước này chỉ làm 1 lần. Nếu thấy chữ đỏ báo lỗi, chụp màn hình gửi Rio.)

### Bước 3: Cài ffmpeg (công cụ ráp video)
Cách đơn giản nhất:
1. Tải ffmpeg bản Windows dạng file nén (.zip) từ trang chính thức
   `ffmpeg.org/download.html` (mục Windows builds).
2. Giải nén → chép file `ffmpeg.exe` (nằm trong thư mục `bin` của bản giải
   nén) **thẳng vào thư mục tool Pixel Studio** (ngang hàng với
   `START-PIXEL.bat`).
   → Tool sẽ tự tìm thấy nó ở đó, không cần cài đặt gì thêm.
   (Nếu máy bạn đã có ffmpeg trong PATH sẵn thì bỏ qua bước này.)

### Bước 4: Model giọng đọc (tự tải lần đầu)
- Lần Render đầu tiên, tool **tự tải model giọng Kokoro** (~350MB) từ nguồn
  chính thức của k2-fsa (nhà phát triển sherpa-onnx) về thư mục `models/`.
- Bạn sẽ thấy dòng log "dang tai Kokoro..." — cứ để nó tải xong (vài phút
  tùy mạng). Từ lần sau không tải lại nữa.
- Nếu thư mục `models/kokoro-en-v0_19` đã có sẵn trong bản tool bạn nhận
  thì bỏ qua, tool dùng luôn.

---

## PHẦN B — Dùng hằng ngày (3 bước)

### Bước 1: Mở tool
- Nhấp đúp file **`START-PIXEL.bat`**.
- Bạn sẽ thấy 1 cửa sổ đen hiện ra (đừng đóng cửa sổ này — đóng là tắt
  tool) và **trình duyệt tự mở** trang Pixel Studio ở địa chỉ
  `localhost:8766`. Nếu trình duyệt không tự mở, tự gõ địa chỉ đó vào
  trình duyệt cũng được.
- Trang hiện ra có **3 cột**: KỊCH BẢN · TỪNG CÂU · XEM TRƯỚC + RENDER.

### Bước 2: Dán kịch bản + chọn cảnh
1. Ở cột 1, dán kịch bản tiếng Anh vào ô chữ. Tool **tự cắt thành từng
   câu** và đếm số câu + ước tính độ dài ngay bên dưới.
2. Ở cột 2, mỗi câu có 1 thẻ: hình **xem trước ĐỘNG** (ảnh GIF chuyển động
   thật của mẫu cảnh) + ô chọn mẫu cảnh. Có 8 mẫu:
   quả cầu nuốt cảnh · cân so sánh · mạng lưới node · dòng thời gian ·
   rơi & xếp chồng · bản đồ hành trình · cỗ máy vận hành · người trong cảnh.
   **Mọi mẫu đều có chuyển động + hiệu ứng riêng** — không có cảnh tĩnh.
3. Mẹo viết kịch bản: muốn AI đọc **đánh vần** 1 thuật ngữ (ví dụ RAG)
   thì viết thành **"R.A.G."** trong kịch bản. Viết thường thì nó đọc
   liền 1 từ.

### Bước 3: Render
1. Cột 3: giọng đọc đã khóa sẵn **am_adam** (không cần chọn), định dạng
   ngang 16:9 (1920×1080).
2. Nhạc nền (không bắt buộc): chép file nhạc `.mp3`/`.wav` vào thư mục
   **`Music`** của tool → tải lại trang → chọn tên file nhạc ở ô "Nhạc
   nền". Nhạc sẽ tự lặp và trộn nhỏ dưới giọng đọc.
3. Bấm nút xanh **RENDER VIDEO** → thanh tiến trình chạy → xong sẽ hiện
   nút **"Mở video"** và **"Mở thư mục Videos"**.
4. Video nằm trong thư mục **`Videos`** của tool, tên dạng
   `video-2026-10-22-1430.mp4` (theo ngày–giờ render).
   Thời lượng từng cảnh = đúng thời lượng giọng đọc câu đó; phụ đề cháy
   sẵn ở dưới khung; âm thanh đã chuẩn hoá −16 LUFS.

### Tắt tool
Quay lại cửa sổ đen → nhấn `Ctrl + C`, hoặc đóng luôn cửa sổ đó.

---

## Khi gặp lỗi
- Cửa sổ đen báo **[LOI] Khong tim thay Python** → chưa cài Python hoặc
  quên tick "Add to PATH" ở Bước 1. Cài lại Python, nhớ tick ô đó.
- Báo **[LOI] Khong tim thay ffmpeg** → làm lại Bước 3.
- Trang web báo lỗi đỏ khi render → đọc dòng lỗi cuối cùng trong ô trạng
  thái ở cột 3, chụp màn hình gửi Rio.
- Render lâu: video 1 phút mất khoảng 5–8 phút trên máy thường (vẽ từng
  khung hình bằng code + sinh giọng đều chạy trên CPU). Cứ để chạy, đừng
  tắt giữa chừng.

## Cấu trúc thư mục (để biết, không cần đụng vào)
- `server.py` — chương trình chính (trang web của tool).
- `engine/` — ruột tool: vẽ cảnh pixel, giọng đọc, ráp video.
- `models/` — model giọng Kokoro.
- `fonts/` — font pixel VT323 + PressStart2P.
- `previews/` — ảnh GIF xem trước của 8 mẫu cảnh (tool tự sinh).
- `Music/` — bạn chép nhạc nền vào đây.
- `Videos/` — video render xong nằm ở đây.
- `work/` — thư mục tạm khi render (tự dọn cũng được).
