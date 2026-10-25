#!/usr/bin/env python3
"""STYLE2 TEMPLATES - thu vien mau canh trich tu video Nokia (Long #1, kenh 16bit_exe).

NGUON TRICH: ~/workspace/16bit-exe/video-01-nokia/render_seg1_style2.py ...
render_seg7_style2.py (7 file, phong cach "style2" Minh chot 23/10/2026:
ke chuyen so lieu, KHONG nhan vat dien, text GO TUNG KY TU, nen pixel
320x180 phong NEAREST len 1920x1080, font PressStart2P + VT323).

GHI CHU PIPELINE (da kiem tra lai trong code goc):
- Render noi bo o 10fps: ca 7 file seg deu dung DT = 0.1, xuat tung frame PNG.
  Buoc upscale/ghep len 30fps nam o khau ghep ffmpeg BEN NGOAI 7 file seg nay
  (khong co trong code trich tai day).
- Thoi luong shot = thoi luong voice + 0.55s, khap ca 7 file:
      DURS = [v + 0.55 for v in VOICE]
- Moi template o day la ham ve 1 frame: fn(t, dur, ...) -> anh RGBA 1920x1080,
  t = thoi gian trong shot (giay), dur = tong thoi luong shot.
  bg=None thi template tu dung nen mac dinh (grid hoac den tuy template).
- Module doc lap: chi phu thuoc PIL (+ math/random) nhu code goc.
  Font lay tu thu muc fonts/ cua tool (fallback ~/workspace/fonts).
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
if not (_FONT_DIR / "PressStart2P.ttf").exists():
    _FONT_DIR = Path("/home/hatch/workspace/fonts")
PS = str(_FONT_DIR / "PressStart2P.ttf")
VT = str(_FONT_DIR / "VT323.ttf")

W, H = 1920, 1080
WHITE = (255, 255, 255); BLACK = (0, 0, 0); YEL = (255, 205, 40)
RED = (255, 70, 70); CYAN = (70, 200, 255); GREEN = (64, 220, 110)
GREY = (150, 158, 175); ORANGE = (255, 140, 40); TEAL = (90, 240, 200)
NAVY = (10, 14, 30); DARK = (8, 10, 22)

# =====================================================================
# HELPER LOI (gop tu 7 file seg, lay ban day du nhat khi trung)
# =====================================================================

def load(p):
    """Mo anh -> RGB."""
    return Image.open(p).convert("RGB")

def to_frame(img):
    """Crop 16:9 giua anh, ha xuong 320x180 roi phong NEAREST len 1920x1080 (chuan pixel 16-bit cua kenh)."""
    w, h = img.size; t = 16 / 9
    if w / h > t:
        nw = int(h * t); x = (w - nw) // 2; img = img.crop((x, 0, x + nw, h))
    else:
        nh = int(w / t); y = (h - nh) // 2; img = img.crop((0, y, w, y + nh))
    return img.resize((320, 180), Image.LANCZOS).resize((W, H), Image.NEAREST).convert("RGBA")

def crop_frame(img, cx, cy, frac_w):
    """Zoom vao diem (cx, cy) (ti le 0..1) voi do rong frac_w cua anh goc, roi to_frame. (tu seg1)"""
    w, h = img.size
    zw = int(w * frac_w); zh = int(zw * 9 / 16)
    x0 = min(max(int(cx * w - zw / 2), 0), w - zw); y0 = min(max(int(cy * h - zh / 2), 0), h - zh)
    return img.crop((x0, y0, x0 + zw, y0 + zh)).resize((320, 180), Image.LANCZOS).resize((W, H), Image.NEAREST).convert("RGBA")

def darken(img, f):
    """Lam toi anh theo he so f (0..1). f>=0.999 tra ban COPY (tranh ve de len nen dung chung)."""
    if f >= 0.999: return img.copy()
    return Image.eval(img.convert("RGB"), lambda v: int(v * f)).convert("RGBA")

def blend(a, b, f):
    """Tron 2 anh theo he so f (0 = a, 1 = b). (tu seg1)"""
    return Image.blend(a.convert("RGB"), b.convert("RGB"), f).convert("RGBA")

# ---------- he thong go chu ----------

def layout_big(text, max_size=96):
    """Tra (size, [dong]) cho caption lon VT323, toi da 2 dong, rong <=1740."""
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    def fits(txt, s): return d.textlength(txt, font=ImageFont.truetype(VT, s)) <= 1740
    size = max_size
    while size > 84 and not fits(text, size): size -= 4
    if fits(text, size): return size, [text]
    words = text.split(); best = None
    for ci in range(1, len(words)):
        l1, l2 = " ".join(words[:ci]), " ".join(words[ci:])
        s2 = 100
        while s2 > 60 and not (fits(l1, s2) and fits(l2, s2)): s2 -= 4
        if fits(l1, s2) and fits(l2, s2):
            sc = abs(len(l1) - len(l2))
            if best is None or sc < best[0]: best = (sc, l1, l2, s2)
    if best is None: return 64, [text]
    return best[3], [best[1], best[2]]

def draw_typed(img, text, t, t0, t1, max_size=96, col=WHITE, y_base=None):
    """Go tung ky tu trong [t0,t1], con tro khoi nhap nhay o cuoi. Dung cho caption lon VT323."""
    if t < t0 or not text: return
    size, lines = layout_big(text, max_size)
    total = sum(len(l) for l in lines)
    prog = min(1.0, (t - t0) / max(0.05, t1 - t0))
    n = int(prog * total + 0.5)
    f = ImageFont.truetype(VT, size)
    d = ImageDraw.Draw(img)
    if y_base is None: y_base = 1064 - len(lines) * size - 6
    shown_lines = []
    left = n
    for l in lines:
        shown_lines.append(l[:max(0, left)]); left -= len(l)
    last_x, last_y = None, None
    for j, sl in enumerate(shown_lines):
        full = lines[j]
        tw_full = d.textlength(full, font=f)
        x0 = (W - tw_full) / 2
        if sl:
            d.text((x0, y_base + j * size), sl, font=f, fill=col, stroke_width=4, stroke_fill=BLACK)
        last_x = x0 + d.textlength(sl, font=f); last_y = y_base + j * size
    if prog < 1.0 and int(t * 2.4) % 2 == 0 and last_x is not None:
        d.rectangle([last_x + 8, last_y + 8, last_x + 8 + size * 0.42, last_y + size - 6], fill=col)

def chunks_timing(chunks, dur):
    """Chia thoi luong shot cho cac cum loi thoai theo so tu -> [(start, end, chunk)]."""
    total = sum(len(c.split()) for c in chunks)
    out, acc = [], 0
    for c in chunks:
        w = len(c.split())
        out.append((acc / total * dur, (acc + w) / total * dur, c)); acc += w
    return out

def typed_caption(img, timing, t):
    """Ve caption go chu theo timing cua chunks_timing tai thoi diem t."""
    for s, e, c in timing:
        if s <= t < e:
            draw_typed(img, c, t, s, e)
            return
    s, e, c = timing[-1]
    draw_typed(img, c, t, s, e)

def typed_ps(img, text, x, y, size, t, t0, t1, col=WHITE, center=False):
    """Go tung ky tu bang font PressStart2P trong [t0,t1], co con tro khoi nhap nhay."""
    if t < t0: return
    f = ImageFont.truetype(PS, size)
    prog = min(1.0, (t - t0) / max(0.05, t1 - t0))
    n = int(prog * len(text) + 0.5)
    shown = text[:n]
    d = ImageDraw.Draw(img)
    xx = x
    if center:
        xx = (W - d.textlength(text, font=f)) / 2
    if shown:
        d.text((xx, y), shown, font=f, fill=col, stroke_width=max(3, size // 18), stroke_fill=BLACK)
    if prog < 1.0 and int(t * 2.4) % 2 == 0:
        cx = xx + d.textlength(shown, font=f) + 10
        d.rectangle([cx, y + 6, cx + size * 0.55, y + size - 2], fill=col)

# ---------- thanh phan ve ----------

# tags: nhom=hieu-ung | VN: nhan dan, the nho, pop | EN: chip, label tag
def chip(img, text, x, y, col=CYAN, size=22, scale=1.0):
    """Nhan dan nho (hop navy vien mau) pop len anh. Gop 2 bien the chip cua seg1/2 va seg4-7."""
    f = ImageFont.truetype(PS, size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = d0.textlength(text, font=f)
    lay = Image.new("RGBA", (int(tw + 36), size + 32), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([0, 0, tw + 35, size + 31], fill=(8, 14, 30, 225), outline=col, width=3)
    ld.text((18, 14), text, font=f, fill=col)
    if scale != 1.0:
        lay = lay.resize((int(lay.width * scale), int(lay.height * scale)), Image.NEAREST)
    img.alpha_composite(lay, (int(x), int(y)))

# tags: nhom=hieu-ung | VN: dau moc do, dong dau | EN: stamp
def stamp(img, text, cx, cy, size=54, col=RED):
    """Con dau vien do xoay 8 do dong len giua diem (cx, cy). (ban seg4-7)"""
    f = ImageFont.truetype(PS, size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = d0.textlength(text, font=f)
    lay = Image.new("RGBA", (int(tw + 70), size + 54), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([4, 4, tw + 65, size + 49], outline=col, width=7)
    ld.text((35, 24), text, font=f, fill=col)
    rot = lay.rotate(8, expand=True, resample=Image.NEAREST)
    img.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))

# tags: nhom=nen | VN: luoi toa do, nen bieu do | EN: grid background
def grid_bg():
    """Nen navy + luoi toa do mo - nen chuan cho cac shot so lieu/bieu do. (tu seg2)"""
    img = Image.new("RGBA", (W, H), (10, 14, 30, 255))
    d = ImageDraw.Draw(img)
    for gx in range(100, 1821, 120):
        d.line([gx, 120, gx, 880], fill=(28, 38, 66), width=2)
    for gy in range(120, 881, 95):
        d.line([100, gy, 1820, gy], fill=(28, 38, 66), width=2)
    return img

def _panel(portrait, xy=(1000, 270), size=(810, 540)):
    """Dung panel chan dung pixel: nen navy + anh chan dung phong NEAREST + vien. (tu _panel cua seg4/5, tham so hoa anh)"""
    img = Image.new("RGBA", (W, H), (10, 14, 30, 255))
    src = portrait.convert("RGB").resize((270, 180), Image.LANCZOS).resize(size, Image.NEAREST).convert("RGBA")
    img.alpha_composite(src, xy)
    d = ImageDraw.Draw(img)
    d.rectangle([xy[0] - 4, xy[1] - 4, xy[0] + size[0] + 4, xy[1] + size[1] + 4], outline=(110, 130, 180), width=4)
    return img

# ---------- hieu ung canh ----------

_rng = random.Random(42)
DUST = [(_rng.uniform(0.30, 0.72), _rng.uniform(0.0, 1.0), _rng.uniform(14, 42), _rng.uniform(2, 5)) for _ in range(80)]
# tags: nhom=hieu-ung | VN: hat bui bay, long den | EN: dust particles
def dust(img, t, strength=1.0):
    """Hat bui vang bay len trong luong sang (ve tren lop phu RGBA). Ban seg1 - day du nhat."""
    d = ImageDraw.Draw(img, "RGBA")
    for (fx, ph, sp, sz) in DUST:
        y = ((ph + t * sp / H) % 1.0) * 780
        x = fx * W + math.sin(t * 0.7 + ph * 9) * 14
        a = int(150 * strength * (0.55 + 0.45 * math.sin(t * 2.1 + ph * 20)))
        if a > 8:
            d.ellipse([x, y, x + sz, y + sz], fill=(255, 225, 150, a))

# tags: nhom=hieu-ung | VN: khoi bay len | EN: smoke plume
def smoke(img, t, x0=1050, y0=430):
    """Cot khoi xam boc len tu diem (x0, y0), to dan mo dan. (tu seg5/6)"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for k in range(7):
        ph = ((t * 0.14 + k / 7) % 1.0)
        x = x0 + ph * 260 + math.sin(ph * 9 + k) * 30
        y = y0 - ph * 330
        r = 22 + ph * 90
        ld.ellipse([x - r, y - r * 0.62, x + r, y + r * 0.62], fill=(40, 40, 48, int(120 * (1 - ph))))
    img.alpha_composite(lay)

