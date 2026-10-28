# PIXEL STUDIO V2.3 — Hướng dẫn dùng (cho người mới, không cần biết code)

Tool làm video giải thích **vẽ hoàn toàn bằng code**, phong cách **PIXEL 16-BIT**
đã khóa cứng: bạn dán kịch bản → tool tự gán cảnh theo nội dung → bấm Render →
có video. Giọng đọc cố định của kênh: **am_adam** (chạy ngay trên máy bạn,
không gửi đi đâu, không tốn phí).

Đây là **dự án riêng cho kênh mới**, tách biệt hẳn tool videos hiện tại —
hai tool không dùng chung gì cả, cứ yên tâm dùng song song.

## MỚI: GIAO DIỆN 3 BƯỚC + THƯ VIỆN DẠNG HỘP MỞ

Trang tool KHÔNG còn là 1 trang dài cuộn mãi nữa — đã chia thành
**3 trang tab** đi theo đúng thứ tự làm việc:

1. **Tab "1 · Kịch bản":** chọn gói phong cách (mục 0) + dán kịch bản.
   Cuối trang có nút xanh **SANG BƯỚC 2 · TỪNG CÂU »**.
2. **Tab "2 · Từng câu":** danh sách thẻ câu như trước; mỗi thẻ có thêm
   nút **Thư Viện** màu hổ phách (xem điểm 2 dưới đây).
3. **Tab "3 · Xem trước & Render":** hộp xem trước + chọn nhạc + nút
   Render + nối video, y như trước nhưng nằm ở trang riêng cho gọn.

Chuyển tab chỉ ẩn/hiện trang — **không tải lại, không mất việc đang làm
dở** (kịch bản đã dán, cảnh đã đổi tay... giữ nguyên hết). Đầu trang 2
và 3 cũng có nút qua lại bước, khỏi cần cuộn lên thanh tab.

**Thư viện Style2 đã dời khỏi cuối trang** thành 1 **hộp mở đè** (mở
lên che màn hình; đóng bằng nút ✕ góc phải, nút "Đóng", hoặc bấm ra
ngoài hộp):

- Bấm nút **THƯ VIỆN** màu hổ phách ở thanh tab (bên phải) để MỞ XEM
  thư viện: tìm kiếm, lọc theo nhóm như cũ — chế độ này chỉ xem, chưa
  gắn vào câu nào; trong hộp sẽ hiện dòng hướng dẫn màu hổ phách.
- Muốn gán 1 ảnh trong thư viện làm nền cho 1 câu cụ thể: sang Bước 2,
  bấm nút **Thư Viện** ngay trong thẻ của câu đó → hộp thư viện mở ra
  kèm dòng "Đang sửa: Câu N · cảnh ..." → bấm **"Đặt làm nền"** ở mục
  muốn dùng → hộp tự đóng, ảnh đã gán vào đúng câu đó.

---

## MỚI: 8 GÓI PHONG CÁCH + HIỆU ỨNG MỚI CHO GÓI CŨ

Mục 0 ở Bước 1 giờ có **8 thẻ gói** (mỗi video vẫn thuộc đúng 1 gói):

1. **PIXEL 16-BIT** — gói gốc (9 cảnh code + 8 template Style2).
2. **STAGE** — kinetic sân khấu gỗ (11 mẫu).
3. **CRT** — terminal xanh lá (11 mẫu, thêm mẫu **alert_warn** cảnh
   báo đỏ).
4. **PAPER** — giấy & mực viết tay (10 mẫu).
5. **ZINE** — cắt dán tạp chí (10 mẫu).
6. **ĐẤT SÉT** (MỚI) — clay stop-motion: khối nặn bo tròn màu kẹo
   trên nền kem, nảy "squash" khi xuất hiện, con sâu đất sét làm
   thanh tiến trình, nút đất sét ở màn cuối (10 mẫu).
7. **FLAT** (MỚI) — đồ họa phẳng hiện đại: nền màu trơn, khối hình
   học gọn, biểu đồ phẳng + số khổng lồ (10 mẫu).
8. **SHOW** (MỚI) — gameshow truyền hình: biển marquee viền bóng đèn
   nhấp nháy đuổi nhau, vòng quay may mắn, bảng điểm LED, bục
   1-2-3, pháo giấy ở màn cuối (10 mẫu).

