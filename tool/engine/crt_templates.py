#!/usr/bin/env python3
"""CRT TEMPLATES - goi phong cach "CRT" (terminal may tinh co) cho Pixel Studio.

Theo mock crt-a1..a3 (~/workspace/pixel-tool-mockup/pack-ideas-v1/):
nen den xanh rat dam, chu JetBrains Mono xanh la phat sang (#33FF66),
diem nhan ho phach (#FFB000) + do canh bao (#FF3B30), vet quet ngang
(scanline), quang sang quanh chu. Quy uoc cua mock: dong lenh/log KHONG
dau tieng Viet, thong diep chinh CO dau.

Hieu ung rieng: giai ma scramble (ky tu loan -> chu that), go tung ky
tu + con tro khoi, nhap nhay canh bao, hard cut. Cam fade/zoom tinh.

Module ve thuan (chi PIL): moi ham fn(t, dur, p) -> RGBA 1280x720.
p = dict tham so CHUOI da merge + khoa tinh toan "_" o crt_scenes
(_layout: 0 = bien the A, 1 = bien the B).
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
JB = str(_FONT_DIR / "JetBrainsMono-Bold.ttf")     # mono dam, du dau + khoi
JBR = str(_FONT_DIR / "JetBrainsMono-Regular.ttf")  # mono thuong (log nho)
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

W, H = 1280, 720
BG_TOP = (4, 18, 8)
BG_BOT = (2, 8, 3)
GREEN = (51, 255, 102)        # #33FF66
GREEN_SOFT = (125, 255, 154)  # #7DFF9A
GREEN_DIM = (34, 140, 66)
AMBER = (255, 176, 0)         # #FFB000
RED = (255, 59, 48)           # #FF3B30
GREY = (90, 120, 96)

SCRAMBLE_CHARS = "#%&@$?/<>*+=01"


def _font(path, size):
    try:
        return ImageFont.truetype(path, int(size))
    except OSError:
        return ImageFont.truetype(FALLBACK, int(size))


_DUMMY = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def _tw(text, f):
    return _DUMMY.textlength(text, font=f)


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease_out_cubic(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def col_of(name, default=GREEN):
    cols = {"green": GREEN, "soft": GREEN_SOFT, "amber": AMBER,
            "red": RED, "dim": GREEN_DIM, "grey": GREY}
    return cols.get(str(name or "").strip().lower(), default)


# ------------------------------------------------------------------ nen
_BG = None


def bg():
    """Nen CRT: gradient xanh den + scanline + vignette (cache 1 lan)."""
    global _BG
    if _BG is not None:
        return _BG.copy()
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / float(H - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * k)
                  for i in range(3))
        d.line([(0, y), (W, y)], fill=c + (255,))
    for y in range(0, H, 3):                       # vet quet ngang
        d.line([(0, y), (W, y)], fill=(0, 0, 0, 46))
    rng = random.Random(4)
    for _ in range(500):                           # nhieu phoi quang nhe
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        d.point((x, y), fill=(80, 255, 140, rng.randint(4, 14)))
    vig = Image.new("L", (W, H), 0)                # toi 4 goc
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-260, -190, W + 260, H + 190], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    img = Image.composite(img, dark, vig.point(lambda v: 90 + v * 165 // 255))
    _BG = img
    return _BG.copy()


# ------------------------------------------------------------------ chu
def glow_text(img, text, x, y, size, col=GREEN, path=JB, anchor="la",
              glow=True):
    """Chu phat sang: lop mo (blur) mau chu o duoi + chu sac net o tren.
    (x, y) la goc tren-trai cua hop chu (anchor mac dinh 'la')."""
    if not text:
        return 0
    f = _font(path, size)
    tw = int(_tw(text, f))
    th = int(size * 1.45)
    lay = Image.new("RGBA", (tw + 24, th + 24), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.text((12, 8), text, font=f, fill=col + (255,))
    if glow:
        g = lay.filter(ImageFilter.GaussianBlur(7))
        img.alpha_composite(g, (int(x - 12), int(y - 8)))
        img.alpha_composite(g, (int(x - 12), int(y - 8)))
    img.alpha_composite(lay, (int(x - 12), int(y - 8)))
    return tw


def text_c(img, text, cy, size, col=GREEN, path=JB, cx=W / 2, glow=True):
    """Chu canh giua theo chieu ngang, tam doc cy. Tra chieu rong."""
    f = _font(path, size)
    tw = _tw(text, f)
    return glow_text(img, text, cx - tw / 2, cy - size / 2, size, col,
                     path, glow=glow)


def fit_size(text, max_w, start, min_size, path=JB):
    size = start
    while size > min_size:
        if _tw(text, _font(path, size)) <= max_w:
            return size
        size -= 4
    return min_size


def cursor_block(img, x, y, size, t, col=GREEN):
    """Con tro khoi nhap nhay tai (x, y) (diem tren-trai)."""
    if int(t * 2.2) % 2 == 0:
        d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + int(size * 0.62), y + int(size * 1.05)],
                    fill=col + (255,))


def typed_slice(text, t, t0, cps):
    """So ky tu da go xong tai thoi diem t (cps = ky tu/giay)."""
    if t < t0:
        return 0
    return min(len(text), int((t - t0) * cps) + 1)


def scramble_text(text, prog, seed=0):
    """Giai ma: prog 0..1 - cac ky tu lan luot khoa ve chu that tu trai,
    phan chua giai ma la ky tu loan mau (tra ve [(ky tu, da_giai_ma)])."""
    rng = random.Random(seed)
    n = len(text)
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            out.append((" ", True))
            continue
        th = (i + 1) / float(max(1, n))
        if prog >= th:
            out.append((ch, True))
        else:
            out.append((rng.choice(SCRAMBLE_CHARS), False))
    return out


def draw_scramble_line(img, text, cx, cy, size, t, t0, decode_dur, seed=0):
    """1 dong headline giai ma canh giua: phan da giai ma xanh sang,
    phan loan mau ho phach."""
    prog = clamp((t - t0) / max(0.05, decode_dur))
    parts = scramble_text(text, prog, seed)
    f = _font(JB, size)
    widths = [_tw(c, f) for c, _ in parts]
    total = sum(widths)
    x = cx - total / 2
    y = cy - size / 2
    lay = Image.new("RGBA", (int(total) + 48, int(size * 1.6) + 32),
                    (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    lx = 24
    for (c, done), wseg in zip(parts, widths):
        ld.text((lx, 12), c, font=f,
                fill=(GREEN if done else AMBER) + (255,))
        lx += wseg
    g = lay.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(g, (int(x - 24), int(y - 12)))
    img.alpha_composite(lay, (int(x - 24), int(y - 12)))
    return prog


def blocks_bar(img, x, y, w_cells, frac, cell_w=26, cell_h=30,
               col=GREEN, empty=(16, 52, 26)):
    """Thanh tien trinh bang o khoi [████░░] ve bang hinh chu nhat."""
    d = ImageDraw.Draw(img)
    lit = int(round(w_cells * clamp(frac)))
    for i in range(w_cells):
        cx0 = x + i * (cell_w + 4)
        c = col if i < lit else empty
        d.rectangle([cx0, y, cx0 + cell_w, y + cell_h], fill=c + (255,))


def window_frame(img, x0, y0, x1, y1, title, t, col=GREEN):
    """Khung cua so terminal: vien + thanh tieu de + 3 o vuong goc phai."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                        fill=(3, 14, 6, 255), outline=col, width=3)
    d.rounded_rectangle([x0, y0, x1, y0 + 46], radius=10, fill=(6, 30, 12, 255))
    d.rectangle([x0, y0 + 24, x1, y0 + 46], fill=(6, 30, 12, 255))
    d.line([(x0, y0 + 46), (x1, y0 + 46)], fill=col + (255,), width=2)
    if title:
        d.text((x0 + 18, y0 + 12), title, font=_font(JBR, 24),
               fill=GREEN_SOFT + (255,))
    for i, c in enumerate([RED, AMBER, GREEN]):
        bx = x1 - 34 - (2 - i) * 32
        d.rectangle([bx, y0 + 13, bx + 18, y0 + 31], outline=c + (255,),
                    width=2)