# tags: nhom=hieu-ung | VN: man hinh phat sang nhip | EN: screen glow pulse
def screen_glow(img, t, level=1.0):
    """Quang sang xanh nhip theo sin o vung man hinh giua khung (toa do theo canh phone-table seg1). (tu seg1)"""
    if level <= 0: return
    pulse = 0.75 + 0.25 * math.sin(t * 2.6)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for (box, aa) in [((520, 580, 1540, 920), 10), ((580, 610, 1480, 890), 14), ((650, 640, 1410, 860), 18)]:
        ld.ellipse(box, fill=(90, 200, 255, int(aa * pulse * level)))
    img.alpha_composite(lay)

# tags: nhom=hieu-ung | VN: lua nhap nhay, chay | EN: fire flicker glow
def flicker_glow(img, t):
    """Quang lua cam nhap nhay bat dinh (dung cho canh chay). (tu seg5)"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    a = int(16 + 12 * math.sin(t * 7.3) * math.sin(t * 3.1))
    ld.ellipse([420, 260, 1560, 760], fill=(255, 120, 30, max(6, a)))
    img.alpha_composite(lay)

# tags: nhom=hieu-ung | VN: nhieu song, vo hinh ngan | EN: glitch slices
def glitch(img, t, t0):
    """Xé ngang 3 dai anh trong 0.22s ke tu t0. Tra anh MOI (khong sua anh dau vao). (tu seg1)"""
    if not (t0 <= t <= t0 + 0.22): return img
    out = img.copy()
    for (y0, y1, dx) in [(300, 360, 26), (520, 566, -34), (700, 780, 18)]:
        strip = img.crop((0, y0, W, y1))
        out.paste(strip, (dx, y0))
    return out

# =====================================================================
# TEMPLATE (tham so hoa tu cac shot s*() cua 7 seg)
# =====================================================================

# tags: nhom=so-lieu | VN: bo dem so chay, dem tien, dem so luong | EN: counter, number count-up
def counter(t, dur, bg=None, label="SOLD:", target=126000000, fmt="{:,}",
            count_dur=1.3, t0=0.0, x=1190, y=610, col=YEL):
    """Bo dem so chay tu 0 -> target trong hop panel (label + so). Trich tu seg2 s5 (dem 126M) + counter_ps seg7."""
    img = bg.copy() if bg is not None else grid_bg()
    p = min(1.0, max(0.0, (t - t0) / max(0.05, count_dur)))
    num = int(target * p)
    lay = Image.new("RGBA", (760, 150), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([4, 4, 756, 146], fill=(8, 14, 30, 225), outline=WHITE, width=4)
    ld.text((28, 24), label, font=ImageFont.truetype(PS, 24), fill=WHITE)
    ld.text((28, 66), fmt.format(num), font=ImageFont.truetype(PS, 34), fill=col)
    img.alpha_composite(lay, (x, y))
    return img

# tags: nhom=so-lieu | VN: bieu do duong, tang truong, lao doc, sup do | EN: line chart, growth, collapse chart
def chart(t, dur, bg=None, points=None, col=RED, title=None, end_label=None,
          draw_frac=0.7, caption_chunks=None):
    """Bieu do duong ve dan theo thoi gian qua cac diem (x, y) toa do 1920x1080. Trich tu seg1 s5C (sup do) + seg2 s4 (di len)."""
    if points is None:
        points = [(220, 210), (520, 260), (820, 380), (1100, 540), (1400, 700), (1700, 800)]
    img = bg.copy() if bg is not None else grid_bg()
    d = ImageDraw.Draw(img)
    if title:
        d.text((100, 56), title, font=ImageFont.truetype(PS, 34), fill=WHITE)
    p = min(1.0, max(0.0, t / max(0.1, dur * draw_frac)))
    segf = p * (len(points) - 1)
    for i in range(len(points) - 1):
        if segf >= i + 1:
            d.line([points[i], points[i + 1]], fill=col, width=10)
        elif segf > i:
            fr = segf - i
            ex = points[i][0] + (points[i + 1][0] - points[i][0]) * fr
            ey = points[i][1] + (points[i + 1][1] - points[i][1]) * fr
            d.line([points[i], (ex, ey)], fill=col, width=10)
            d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=col, outline=WHITE, width=3)
            break
    if end_label and p >= 1.0:
        stamp(img, end_label, 1380, 185, 34, col=col)
    if caption_chunks:
        typed_caption(img, chunks_timing(caption_chunks, dur), t)
    return img

# tags: nhom=so-lieu | VN: thanh gia so sanh, gia ban vs doanh thu, thanh ngang | EN: price bars, comparison bars
def price_bars(t, dur, bg=None, bars=None, title="THE PRICE", caption_chunks=None):
    """Thanh ngang so sanh do lon (gia ban vs doanh thu...). bars = [{label, value_text, frac, col, at, grow}]. Trich tu seg7 s2."""
    if bars is None:
        bars = [
            {"label": "", "value_text": "EUR 5.44 BILLION", "frac": 0.154, "col": YEL, "at": 0.2, "grow": 1.6},
            {"label": "REVENUE IN 2007 ALONE:", "value_text": "EUR 51 BILLION", "frac": 1.0, "col": TEAL, "at": 2.2, "grow": 3.0},
        ]
    img = bg.copy() if bg is not None else grid_bg()
    d = ImageDraw.Draw(img)
    if title:
        typed_ps(img, title, 100, 60, 34, t, 0.2, 1.0, col=YEL)
    y = 250
    for b in bars:
        at = b.get("at", 0.2); grow = b.get("grow", 1.6)
        if b.get("label") and t >= at:
            typed_ps(img, b["label"], 140, y - 70, 26, t, at, at + 1.2, col=b["col"])
        p = min(1.0, max(0.0, (t - at) / max(0.05, grow)))
        wpx = int(1620 * b["frac"] * p)
        if wpx > 0:
            d.rectangle([140, y, 140 + wpx, y + 90], fill=b["col"])
        if t >= at + 0.4:
            vx = 140 + int(1620 * b["frac"]) + 30
            if vx + 500 > W: vx = 170
            typed_ps(img, b["value_text"], vx, y + 28, 26, t, at + 0.4, at + 1.3, col=b["col"])
        y += 270
    if caption_chunks:
        typed_caption(img, chunks_timing(caption_chunks, dur), t)
    return img

# tags: nhom=text | VN: the trich dan, cau noi noi tieng, memo | EN: quote card
def quote_card(attrib, lines_spec, chunks):
    """The trich dan: tra ve ham shot fn(t, dur). lines_spec = [(text, y, size, col, chunk_idx, delay)]. Nguyen ban tu seg5 (the memo Elop)."""
    def fn(t, dur):
        tim = chunks_timing(chunks, dur)
        img = Image.new("RGBA", (W, H), (8, 10, 22, 255))
        d = ImageDraw.Draw(img)
        d.text((120, 110), attrib, font=ImageFont.truetype(PS, 26), fill=(150, 160, 190))
        for (txt, y, size, col, cidx, delay) in lines_spec:
            if t >= tim[cidx][0] + delay:
                typed_ps(img, txt, 0, y, size, t, tim[cidx][0] + delay,
                         tim[cidx][0] + delay + max(0.8, len(txt) * 0.045), col=col, center=True)
        typed_caption(img, tim, t)
        return img
    return fn

# tags: nhom=so-lieu | VN: vong xoay tu than, khong app khong nguoi dung, vong lap chet | EN: death spiral, no apps no users loop
def death_spiral(t, dur, bg=None, label_a="NO APPS", label_b="NO USERS",
                 caption="A DEATH SPIRAL", t0=0.0, caption_at=None):
    """Vong cham xoay + 2 nhan doi nhau o tam + caption ket. Trich tu seg6 s5 (Lumia)."""
    img = bg.copy() if bg is not None else grid_bg()
    d = ImageDraw.Draw(img)
    cx, cy, r = 960, 400, 210
    for k in range(28):
        a = t * 0.9 + k * (2 * math.pi / 28)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED if k % 2 == 0 else GREY)
    typed_ps(img, label_a, 0, 330, 36, t, t0, t0 + 0.7, col=RED, center=True)
    typed_ps(img, label_b, 0, 396, 36, t, t0 + 0.6, t0 + 1.3, col=RED, center=True)
    ca = caption_at if caption_at is not None else t0 + 2.0
    if caption and t >= ca:
        typed_ps(img, caption, 0, 700, 40, t, ca, ca + 1.0, col=YEL, center=True)
    return img

# tags: nhom=text | VN: the dinh nghia, giai thich thuat ngu, osborne | EN: definition card, term explainer
def definition_card(t, dur, bg=None, title="THE OSBORNE EFFECT",
                    line1="ANNOUNCE THE FUTURE TOO EARLY -",
                    line2="KILL THE PRESENT BEFORE IT ARRIVES",
                    t_title=0.0, t_lines=1.5, caption_chunks=None):
    """The dinh nghia thuat ngu: tieu de vang go chu + 2 dong giai thich (trang/do). Trich tu seg6 s3 (Osborne effect)."""
    img = bg.copy() if bg is not None else Image.new("RGBA", (W, H), (8, 10, 22, 255))
    if t >= t_title:
        typed_ps(img, title, 0, 300, 54, t, t_title, t_title + 1.3, col=YEL, center=True)
    if t >= t_lines:
        typed_ps(img, line1, 0, 460, 28, t, t_lines, t_lines + 1.2, col=WHITE, center=True)
        typed_ps(img, line2, 0, 520, 28, t, t_lines + 1.0, t_lines + 2.2, col=RED, center=True)
    if caption_chunks:
        typed_caption(img, chunks_timing(caption_chunks, dur), t)
    return img

# tags: nhom=end-card | VN: man game over, ket thuc thua | EN: game over screen
def game_over(t, dur, bg=None, text="GAME OVER.", col=RED, size=84, caption_chunks=None):
    """Man den + chu GAME OVER go tung ky tu o giua. Trich tu seg7 s7."""
    img = bg.copy() if bg is not None else Image.new("RGBA", (W, H), (0, 0, 0, 255))
    typed_ps(img, text, 0, 470, size, t, 0.3, 1.6, col=col, center=True)
    if caption_chunks:
        typed_caption(img, chunks_timing(caption_chunks, dur), t)
    return img

# tags: nhom=end-card | VN: the ket thuc kenh, logo cuoi video | EN: end card, channel outro
def end_card(t, dur, bg=None, text="16BIT_EXE", col=CYAN, size=44):
    """The ket: nen den + ten kenh go chu o giua. Trich tu seg7 s15 (code goc ghi '16BIT.EXE' — da sua mac dinh thanh '16BIT_EXE', ten kenh dung la gach duoi, V2.2)."""
    img = bg.copy() if bg is not None else Image.new("RGBA", (W, H), (0, 0, 0, 255))
    typed_ps(img, text, 0, 500, size, t, 0.2, 1.4, col=col, center=True)
    return img