Cách dùng không đổi: chọn gói → dán kịch bản → tool tự gán cảnh của
gói đó → chỉnh tay ở Bước 2 → Render ở Bước 3. Job cũ của mọi gói vẫn
mở và render như trước.

**Hiệu ứng mới cho gói cũ** (đều là TÙY CHỌN thêm — không chọn thì
mọi thứ y như cũ):

- **PIXEL:** thêm cảnh **#9 Sao băng quét cảnh**. Muốn chuyển cảnh
  "vỡ pixel" cho 1 câu: thêm tham số `fx = pixelate` cho câu đó
  (đầu câu vỡ pixel rồi rõ dần, cuối câu vỡ lại).
- **STAGE:** màn cuối `follow_end` có **biến thể 3 = pháo giấy
  pixel** ăn mừng (ô "Biến thể bố cục" trên thẻ câu, điền 3). Mẫu
  `stage_text` điền tham số **Hiệu ứng = sweep** để đèn sân khấu
  quét ngang.
- **CRT / PAPER / ZINE:** trên thẻ câu có thêm ô tham số **"Hiệu
  ứng"**: CRT điền `static` (nhiễu mất sóng đầu/cuối câu); PAPER
  điền `flip` (lật trang cong) hoặc `circle` ở mẫu note_hook
  (khoanh tròn 2 vòng từ khóa); ZINE điền `tape` (băng dính kéo
  ngang lau cảnh) hoặc `jitter` ở mẫu tile_hook (ô chữ rung).
  Gộp được nhiều hiệu ứng bằng dấu phẩy, ví dụ `flip,circle`.

---

## MỚI Ở V2.3 (25/10/2026)

1. **Thư viện gọn + tìm được:** thư viện Style2 (nay mở bằng nút
   **THƯ VIỆN** — xem mục mới ở đầu tài liệu này) đã chia nhóm có
   tiêu đề (Điện thoại · Cảnh nền · Ẩn dụ · Template — số liệu · Chân
   dung pixel), có **ô tìm kiếm** lọc theo tên/từ khoá/nhóm, mỗi mục
   hiện sẵn **từ khoá** dưới tên. 3 ảnh thật chuyển vào mục **"Tham
   chiếu vẽ"** thu gọn ở cuối thư viện (chỉ để tham chiếu vẽ, KHÔNG
   dùng làm nền); 5 mục hỗ trợ nội bộ của template được ẩn khỏi lưới.
   Mỗi ảnh có nút **"Đặt làm nền"** — gán thẳng làm ảnh nền cho câu
   đang mở thư viện ở Bước 2.
2. **8 template Style2 thành mẫu cảnh thật:** counter, chart,
   price_bars, death_spiral, quote_card, definition_card, game_over,
   end_card — chọn ở bảng **Đổi cảnh** (nhóm "Style2 — số liệu"). Mỗi
   thẻ câu hiện **form sửa tham số** ngay trên thẻ (tiêu đề, nhãn, số
   liệu... sửa là render ra shot mới, không còn chữ Nokia nướng cứng);
   có thêm **chữ chạy** gõ từng ký tự (mặc định lấy chữ của câu, tắt
   hoặc ghi đè được) và **caption pop-up** chữ lớn vàng hiện ~1,2 giây
   đầu cảnh, phủ lên trên media.
3. **Định dạng dọc 9:16 cho Shorts:** ô **Định dạng** ở Bước 3 đã mở
   khoá — chọn "Dọc 9:16 (1080×1920)" để render video dọc: nền sao phủ
   kín cả khung, nội dung cảnh nằm giữa khung theo chiều dọc, không
   kéo giãn méo hình. Áp dụng cho cả cảnh code lẫn template Style2.

---

## MỚI Ở V2.2 (25/10/2026)

1. **Thư viện style2 từ video Nokia** — 30 ảnh nền + 8 template + nhạc
   dark-empire-loop; mở bằng nút **THƯ VIỆN** trên đầu trang (bấm vào
   từng mục để xem lớn ở hộp xem trước tại Bước 3).
2. **Chuẩn mix kênh:** nhạc 0.34, loudnorm -15 LUFS.
3. **End card mặc định đúng tên kênh 16BIT_EXE.**
4. **Bản repo GitHub đã đồng bộ khớp bản chính.**

---

## Có gì mới ở bản V2 này?

