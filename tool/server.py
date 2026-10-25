#!/usr/bin/env python3
"""
PIXEL STUDIO V2 - web server (Python chuan, khong can web framework).
Mo http://localhost:8766 — giao dien 3 cot:
  Cot 1: dan kich ban -> tu cat cau -> TU GAN CANH theo noi dung
         (luat tu khoa chay offline, cong tac mac dinh BAT) + xem truoc
         kich ban co to mau manh moi.
  Cot 2: moi cau 1 the: GIF preview + nhan TU GAN + ly do + chip du kien
         + thanh do khop + o doi tay (doi tay khoa the) + nhan chu thich
         mui ten + chon anh nen lai.
  Cot 3: xem truoc + giong khoa am_adam + thu vien nhac retro + RENDER.
Du an RIENG cho kenh moi — khong dung chung code voi tool videos cu.
"""
import base64
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(TOOL_DIR, "engine")
sys.path.insert(0, ENGINE_DIR)

import autosuggest as auto_mod  # noqa: E402
import previews as previews_mod  # noqa: E402
import render as render_mod  # noqa: E402
import scenes as scenes_mod  # noqa: E402

PORT = 8766
VIDEOS_DIR = os.path.join(TOOL_DIR, "Videos")
MUSIC_DIR = os.path.join(TOOL_DIR, "music")
UPLOADS_DIR = os.path.join(TOOL_DIR, "uploads")
FONTS_DIR = os.path.join(TOOL_DIR, "fonts")
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")

_job = {"state": "idle", "progress": 0.0, "video": None, "error": None,
        "log": []}
_job_lock = threading.Lock()


def _job_log(msg):
    with _job_lock:
        _job["log"].append(msg)
        _job["log"] = _job["log"][-60:]
    print(msg, flush=True)


def _run_job(sentences, music_path):
    with _job_lock:
        _job.update(state="running", progress=0.0, video=None, error=None,
                    log=[])
    try:
        def prog(k):
            with _job_lock:
                _job["progress"] = round(k * 100, 1)
        out = render_mod.render_job(sentences, music_path=music_path,
                                    progress=prog, log=_job_log)
        with _job_lock:
            _job.update(state="done", progress=100.0,
                        video=os.path.basename(out))
    except Exception as e:  # bao loi LOUD len giao dien
        with _job_lock:
            _job.update(state="error", error=str(e))
        _job_log("[LOI] " + str(e))


def _music_files():
    os.makedirs(MUSIC_DIR, exist_ok=True)
    exts = (".mp3", ".wav", ".ogg", ".m4a", ".flac")
    return sorted(f for f in os.listdir(MUSIC_DIR)
                  if f.lower().endswith(exts))