def fx_glitch_cut(img, t, t0=0.0, dur=0.14):
    """Giat cat ngang dau shot (chuyen canh kieu CRT): lech dai anh."""
    if not (t0 <= t < t0 + dur):
        return img
    out = img.copy()
    k = 1.0 - (t - t0) / dur
    for (y0, y1, dx) in [(140, 190, 26), (380, 430, -34), (560, 620, 18)]:
        strip = img.crop((0, y0, W, y1))
        out.paste(strip, (int(dx * k), y0))
    return out


def fx_static(img, t, dur_shot, head=0.30, tail=0.28):
    """Nhieu mat song (static burst) o dau va cuoi shot - chi khi
    nguoi dung chon fx=static: tuyet nhieu trang/xanh + vai dai ngang
    loan, manh nhat o mep thoi gian roi tan dan."""
    if t < head:
        k = 1.0 - t / head
    elif t > dur_shot - tail:
        k = (t - (dur_shot - tail)) / tail
    else:
        return img
    if k <= 0.02:
        return img
    out = img.copy()
    d = ImageDraw.Draw(out, "RGBA")
    rng = random.Random(int(t * 24) * 7919 + 13)
    n = int(2600 * k)
    for _ in range(n):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        v = rng.randint(90, 255)
        col = (v, v, v) if rng.random() < 0.6 else (120, 255, 160)
        d.point((x, y), fill=col + (int(200 * k),))
    for _ in range(int(7 * k) + 1):
        y = rng.randint(0, H - 8)
        d.rectangle([0, y, W, y + rng.randint(2, 6)],
                    fill=(220, 230, 220, int(90 * k)))
    return out


