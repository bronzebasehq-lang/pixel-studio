#!/usr/bin/env python3
"""
PIXEL VIDEO - web server (Python chuan, khong can cai them web framework).
Mo http://localhost:8766 — giao dien 1 trang 3 cot dung mockup da duyet:
  Cot 1: dan kich ban -> tu cat cau -> dem cau.
  Cot 2: moi cau 1 the: chon mau canh (GIF preview DONG) + thoi gian uoc tinh.
  Cot 3: xem truoc + giong khoa am_adam + nhac nen + RENDER -> tien trinh
         -> mo video / mo thu muc Videos.
Du an RIENG cho kenh moi — khong dung chung code voi tool videos cu.
"""
import json
import os
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

import previews as previews_mod  # noqa: E402
import render as render_mod  # noqa: E402
import scenes as scenes_mod  # noqa: E402

PORT = 8766
VIDEOS_DIR = os.path.join(TOOL_DIR, "Videos")
MUSIC_DIR = os.path.join(TOOL_DIR, "Music")
FONTS_DIR = os.path.join(TOOL_DIR, "fonts")

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


PAGE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>PIXEL VIDEO — Tool video vẽ bằng code (Pixel 16-bit)</title>
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
main { display:grid; grid-template-columns: 30% 37% 33%; gap:14px; padding:14px 22px 26px; }
.panel { border:2px solid #584ca8; background:#181530; padding:14px; position:relative; }
.panel h2 { font-family:'VT323'; font-size:24px; color:#40c8dc; margin:0 0 10px; font-weight:normal; }
textarea { width:100%; height:300px; background:#100e28; color:#fff; border:1px solid #584ca8; padding:10px; font-size:15px; resize:vertical; }
.chips { margin:10px 0; }
.chip { display:inline-block; border:2px solid #40c8dc; color:#40c8dc; padding:4px 12px; margin-right:8px; font-family:'VT323'; font-size:19px; }
.note { color:#a8a8c8; font-size:13.5px; line-height:1.55; }
.card { border:2px solid #3a3570; background:#221f42; padding:10px; margin-bottom:12px; display:flex; gap:10px; }
.card img { width:176px; height:99px; image-rendering:pixelated; border:1px solid #584ca8; background:#000; }
.card .txt { font-size:14.5px; margin-bottom:6px; }
.card select, .row select, .row input { background:#100e28; color:#fff; border:1px solid #a8a8c8; padding:6px; font-size:14px; width:100%; }
.card .time { color:#a8a8c8; font-size:12.5px; margin-top:5px; }
label.lbl { font-family:'VT323'; font-size:20px; color:#40c8dc; display:block; margin:12px 0 5px; }
#previewBox { border:2px solid #584ca8; background:#000; }
#previewBox img { width:100%; display:block; image-rendering:pixelated; }
#previewCap { background:#04040a; color:#ffd84f; text-align:center; padding:7px 6px; font-size:14px; }
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
  <h1>PIXEL VIDEO <span class="tag">— tool video vẽ bằng code</span></h1>
  <p class="sub">Dán kịch bản → mỗi câu chọn 1 mẫu cảnh pixel vẽ bằng code → giọng cố định → Render. Không cần biết code.</p>
  <div class="lock"><b>PHONG CÁCH ĐÃ KHÓA: PIXEL 16-BIT</b> — lưới 320×180, phóng NEAREST, đổ bóng 2–3 tông + dithering. Mọi video từ tool này đều cùng 1 chất pixel.<br>
  <span class="c2">DỰ ÁN RIÊNG CHO KÊNH MỚI — tách biệt hẳn tool videos hiện tại.</span></div>
</header>
<main>
  <section class="panel">
    <h2>1 · KỊCH BẢN (dán chữ vào)</h2>
    <textarea id="script">You've seen the terms. LLM. R.A.G. AI Agent. MCP. System Prompt. Sounds like a PhD thesis. Sounds complicated.</textarea>
    <div class="chips"><span class="chip" id="chipCount">0 câu thoại</span><span class="chip" id="chipDur">~0 giây</span></div>
    <p class="note">Tool tự cắt kịch bản theo từng câu. Mỗi câu = 1 cảnh, thời lượng cảnh = đúng thời lượng giọng đọc câu đó.<br><br>
    Mẹo: muốn AI đọc đánh vần 1 thuật ngữ (ví dụ RAG) thì viết "R.A.G." trong kịch bản.<br><br>
    Thư viện mẫu cảnh hiện có: <b>8 mẫu</b> — Quả cầu nuốt cảnh · Cân so sánh · Mạng lưới node · Dòng thời gian · Rơi &amp; xếp chồng · Bản đồ hành trình · Cỗ máy vận hành · Người trong cảnh.<br><br>
    Mọi mẫu cảnh đều CÓ CHUYỂN ĐỘNG + HIỆU ỨNG (cầu lớn dần, cân nghiêng, node sáng lần lượt, bánh răng quay...). Không có cảnh tĩnh.</p>
  </section>
  <section class="panel">
    <h2>2 · TỪNG CÂU — CHỌN MẪU CẢNH</h2>
    <div id="cards"><p class="note">Đang tải...</p></div>
  </section>
  <section class="panel">
    <h2>3 · XEM TRƯỚC + RENDER</h2>
    <div id="previewBox"><img id="previewImg" src="/previews/scene-01.gif" alt="xem trước">
    <div id="previewCap">Xem trước động của mẫu cảnh đang chọn ở cột 2.</div></div>
    <label class="lbl">Giọng đọc (cố định):</label>
    <div class="row"><select id="voice" disabled><option>am_adam — giọng cố định của kênh</option></select></div>
    <label class="lbl">Định dạng:</label>
    <div class="row"><select id="fmt" disabled><option>Ngang 16:9 (1920×1080)</option></select></div>
    <label class="lbl">Nhạc nền:</label>
    <div class="row"><select id="music"><option value="">Không nhạc</option></select></div>
    <p class="note">Muốn dùng nhạc: chép file nhạc (.mp3/.wav) vào thư mục <b>Music</b> của tool rồi tải lại trang. Nhạc sẽ tự lặp + trộn nhỏ dưới giọng đọc.</p>
    <button id="renderBtn">▶ RENDER VIDEO</button>
    <div id="barWrap"><div id="bar"></div></div>
    <div id="status"></div>
    <div id="doneBox">
      <a id="openVideo" href="#" target="_blank">▶ Mở video</a>
      <a href="#" id="openFolder">📁 Mở thư mục Videos</a>
    </div>
  </section>
</main>
<script>
const SCENES = __SCENES_JSON__;
let sentences = [];
function splitScript(text){
  return text.split(/(?<=[.!?])\s+|\n+/).map(s=>s.trim()).filter(Boolean);
}
function estDur(txt){ return Math.max(1.2, txt.split(/\s+/).length / 2.67); }
function rebuild(){
  const ta = document.getElementById('script');
  sentences = splitScript(ta.value);
  document.getElementById('chipCount').textContent = sentences.length + ' câu thoại';
  const tot = sentences.reduce((a,s)=>a+estDur(s),0);
  document.getElementById('chipDur').textContent = '~' + Math.round(tot) + ' giây';
  const box = document.getElementById('cards');
  box.innerHTML = '';
  sentences.forEach((s, i) => {
    const def = SCENES[i % SCENES.length];
    const card = document.createElement('div'); card.className='card';
    card.innerHTML = '<img src="/previews/scene-0'+def.id+'.gif" alt="">' +
      '<div style="flex:1"><div class="txt"></div>' +
      '<select data-i="'+i+'"></select>' +
      '<div class="time">Ước tính ~'+estDur(s).toFixed(1)+'s · hiệu ứng: hiện dần + chuyển động riêng của mẫu</div></div>';
    card.querySelector('.txt').textContent = s;
    const sel = card.querySelector('select');
    SCENES.forEach(sc => {
      const o = document.createElement('option');
      o.value = sc.id; o.textContent = sc.id + ' · ' + sc.name;
      if (sc.id === def.id) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener('change', () => {
      card.querySelector('img').src = '/previews/scene-0'+sel.value+'.gif';
      document.getElementById('previewImg').src = '/previews/scene-0'+sel.value+'.gif';
    });
    card.querySelector('img').addEventListener('click', () => {
      document.getElementById('previewImg').src = '/previews/scene-0'+sel.value+'.gif';
    });
    box.appendChild(card);
  });
}
document.getElementById('script').addEventListener('input', rebuild);
fetch('/api/music').then(r=>r.json()).then(list=>{
  const sel = document.getElementById('music');
  list.forEach(f=>{ const o=document.createElement('option'); o.value=f; o.textContent=f; sel.appendChild(o); });
});
let poll = null;
document.getElementById('renderBtn').addEventListener('click', async () => {
  const cards = document.querySelectorAll('#cards select');
  const job = sentences.map((s,i)=>({text:s, scene:parseInt(cards[i].value)}));
  if (!job.length){ alert('Chưa có câu thoại nào.'); return; }
  const music = document.getElementById('music').value;
  const btn = document.getElementById('renderBtn');
  btn.disabled = true; btn.textContent = 'ĐANG RENDER...';
  document.getElementById('barWrap').style.display='block';
  document.getElementById('doneBox').style.display='none';
  await fetch('/api/render', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({sentences: job, music: music})});
  poll = setInterval(async () => {
    const st = await (await fetch('/api/status')).json();
    document.getElementById('bar').style.width = st.progress + '%';
    const stEl = document.getElementById('status');
    stEl.textContent = (st.log || []).slice(-6).join('\n');
    if (st.state === 'done'){
      clearInterval(poll); btn.disabled=false; btn.textContent='▶ RENDER VIDEO';
      document.getElementById('openVideo').href = '/videos/' + encodeURIComponent(st.video);
      document.getElementById('doneBox').style.display='block';
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
            scenes_json = json.dumps(
                [{"id": sid, "name": v[0], "desc": v[1]}
                 for sid, v in sorted(scenes_mod.SCENES.items())])
            self._send(200, PAGE.replace("__SCENES_JSON__", scenes_json))
        elif path == "/api/music":
            self._send(200, json.dumps(_music_files()), "application/json")
        elif path == "/api/status":
            with _job_lock:
                self._send(200, json.dumps(dict(_job)), "application/json")
        elif path.startswith("/previews/"):
            self._send_file(os.path.join(TOOL_DIR, path.lstrip("/")),
                            "image/gif")
        elif path.startswith("/fonts/"):
            self._send_file(os.path.join(FONTS_DIR, os.path.basename(path)),
                            "font/ttf")
        elif path.startswith("/videos/"):
            self._send_file(os.path.join(VIDEOS_DIR, os.path.basename(path)),
                            "video/mp4")
        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        if u.path == "/api/render":
            try:
                data = json.loads(raw.decode("utf-8"))
                sentences = [{"text": s["text"], "scene": int(s["scene"])}
                             for s in data["sentences"] if s["text"].strip()]
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
        elif u.path == "/api/open-videos":
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
    previews_mod.ensure_previews(log=lambda m: print(m, flush=True))
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = "http://localhost:%d" % PORT
    print("PIXEL VIDEO dang chay o %s (Ctrl+C de tat)" % url, flush=True)
    if not os.environ.get("PIXEL_NO_OPEN"):
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
