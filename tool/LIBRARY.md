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