def _lay(p):
    return int(p.get("_layout", 0))


# =====================================================================
# 11. ALERT WARN - canh bao do nhap nhay toan khung (mau moi V2.6)
# =====================================================================
def alert_warn(t, dur, p):
    img = bg()
    lay = _lay(p)
    d = ImageDraw.Draw(img)
    blink_on = int(t * 2.4) % 2 == 0
    # soc hazard tren/duoi
    for x in range(-40, W, 56):
        col = RED if blink_on else (150, 40, 34)
        d.polygon([(x, 0), (x + 28, 0), (x + 14, 30), (x - 14, 30)],
                  fill=col + (255,))
        d.polygon([(x, H), (x + 28, H), (x + 14, H - 30), (x - 14, H - 30)],
                  fill=col + (255,))
    # khung vien do nhap nhay
    bw = 6 if blink_on else 3
    d.rectangle([26, 44, W - 26, H - 44], outline=RED + (255,), width=bw)
    head = p["head"]
    if blink_on or t < 0.4:
        size = fit_size(head, 1120, 120, 52)
        text_c(img, head, 190, size, RED, JB)
    else:
        size = fit_size(head, 1120, 120, 52)
        text_c(img, head, 190, size, (170, 50, 44), JB)
    if p["sub"]:
        n = typed_slice(p["sub"], t, 0.7, 30)
        if n > 0:
            x = 110 if lay == 1 else W / 2 - _tw(p["sub"][:n],
                                                 _font(JBR, 40)) / 2
            glow_text(img, p["sub"][:n], x, 268, 40, AMBER, JBR)
    lines = [x.strip() for x in p["lines"].split("|") if x.strip()]
    for i, ln in enumerate(lines[:4]):
        at = 1.1 + i * 0.4
        if t < at:
            continue
        y = 356 + i * 62
        glow_text(img, "[!]", 110, y, 38, RED, JB, glow=False)
        glow_text(img, ln, 190, y, 38, GREEN_SOFT, JBR, glow=False)
    if lay == 1:
        glow_text(img, "muc do: NGHIEM TRONG", 110, 640, 30, RED, JB,
                  glow=False)
    return img


