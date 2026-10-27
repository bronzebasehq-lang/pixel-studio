# LIBRARY — Thư viện nguyên liệu Pixel Studio

- **Nguồn nạp:** Video #1 kênh 16bit_exe — "The Fall of Nokia" (Long #1, phong cách style2), thư mục `~/workspace/16bit-exe/video-01-nokia/` + nhạc `~/workspace/16bit-exe-music-dark/`.
- **Ngày nạp:** 2026-10-25
- **Phạm vi đã duyệt:** Nhóm A (ảnh) + Nhóm B (template code) + Nhóm C (nhạc + cấu hình).
- **Nhóm D — BỊ LOẠI TRỪ (không nạp):** file `.json` đi kèm ảnh trong `assets-style2/`; file voice `.wav` của các seg; thư mục `assets/` và `assets-game/` (nguyên liệu render game-style cũ); thumbnail nháp (`thumb-a/b/c/d.png`, `thumb-sheet.png` — bản chốt `thumb-e.png` cũng không nạp vì là ấn phẩm của video, không phải nguyên liệu tái dùng); frames trung gian trong các thư mục `render-seg*/frames/`; file nhạc `.wav` (chỉ nạp bản `.mp3`).

## Ảnh — nhóm NGƯỜI (uploads/)

| Tên | File | Tags |
|---|---|---|
| jobs-portrait | `uploads/jobs-portrait.webp` | chan dung nguoi noi tieng steve jobs portrait keynote |
| ollila-portrait | `uploads/ollila-portrait.webp` | chan dung ceo jorma ollila portrait |
| elop-portrait | `uploads/elop-portrait.webp` | chan dung ceo stephen elop portrait |
| jobs-ref | `uploads/jobs-ref.jpg` | anh that tham chieu chan dung reference photo |
| ollila-ref | `uploads/ollila-ref.jpg` | anh that tham chieu chan dung reference photo |
| elop-ref | `uploads/elop-ref.jpg` | anh that tham chieu chan dung reference photo |

## Ảnh — nhóm ĐIỆN THOẠI (uploads/)

| Tên | File | Tags |
|---|---|---|
| 3310-monument | `uploads/3310-monument.webp` | dien thoai nokia 3310 tuong dai monument phone |
| 3310-solo | `uploads/3310-solo.webp` | dien thoai nokia 3310 mot minh solo phone |
| iphone-solo | `uploads/iphone-solo.webp` | dien thoai iphone mot minh solo phone |
| keynote-phone | `uploads/keynote-phone.webp` | dien thoai tren san khau keynote phone stage |
| symbian-phone | `uploads/symbian-phone.webp` | dien thoai symbian phone keypad |
| lumia | `uploads/lumia.webp` | dien thoai lumia windows phone |
| meego-phone | `uploads/meego-phone.webp` | dien thoai meego n9 phone |
| phone-table | `uploads/phone-table.webp` | dien thoai tren ban phone table prototype |
| 1011-pedestal | `uploads/1011-pedestal.webp` | dien thoai nokia 1011 be bao tang pedestal museum |

## Ảnh — nhóm CẢNH nền (uploads/)

| Tên | File | Tags |
|---|---|---|
| factory | `uploads/factory.webp` | nha may cong nghiep factory industry |
| warehouse | `uploads/warehouse.webp` | kho hang warehouse storage |
| mill-dusk | `uploads/mill-dusk.webp` | xuong giay hoang hon mill dusk river |
| paper-machine | `uploads/paper-machine.webp` | may lam giay paper machine factory |
| boardroom-night | `uploads/boardroom-night.webp` | phong hop ban dem boardroom night |
| store-shuttered | `uploads/store-shuttered.webp` | cua hang dong cua sap tiem store shuttered closed |
| blueprint-lab | `uploads/blueprint-lab.webp` | phong lab ban ve blueprint lab prototype |
| 5g-tower | `uploads/5g-tower.webp` | thap song 5g tower antenna network |
| ecosystem | `uploads/ecosystem.webp` | he sinh thai ecosystem apps |
| camera-measure | `uploads/camera-measure.webp` | camera do toc do camera measure studio |
| thumb-bg | `uploads/thumb-bg.webp` | nen thumbnail thumb background |
| skyline-dusk | `uploads/skyline-dusk.webp` | thanh pho hoang hon skyline dusk city |
| skyline-night | `uploads/skyline-night.webp` | thanh pho ban dem skyline night city |