def _library_items():
    """Doc library-catalog.json (thu vien style2 tu video Nokia).
    Thieu/hong file thi tra danh sach rong — khong duoc lam sap server."""
    try:
        with open(os.path.join(TOOL_DIR, "library-catalog.json"),
                  encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("items", [])
    except Exception:
        return []
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        out.append({"name": it.get("name", ""), "kind": it.get("kind", ""),
                    "group": it.get("group", ""), "tags": it.get("tags", ""),
                    "file": it.get("file", ""),
                    "preview": it.get("preview", "")})
    return out


PAGE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>PIXEL STUDIO V2.2 — Tự gán cảnh + mũi tên chú thích + nhạc retro</title>
<style>
@font-face { font-family:'VT323'; src:url('/fonts/VT323.ttf'); }
@font-face { font-family:'PS2P'; src:url('/fonts/PressStart2P.ttf'); }
* { box-sizing:border-box; }
body { margin:0; background:#0a091a; color:#eeeeF8; font-family:'Segoe UI',Arial,sans-serif; }
header { padding:16px 22px 6px; }
h1 { font-family:'PS2P'; font-size:20px; margin:0; color:#fff; display:inline; }
h1 .tag { font-family:'VT323'; font-size:22px; color:#ffd84f; }
.sub { color:#a8a8c8; margin:6px 0 10px; font-size:14px; }
.lock { border:2px solid #584ca8; background:#1e1a38; padding:8px 14px; font-size:13.5px; line-height:1.5; }
.lock b { color:#ffd84f; } .lock .c2 { color:#40c8dc; font-weight:bold; }
.lock .c3 { color:#46c878; font-weight:bold; }
main { display:grid; grid-template-columns: 30% 37% 33%; gap:14px; padding:14px 22px 26px; }
.panel { border:2px solid #584ca8; background:#181530; padding:14px; position:relative; }
.panel h2 { font-family:'VT323'; font-size:24px; color:#40c8dc; margin:0 0 10px; font-weight:normal; }
textarea { width:100%; height:270px; background:#100e28; color:#fff; border:1px solid #584ca8; padding:10px; font-size:15px; resize:vertical; }
.chips { margin:10px 0; }
.chip { display:inline-block; border:2px solid #40c8dc; color:#40c8dc; padding:4px 12px; margin-right:8px; font-family:'VT323'; font-size:19px; }
.chip.warn { border-color:#ff9d5c; color:#ff9d5c; }
.note { color:#a8a8c8; font-size:13.5px; line-height:1.55; }
.toggleRow { display:flex; align-items:center; gap:10px; margin:12px 0 4px; }
.toggleRow .tlbl { font-family:'VT323'; font-size:21px; color:#40c8dc; }
.switch { position:relative; width:56px; height:28px; flex:none; }
.switch input { opacity:0; width:0; height:0; }
.slider { position:absolute; inset:0; background:#2a2650; border:2px solid #584ca8; cursor:pointer; }
.slider:before { content:''; position:absolute; width:20px; height:20px; left:3px; top:2px; background:#5a548a; transition:.15s; }
.switch input:checked + .slider { background:#123d24; border-color:#46c878; }
.switch input:checked + .slider:before { transform:translateX(26px); background:#46c878; }
#toggleState { font-family:'VT323'; font-size:21px; color:#46c878; }
#hlPreview { border:1px solid #584ca8; background:#100e28; padding:10px 12px; margin-top:12px; font-size:14.5px; line-height:1.6; max-height:260px; overflow:auto; }
#hlPreview .snum { color:#a8a8c8; }
#hlPreview p { margin:0 0 8px; }
mark { background:none; font-weight:bold; padding:0 1px; }
.hl-pct { color:#ffd84f; } .hl-vs { color:#40c8dc; } .hl-step { color:#46c878; }
.hl-year { color:#ff9d5c; } .hl-num { color:#ffd84f; }
.card { border:2px solid #3a3570; background:#221f42; padding:10px; margin-bottom:12px; }
.card.manual { border-color:#ffd84f; }
.card.unassigned { border-color:#ff5d73; }
.card .top { display:flex; gap:10px; }
.card img.pv { width:176px; height:99px; image-rendering:pixelated; border:1px solid #584ca8; background:#000; flex:none; }
.card .txt { font-size:14.5px; margin-bottom:6px; }
.card select, .row select, .card input[type=text] { background:#100e28; color:#fff; border:1px solid #a8a8c8; padding:6px; font-size:14px; width:100%; }
.card .time { color:#a8a8c8; font-size:12.5px; margin-top:5px; }
.autoLbl { color:#46c878; font-weight:bold; font-size:13.5px; margin:4px 0 2px; }
.manualLbl { color:#ffd84f; font-weight:bold; font-size:13.5px; margin:4px 0 2px; }
.reason { color:#c8c8e8; font-size:13px; line-height:1.45; }
.fchips { margin:6px 0 2px; }
.fchip { display:inline-block; border:2px solid #40c8dc; color:#40c8dc; padding:2px 10px; margin:0 6px 4px 0; font-family:'VT323'; font-size:18px; }
.matchbar { margin:5px 0 2px; font-size:12.5px; color:#a8a8c8; }
.matchbar .cell { display:inline-block; width:17px; height:11px; margin-right:3px; background:#2a2650; border:1px solid #584ca8; vertical-align:middle; }
.matchbar .cell.on { background:#46c878; }
.warnTxt { color:#ff5d73; font-weight:bold; font-size:13.5px; margin:4px 0; }
.lowTxt { color:#ff9d5c; font-size:12.5px; }
.card .lbl2 { font-family:'VT323'; font-size:18px; color:#40c8dc; display:block; margin:9px 0 4px; }
.card .annotRow { display:flex; gap:8px; margin-top:4px; }
.card .annotRow input { flex:1.4; } .card .annotRow select { flex:1; }
.card .bgRow { display:flex; gap:8px; align-items:center; margin-top:6px; }
.card .bgRow .bgName { font-size:12.5px; color:#a8a8c8; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.card.active { border-color:#40c8dc; box-shadow:0 0 0 1px #40c8dc; }
.sceneRow { display:flex; gap:8px; align-items:center; margin-top:4px; }
.sceneRow .cur { flex:1; font-size:14px; color:#fff; background:#100e28; border:1px solid #584ca8; padding:7px 8px; }
#picker { position:fixed; inset:0; background:rgba(4,4,12,.85); display:none; z-index:50; }
#picker .box { max-width:1060px; margin:30px auto; background:#16143a; border:2px solid #40c8dc; padding:16px 18px; max-height:90vh; overflow:auto; }
#picker h3 { font-family:'VT323'; font-size:25px; color:#40c8dc; margin:0 0 4px; font-weight:normal; }
#pickerSent { color:#fff; font-size:14.5px; margin-bottom:10px; }
#pickerSearch { width:100%; background:#100e28; color:#fff; border:1px solid #a8a8c8; padding:9px; font-size:15px; box-sizing:border-box; }
.pchips { margin:10px 0 2px; }
.pchip { display:inline-block; border:2px solid #584ca8; color:#a8a8c8; padding:3px 12px; margin:0 6px 6px 0; font-family:'VT323'; font-size:18px; cursor:pointer; }
.pchip.on { border-color:#46c878; color:#46c878; }
#suggLbl { font-family:'VT323'; font-size:19px; color:#ffd84f; display:none; margin:8px 0 4px; }
#pickerSugg { display:none; gap:10px; margin:4px 0 12px; }
.suggItem { flex:1; max-width:330px; border:2px solid #ffd84f; padding:6px; cursor:pointer; background:#221f42; }
.suggItem img { width:100%; display:block; image-rendering:pixelated; }
.suggItem .sn { font-size:13.5px; margin-top:5px; }
.pgrid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-top:6px; }
.pitem { border:2px solid #3a3570; padding:6px; cursor:pointer; background:#221f42; }
.pitem:hover { border-color:#40c8dc; }
.pitem img { width:100%; display:block; image-rendering:pixelated; }
.pitem .sn { font-size:13.5px; margin-top:5px; }
.pitem .sg { font-size:12px; color:#a8a8c8; }
#pickerEmpty { color:#ff9d5c; font-size:14px; display:none; }
#pickerClose { margin-top:12px; }
#joinBox { margin-top:16px; border:2px solid #3a3570; padding:10px 12px; }
#joinBox h3 { font-family:'VT323'; font-size:21px; color:#40c8dc; margin:0 0 6px; font-weight:normal; }
#joinList label { display:block; font-size:14px; padding:3px 0; cursor:pointer; }
#joinList input { margin-right:8px; }
button#joinBtn { width:100%; background:#221f42; border:2px solid #40c8dc; color:#40c8dc; padding:11px; font-family:'PS2P'; font-size:12px; cursor:pointer; margin-top:8px; }
#joinStatus { font-size:13.5px; margin-top:7px; color:#c8c8e8; }
#joinStatus a { color:#46c878; }
button.mini { background:#221f42; border:2px solid #40c8dc; color:#40c8dc; padding:5px 10px; cursor:pointer; font-family:'VT323'; font-size:16px; flex:none; }
label.lbl { font-family:'VT323'; font-size:20px; color:#40c8dc; display:block; margin:12px 0 5px; }
#previewBox { border:2px solid #584ca8; background:#000; }
#previewBox img { width:100%; display:block; image-rendering:pixelated; }
#previewCap { background:#04040a; color:#ffd84f; text-align:center; padding:7px 6px; font-size:14px; }
#libBox { margin-top:16px; border:2px solid #3a3570; padding:10px 12px; }
#libBox h3 { font-family:'VT323'; font-size:21px; color:#40c8dc; margin:0 0 6px; font-weight:normal; }
#libGrid { display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; }
.libcell { border:2px solid #584ca8; background:#000; cursor:pointer; }
.libcell:hover { border-color:#ffd84f; }
.libcell img { width:100%; display:block; image-rendering:pixelated; aspect-ratio:16/9; object-fit:cover; }
.libcap { font-family:'VT323'; font-size:15px; color:#eeeeF8; text-align:center; padding:3px 2px 5px; }
button#renderBtn { width:100%; background:#46c878; border:none; padding:16px; font-family:'PS2P'; font-size:15px; cursor:pointer; margin-top:14px; }
button#renderBtn:disabled { background:#3a5a48; color:#9db8a8; cursor:wait; }
#barWrap { height:16px; border:2px solid #584ca8; margin-top:12px; display:none; }
#bar { height:100%; width:0%; background:repeating-linear-gradient(90deg,#40c8dc 0 10px,#2a9ab0 10px 20px); }
#status { font-size:13.5px; color:#a8a8c8; margin-top:8px; white-space:pre-wrap; max-height:150px; overflow:auto; }
#doneBox { display:none; margin-top:12px; }
#doneBox a { display:inline-block; margin-right:10px; background:#221f42; border:2px solid #40c8dc; color:#40c8dc; padding:9px 14px; text-decoration:none; font-family:'VT323'; font-size:19px; }
.err { color:#ff5d73 !important; }
</style>
</head>
<body>
<header>
  <h1>PIXEL STUDIO <span class="tag">— V2.2 · tool video vẽ bằng code</span></h1>
  <p class="sub">Dán kịch bản → tool TỰ GÁN cảnh theo nội dung từng câu → chỉnh tay nếu muốn → Render. Không cần biết code.</p>
  <div class="lock"><b>PHONG CÁCH ĐÃ KHÓA: PIXEL 16-BIT</b> — lưới 320×180, phóng NEAREST, đổ bóng 2–3 tông + dithering.<br>
  <span class="c3">MỚI Ở V2.2: THƯ VIỆN STYLE2 TỪ VIDEO NOKIA (30 ẢNH + 8 TEMPLATE CÓ GIF XEM TRƯỚC) · CHUẨN MIX KÊNH 16BIT_EXE.</span><br>
  <span class="c2">DỰ ÁN RIÊNG CHO KÊNH MỚI — tách biệt hẳn tool videos hiện tại.</span></div>
</header>
<main>
  <section class="panel">
    <h2>1 · KỊCH BẢN (dán chữ vào)</h2>
    <textarea id="script">It grew 300% in just 3 years. ChatGPT vs Claude: which one wins? First, connect the tools. Then the system runs itself.</textarea>
    <div class="toggleRow">
      <span class="tlbl">TỰ GÁN CẢNH THEO NỘI DUNG:</span>
      <label class="switch"><input type="checkbox" id="autoToggle" checked><span class="slider"></span></label>
      <span id="toggleState">BẬT</span>
    </div>
    <p class="note">Dán script xong, tool tự đọc từng câu và gán cảnh khớp nội dung (chạy 100% trên máy bạn, không gửi đi đâu). Gán chưa đúng ý thì đổi tay ở cột 2 — lựa chọn của bạn luôn thắng.</p>
    <div id="hlPreview"></div>
    <p class="note" style="margin-top:8px">Manh mối gán cảnh: <span class="hl-pct">■ số %/tăng</span> · <span class="hl-vs">■ so sánh</span> · <span class="hl-step">■ thứ tự bước</span> · <span class="hl-year">■ mốc năm</span></p>
    <div class="chips"><span class="chip" id="chipCount">0 câu thoại</span><span class="chip" id="chipAuto">0 / 0 đã TỰ GÁN</span><span class="chip" id="chipDur">~0 giây</span></div>
    <p class="note">Thư viện mẫu cảnh hiện có: <b>8 mẫu</b> — Quả cầu nuốt cảnh · Cân so sánh · Mạng lưới node · Dòng thời gian · Rơi &amp; xếp chồng · Bản đồ hành trình · Cỗ máy vận hành · Người trong cảnh.<br><br>
    Mọi mẫu cảnh đều CÓ CHUYỂN ĐỘNG + HIỆU ỨNG. Dữ kiện trích từ câu (số %, tên 2 phía, số năm...) được đưa thẳng vào hình khi render.</p>
  </section>
  <section class="panel">
    <h2>2 · TỪNG CÂU — TỰ GÁN CẢNH</h2>
    <div id="cards"><p class="note">Đang tải...</p></div>
  </section>
  <section class="panel">
    <h2>3 · XEM TRƯỚC + RENDER</h2>
    <div id="previewBox"><img id="previewImg" src="/previews/scene-01.gif" alt="xem trước">
    <div id="previewCap">Xem trước động của mẫu cảnh đang chọn ở cột 2.</div></div>
    <div id="libBox">
      <h3>THƯ VIỆN STYLE2 (TỪ VIDEO NOKIA)</h3>
      <div id="libGrid"></div>
      <p class="note" id="libNote">Đang tải thư viện...</p>
    </div>
    <label class="lbl">Giọng đọc (cố định):</label>
    <div class="row"><select id="voice" disabled><option>am_adam — giọng cố định của kênh</option></select></div>
    <label class="lbl">Định dạng:</label>
    <div class="row"><select id="fmt" disabled><option>Ngang 16:9 (1920×1080)</option></select></div>
    <label class="lbl">Nhạc nền (thư viện retro có sẵn):</label>
    <div class="row"><select id="music"><option value="">Không nhạc</option></select></div>
    <p class="note">11 bài nhạc chiptune 8/16-bit đã tích hợp sẵn trong tool — chọn 1 bài, nhạc tự lặp liền mạch hết video và nằm nhỏ dưới giọng đọc. Muốn thêm bài riêng: chép file .mp3 vào thư mục <b>music</b> của tool rồi tải lại trang.</p>
    <button id="renderBtn">▶ RENDER VIDEO</button>
    <div id="barWrap"><div id="bar"></div></div>
    <div id="status"></div>
    <div id="doneBox">
      <a id="openVideo" href="#" target="_blank">▶ Mở video</a>
      <a href="#" id="openFolder">📁 Mở thư mục Videos</a>
    </div>
    <div id="joinBox">
      <h3>NỐI VIDEO (ghép các khúc đã render)</h3>
      <p class="note">Render từng khúc ~30 giây rồi tick chọn các khúc theo đúng thứ tự (danh sách xếp theo tên file) và bấm NỐI. Chỉ nối được các video do chính tool này xuất ra.</p>
      <div id="joinList"></div>
      <button id="joinBtn">NỐI CÁC VIDEO ĐÃ CHỌN</button>
      <div id="joinStatus"></div>
    </div>
  </section>
</main>
<div id="picker">
  <div class="box">
    <h3>CHỌN MẪU CẢNH</h3>
    <div id="pickerSent"></div>
    <input id="pickerSearch" type="text" placeholder="Gõ tên cảnh hoặc từ khóa: sụp đổ, tiền, vs...">
    <div class="pchips" id="pickerGroups"></div>
    <div id="suggLbl">GỢI Ý CHO CÂU NÀY (bấm 1 cái là gán xong):</div>
    <div id="pickerSugg"></div>
    <div id="pickerGrid" class="pgrid"></div>
    <p id="pickerEmpty">Không tìm thấy cảnh nào khớp. Thử từ khóa khác hoặc chọn nhóm "Tất cả".</p>
    <button class="mini" id="pickerClose">Đóng (không đổi)</button>
  </div>
</div>
<script>
const SCENES = __SCENES_JSON__;
const TARGETS = ['Trên – trái','Trên – giữa','Trên – phải','Giữa – trái','Chính giữa','Giữa – phải','Dưới – trái','Dưới – giữa','Dưới – phải'];
let sentences = [];
let cardsState = [];
let analyzeSeq = 0;
let activeCard = 0;
let pickerCard = -1;
let pickerGroup = 'Tất cả';
function sceneById(id){ return SCENES.find(x => x.id === id); }
function sceneGif(id){ return '/previews/scene-0' + id + '.gif'; }
function setActive(i){
  activeCard = i;
  document.querySelectorAll('#cards .card').forEach((c, j) => c.classList.toggle('active', j === i));
  const st = cardsState[i];
  if (st && st.scene){
    document.getElementById('previewImg').src = sceneGif(st.scene);
    const sc = sceneById(st.scene);
    document.getElementById('previewCap').textContent = 'Câu ' + (i + 1) + ' · ' + (sc ? sc.name : '');
  }
}
function usageMap(){ try { return JSON.parse(localStorage.getItem('ps_usage') || '{}'); } catch(e){ return {}; } }
function bumpUsage(id){ const u = usageMap(); u[id] = (u[id] || 0) + 1; try { localStorage.setItem('ps_usage', JSON.stringify(u)); } catch(e){} }

function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function splitScript(text){
  return text.split(/(?<=[.!?])\s+|\n+/).map(s=>s.trim()).filter(Boolean);
}
function estDur(txt){ return Math.max(1.2, txt.split(/\s+/).length / 2.67); }
function autoOn(){ return document.getElementById('autoToggle').checked; }

function hlSentence(text, highlights){
  if (!highlights || !highlights.length) return esc(text);
  const hs = highlights.slice().sort((a,b)=>a.start-b.start);
  let out = '', pos = 0;
  hs.forEach(h => {
    if (h.start < pos || h.end > text.length) return;
    out += esc(text.slice(pos, h.start)) + '<mark class="' + h.cls + '">' + esc(text.slice(h.start, h.end)) + '</mark>';
    pos = h.end;
  });
  return out + esc(text.slice(pos));
}

function renderHlPreview(results){
  const box = document.getElementById('hlPreview');
  if (!autoOn()){ box.innerHTML = '<p class="note">Tự gán đang TẮT — bạn chọn cảnh tay cho từng câu ở cột 2.</p>'; return; }
  box.innerHTML = sentences.map((s,i) =>
    '<p><span class="snum">' + (i+1) + '.</span> ' + hlSentence(s, results && results[i] ? results[i].highlights : []) + '</p>'
  ).join('');
}

function barHTML(m){
  let s = '';
  for (let i=0;i<5;i++) s += '<span class="cell' + (i < m ? ' on' : '') + '"></span>';
  return s;
}

function renderCards(results){
  const box = document.getElementById('cards');
  box.innerHTML = '';
  const prev = cardsState;
  cardsState = sentences.map((s, i) => {
    const old = (prev[i] && prev[i].text === s) ? prev[i] : null;
    const st = old || { text:s, scene:null, source:'none', auto:null, label:'', target:4, bgFile:null, bgName:'' };
    st.text = s;
    if (!old){
      if (autoOn() && results && results[i]){
        st.auto = results[i];
        st.scene = results[i].scene;
        st.source = results[i].scene ? 'auto' : 'none';
      } else if (!autoOn()){
        const def = SCENES[i % SCENES.length];
        st.scene = def.id; st.source = 'default'; st.auto = null;
      }
    }
    return st;
  });
  let autoCount = 0;
  cardsState.forEach((st, i) => {
    const s = st.text;
    if (st.source === 'auto') autoCount++;
    const card = document.createElement('div');
    card.className = 'card' + (st.source === 'manual' ? ' manual' : '') + (st.scene ? '' : ' unassigned');
    card.addEventListener('click', (e) => {
      if (e.target.closest('input, select, button, textarea, a, label')) return;
      setActive(i);
    });
    const top = document.createElement('div'); top.className = 'top';
    const img = document.createElement('img'); img.className = 'pv';
    img.src = '/previews/scene-0' + (st.scene || 1) + '.gif';
    img.alt = '';
    img.addEventListener('click', () => { setActive(i); });
    const right = document.createElement('div'); right.style.flex = '1';
    const txt = document.createElement('div'); txt.className = 'txt'; txt.textContent = s;
    right.appendChild(txt);
    if (st.auto && st.source !== 'default'){
      if (st.source === 'auto'){
        const lb = document.createElement('div'); lb.className = 'autoLbl';
        lb.textContent = '■ TỰ GÁN: ' + st.auto.name;
        right.appendChild(lb);
        const rs = document.createElement('div'); rs.className = 'reason';
        rs.textContent = 'Lý do: ' + st.auto.reason;
        right.appendChild(rs);
        if (st.auto.chips && st.auto.chips.length){
          const ch = document.createElement('div'); ch.className = 'fchips';
          ch.innerHTML = st.auto.chips.map(c => '<span class="fchip">' + esc(c) + '</span>').join('');
          right.appendChild(ch);
        }
        const mb = document.createElement('div'); mb.className = 'matchbar';
        mb.innerHTML = 'Độ khớp manh mối: ' + barHTML(st.auto.match || 0) +
          (st.auto.low_match ? ' <span class="lowTxt">khớp thấp — nên kiểm tra lại</span>' : '');
        right.appendChild(mb);
      } else if (st.source === 'manual'){
        const lb = document.createElement('div'); lb.className = 'manualLbl';
        lb.textContent = '✎ ĐỔI TAY — lựa chọn của bạn đã khóa cho câu này';
        right.appendChild(lb);
      }
    }
    if (!st.scene){
      const w = document.createElement('div'); w.className = 'warnTxt';
      w.textContent = '⚠ CHƯA GÁN — câu này chưa có cảnh, hãy chọn tay bên dưới trước khi Render.';
      right.appendChild(w);
    }
    const selLbl = document.createElement('span'); selLbl.className = 'lbl2';
    selLbl.textContent = 'MẪU CẢNH (đổi tay ở đây):';
    right.appendChild(selLbl);
    const sRow = document.createElement('div'); sRow.className = 'sceneRow';
    const cur = document.createElement('div'); cur.className = 'cur';
    cur.textContent = st.scene ? (st.scene + ' · ' + ((sceneById(st.scene) || {}).name || '')) : '— chưa chọn cảnh —';
    const chBtn = document.createElement('button'); chBtn.className = 'mini'; chBtn.textContent = 'Đổi cảnh';
    chBtn.addEventListener('click', () => openPicker(i));
    sRow.appendChild(cur); sRow.appendChild(chBtn);
    right.appendChild(sRow);
    const tm = document.createElement('div'); tm.className = 'time';
    tm.textContent = 'Ước tính ~' + estDur(s).toFixed(1) + 's · hiệu ứng: hiện dần + chuyển động riêng của mẫu';
    right.appendChild(tm);
    top.appendChild(img); top.appendChild(right);
    card.appendChild(top);
    const aLbl = document.createElement('span'); aLbl.className = 'lbl2';
    aLbl.textContent = 'MŨI TÊN CHÚ THÍCH (tùy chọn):';
    card.appendChild(aLbl);
    const aRow = document.createElement('div'); aRow.className = 'annotRow';
    const aIn = document.createElement('input'); aIn.type = 'text';
    aIn.placeholder = 'Chữ nhãn — vd: 300% GROWTH (để trống = không chú thích)';
    aIn.value = st.label || '';
    aIn.addEventListener('input', () => { st.label = aIn.value; });
    const tSel = document.createElement('select');
    TARGETS.forEach((name, idx) => {
      const o = document.createElement('option');
      o.value = idx; o.textContent = 'Điểm chỉ tới: ' + name;
      tSel.appendChild(o);
    });
    tSel.value = String(st.target != null ? st.target : 4);
    tSel.addEventListener('change', () => { st.target = parseInt(tSel.value); });
    aRow.appendChild(aIn); aRow.appendChild(tSel);
    card.appendChild(aRow);
    const bLbl = document.createElement('span'); bLbl.className = 'lbl2';
    bLbl.textContent = 'ẢNH NỀN LAI (tùy chọn):';
    card.appendChild(bLbl);
    const bRow = document.createElement('div'); bRow.className = 'bgRow';
    const fIn = document.createElement('input'); fIn.type = 'file';
    fIn.accept = 'image/png,image/jpeg,image/webp'; fIn.style.display = 'none';
    const bBtn = document.createElement('button'); bBtn.className = 'mini';
    bBtn.textContent = st.bgFile ? 'Đổi ảnh nền' : 'Chọn ảnh PNG nền';
    const bName = document.createElement('span'); bName.className = 'bgName';
    bName.textContent = st.bgFile ? ('Đang dùng: ' + st.bgName + ' (nền ảnh thay cảnh code)') : 'Chưa có — đang dùng cảnh vẽ bằng code.';
    bBtn.addEventListener('click', () => fIn.click());
    fIn.addEventListener('change', async () => {
      const f = fIn.files[0]; if (!f) return;
      bName.textContent = 'Đang tải ảnh lên...';
      const dataUrl = await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
      const resp = await fetch('/api/upload-bg', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ name: f.name, data: dataUrl }) });
      const out = await resp.json();
      if (out.file){ st.bgFile = out.file; st.bgName = f.name; bName.textContent = 'Đang dùng: ' + f.name + ' (nền ảnh thay cảnh code)'; bBtn.textContent = 'Đổi ảnh nền'; }
      else { bName.textContent = 'Tải ảnh lỗi: ' + (out.error || 'không rõ'); }
    });
    bRow.appendChild(fIn); bRow.appendChild(bBtn); bRow.appendChild(bName);
    if (st.bgFile){
      const clr = document.createElement('button'); clr.className = 'mini'; clr.textContent = 'Bỏ ảnh nền';
      clr.addEventListener('click', () => { st.bgFile = null; st.bgName = ''; renderCards(null); });
      bRow.appendChild(clr);
    }
    card.appendChild(bRow);
    box.appendChild(card);
  });
  document.getElementById('chipCount').textContent = sentences.length + ' câu thoại';
  const ca = document.getElementById('chipAuto');
  ca.textContent = autoOn() ? (autoCount + ' / ' + sentences.length + ' đã TỰ GÁN') : 'Tự gán: TẮT';
  ca.className = 'chip' + (autoOn() && autoCount < sentences.length ? ' warn' : '');
  const tot = sentences.reduce((a,s)=>a+estDur(s),0);
  document.getElementById('chipDur').textContent = '~' + Math.round(tot) + ' giây';
  if (cardsState.length) setActive(Math.min(activeCard, cardsState.length - 1));
}

async function rebuild(){
  const ta = document.getElementById('script');
  sentences = splitScript(ta.value);
  const seq = ++analyzeSeq;
  let results = null;
  if (autoOn() && sentences.length){
    try {
      const r = await fetch('/api/analyze', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ sentences: sentences }) });
      const out = await r.json();
      if (seq !== analyzeSeq) return;
      results = out.results;
    } catch(e) { /* loi mang cuc bo: giu the khong tu gan */ }
  }
  if (seq !== analyzeSeq) return;
  renderHlPreview(results);
  renderCards(results);
}

let deb = null;
document.getElementById('script').addEventListener('input', () => {
  clearTimeout(deb); deb = setTimeout(rebuild, 350);
});
document.getElementById('autoToggle').addEventListener('change', () => {
  document.getElementById('toggleState').textContent = autoOn() ? 'BẬT' : 'TẮT';
  cardsState = [];
  rebuild();
});
fetch('/api/music').then(r=>r.json()).then(list=>{
  const sel = document.getElementById('music');
  list.forEach(f=>{ const o=document.createElement('option'); o.value=f; o.textContent=f; sel.appendChild(o); });
});
let poll = null;
document.getElementById('renderBtn').addEventListener('click', async () => {
  const missing = cardsState.findIndex(st => !st.scene);
  if (!cardsState.length){ alert('Chưa có câu thoại nào.'); return; }
  if (missing >= 0){
    alert('Câu ' + (missing+1) + ' chưa có cảnh. Hãy chọn mẫu cảnh cho câu đó ở cột 2 trước khi Render.');
    return;
  }
  const job = cardsState.map(st => {
    const item = { text: st.text, scene: st.scene };
    if (st.source === 'auto' && st.auto && st.auto.params && Object.keys(st.auto.params).length)
      item.params = st.auto.params;
    const lbl = (st.label || '').trim();
    if (lbl) item.annotation = { label: lbl, target: st.target != null ? st.target : 4 };
    if (st.bgFile) item.bg = st.bgFile;
    return item;
  });
  const music = document.getElementById('music').value;
  const btn = document.getElementById('renderBtn');
  btn.disabled = true; btn.textContent = 'ĐANG RENDER...';
  document.getElementById('barWrap').style.display='block';
  document.getElementById('doneBox').style.display='none';
  const resp = await fetch('/api/render', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({sentences: job, music: music})});
  if (!resp.ok){
    const e = await resp.json().catch(()=>({}));
    btn.disabled=false; btn.textContent='▶ RENDER VIDEO';
    alert('Không render được: ' + (e.error || resp.status));
    return;
  }
  poll = setInterval(async () => {
    const st = await (await fetch('/api/status')).json();
    document.getElementById('bar').style.width = st.progress + '%';
    const stEl = document.getElementById('status');
    stEl.textContent = (st.log || []).slice(-6).join('\n');
    if (st.state === 'done'){
      clearInterval(poll); btn.disabled=false; btn.textContent='▶ RENDER VIDEO';
      document.getElementById('openVideo').href = '/videos/' + encodeURIComponent(st.video);
      document.getElementById('doneBox').style.display='block';
      loadJoinList();
      stEl.textContent = 'XONG! Video: ' + st.video;
    } else if (st.state === 'error'){
      clearInterval(poll); btn.disabled=false; btn.textContent='▶ RENDER VIDEO';
      stEl.textContent = 'LỖI: ' + st.error; stEl.className='err';
    }
  }, 1200);
});
document.getElementById('openFolder').addEventListener('click', async (e) => {
  e.preventDefault(); await fetch('/api/open-videos', {method:'POST'});
});

// ===== BO CHON CANH MOI (tim kiem + nhom + top-3 goi y + luoi anh) =====
function openPicker(i){
  pickerCard = i; pickerGroup = 'Tất cả'; setActive(i);
  const st = cardsState[i];
  document.getElementById('pickerSent').textContent = 'Câu ' + (i + 1) + ': "' + st.text + '"';
  document.getElementById('pickerSearch').value = '';
  buildPickerGroups(); buildPickerSugg(); renderPickerGrid();
  document.getElementById('picker').style.display = 'block';
}
function closePicker(){ document.getElementById('picker').style.display = 'none'; pickerCard = -1; }
function buildPickerGroups(){
  const groups = ['Tất cả'].concat([...new Set(SCENES.map(x => x.group))]);
  const box = document.getElementById('pickerGroups'); box.innerHTML = '';
  groups.forEach(g => {
    const c = document.createElement('span'); c.className = 'pchip' + (g === pickerGroup ? ' on' : '');
    c.textContent = g;
    c.addEventListener('click', () => { pickerGroup = g; buildPickerGroups(); renderPickerGrid(); });
    box.appendChild(c);
  });
}
function buildPickerSugg(){
  const st = cardsState[pickerCard];
  const row = document.getElementById('pickerSugg');
  const lbl = document.getElementById('suggLbl');
  row.innerHTML = '';
  const top3 = (st && st.auto && st.auto.top3) ? st.auto.top3 : [];
  if (!top3.length){ row.style.display = 'none'; lbl.style.display = 'none'; return; }
  lbl.style.display = 'block'; row.style.display = 'flex';
  top3.forEach(t => {
    const it = document.createElement('div'); it.className = 'suggItem';
    const im = document.createElement('img'); im.src = sceneGif(t.scene); it.appendChild(im);
    const nm = document.createElement('div'); nm.className = 'sn'; nm.textContent = t.scene + ' · ' + t.name; it.appendChild(nm);
    const mb = document.createElement('div'); mb.className = 'matchbar'; mb.innerHTML = barHTML(t.match || 0); it.appendChild(mb);
    it.addEventListener('click', () => pickScene(t.scene));
    row.appendChild(it);
  });
}
function renderPickerGrid(){
  const q = document.getElementById('pickerSearch').value.trim().toLowerCase();
  const u = usageMap();
  const list = SCENES.filter(sc => (pickerGroup === 'Tất cả' || sc.group === pickerGroup) &&
    (!q || sc.name.toLowerCase().includes(q) || (sc.tags || '').includes(q)));
  list.sort((a, b) => ((u[b.id] || 0) - (u[a.id] || 0)) || (a.id - b.id));
  const grid = document.getElementById('pickerGrid'); grid.innerHTML = '';
  document.getElementById('pickerEmpty').style.display = list.length ? 'none' : 'block';
  list.forEach(sc => {
    const it = document.createElement('div'); it.className = 'pitem';
    const im = document.createElement('img'); im.src = sceneGif(sc.id); it.appendChild(im);
    const nm = document.createElement('div'); nm.className = 'sn'; nm.textContent = sc.id + ' · ' + sc.name; it.appendChild(nm);
    const gp = document.createElement('div'); gp.className = 'sg'; gp.textContent = 'nhóm: ' + sc.group; it.appendChild(gp);
    it.addEventListener('click', () => pickScene(sc.id));
    grid.appendChild(it);
  });
}
function pickScene(id){
  const st = cardsState[pickerCard]; if (!st) return;
  st.scene = id; st.source = 'manual'; bumpUsage(id);
  const idx = pickerCard; closePicker(); renderCards(null); setActive(idx);
}
document.getElementById('pickerSearch').addEventListener('input', renderPickerGrid);
document.getElementById('pickerClose').addEventListener('click', closePicker);
document.getElementById('picker').addEventListener('click', (e) => { if (e.target.id === 'picker') closePicker(); });

// ===== NOI VIDEO =====
async function loadJoinList(){
  const box = document.getElementById('joinList'); if (!box) return;
  try {
    const vids = await (await fetch('/api/videos')).json();
    box.innerHTML = vids.length ? '' : '<p class="note">Chưa có video nào trong thư mục Videos.</p>';
    vids.forEach(v => {
      const lb = document.createElement('label');
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.value = v.name; cb.className = 'joinChk';
      lb.appendChild(cb);
      lb.appendChild(document.createTextNode(v.name + ' (' + v.size_mb + ' MB)'));
      box.appendChild(lb);
    });
  } catch(e){}
}
document.getElementById('joinBtn').addEventListener('click', async () => {
  const files = [...document.querySelectorAll('.joinChk:checked')].map(x => x.value);
  const stEl = document.getElementById('joinStatus');
  if (files.length < 2){ stEl.textContent = 'Hãy tick ít nhất 2 video để nối.'; return; }
  stEl.textContent = 'Đang nối ' + files.length + ' video...';
  const resp = await fetch('/api/join', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({files: files})});
  const out = await resp.json().catch(() => ({}));
  if (out.ok){ stEl.innerHTML = 'NỐI XONG: <a href="/videos/' + encodeURIComponent(out.file) + '" target="_blank">' + out.file + '</a>'; loadJoinList(); }
  else stEl.textContent = 'Lỗi: ' + (out.error || resp.status);
});
loadJoinList();

// ===== THU VIEN STYLE2 (V2.2) =====
function showLibItem(it, src){
  document.getElementById('previewImg').src = src;
  document.getElementById('previewCap').textContent =
    'THƯ VIỆN: ' + it.name + ' (' + it.kind + ' · ' + it.group + ') — ' + it.tags;
}
fetch('/api/library').then(r => r.json()).then(list => {
  const grid = document.getElementById('libGrid');
  const note = document.getElementById('libNote');
  const shown = (list || []).filter(it => it.kind === 'template' || it.kind === 'image');
  if (!shown.length){ note.textContent = 'Thư viện trống.'; return; }
  note.textContent = shown.length + ' mục (template có GIF động, ảnh là nền style2) — bấm vào 1 mục để xem lớn ở hộp xem trước phía trên.';
  shown.forEach(it => {
    const cell = document.createElement('div'); cell.className = 'libcell';
    const src = '/' + (it.kind === 'template' ? (it.preview || it.file) : it.file);
    const img = document.createElement('img');
    img.src = src; img.alt = it.name; img.loading = 'lazy';
    const cap = document.createElement('div'); cap.className = 'libcap'; cap.textContent = it.name;
    cell.title = it.name + ' · ' + it.group + ' · ' + it.tags;
    cell.appendChild(img); cell.appendChild(cap);
    cell.addEventListener('click', () => showLibItem(it, src));
    grid.appendChild(cell);
  });
}).catch(() => { document.getElementById('libNote').textContent = 'Không tải được thư viện.'; });

rebuild();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, ctype):
        if not os.path.isfile(path):
            return self._send(404, "Not found", "text/plain")
        with open(path, "rb") as f:
            data = f.read()
        self._send(200, data, ctype)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(u.path)
        if path == "/":
            cat = {c["id"]: c for c in auto_mod.scene_catalog()}
            scenes_json = json.dumps(
                [{"id": sid, "name": v[0], "desc": v[1],
                  "group": cat.get(sid, {}).get("group", "Khác"),
                  "tags": cat.get(sid, {}).get("tags", "")}
                 for sid, v in sorted(scenes_mod.SCENES.items())])
            self._send(200, PAGE.replace("__SCENES_JSON__", scenes_json))
        elif path == "/api/music":
            self._send(200, json.dumps(_music_files()), "application/json")
        elif path == "/api/library":
            self._send(200, json.dumps(_library_items()), "application/json")
        elif path == "/api/videos":
            os.makedirs(VIDEOS_DIR, exist_ok=True)
            vids = []
            for name in sorted(os.listdir(VIDEOS_DIR)):
                if name.lower().endswith(".mp4"):
                    fp = os.path.join(VIDEOS_DIR, name)
                    vids.append({"name": name,
                                 "size_mb": round(os.path.getsize(fp) / 1048576.0, 1)})
            self._send(200, json.dumps(vids), "application/json")
        elif path == "/api/status":
            with _job_lock:
                self._send(200, json.dumps(dict(_job)), "application/json")
        elif path.startswith("/previews/"):
            self._send_file(os.path.join(TOOL_DIR, path.lstrip("/")),
                            "image/gif")
        elif path.startswith("/uploads/"):
            name = os.path.basename(path)
            ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
            self._send_file(os.path.join(UPLOADS_DIR, name), ctype)
        elif path.startswith("/fonts/"):
            self._send_file(os.path.join(FONTS_DIR, os.path.basename(path)),
                            "font/ttf")
        elif path.startswith("/videos/"):
            self._send_file(os.path.join(VIDEOS_DIR, os.path.basename(path)),
                            "video/mp4")
        else:
            self._send(404, "Not found", "text/plain")

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/analyze":
            try:
                data = self._read_json()
                texts = [str(x) for x in data.get("sentences", [])]
                results = [auto_mod.analyze(t) for t in texts]
                self._send(200, json.dumps({"results": results}),
                           "application/json")
            except Exception as e:
                self._send(400, json.dumps({"error": str(e)}),
                           "application/json")
        elif u.path == "/api/upload-bg":
            try:
                data = self._read_json()
                name = os.path.basename(str(data.get("name", "bg.png")))
                name = re.sub(r"[^A-Za-z0-9._-]", "_", name) or "bg.png"
                if not name.lower().endswith(IMG_EXTS):
                    raise ValueError("Chi nhan anh .png/.jpg/.webp")
                b64 = str(data.get("data", ""))
                if "," in b64[:64]:
                    b64 = b64.split(",", 1)[1]
                raw = base64.b64decode(b64)
                if len(raw) > 25 * 1024 * 1024:
                    raise ValueError("Anh qua lon (>25MB)")
                os.makedirs(UPLOADS_DIR, exist_ok=True)
                fname = "%d-%s" % (int(time.time()), name)
                with open(os.path.join(UPLOADS_DIR, fname), "wb") as f:
                    f.write(raw)
                self._send(200, json.dumps({"file": fname}),
                           "application/json")
            except Exception as e:
                self._send(400, json.dumps({"error": str(e)}),
                           "application/json")
        elif u.path == "/api/render":
            try:
                data = self._read_json()
                sentences = []
                for s in data["sentences"]:
                    if not str(s.get("text", "")).strip():
                        continue
                    if s.get("scene") in (None, ""):
                        raise ValueError(
                            "Co cau chua chon canh — hay chon tay truoc "
                            "khi Render")
                    item = {"text": str(s["text"]),
                            "scene": int(s["scene"])}
                    if isinstance(s.get("params"), dict) and s["params"]:
                        item["params"] = s["params"]
                    ann = s.get("annotation")
                    if isinstance(ann, dict) and str(
                            ann.get("label", "")).strip():
                        item["annotation"] = {
                            "label": str(ann["label"]).strip(),
                            "target": int(ann.get("target", 4))}
                    if s.get("bg"):
                        p = os.path.join(
                            UPLOADS_DIR, os.path.basename(str(s["bg"])))
                        if os.path.isfile(p):
                            item["bg"] = p
                    sentences.append(item)
                if not sentences:
                    raise ValueError("Kich ban rong")
                music = data.get("music") or ""
                music_path = (os.path.join(MUSIC_DIR, os.path.basename(music))
                              if music else None)
                if music_path and not os.path.isfile(music_path):
                    music_path = None
                with _job_lock:
                    if _job["state"] == "running":
                        return self._send(409, json.dumps(
                            {"error": "Dang co 1 video dang render"}),
                            "application/json")
                threading.Thread(target=_run_job,
                                 args=(sentences, music_path),
                                 daemon=True).start()
                self._send(200, json.dumps({"ok": True}), "application/json")
            except Exception as e:
                self._send(400, json.dumps({"error": str(e)}),
                           "application/json")
        elif u.path == "/api/join":
            try:
                data = self._read_json()
                names = [os.path.basename(str(x)) for x in data.get("files", [])]
                names = [n for n in names if n.lower().endswith(".mp4")]
                if len(names) < 2:
                    raise ValueError("Chon it nhat 2 video de noi")
                paths = []
                for n in names:
                    fp = os.path.join(VIDEOS_DIR, n)
                    if not os.path.isfile(fp):
                        raise ValueError("Khong thay file: " + n)
                    paths.append(fp)
                stamp = time.strftime("%Y%m%d-%H%M%S")
                out_name = "ghep-%s.mp4" % stamp
                out_path = os.path.join(VIDEOS_DIR, out_name)
                list_path = os.path.join(VIDEOS_DIR, "_join_list.txt")
                with open(list_path, "w", encoding="utf-8") as f:
                    for fp in paths:
                        f.write("file '%s'\n" % fp.replace("'", "'\\''"))
                r = subprocess.run(
                    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                     list_path, "-c", "copy", out_path],
                    capture_output=True, text=True, timeout=1200)
                os.remove(list_path)
                if r.returncode != 0 or not os.path.isfile(out_path):
                    tail = (r.stderr or "")[-600:]
                    raise ValueError(
                        "Noi that bai - cac file co the khac dinh dang. "
                        "Chi noi duoc cac video cung tu tool nay. " + tail)
                self._send(200, json.dumps({"ok": True, "file": out_name}),
                           "application/json")
            except Exception as e:
                self._send(400, json.dumps({"error": str(e)}),
                           "application/json")
        elif u.path == "/api/open-videos":
            self._read_json()
            os.makedirs(VIDEOS_DIR, exist_ok=True)
            try:
                if sys.platform.startswith("win"):
                    os.startfile(VIDEOS_DIR)  # noqa: S606
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", VIDEOS_DIR])
                else:
                    subprocess.Popen(["xdg-open", VIDEOS_DIR])
                self._send(200, json.dumps({"ok": True}), "application/json")
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}),
                           "application/json")
        else:
            self._send(404, "Not found", "text/plain")


def main():
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    previews_mod.ensure_previews(log=lambda m: print(m, flush=True))
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = "http://localhost:%d" % PORT
    print("PIXEL STUDIO V2 dang chay o %s (Ctrl+C de tat)" % url, flush=True)
    if not os.environ.get("PIXEL_NO_OPEN"):
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