# =====================================================================
# 1. DECODE HOOK - dong lenh + headline giai ma scramble (mock a1)
# =====================================================================
def decode_hook(t, dur, p):
    img = bg()
    lay = _lay(p)
    cmd = "> " + p["cmd"]
    cy_cmd = 96 if lay == 0 else 560
    n = typed_slice(cmd, t, 0.15, 26)
    tw = glow_text(img, cmd[:n], 70, cy_cmd, 40, GREEN, JBR)
    if n < len(cmd) or t < 1.0:
        cursor_block(img, 70 + tw + 10, cy_cmd + 2, 40, t)
    head = p["head"]
    size = fit_size(head, 1180, 118, 54)
    lines = [head]
    if _tw(head, _font(JB, size)) > 1180:
        words = head.split()
        lines, cur = [], ""
        f = _font(JB, size)
        for w_ in words:
            trial = (cur + " " + w_).strip()
            if _tw(trial, f) <= 1180 or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w_
        lines.append(cur)
    cx = W / 2 if lay == 0 else 660
    y0 = 300 if lay == 0 else 240
    prog = 0.0
    for j, ln in enumerate(lines[:2]):
        prog = draw_scramble_line(img, ln, cx, y0 + j * int(size * 1.25),
                                  size, t, 0.55, 1.25, seed=j * 7 + 3)
    by = 596 if lay == 0 else 470
    _lw = glow_text(img, "GIAI MA: %d%%" % int(prog * 100), 70, by, 34,
                    AMBER, JB)
    blocks_bar(img, 70 + int(_lw) + 26, by + 2, 18, prog, cell_w=24,
               cell_h=30, col=AMBER)
    if p["sub"]:
        if t > 0.9:
            glow_text(img, "> " + p["sub"], 70, by - 64, 30, GREEN_DIM, JBR)
    return img


# =====================================================================
# 2. LOG WINDOW - cua so log [OK]/[..] + thanh khoi (mock a2)
# =====================================================================
def _status_col(st):
    return {"OK": GREEN, "RUN": AMBER, "..": AMBER, "X": RED,
            "ERR": RED}.get(st.strip().upper(), GREEN_SOFT)


def _parse_log_lines(p):
    out = []
    statuses = [s.strip() for s in p["statuses"].split(",")]
    for i, raw in enumerate([x for x in p["lines"].split("|")]):
        parts = [q.strip() for q in raw.split("::")]
        tm = parts[0] if len(parts) > 1 else "00:%02d" % (i + 1)
        txt = parts[1] if len(parts) > 1 else parts[0]
        st = statuses[i] if i < len(statuses) else "OK"
        out.append((tm, st, txt))
    return out


def log_window(t, dur, p):
    img = bg()
    lay = _lay(p)
    x0, y0, x1, y1 = (70, 70, 1210, 650) if lay == 0 else (150, 96, 1130, 624)
    window_frame(img, x0, y0, x1, y1, p["title"], t)
    lines = _parse_log_lines(p)
    starts = p["_starts"]
    d = ImageDraw.Draw(img)
    for i, (tm, st, txt) in enumerate(lines[:7]):
        if t < starts[i]:
            continue
        y = y0 + 84 + i * 62
        glow_text(img, tm, x0 + 34, y, 32, GREEN_DIM, JBR, glow=False)
        glow_text(img, "[%s]" % st, x0 + 170, y, 32, _status_col(st), JB,
                  glow=False)
        n = typed_slice(txt, t, starts[i], 34)
        glow_text(img, txt[:n], x0 + 330, y, 32, GREEN_SOFT, JBR, glow=False)
    pct = float(p["_pct"])
    fill = clamp((t - 0.4) / max(0.4, dur * 0.4))
    glow_text(img, "> dang chay kiem tra ...", x0 + 34, y1 - 118, 28,
              GREEN_DIM, JBR, glow=False)
    blocks_bar(img, x0 + 34, y1 - 72, 30, pct / 100.0 * fill,
               cell_w=22, cell_h=26, col=GREEN)
    glow_text(img, "%d%%" % int(pct * fill), x0 + 34 + 30 * 26 + 26,
              y1 - 74, 32, AMBER, JB, glow=False)
    return img