## Ảnh — nhóm ẨN DỤ (uploads/)

| Tên | File | Tags |
|---|---|---|
| burning-platform | `uploads/burning-platform.webp` | gian khoan chay an du burning platform metaphor fire ocean |
| train-wings | `uploads/train-wings.webp` | tau gan canh an du train wings metaphor smoke |

## Template code — SỐ LIỆU (engine/style2_templates.py)

| Tên | File | Preview (GIF) | Tags |
|---|---|---|---|
| counter | `engine/style2_templates.py` | `previews/style2-counter.gif` | bo dem so chay dem tien so luong counter count-up number |
| chart | `engine/style2_templates.py` | `previews/style2-chart.gif` | bieu do duong tang truong lao doc sup do line chart growth collapse |
| price_bars | `engine/style2_templates.py` | `previews/style2-price_bars.gif` | thanh gia so sanh gia ban doanh thu comparison price bars |
| death_spiral | `engine/style2_templates.py` | `previews/style2-death_spiral.gif` | vong xoay tu than khong app khong nguoi dung death spiral loop |

## Template code — TEXT (engine/style2_templates.py)

| Tên | File | Preview (GIF) | Tags |
|---|---|---|---|
| quote_card | `engine/style2_templates.py` | `previews/style2-quote_card.gif` | the trich dan cau noi memo quote card |
| definition_card | `engine/style2_templates.py` | `previews/style2-definition_card.gif` | the dinh nghia giai thich thuat ngu osborne definition card explainer |
| typed_ps + draw_typed + typed_caption | `engine/style2_templates.py` | — | go chu tung ky tu caption lon typewriter typed text |

## Template code — HIỆU ỨNG / helper (engine/style2_templates.py)

| Tên | File | Preview (GIF) | Tags |
|---|---|---|---|
| chip | `engine/style2_templates.py` | — | nhan dan the nho pop label chip tag |
| stamp | `engine/style2_templates.py` | — | con dau do dong dau stamp rejected killed |
| dust / smoke / screen_glow / flicker_glow / glitch | `engine/style2_templates.py` | — | hat bui khoi phat sang nhay lua nhieu song dust smoke glow flicker glitch |
| grid_bg / _panel | `engine/style2_templates.py` | — | nen luoi toa do panel chan dung grid background portrait panel |

## Template code — END CARD (engine/style2_templates.py)

| Tên | File | Preview (GIF) | Tags |
|---|---|---|---|
| game_over | `engine/style2_templates.py` | `previews/style2-game_over.gif` | man game over ket thuc thua game over screen |
| end_card | `engine/style2_templates.py` | `previews/style2-end_card.gif` | the ket thuc kenh logo cuoi video end card outro |

## Âm thanh

| Tên | File | Tags |
|---|---|---|
| dark-empire-loop | `music/11-dark-empire-loop.mp3` | nhac nen tram hung de che dark empire loop background music |

## Cấu hình chuẩn kênh 16bit_exe

| Tên | File | Tags |
|---|---|---|
| voice-am-adam | `engine/voice.py` | giong doc am_adam sid 5 speed 1.0 kokoro voice config |
| music-mix-0.34 | `engine/render.py` | tron nhac nen volume 0.34 music mix config |
| loudnorm-i-15 | `engine/render.py` | chuan am luong loudnorm I=-15 TP=-1.5 LRA=11 loudness config |

## Ghi chú dùng template

- Mỗi template là hàm vẽ 1 frame `fn(t, dur, ...)` trả ảnh RGBA 1920×1080; pipeline gốc render nội bộ 10fps (DT=0.1) rồi upscale/ghep 30fps ở khâu ffmpeg ngoài file seg.
- Thời lượng shot = thời lượng voice + 0.55s (`DURS = [v + 0.55 for v in VOICE]`).
- Giọng chuẩn: Kokoro am_adam — `engine/voice.py`: SID_AM_ADAM = 5, SPEED = 1.0.
- Mix chuẩn: nhạc nền volume 0.34, loudnorm I=-15 : TP=-1.5 : LRA=11 (`engine/render.py`).

## Gói test01 — kinetic (thêm 2026-10-27)