1. **TỰ GÁN CẢNH theo nội dung** — dán kịch bản xong, tool tự đọc từng câu
   và chọn mẫu cảnh khớp nội dung (bằng luật từ khóa cài sẵn, chạy 100%
   offline trên máy bạn). Mỗi câu đều hiện rõ **lý do gán** + **dữ kiện trích
   từ câu** để bạn kiểm chứng. Gán chưa đúng ý → đổi tay 1 chạm, lựa chọn
   của bạn luôn thắng.
2. **Dữ kiện trong câu được đưa thẳng vào hình** — câu có "300%" thì quả
   cầu phình theo đúng 300% và hiện chữ 300% trong cầu; câu có "X vs Y"
   thì cân hiện nhãn X/Y; câu có mốc năm thì dòng thời gian hiện năm đó...
3. **MŨI TÊN CHÚ THÍCH** — mỗi câu gắn thêm được 1 mũi tên vàng chỉ vào
   1 điểm trong khung kèm hộp chữ nhãn (ví dụ: "300% GROWTH"), hiện bật ra
   ở đầu cảnh.
4. **ẢNH NỀN LAI** — mỗi câu tải lên được 1 ảnh nền riêng (kiểu ảnh pixel
   điện ảnh): tool tự pixel hóa ảnh về đúng lưới 320×180 làm nền thay cho
   cảnh vẽ code, vẫn có giọng đọc + phụ đề + mũi tên chú thích như thường.
5. **THƯ VIỆN NHẠC RETRO tích hợp sẵn 11 bài** chiptune 8/16-bit soạn
   riêng cho kênh — mở tool là chọn được ngay, không phải chép file nữa.
6. **Chữ phụ đề nét hơn** — phụ đề và chữ nhãn được vẽ ở độ phân giải thật
   1920×1080 nên nét căng như chữ trong các Short trước đây.

---

## PHẦN A — Cài đặt 1 lần duy nhất (khoảng 15–20 phút)

Giống hệt bản V1 — nếu máy bạn đã cài cho V1 rồi thì **bỏ qua phần này**,
chỉ cần mở file `START-PIXEL-V2.bat` ở Phần B.

### Bước 1: Cài Python
1. Vào trang `python.org/downloads` → bấm nút tải Python 3 (bản mới nhất).
2. Mở file vừa tải → ở màn hình cài đầu tiên, **tick vào ô "Add python.exe
   to PATH"** ở dưới cùng (quan trọng nhất, quên là tool không chạy) → bấm
   **Install Now**.
3. Xong bạn sẽ thấy dòng **"Setup was successful"** → đóng cửa sổ đó lại.

### Bước 2: Cài 3 thư viện cho tool
1. Mở thư mục chứa tool Pixel Studio V2 (thư mục có file
   `START-PIXEL-V2.bat`).
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
   nén) **thẳng vào thư mục tool Pixel Studio V2** (ngang hàng với
   `START-PIXEL-V2.bat`).
   → Tool sẽ tự tìm thấy nó ở đó, không cần cài đặt gì thêm.
   (Nếu máy bạn đã có ffmpeg trong PATH sẵn thì bỏ qua bước này.)

### Bước 4: Model giọng đọc (tự tải lần đầu)
- Lần Render đầu tiên, tool **tự tải model giọng Kokoro** (~350MB) từ nguồn
  chính thức của k2-fsa (nhà phát triển sherpa-onnx) về thư mục `models/`.
- Bạn sẽ thấy dòng log "dang tai Kokoro..." — cứ để nó tải xong (vài phút
  tùy mạng). Từ lần sau không tải lại nữa.

---

## PHẦN B — Dùng hằng ngày

### Bước 1: Mở tool
- Nhấp đúp file **`START-PIXEL-V2.bat`**.
- Bạn sẽ thấy 1 cửa sổ đen hiện ra (đừng đóng cửa sổ này — đóng là tắt
  tool) và **trình duyệt tự mở** trang Pixel Studio V2 ở địa chỉ
  `localhost:8766`. Nếu trình duyệt không tự mở, tự gõ địa chỉ đó vào
  trình duyệt cũng được.
- Trang hiện ra mở sẵn ở **tab 1 · Kịch bản**. Trên đầu trang có thanh
  tab: **1 · Kịch bản | 2 · Từng câu | 3 · Xem trước & Render** và nút
  **THƯ VIỆN** màu hổ phách ở bên phải.