# =====================================================================
# 3. GLOW HEADLINE - chu lon phat sang + dong phu go chu
# =====================================================================
def glow_headline(t, dur, p):
    img = bg()
    lay = _lay(p)
    d = ImageDraw.Draw(img)
    cx = W / 2 if lay == 0 else 640
    x_text = 70 if lay == 1 else None
    if p["small"]:
        if lay == 0:
            text_c(img, p["small"], 168, 42, GREEN_SOFT, JBR)
        else:
            glow_text(img, p["small"], 70, 120, 42, GREEN_SOFT, JBR)
    size = fit_size(p["big"], 1160, 128, 56)
    if lay == 0:
        text_c(img, p["big"], 330, size, GREEN, JB)
    else:
        f = _font(JB, size)
        glow_text(img, p["big"], 70, 330 - size / 2, size, GREEN, JB)
    if p["big2"]:
        size2 = fit_size(p["big2"], 1160, 128, 56)
        col2 = col_of(p["big2_col"], AMBER)
        if lay == 0:
            if t >= 0.55:
                text_c(img, p["big2"], 330 + int(size * 1.2), size2, col2, JB)
        else:
            if t >= 0.55:
                glow_text(img, p["big2"], 70, 330 + int(size * 0.7), size2,
                          col2, JB)
    if p["sub"]:
        n = typed_slice(p["sub"], t, 1.0, 30)
        if n > 0:
            if lay == 0:
                f = _font(JBR, 36)
                tw = _tw(p["sub"][:n], f)
                glow_text(img, p["sub"][:n], cx - tw / 2, 560, 36,
                          GREEN_SOFT, JBR)
                cursor_block(img, cx + tw / 2 + 8, 562, 36, t)
            else:
                tw = glow_text(img, p["sub"][:n], 70, 560, 36, GREEN_SOFT,
                               JBR)
                cursor_block(img, 70 + tw + 8, 562, 36, t)
    # khung HUD 4 goc
    m, L = 36, 44
    for (gx, gy, sx, sy) in [(m, m, 1, 1), (W - m, m, -1, 1),
                             (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        d.line([(gx, gy), (gx + sx * L, gy)], fill=GREEN_DIM + (255,),
               width=3)
        d.line([(gx, gy), (gx, gy + sy * L)], fill=GREEN_DIM + (255,),
               width=3)
    return img


# =====================================================================
# 4. AB WINDOWS - 2 cua so: trai mo tinh vs phai sang day du
# =====================================================================
def ab_windows(t, dur, p):
    img = bg()
    lay = _lay(p)
    text_c(img, p["head"], 76, 44, GREEN, JB)
    swapped = (lay == 1)
    lx, rx = (70, 680) if not swapped else (680, 70)
    # cua so mo (A): dong log dung yen, xam xanh
    if t >= 0.35:
        window_frame(img, lx, 150, lx + 530, 560, p["title_a"], t,
                     col=GREEN_DIM)
        d = ImageDraw.Draw(img)
        rng = random.Random(11)
        for i in range(6):
            yy = 226 + i * 52
            wseg = rng.randint(180, 380)
            d.rectangle([lx + 30, yy, lx + 30 + wseg, yy + 16],
                        fill=(24, 66, 34, 255))
        glow_text(img, "NO SIGNAL ...", lx + 30, 500, 30, GREEN_DIM, JBR,
                  glow=False)
    # cua so sang (B): noi dung chay
    if t >= 0.75:
        window_frame(img, rx, 150, rx + 530, 560, p["title_b"], t, col=GREEN)
        lines = [x for x in p["lines_b"].split("|")]
        for i, ln in enumerate(lines[:6]):
            st = 0.95 + i * 0.16
            if t < st:
                continue
            n = typed_slice(ln, t, st, 40)
            glow_text(img, ln[:n], rx + 30, 218 + i * 52, 29, GREEN_SOFT,
                      JBR, glow=False)
    if t >= 1.05:
        d = ImageDraw.Draw(img)
        d.ellipse([592, 307, 688, 403], fill=(2, 10, 4, 255),
                  outline=AMBER, width=3)
        f = _font(JB, 30)
        d.text((640 - _tw("VS", f) / 2, 340), "VS", font=f,
               fill=AMBER + (255,))
    la_x = lx + 265 if not swapped else rx + 265
    lb_x = rx + 265 if not swapped else lx + 265
    if t >= 1.15:
        f = _font(JB, 32)
        tw = _tw(p["label_a"], f)
        glow_text(img, p["label_a"], la_x - tw / 2, 584, 32, GREY, JB,
                  glow=False)
    if t >= 1.3:
        f = _font(JB, 32)
        tw = _tw(p["label_b"], f)
        glow_text(img, p["label_b"], lb_x - tw / 2, 584, 32, GREEN, JB,
                  glow=False)
    return img


# =====================================================================
# 5. LOG LIST - danh sach [OK] hien dan toan khung
# =====================================================================
def log_list(t, dur, p):
    img = bg()
    lay = _lay(p)
    cmd = "> " + p["cmd"]
    n = typed_slice(cmd, t, 0.12, 30)
    glow_text(img, cmd[:n], 70, 64, 38, GREEN, JBR)
    items = _parse_log_lines(p)
    starts = p["_starts"]
    x_txt = 380 if lay == 0 else 300
    for i, (tm, st, txt) in enumerate(items[:7]):
        if t < starts[i]:
            continue
        y = 168 + i * 68
        glow_text(img, tm, 70, y, 34, GREEN_DIM, JBR, glow=False)
        glow_text(img, "[%s]" % st, 190, y, 34, _status_col(st), JB,
                  glow=False)
        glow_text(img, txt, x_txt, y, 36, GREEN_SOFT, JB, glow=False)
        if st.strip().upper() in ("..", "RUN") and int(t * 2.2) % 2 == 0:
            cursor_block(img, x_txt + int(_tw(txt, _font(JB, 36))) + 14,
                         y + 2, 34, t, AMBER)
    return img


# =====================================================================
# 6. ODOMETER - so mono chay tang, chu so cuoi loan den khi dung
# =====================================================================
def odometer(t, dur, p):
    img = bg()
    lay = _lay(p)
    target = float(p["_target"])
    cd = float(p["_count_dur"])
    pr = ease_out_cubic((t - 0.25) / max(0.05, cd))
    val = target * pr
    txt = "{:,.0f}".format(val).replace(",", ".")
    size = fit_size(txt, 1100, 170, 70)
    cy = 268 if lay == 0 else 210
    if lay == 0:
        text_c(img, txt, cy, size, GREEN, JB)
    else:
        glow_text(img, txt, 90, cy - size / 2, size, GREEN, JB)
    # chu so cuoi scramble nhe khi dang chay
    if pr < 0.98 and t > 0.3:
        rng = random.Random(int(t * 14))
        ch = rng.choice("0123456789")
        f = _font(JB, size)
        tw = _tw(txt, f)
        x_last = (W / 2 - tw / 2 if lay == 0 else 90) + tw - _tw(txt[-1], f)
        glow_text(img, ch, x_last, cy - size / 2, size, AMBER, JB)
    d = ImageDraw.Draw(img)
    for i in range(41):                            # thuoc tick duoi so
        x = 190 + i * 22
        hh = 26 if i % 5 == 0 else 13
        d.line([(x, 420), (x, 420 + hh)], fill=GREEN_DIM + (255,), width=3)
    if t >= 0.25 + cd * 0.5:
        glow_text(img, p["label"], 90 if lay == 1 else 190, 486, 46,
                  col_of(p["label_col"], AMBER), JB, glow=False) \
            if lay == 1 else text_c(img, p["label"], 512, 46,
                                    col_of(p["label_col"], AMBER), JB)
    if p["sub"] and t >= 0.25 + cd + 0.25:
        if lay == 0:
            text_c(img, p["sub"], 606, 32, GREEN_SOFT, JBR)
        else:
            glow_text(img, p["sub"], 90, 580, 32, GREEN_SOFT, JBR)
    return img


# =====================================================================
# 7. PROCESS GRID - luoi o tien trinh sang dan
# =====================================================================
def process_grid(t, dur, p):
    img = bg()
    lay = _lay(p)
    text_c(img, p["title"], 80, 46, GREEN, JB) if lay == 0 else \
        glow_text(img, p["title"], 70, 56, 46, GREEN, JB)
    total = int(p["_total"])
    cols = int(p["_cols"])
    rows = int(math.ceil(total / float(cols)))
    step = float(p["_step"])
    cell_w, cell_h, gap = 264, 118, 18
    gw = cols * cell_w + (cols - 1) * gap
    x0 = (W - gw) // 2 if lay == 0 else 70
    y0 = 150
    d = ImageDraw.Draw(img)
    rng = random.Random(23)
    for i in range(total):
        at = 0.45 + i * step
        r, c = divmod(i, cols)
        cx0 = x0 + c * (cell_w + gap)
        cy0 = y0 + r * (cell_h + gap)
        on = t >= at
        col = GREEN if on else GREEN_DIM
        d.rounded_rectangle([cx0, cy0, cx0 + cell_w, cy0 + cell_h],
                            radius=8, outline=col + (255,), width=3,
                            fill=(5, 26, 10, 255) if on else (2, 10, 4, 255))
        pid = 1000 + ((i * 137 + 42) % 9000)
        d.text((cx0 + 16, cy0 + 12), "PID %d" % pid, font=_font(JBR, 24),
               fill=(GREEN_SOFT if on else GREY) + (255,))
        frac = clamp((t - at) / 0.5) if on else 0.0
        bw = int((cell_w - 32) * frac)
        d.rectangle([cx0 + 16, cy0 + 62, cx0 + cell_w - 16, cy0 + 78],
                    outline=GREEN_DIM + (255,), width=2)
        if bw > 0:
            d.rectangle([cx0 + 17, cy0 + 63, cx0 + 16 + bw, cy0 + 77],
                        fill=(AMBER if i == total - 1 else GREEN) + (255,))
        st = "RUN" if on else "..."
        d.text((cx0 + 16, cy0 + 88), st, font=_font(JBR, 20),
               fill=(AMBER if on else GREY) + (255,))
    if p["caption"] and t >= 0.45 + total * step + 0.15:
        glow_text(img, p["caption"], x0, y0 + rows * (cell_h + gap) + 16,
                  30, AMBER, JBR, glow=False)
    return img


# =====================================================================
# 8. PROGRESS BLOCKS - thanh khoi / thanh nhiet
# =====================================================================
def progress_blocks(t, dur, p):
    img = bg()
    lay = _lay(p)
    pct = float(p["_pct"])
    fill_dur = float(p["_fill_dur"])
    t_lines = float(p["_t_lines"])
    style = p["style"].strip().lower()
    pr = ease_out_cubic((t - 0.3) / max(0.05, fill_dur))
    cur = pct * pr
    bar_y = 190 if lay == 0 else 500
    txt_y = 330 if lay == 0 else 130
    glow_text(img, "%d%%" % int(round(cur)), 90, bar_y - 108, 84, GREEN, JB)
    if style == "heat":
        # thanh nhiet: doan mau xanh -> vang -> do
        x0, x1, hh = 90, 1190, 54
        d = ImageDraw.Draw(img)
        nseg = 40
        lit = int(round(nseg * cur / 100.0))
        for i in range(nseg):
            sx0 = x0 + (x1 - x0) * i / nseg
            sx1 = x0 + (x1 - x0) * (i + 1) / nseg - 3
            k = i / float(nseg - 1)
            col = (int(51 + 204 * min(1, k * 1.6)),
                   int(255 - 140 * max(0, k - 0.35) / 0.65), 60)
            if i < lit:
                d.rectangle([sx0, bar_y, sx1, bar_y + hh], fill=col + (255,))
            else:
                d.rectangle([sx0, bar_y, sx1, bar_y + hh],
                            outline=(70, 70, 60, 255), width=1)
        glow_text(img, "NHIET DO: %.0f°C" % (30 + cur * 0.9), 90,
                  bar_y + hh + 18, 32, RED if cur > 80 else AMBER, JB,
                  glow=False)
    else:
        glow_text(img, "[", 90, bar_y, 64, GREEN_SOFT, JB, glow=False)
        blocks_bar(img, 140, bar_y + 14, 34, cur / 100.0, cell_w=26,
                   cell_h=34, col=GREEN)
        glow_text(img, "]", 140 + 34 * 30 + 8, bar_y, 64, GREEN_SOFT, JB,
                  glow=False)
    entries = [(p["line1"], 44, GREEN_SOFT, t_lines),
               (p["question"], 56, col_of(p["question_col"], AMBER),
                t_lines + 0.55),
               (p["answer"], 46, GREEN, t_lines + 1.10)]
    yy = txt_y
    for txt, size, colr, at in entries:
        if t >= at and txt:
            n = typed_slice(txt, t, at, 46)
            glow_text(img, txt[:n], 90, yy, size, colr, JB, glow=False)
        yy += 84
    return img


# =====================================================================
# 9. OVERCLOCK - leo thang xN + thong so + thanh nhiet + canh bao
# =====================================================================
def overclock(t, dur, p):
    img = bg()
    lay = _lay(p)
    sx = int(p["_start_x"])
    mx = int(p["_max_x"])
    step = float(p["_step"])
    cur, last_at = sx, 0.4
    for n in range(sx, mx + 1):
        at = 0.4 + (n - sx) * step
        if t >= at:
            cur, last_at = n, at
    n_cmd = typed_slice("> " + p["cmd"], t, 0.1, 30)
    glow_text(img, ("> " + p["cmd"])[:n_cmd], 70, 60, 36, GREEN, JBR)
    big = "OVERCLOCK ×%d" % cur
    size = fit_size(big, 1150, 120, 60)
    col_big = AMBER if cur < mx else RED
    if lay == 0:
        text_c(img, big, 226, size, col_big, JB)
    else:
        glow_text(img, big, 70, 226 - size / 2, size, col_big, JB)
    specs = [x.strip() for x in p["specs"].split("|") if x.strip()]
    for i, sp in enumerate(specs[:3]):
        at = last_at + 0.1 + i * 0.18
        if t < at:
            continue
        y = 330 + i * 56
        if "::" in sp:
            k, v = [q.strip() for q in sp.split("::", 1)]
            glow_text(img, k, 150, y, 36, GREEN_SOFT, JBR, glow=False)
            glow_text(img, ": " + v, 700, y, 36, GREEN, JB, glow=False)
        else:
            glow_text(img, sp, 150, y, 36, GREEN_SOFT, JBR, glow=False)
    heat = clamp((cur - sx + clamp((t - last_at) / max(step, 0.05))) /
                 max(1, mx - sx + 1))
    d = ImageDraw.Draw(img)
    glow_text(img, "NHIET DO NHIP VIDEO", 90, 520, 28, GREEN_DIM, JBR,
              glow=False)
    nseg = 44
    lit = int(round(nseg * heat))
    for i in range(nseg):
        sx0 = 90 + (1190 - 90) * i / nseg
        sx1 = 90 + (1190 - 90) * (i + 1) / nseg - 3
        k = i / float(nseg - 1)
        col = (int(51 + 204 * min(1, k * 1.6)),
               int(255 - 140 * max(0, k - 0.35) / 0.65), 60)
        if i < lit:
            d.rectangle([sx0, 560, sx1, 596], fill=col + (255,))
        else:
            d.rectangle([sx0, 560, sx1, 596], outline=(70, 70, 60, 255),
                        width=1)
    temp = 30 + heat * 90
    glow_text(img, "%.0f°C" % temp, 1050, 500, 40,
              RED if temp > 100 else AMBER, JB, glow=False)
    if cur >= mx and int(t * 3) % 2 == 0:
        glow_text(img, "[!] GAN CHAY - NHUNG DANG GIU NGUOI XEM", 90, 636,
                  30, RED, JB, glow=False)
    return img


# =====================================================================
# 10. FOLLOW END - dong follow + con tro khoi + trang thai DA THEO DOI
# =====================================================================
def follow_end(t, dur, p):
    img = bg()
    lay = _lay(p)
    click_at = float(p["_click_at"])
    if lay == 0:
        text_c(img, p["main"], 190, 52, GREEN, JB)
        text_c(img, p["sub"], 268, 52, GREEN_SOFT, JB)
    else:
        glow_text(img, p["main"], 70, 150, 52, GREEN, JB)
        glow_text(img, p["sub"], 70, 228, 52, GREEN_SOFT, JB)
    prompt = "> " + p["prompt"]
    n = typed_slice(prompt, t, 0.9, 26)
    px = 70 if lay == 1 else 300
    tw = glow_text(img, prompt[:n], px, 420, 42, GREEN, JBR)
    clicked = t >= click_at
    if not clicked:
        cursor_block(img, px + tw + 10, 422, 42, t)
    if clicked:
        bx, by = px, 510
        d = ImageDraw.Draw(img)
        label = "[OK] " + p["done_text"]
        f = _font(JB, 40)
        bw = int(_tw(label, f)) + 56
        d.rectangle([bx, by, bx + bw, by + 76], fill=GREEN + (255,))
        d.text((bx + 28, by + 16), label, font=f, fill=(2, 12, 4, 255))
        if t < click_at + 0.35 and int(t * 10) % 2 == 0:
            glow_text(img, ">> ENTER", bx + bw + 30, by + 18, 34, AMBER, JB,
                      glow=False)
    else:
        bx, by = px, 510
        d = ImageDraw.Draw(img)
        f = _font(JB, 40)
        bw = int(_tw(p["button"], f)) + 56
        d.rectangle([bx, by, bx + bw, by + 76], outline=GREEN + (255,),
                    width=3)
        d.text((bx + 28, by + 16), p["button"], font=f, fill=GREEN + (255,))
    return img