- **Là gì:** gói phong cách thứ hai cạnh Style2, theo SPEC v2 tại `~/workspace/pixel-tool-mockup/kinetic-pack-v1/SPEC.md`: chữ là diễn viên chính trên nền nâu đen (#1F0D08→#0D0604), nhấn đỏ cam/xanh ngọc/trắng kem/vàng, nhịp biến cố liên tục, KHÔNG linh vật.
- **Chọn trong UI:** bảng Đổi cảnh → nhóm **"test01 — kinetic"** (id cảnh `t1:<key>`), sửa chữ/số bằng form tham số trên thẻ câu như Style2. Gói pixel/Style2 cũ giữ nguyên 100%.
- **Code:** `engine/test01_templates.py` (11 hàm vẽ frame 1280×720, chỉ PIL) + `engine/test01_scenes.py` (registry + `events_for` + bộ quét nhịp `scan_pacing` — cảnh báo khi >5s không biến cố, ghi vào log render) + `engine/make_test01_previews.py` (sinh GIF preview `previews/test01-<key>.gif`). `server.py`/`engine/render.py` chỉ thêm nhánh dispatch theo `tpack`, không đổi hành vi cũ.
- **11 mẫu:** hook_cards (thẻ xòe quạt) · stamp_big (đóng dấu) · type_window (cửa sổ gõ chữ) · stage_text (sân khấu chữ, glitch RGB ở từ khóa) · ab_compare (A/B) · item_rows (hàng mục) · big_counter (bộ đếm) · cell_grid (lưới ô) · progress_bar (% + HP) · combo_chain (×N + thanh năng lượng) · follow_end (nút THEO DÕI + con trỏ bấm).
- **Font hệ A:** `fonts/NotoSans-Black.ttf` (chép từ /usr/share/fonts — máy KHÔNG có Be Vietnam Pro; Noto Sans Black phủ đủ dấu tiếng Việt). Hệ B: PressStart2P/VT323 sẵn có.
- **SFX:** project chưa có thư viện tiếng → tự tổng hợp bằng ffmpeg (sine/noise) qua `engine/test01_sfx.py`, file tại `sfx-test01/` (pop/stamp/type/tick/tick_rise_0..10/glitch/click/whoosh).
- **Video mẫu kiểm chứng:** `test01-sample/test01-sample.mp4` (42,8s, 1280×720, không giọng, nhạc 09-retro-chase lặp + SFX theo biến cố, loudnorm −16) + 12 khung tĩnh `frame-XX-*.png` + `scan.txt` (quét nhịp: ĐẠT) + script `test01-sample/render_sample.py`.

## 5 GÓI PHONG CÁCH + LỚP BIẾN THỂ (tái cấu trúc 2026-10-27)

- **Chọn gói ở đâu:** mục **0 · GÓI PHONG CÁCH** ngay đầu giao diện (5 thẻ: PIXEL 16-BIT / STAGE / CRT / PAPER / ZINE, mỗi thẻ có mô tả + số mẫu). Mỗi video thuộc đúng 1 gói — bảng Đổi cảnh và bộ tự gán CHỈ hiện mẫu của gói đang chọn. Đổi gói = gán lại cảnh từ đầu (chữ kịch bản giữ nguyên). Registry trung tâm: `engine/packs.py` (PACKS + module_for + resolve_layout + scan_pacing/scan_duplicates dùng chung + suggest theo từ khóa cho 4 gói template qua `/api/suggest-pack`).
- **PIXEL 16-BIT** (gói gốc, id nội bộ `style2`/cảnh code): 8 cảnh code + 8 template Style2 — hành vi giữ nguyên 100%, job cũ mở/render y như trước.
- **STAGE** (tên cũ **test01**, đổi tên hiển thị 2026-10-27): 11 mẫu kinetic nền nâu đen (mục "Gói test01" ở trên vẫn đúng về code; id cảnh `t1:<key>` và payload `tpack: "test01"` cũ vẫn được chấp nhận — server tự hiểu là stage). Nhóm hiển thị: "STAGE — kinetic".
- **CRT** (10 mẫu, id `ct:`): terminal xanh lá phát sáng trên đen — decode_hook (headline scramble giải mã từng ký tự) · log_window (log [OK]/[..] + mốc thời gian) · glow_headline · ab_windows · log_list · odometer (số mono chạy) · process_grid · progress_blocks (khối █ + biến thể thanh nhiệt) · overclock (×2 ×3 + thanh nhiệt) · follow_end (con trỏ khối nhấp nháy). Font JetBrains Mono Bold (`fonts/JetBrainsMono-Bold.ttf`, đủ dấu VN + glyph khối). Quy ước: dòng log/lệnh không dấu, thông điệp chính có dấu. SFX tự tổng hợp `engine/crt_sfx.py` → `sfx-crt/` (type/beep/beep_hi/tick/alarm/enter/hum/scan). Code: `engine/crt_templates.py` + `engine/crt_scenes.py`.
- **PAPER** (10 mẫu, id `pp:`): giấy kem sáng, mực đen — note_hook (note vàng + quẹt dạ quang) · stamp_verdict (tem đỏ đóng + rung giấy) · notebook_demo (chữ viết tay hiện dần) · paper_ab · checklist (tích tay) · big_number_ink (số lớn + khoanh đỏ) · note_grid · progress_hand (tiến trình vẽ tay) · steps_up (bậc thang leo ý) · follow_end_paper (nút giấy THEO DÕI + mũi tên tay). Font viết tay Itim (`fonts/Itim-Regular.ttf`) + Noto Sans Black cho headline. SFX `engine/paper_sfx.py` → `sfx-paper/` (pop/draw/stamp/flip/tick/tape). Code: `engine/paper_templates.py` + `engine/paper_scenes.py`. Chuyển cảnh: lật trang ở đầu shot (nằm trong draw).
- **ZINE** (10 mẫu, id `zn:`): cắt dán tạp chí — mỗi từ 1 ô giấy (8 kiểu ô luân phiên font/màu: Noto Sans Black / Noto Serif / JetBrains Mono / Itim; nghiêng ±3°, bóng giấy, băng dính/đinh ghim) trên nền giấy báo mờ — tile_hook · verdict_tag (nhãn sao) · clipping_window (mẩu báo) · ab_clippings · pinned_list (bảng ghim) · price_number (nhãn giá) · tile_grid · ruler_progress · stack_combo (×N dán chồng) · poster_end (poster PHẦN 2). Font serif báo: `fonts/NotoSerif-Bold.ttf` + `NotoSerif-Black.ttf`. SFX `engine/zine_sfx.py` → `sfx-zine/` (paste/tear/pin/pop/stamp). Code: `engine/zine_templates.py` + `engine/zine_scenes.py`. Chuyển cảnh: xé giấy ở đầu shot. Biến thể ruột: ô tự xáo font/màu/góc theo seed của job+shot (`set_shot_context`) — cùng job render lại = cùng kết quả.
- **LỚP BIẾN THỂ CHỐNG TRÙNG KHUÔN** (stage/crt/paper/zine): mỗi mẫu có tham số **"Biến thể bố cục" (layout)** 2 biến thể (A = mặc định/bản gốc; B = đổi trục bố cục: căn trái thay vì giữa, khối chính trên↔dưới, hoán đổi panel...). Để trống = tool TỰ XOAY theo vị trí câu + seed của job (seed = crc32 của toàn bộ kịch bản → cùng job render lại ra cùng tổ hợp, job khác ra tổ hợp khác); điền 1/2 = khóa tay. Gói pixel: biến thể ở mức nền + màu nhấn vốn có sẵn (cảnh code có tham số riêng), không thêm layout để giữ hành vi cũ tuyệt đối.
- **Quét khi render (mọi gói):** log render luôn có dòng `[nhip]` (quét nhịp — đoạn >5s không biến cố hình ảnh thì cảnh báo; cảnh pixel/style2 đóng góp nhịp 2,5s/lần theo chu kỳ vẽ lại) và `[trung]` (quét trùng khuôn — chỉ 4 gói template: mẫu dùng >2 lần hoặc 1 biến thể của 1 mẫu lặp >3 lần trong 1 video thì cảnh báo).
- **GIF preview:** `previews/crt-<key>.gif`, `paper-<key>.gif`, `zine-<key>.gif` (480×270, ~2s) — sinh bằng `engine/make_pack_previews.py`.
- **Video mẫu kiểm chứng:** `crt-sample/crt-sample.mp4` (38,8s, nhạc 05-night-ledger) · `paper-sample/paper-sample.mp4` (34,6s, nhạc 10-credits-roll) · `zine-sample/zine-sample.mp4` (34,8s, nhạc 04-coin-rush) — mỗi thư mục có `render_sample.py` + frame trích từng mẫu + `scan.txt` (quét nhịp + quét trùng: đều ĐẠT).