### Bước 2: Dán kịch bản — tool TỰ GÁN cảnh
1. Ở Bước 1 (tab Kịch bản), dán kịch bản tiếng Anh vào ô chữ.
   → Ngay bên dưới, tool hiện lại kịch bản với **các từ manh mối được tô
   màu** (vàng = số %/tăng trưởng, xanh dương = so sánh, xanh lá = thứ tự
   bước, cam = mốc năm) và 2 ô thống kê: số câu + **bao nhiêu câu đã được
   TỰ GÁN**.
2. Công tắc **"TỰ GÁN CẢNH THEO NỘI DUNG"** mặc định **BẬT**. Tắt nó đi
   thì tool quay về cách chọn tay toàn bộ như bản V1.
3. Chuyển sang Bước 2 (bấm tab "2 · Từng câu" hoặc nút **SANG BƯỚC 2**
   ở cuối trang): mỗi câu là 1 thẻ. Với câu được tự gán, bạn sẽ thấy:
   - Dòng xanh lá **"■ TỰ GÁN: <tên cảnh>"** và **dòng lý do** (tool gán
     vì trúng từ khóa/mẫu nào trong câu).
   - **Chip dữ kiện** (khung xanh nhỏ): ví dụ `300%` `3 years`, hoặc
     `A: ChatGPT` `B: Claude`, hoặc `2 chặng`. Đây là dữ kiện tool trích
     từ câu và sẽ **đưa thẳng vào hình** khi render.
   - **Thanh độ khớp manh mối** (5 ô): càng nhiều ô sáng, manh mối càng
     rõ. Nếu hiện chữ cam "khớp thấp" thì bạn nên xem lại thẻ đó kỹ hơn.
4. **Đổi tay:** ở mỗi thẻ có ô **"MẪU CẢNH (đổi tay ở đây)"** — chọn cảnh
   khác là xong, thẻ chuyển viền vàng và ghi "ĐỔI TAY — đã khóa", máy
   không gán đè nữa.
5. **Câu không có manh mối rõ:** thẻ viền đỏ + dòng **"⚠ CHƯA GÁN"** —
   tool cố tình để trống chứ không gán bừa. Bạn **phải chọn tay** cho câu
   đó, không chọn thì bấm Render tool sẽ báo lỗi nhắc bạn quay lại chọn.

### Bước 3: (Tùy chọn) Mũi tên chú thích cho 1 câu
1. Trong thẻ của câu, ở mục **"MŨI TÊN CHÚ THÍCH"**, gõ chữ nhãn vào ô
   (ví dụ: `300% GROWTH`). Để trống = câu đó không có chú thích.
2. Ở ô bên cạnh, chọn **điểm chỉ tới** (mũi tên sẽ chỉ vào đâu trong
   khung: trên/giữa/dưới × trái/giữa/phải — mặc định là chính giữa).
   → Khi render, ở đầu cảnh đó, một **hộp nhãn viền vàng bật ra** kèm
   **mũi tên vàng chỉ tới điểm bạn chọn**. Hộp tự co vừa đúng độ dài chữ.

### Bước 4: (Tùy chọn) Ảnh nền lai cho 1 câu
1. Trong thẻ của câu, ở mục **"ẢNH NỀN LAI"**, bấm **"Chọn ảnh PNG nền"**
   → chọn 1 file ảnh (.png/.jpg) trên máy bạn.
   → Tên ảnh hiện ra kèm dòng "nền ảnh thay cảnh code".
2. Khi render, câu đó sẽ dùng **ảnh của bạn làm nền** (tool tự pixel hóa
   ảnh về lưới 320×180 cho đúng chất pixel) thay cho cảnh vẽ bằng code.
   Giọng đọc, phụ đề và mũi tên chú thích vẫn có như thường.
3. Muốn quay lại cảnh code: bấm **"Bỏ ảnh nền"** trên thẻ.
4. **Cách khác — dùng ảnh có sẵn trong thư viện của tool:** ngay trong
   thẻ câu có nút **Thư Viện** màu hổ phách → hộp thư viện mở ra (đầu
   hộp ghi rõ "Đang sửa: Câu N") → tìm/chọn 1 ảnh → bấm **"Đặt làm
   nền"** → hộp tự đóng và ảnh đã thành nền của câu đó. Giống hệt cách
   tải ảnh lên ở trên, chỉ khác là ảnh lấy từ kho có sẵn.

### Bước 5: Chọn nhạc + Render
1. Chuyển sang Bước 3 (tab "3 · Xem trước & Render"): giọng đọc đã
   khóa sẵn **am_adam** (không cần chọn). Ô
   **Định dạng**: Ngang 16:9 (1920×1080, mặc định) hoặc **Dọc 9:16
   (1080×1920)** nếu làm Shorts.
2. Ở ô **"Nhạc nền"**: chọn 1 trong **11 bài retro có sẵn** (bài 00 là
   nhạc chủ đề chính của kênh; 01–10 theo các tâm trạng: đi lên, căng
   thẳng, sụp đổ, thắng lợi...), hoặc để **"Không nhạc"**.
   → Nhạc sẽ **tự lặp liền mạch** từ đầu tới cuối video, âm lượng nhỏ
   nằm dưới giọng đọc.
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
  thái ở Bước 3, chụp màn hình gửi Rio.
- Bấm Render mà bị nhắc **"Câu N chưa có cảnh"** → quay lại Bước 2, chọn
  tay mẫu cảnh cho câu đó (thẻ viền đỏ) rồi render lại.
- Render lâu: video 1 phút mất khoảng 5–8 phút trên máy thường (vẽ từng
  khung hình bằng code + sinh giọng đều chạy trên CPU). Cứ để chạy, đừng
  tắt giữa chừng.

## Cấu trúc thư mục (để biết, không cần đụng vào)
- `server.py` — chương trình chính (trang web của tool).
- `START-PIXEL-V2.bat` — file mở tool bản V2.
- `engine/` — ruột tool: vẽ cảnh pixel, tự gán cảnh, giọng đọc, ráp video.
- `models/` — model giọng Kokoro (tool tự tải lần render đầu).
- `fonts/` — font pixel VT323 + PressStart2P.
- `previews/` — ảnh GIF xem trước của 8 mẫu cảnh (tool tự sinh).
- `music/` — thư viện nhạc nền: 11 bài retro có sẵn + bài bạn chép thêm.
- `uploads/` — ảnh nền lai bạn tải lên từ giao diện.
- `Videos/` — video render xong nằm ở đây.
- `work/` — thư mục tạm khi render (tự dọn cũng được).

---

## MỚI Ở BẢN 2.1 (đợt vá 22/10/2026)

### 1. Bộ chọn mẫu cảnh mới (nút "Đổi cảnh" trên mỗi thẻ câu)
Bấm **Đổi cảnh** ở thẻ câu → mở bảng chọn cảnh có:
- **Gợi ý cho câu này:** tối đa 3 cảnh hợp nhất theo nội dung câu, kèm thanh độ khớp — bấm 1 cái là gán xong.
- **Ô tìm kiếm:** gõ tên cảnh hoặc từ khóa (vd: `sụp đổ`, `tiền`, `vs`, `mạng lưới`) là lọc ngay, khỏi cuộn tìm.
- **Chip nhóm:** Tất cả · Tăng trưởng · So sánh · Công nghệ · Thời gian · Con người — bấm nhóm để thu hẹp.
- **Lưới ảnh động:** nhìn hình chọn cảnh, nhanh hơn đọc tên. Cảnh nào bạn chọn tay nhiều lần sẽ tự nổi lên đầu lưới.

### 2. Ô xem trước tự bám theo thẻ câu
Bấm vào bất kỳ thẻ câu nào ở Bước 2 → ô **XEM TRƯỚC** ở Bước 3 tự đổi sang đúng cảnh của câu đó (không cần bấm ảnh nhỏ nữa).

### 3. Nối video (ở Bước 3, dưới nút Render)
Quy trình làm video dài: **render từng khúc khoảng 30 giây** (mỗi khúc 4–5 câu) → các khúc hiện trong danh sách **NỐI VIDEO** → **tick chọn các khúc theo đúng thứ tự** (danh sách xếp theo tên file) → bấm **NỐI CÁC VIDEO ĐÃ CHỌN** → tool tạo 1 file `ghep-<ngày-giờ>.mp4` trong thư mục Videos.
Lưu ý: chỉ nối được các video do chính tool này xuất ra (cùng định dạng). Đặt tên khúc có số thứ tự (01, 02, 03...) thì thứ tự nối luôn đúng.

