#!/usr/bin/env python3
"""PAPER TEMPLATES - goi phong cach "PAPER" (giay & muc viet tay).

Theo mock paper-b1..b3: nen giay kem SANG (#F6F1E7) ke ngang + le do,
chu muc den (#1A1714), diem nhan but do (#E23B2E), da quang vang
(#FFD94A), but xanh (#2456C8). Font viet tay Itim (du dau tieng Viet)
+ Noto Sans Black cho headline muc.

Hieu ung rieng: net ve hien dan (draw-on tung ky tu/segment), quet da
quang lan ngang, note dan roi + nghieng, dong tem muc mon + rung giay
nhe, lat trang o dau shot. Cam fade/zoom tinh.

Moi ham fn(t, dur, p) -> RGBA 1280x720; p co "_layout" (0/1) tu scenes.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
ITIM = str(_FONT_DIR / "Itim-Regular.ttf")
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")
FALLBACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"

W, H = 1280, 720
PAPER = (246, 241, 231)
PAPER_DARK = (236, 228, 210)
INK = (26, 23, 20)
INK_SOFT = (74, 68, 60)
RED = (226, 59, 46)
BLUE = (36, 86, 200)
HIGHLIGHT = (255, 217, 74)
NOTE_COLS = [(255, 217, 74), (255, 183, 197), (168, 216, 255),
             (183, 230, 183)]
LINE_BLUE = (172, 192, 216)
MARGIN_RED = (238, 150, 138)
TAPE = (246, 231, 183, 175)


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


def ease_out_back(k, s=1.70158):
    k = clamp(k)
    return 1 + (s + 1) * (k - 1) ** 3 + s * (k - 1) ** 2


def pop_scale(t, t0, dur=0.22):
    if t < t0:
        return 0.0
    return max(0.01, ease_out_back((t - t0) / max(0.05, dur)))


def col_of(name, default=INK):
    cols = {"ink": INK, "red": RED, "blue": BLUE, "soft": INK_SOFT}
    return cols.get(str(name or "").strip().lower(), default)


# ------------------------------------------------------------------ nen
def bg(style="ruled"):
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(8)
    for _ in range(700):                           # van giay nhe
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        d.point((x, y), fill=(120, 100, 70, rng.randint(5, 13)))
    if style == "ruled":
        for y in range(64, H, 46):
            d.line([(0, y), (W, y)], fill=LINE_BLUE + (160,), width=2)
        d.line([(88, 0), (88, H)], fill=MARGIN_RED + (200,), width=2)
    elif style == "grid":
        for x in range(40, W, 40):
            for y in range(40, H, 40):
                d.ellipse([x - 2, y - 2, x + 2, y + 2],
                          fill=(170, 160, 140, 120))
    return img


def wobbly_line(d, x0, y0, x1, y1, col, width=3, seed=0, amp=1.6):
    """Duong thang ve tay: chia doan + jitter xac dinh theo seed."""
    rng = random.Random(seed)
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 26))
    pts = []
    for i in range(n + 1):
        k = i / float(n)
        jx = rng.uniform(-amp, amp) if 0 < i < n else 0
        jy = rng.uniform(-amp, amp) if 0 < i < n else 0
        pts.append((x0 + (x1 - x0) * k + jx, y0 + (y1 - y0) * k + jy))
    d.line(pts, fill=col, width=width, joint="curve")


def wobbly_rect(d, x0, y0, x1, y1, col, width=3, seed=0, amp=1.6):
    wobbly_line(d, x0, y0, x1, y0, col, width, seed + 1, amp)
    wobbly_line(d, x1, y0, x1, y1, col, width, seed + 2, amp)
    wobbly_line(d, x1, y1, x0, y1, col, width, seed + 3, amp)
    wobbly_line(d, x0, y1, x0, y0, col, width, seed + 4, amp)


def tape_strip(img, cx, cy, wdt=130, ang=-14):
    lay = Image.new("RGBA", (wdt + 20, 54), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([10, 12, wdt + 10, 42], fill=TAPE)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2),
                              int(cy - lay.height / 2)))


def shadow_rect(img, x0, y0, x1, y1, off=8, alpha=46):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0 + off, y0 + off, x1 + off, y1 + off],
                fill=(60, 50, 30, alpha))


# ------------------------------------------------------------------ chu
def hand_text(img, text, x, y, size, col=INK, prog=1.0, seed=0):
    """Chu viet tay hien dan (draw-on): ve prog (0..1) so ky tu, moi ky
    tu lech doc nhe nhu viet tay. Tra chieu rong phan da ve."""
    if not text or prog <= 0:
        return 0
    f = _font(ITIM, size)
    n = max(1, int(round(len(text) * clamp(prog))))
    d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    cx = x
    full_w = _tw(text, f)
    for i, ch in enumerate(text[:n]):
        jy = rng.uniform(-1.6, 1.6)
        d.text((cx, y + jy), ch, font=f, fill=col + (255,))
        cx += _tw(ch, f)
    return full_w * clamp(prog)


def ink_text_c(img, text, cy, size, col=INK, cx=W / 2, path=SANS):
    f = _font(path, size)
    tw = _tw(text, f)
    d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, cy - size / 2), text, font=f, fill=col + (255,))
    return tw


def fit_size(text, max_w, start, min_size, path=SANS):
    size = start
    while size > min_size:
        if _tw(text, _font(path, size)) <= max_w:
            return size
        size -= 4
    return min_size


def highlight_swipe(img, x, y, wdt, hgt, t, t0, dur=0.4):
    """Quet da quang: hop vang mo lan ngang sau chu."""
    pr = ease_out_cubic((t - t0) / max(0.05, dur))
    if pr <= 0 or wdt <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([x, y, x + wdt * pr, y + hgt], radius=hgt // 2,
                        fill=HIGHLIGHT + (140,))


def hand_arrow(img, x0, y0, x1, y1, t, t0, dur=0.5, col=RED, bend=60):
    """Mui ten ve tay cong: hien dan theo prog, dau mui ten o cuoi."""
    pr = ease_out_cubic((t - t0) / max(0.05, dur))
    if pr <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    n = 26
    pts = []
    for i in range(n + 1):
        k = i / float(n)
        if k > pr:
            break
        # bezier bac 2: diem dieu khien lech vuong goc
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        L = max(1.0, math.hypot(dx, dy))
        cxp, cyp = mx - dy / L * bend, my + dx / L * bend
        px = (1 - k) ** 2 * x0 + 2 * (1 - k) * k * cxp + k * k * x1
        py = (1 - k) ** 2 * y0 + 2 * (1 - k) * k * cyp + k * k * y1
        pts.append((px, py))
    if len(pts) > 1:
        d.line(pts, fill=col + (255,), width=5, joint="curve")
    if pr >= 0.98:
        ang = math.atan2(y1 - pts[-2][1], x1 - pts[-2][0])
        for da in (2.65, -2.65):
            hx = x1 - 26 * math.cos(ang + da * 0.24)
            hy = y1 - 26 * math.sin(ang + da * 0.24)
            d.line([(x1, y1), (hx, hy)], fill=col + (255,), width=5)


def draw_stamp(img, text, cx, cy, t, t0, col=RED, size=54, ang=-10):
    """Tem muc do: dong xuong (scale 1.6->1) + mon muc (cham trong)."""
    if t < t0:
        return
    pr = clamp((t - t0) / 0.10)
    sc = 1.6 - 0.6 * pr
    f = _font(SANS, size)
    tw = int(_tw(text, f))
    lay = Image.new("RGBA", (tw + 56, size + 52), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([5, 5, tw + 50, size + 46], radius=10,
                         outline=col + (255,), width=7)
    ld.text((28, 22), text, font=f, fill=col + (255,))
    rng = random.Random(5)                          # mon muc: cham trong
    md = ImageDraw.Draw(lay)
    for _ in range(240):
        x, y = rng.randint(0, lay.width - 1), rng.randint(0, lay.height - 1)
        md.point((x, y), fill=(0, 0, 0, 0))
    lay.putalpha(lay.split()[3])  # giu alpha (diem trong da xoa o tren)
    nw, nh = max(2, int(lay.width * sc)), max(2, int(lay.height * sc))
    lay = lay.resize((nw, nh), Image.LANCZOS)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2),
                              int(cy - lay.height / 2)))


def paper_shake(img, t, t0, dur=0.08, mag=3):
    if not (t0 <= t < t0 + dur):
        return img
    k = 1.0 - (t - t0) / dur
    dx = int(mag * k) * (1 if int((t - t0) * 60) % 2 == 0 else -1)
    out = Image.new("RGBA", (W, H), PAPER + (255,))
    out.alpha_composite(img, (dx, 0))
    return out


def page_in(img, t, dur_in=0.32):
    """Lat trang dau shot: tam giay cu truot sang phai lo dan noi dung."""
    if t >= dur_in:
        return img
    pr = ease_out_cubic(t / dur_in)
    x = int(W * pr)
    if x >= W:
        return img
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x, 0, W, H], fill=PAPER_DARK + (255,))
    for i in range(26):                             # bong o mep lat
        a = int(70 * (1 - i / 26.0))
        d.line([(x + i, 0), (x + i, H)], fill=(90, 78, 55, a))
    for y in range(64, H, 46):
        d.line([(x + 30, y), (W, y)], fill=LINE_BLUE + (120,), width=2)
    return img


def _lay(p):
    return int(p.get("_layout", 0))


def _bg(p):
    return bg(p.get("bg", "ruled"))


# =====================================================================
# 1. NOTE HOOK - note vang roi + headline muc + quet da quang (mock b1)
# =====================================================================
def note_hook(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    note_w, note_h = 470, 250
    nx = 130 if lay == 0 else W - 130 - note_w
    final_y = 92
    drop = ease_out_back((t - 0.15) / 0.5)
    ny = int(final_y - (1 - clamp(drop)) * 460)
    ang = -3 if lay == 0 else 3
    if t >= 0.15:
        note = Image.new("RGBA", (note_w + 30, note_h + 30), (0, 0, 0, 0))
        nd = ImageDraw.Draw(note)
        nd.rectangle([15 + 7, 15 + 8, 15 + note_w + 7, 15 + note_h + 8],
                     fill=(60, 50, 30, 46))
        nd.rectangle([15, 15, 15 + note_w, 15 + note_h],
                     fill=NOTE_COLS[0] + (255,))
        note = note.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(note, (nx - 15, ny - 15))
        tape_strip(img, nx + note_w // 2, ny + 8, 140, ang)
        prog = clamp((t - 0.65) / max(0.3, len(p["note"]) * 0.016))
        hand_text(img, p["note"], nx + 42, ny + 66, 54, INK, prog, seed=3)
    head = p["head"]
    size = fit_size(head, 1170, 118, 52)
    hy = 452 if lay == 0 else 430
    accent = p["accent"]
    if accent and accent in head:
        a, b = head.split(accent, 1)
        f = _font(SANS, size)
        tw_a, tw_acc = _tw(a, f), _tw(accent, f)
        total = tw_a + tw_acc + _tw(b, f)
        x0 = (W - total) / 2 if lay == 0 else 110
        highlight_swipe(img, x0 + tw_a - 8, hy + size * 0.52,
                        tw_acc + 16, int(size * 0.52), t, 1.05)
        d = ImageDraw.Draw(img)
        d.text((x0, hy - size / 2), a, font=f, fill=INK + (255,))
        d.text((x0 + tw_a, hy - size / 2), accent, font=f,
               fill=INK + (255,))
        d.text((x0 + tw_a + tw_acc, hy - size / 2), b, font=f,
               fill=INK + (255,))
    else:
        ink_text_c(img, head, hy, size, INK, cx=W / 2 if lay == 0 else 640)
    hand_arrow(img, nx + note_w - 40, ny + note_h + 26, 900, hy - 90,
               t, 0.9, 0.5, RED, bend=70)
    if p["sub"]:
        hand_text(img, p["sub"], 118, 622, 42, INK_SOFT,
                  clamp((t - 1.5) / 0.8), seed=9)
    return img


# =====================================================================
# 2. STAMP VERDICT - chu muc lon + tem do dong xuong
# =====================================================================
def stamp_verdict(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    size = fit_size(p["big"], 1150, 116, 52)
    cy = 268 if lay == 0 else 238
    if lay == 0:
        ink_text_c(img, p["big"], cy, size, INK)
    else:
        f = _font(SANS, size)
        d = ImageDraw.Draw(img)
        d.text((110, cy - size / 2), p["big"], font=f, fill=INK + (255,))
    stamp_at = float(p["_stamp_at"])
    scx = 880 if lay == 0 else 320
    draw_stamp(img, p["stamp"], scx, cy + int(size * 0.95) + 34, t, stamp_at,
               col=col_of(p["stamp_col"], RED), size=58)
    if p["sub"]:
        hand_text(img, p["sub"], 118, 560, 46, INK_SOFT,
                  clamp((t - stamp_at - 0.3) / 0.9), seed=4)
    return paper_shake(img, t, stamp_at)


# =====================================================================
# 3. NOTEBOOK DEMO - trang so, chu viet tay hien dan tung dong
# =====================================================================
def notebook_demo(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    x0 = 130 if lay == 0 else 90
    d = ImageDraw.Draw(img)
    for i in range(9):                              # lo xo so tay
        yy = 70 + i * 72
        d.ellipse([x0 - 42, yy, x0 - 14, yy + 28], outline=INK_SOFT,
                  width=3)
    if p["title"]:
        hand_text(img, p["title"], x0 + 20, 66, 54, INK,
                  clamp((t - 0.2) / 0.7), seed=6)
        wobbly_line(d, x0 + 20, 138, x0 + 20 + _tw(p["title"],
                    _font(ITIM, 54)) * clamp((t - 0.2) / 0.7), 138,
                    RED, 4, seed=12)
    lines = [x for x in p["lines"].split("|")]
    starts = p["_line_starts"]
    pen = None
    for i, ln in enumerate(lines[:6]):
        st, en = starts[i]
        if t < st:
            break
        prog = clamp((t - st) / max(0.05, en - st))
        y = 196 + i * 76
        w = hand_text(img, ln, x0 + 20, y, 48,
                      col_of(p["colors"].split(",")[i % len(
                          p["colors"].split(","))], INK) if False else INK,
                      prog, seed=20 + i)
        pen = (x0 + 20 + w, y + 40)
    if pen and prog < 1.0:
        d.ellipse([pen[0] - 5, pen[1] - 5, pen[0] + 5, pen[1] + 5],
                  fill=RED + (255,))
    return img


# =====================================================================
# 4. PAPER AB - 2 to giay: trai phac xam vs phai muc day du
# =====================================================================
def _sheet(img, x0, y0, x1, y1, full, t):
    shadow_rect(img, x0, y0, x1, y1)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0, y0, x1, y1], fill=(252, 250, 244, 255))
    tape_strip(img, (x0 + x1) // 2, y0 + 4, 120, -8)
    if not full:
        for i in range(5):
            yy = y0 + 66 + i * 58
            wobbly_line(d, x0 + 36, yy, x0 + 36 + (300 - i * 28), yy,
                        (168, 162, 150), 5, seed=30 + i, amp=2.4)
        d.text((x0 + 36, y1 - 64), "chua co gi ca ...", font=_font(ITIM, 36),
               fill=(150, 144, 132, 255))
    else:
        pts = []
        for i in range(6):
            px = x0 + 46 + i * 76
            py = y1 - 90 - int(150 * (0.25 + 0.12 * i + 0.1 *
                                      math.sin(i * 1.7)))
            pts.append((px, py))
        pr = ease_out_cubic((t - 0.8) / 0.9)
        n = max(2, int(len(pts) * pr))
        d.line(pts[:n], fill=RED + (255,), width=6, joint="curve")
        for (px, py) in pts[:n]:
            d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=BLUE + (255,))
        for i in range(3):
            yy = y0 + 52 + i * 44
            wobbly_line(d, x0 + 36, yy, x0 + 300 - i * 40, yy, INK, 4,
                        seed=40 + i)


def paper_ab(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    hand_text(img, p["head"], 118, 48, 50, INK, clamp((t - 0.1) / 0.6),
              seed=5)
    swapped = (lay == 1)
    lx, rx = (80, 690) if not swapped else (690, 80)
    if t >= 0.35:
        _sheet(img, lx, 150, lx + 510, 540, full=swapped, t=t)
    if t >= 0.7:
        _sheet(img, rx, 150, rx + 510, 540, full=not swapped, t=t)
    if t >= 1.0:
        d = ImageDraw.Draw(img)
        d.ellipse([592, 300, 688, 396], fill=PAPER + (255,),
                  outline=INK, width=4)
        f = _font(SANS, 30)
        d.text((640 - _tw("VS", f) / 2, 330), "VS", font=f,
               fill=RED + (255,))
    la_x, lb_x = (lx + 255, rx + 255) if not swapped else (rx + 255, lx + 255)
    hand_text(img, p["label_a"], la_x - 160, 566, 40, INK_SOFT,
              clamp((t - 1.15) / 0.5), seed=7)
    hand_text(img, p["label_b"], lb_x - 160, 566, 40, BLUE,
              clamp((t - 1.3) / 0.5), seed=8)
    return img


# =====================================================================
# 5. CHECKLIST - tich tay tung muc + khoanh do muc cuoi
# =====================================================================
def checklist(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    x0 = 118 if lay == 0 else 150
    hand_text(img, p["title"], x0, 54, 56, INK, clamp((t - 0.15) / 0.7),
              seed=11)
    d = ImageDraw.Draw(img)
    tw_t = _tw(p["title"], _font(ITIM, 56)) * clamp((t - 0.15) / 0.7)
    wobbly_line(d, x0, 128, x0 + tw_t, 128, RED, 4, seed=13)
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    starts = p["_starts"]
    for i, it in enumerate(items[:6]):
        if t < starts[i]:
            continue
        y = 176 + i * 82
        wobbly_rect(d, x0, y, x0 + 46, y + 46, INK, 4, seed=50 + i)
        cpr = clamp((t - starts[i] - 0.32) / 0.22)
        if cpr > 0:                                 # dau tich ve dan
            p1 = (x0 + 9, y + 24)
            p2 = (x0 + 20, y + 36)
            p3 = (x0 + 40, y + 10)
            if cpr <= 0.45:
                k = cpr / 0.45
                ex, ey = p1[0] + (p2[0] - p1[0]) * k, p1[1] + (p2[1] - p1[1]) * k
                d.line([p1, (ex, ey)], fill=RED + (255,), width=6)
            else:
                k = (cpr - 0.45) / 0.55
                ex, ey = p2[0] + (p3[0] - p2[0]) * k, p2[1] + (p3[1] - p2[1]) * k
                d.line([p1, p2], fill=RED + (255,), width=6)
                d.line([p2, (ex, ey)], fill=RED + (255,), width=6)
        hand_text(img, it, x0 + 70, y - 2, 48, INK,
                  clamp((t - starts[i]) / 0.3), seed=60 + i)
        if i == len(items) - 1 and p["circle"] and p["circle"] in it:
            cpr2 = clamp((t - starts[i] - 0.55) / 0.4)
            if cpr2 > 0:
                idx = it.index(p["circle"])
                f = _font(ITIM, 48)
                cx0 = x0 + 70 + _tw(it[:idx], f) - 10
                cw = _tw(p["circle"], f) + 20
                d.arc([cx0, y - 8, cx0 + cw, y + 58], start=-90,
                      end=-90 + 360 * cpr2, fill=RED + (255,), width=4)
    return img


# =====================================================================
# 6. BIG NUMBER INK - so muc chay tang + khoanh tron do
# =====================================================================
def big_number_ink(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    target = float(p["_target"])
    cd = float(p["_count_dur"])
    pr = ease_out_cubic((t - 0.25) / max(0.05, cd))
    txt = "{:,.0f}".format(target * pr).replace(",", ".")
    size = fit_size(txt, 1050, 240, 90)
    cy = 300 if lay == 0 else 260
    cx = W / 2 if lay == 0 else 640
    tw = ink_text_c(img, txt, cy, size, INK, cx=cx)
    if pr >= 0.99:                                  # khoanh do 2 vong lech
        cpr = clamp((t - 0.25 - cd) / 0.45)
        d = ImageDraw.Draw(img)
        for j, (ox, oy) in enumerate([(0, 0), (10, 6)]):
            d.arc([cx - tw / 2 - 26 + ox, cy - size * 0.62 + oy,
                   cx + tw / 2 + 26 + ox, cy + size * 0.62 + oy],
                  start=-80 + j * 14, end=-80 + j * 14 + 330 * cpr,
                  fill=RED + (255,), width=6)
    if t >= 0.25 + cd * 0.5:
        hand_text(img, p["label"], cx - 200 if lay == 0 else 118, 486, 52,
                  RED, clamp((t - 0.25 - cd * 0.5) / 0.5), seed=15)
    if p["sub"]:
        hand_text(img, p["sub"], 118, 600, 40, INK_SOFT,
                  clamp((t - 0.25 - cd - 0.2) / 0.6), seed=16)
    return img


# =====================================================================
# 7. NOTE GRID - luoi note dan nhieu mau
# =====================================================================
def note_grid(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    hand_text(img, p["title"], 118, 50, 52, INK, clamp((t - 0.1) / 0.6),
              seed=17)
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    total = max(1, int(p["_total"]))
    cols = max(1, int(p["_cols"]))
    items = (items + [""] * total)[:total]
    rows = int(math.ceil(total / float(cols)))
    step = float(p["_step"])
    nw, nh, gap = 218, 150, 22
    gw = cols * nw + (cols - 1) * gap
    x0 = (W - gw) // 2 if lay == 0 else 110
    y0 = 168
    for i in range(total):
        at = 0.45 + i * step
        if t < at:
            continue
        sc = pop_scale(t, at, 0.2)
        r, c = divmod(i, cols)
        cx0 = x0 + c * (nw + gap)
        cy0 = y0 + r * (nh + gap)
        note = Image.new("RGBA", (nw + 16, nh + 16), (0, 0, 0, 0))
        nd = ImageDraw.Draw(note)
        nd.rectangle([8 + 5, 8 + 6, 8 + nw + 5, 8 + nh + 6],
                     fill=(60, 50, 30, 40))
        nd.rectangle([8, 8, 8 + nw, 8 + nh],
                     fill=NOTE_COLS[i % len(NOTE_COLS)] + (255,))
        f = _font(ITIM, 44)
        label = items[i] or str(i + 1)
        nd.text((8 + nw / 2 - _tw(label, f) / 2, 8 + nh / 2 - 26), label,
                font=f, fill=INK + (255,))
        f2 = _font(SANS, 24)
        nd.text((8 + 14, 8 + 10), "%02d" % (i + 1), font=f2,
                fill=(0, 0, 0, 90))
        nw2, nh2 = max(2, int(note.width * sc)), max(2, int(note.height * sc))
        note = note.resize((nw2, nh2), Image.LANCZOS)
        note = note.rotate(-2 if i % 2 == 0 else 2, expand=True,
                           resample=Image.BICUBIC)
        img.alpha_composite(note, (int(cx0 + nw / 2 - note.width / 2),
                                   int(cy0 + nh / 2 - note.height / 2)))
    if p["caption"]:
        hand_text(img, p["caption"], x0, y0 + rows * (nh + gap) + 14, 40,
                  BLUE, clamp((t - 0.45 - total * step - 0.1) / 0.6),
                  seed=18)
    return img


# =====================================================================
# 8. PROGRESS HAND - thanh ve tay dien gach cheo + 3 dong chu
# =====================================================================
def progress_hand(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    pct = float(p["_pct"])
    fill_dur = float(p["_fill_dur"])
    t_lines = float(p["_t_lines"])
    pr = ease_out_cubic((t - 0.3) / max(0.05, fill_dur))
    cur = pct * pr
    bar_y = 210 if lay == 0 else 470
    txt_y = 330 if lay == 0 else 130
    x0, x1, bh = 118, 1162, 74
    d = ImageDraw.Draw(img, "RGBA")
    hand_text(img, "%d%%" % int(round(cur)), x0, bar_y - 92, 72, INK, 1.0,
              seed=21)
    wobbly_rect(d, x0, bar_y, x1, bar_y + bh, INK, 5, seed=77, amp=2.2)
    if cur > 0.5:                                   # gach cheo dien day
        fw = int((x1 - x0 - 12) * cur / 100.0)
        clip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(clip)
        for gx in range(x0 + 8 - bh, x0 + 8 + fw, 17):
            cd.line([(gx, bar_y + bh - 6), (gx + bh - 10, bar_y + 6)],
                    fill=BLUE + (200,), width=7)
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        md.rectangle([x0 + 6, bar_y + 5, x0 + 6 + fw, bar_y + bh - 5],
                     fill=255)
        img.alpha_composite(Image.composite(
            clip, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
        d = ImageDraw.Draw(img, "RGBA")
    entries = [(p["line1"], INK, t_lines), (p["question"], RED,
               t_lines + 0.55), (p["answer"], INK, t_lines + 1.10)]
    yy = txt_y
    for txt, colr, at in entries:
        if txt:
            hand_text(img, txt, x0, yy, 52, colr,
                      clamp((t - at) / 0.55), seed=int(at * 10) + 30)
        yy += 82
    return img


# =====================================================================
# 9. STEPS UP - bac thang giay leo y + mui ten tay (mock b3)
# =====================================================================
def steps_up(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    steps = [x.strip() for x in p["steps"].split("|") if x.strip()]
    starts = p["_starts"]
    hand_text(img, p["title"], 118, 50, 46, INK_SOFT,
              clamp((t - 0.1) / 0.6), seed=23)
    n = len(steps)
    cw, chh = 400, 170
    for i, s in enumerate(steps[:4]):
        if t < starts[i]:
            continue
        sc = pop_scale(t, starts[i], 0.22)
        if lay == 0:
            cx0 = 110 + i * 250
        else:
            cx0 = W - 110 - cw - i * 250
        cy0 = 500 - i * 108
        card = Image.new("RGBA", (cw + 24, chh + 24), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rectangle([12 + 6, 12 + 7, 12 + cw + 6, 12 + chh + 7],
                     fill=(60, 50, 30, 42))
        cd.rectangle([12, 12, 12 + cw, 12 + chh], fill=(252, 250, 244, 255),
                     outline=INK + (255,), width=3)
        parts = s.split("::")
        head = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        cd.text((36, 30), head, font=_font(ITIM, 56), fill=INK + (255,))
        if body:
            cd.text((36, 102), body, font=_font(ITIM, 38),
                    fill=INK_SOFT + (255,))
        nw2, nh2 = max(2, int(card.width * sc)), max(2, int(card.height * sc))
        card = card.resize((nw2, nh2), Image.LANCZOS)
        img.alpha_composite(card, (int(cx0 + cw / 2 - nw2 / 2),
                                   int(cy0 + chh / 2 - nh2 / 2)))
        if i > 0:
            ax0 = cx0 + cw + 16 if lay == 0 else cx0 - 16
            ax1 = cx0 + cw + 74 if lay == 0 else cx0 - 74
            hand_arrow(img, ax0, cy0 + 130, ax1, cy0 + 40, t,
                       starts[i] + 0.15, 0.35, INK, bend=24)
    if p["stamp"] and n:
        last_at = starts[min(n, 4) - 1] + 0.45
        draw_stamp(img, p["stamp"], W / 2, 380, t, last_at, col=RED, size=46)
    return img


# =====================================================================
# 10. FOLLOW END PAPER - nut giay THEO DOI + khoanh do
# =====================================================================
def follow_end_paper(t, dur, p):
    img = _bg(p)
    lay = _lay(p)
    ink_text_c(img, p["main"], 190, 54, INK, cx=W / 2 if lay == 0 else 640)
    ink_text_c(img, p["sub"], 268, 54, INK_SOFT,
               cx=W / 2 if lay == 0 else 640)
    click_at = float(p["_click_at"])
    clicked = t >= click_at
    bx0, by0, bx1, by1 = (430, 470, 850, 556) if lay == 0 else \
        (150, 470, 570, 556)
    if t >= 0.9:
        sc = pop_scale(t, 0.9, 0.2)
        if clicked and t < click_at + 0.08:
            sc *= 0.94
        bw, bh = bx1 - bx0, by1 - by0
        lay2 = Image.new("RGBA", (bw + 16, bh + 16), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay2)
        ld.rectangle([8 + 5, 8 + 6, 8 + bw + 5, 8 + bh + 6],
                     fill=(60, 50, 30, 42))
        fillc = INK if clicked else (252, 250, 244)
        txtc = PAPER if clicked else INK
        txt = p["done_text"] if clicked else p["button"]
        ld.rectangle([8, 8, 8 + bw, 8 + bh], fill=fillc + (255,),
                     outline=INK + (255,), width=4)
        f = _font(SANS, 38)
        ld.text((8 + bw / 2 - _tw(txt, f) / 2, 8 + bh / 2 - 24), txt,
                font=f, fill=txtc + (255,))
        nw2, nh2 = max(2, int(lay2.width * sc)), max(2, int(lay2.height * sc))
        lay2 = lay2.resize((nw2, nh2), Image.LANCZOS)
        img.alpha_composite(lay2, (int((bx0 + bx1) / 2 - nw2 / 2),
                                   int((by0 + by1) / 2 - nh2 / 2)))
        hand_arrow(img, bx1 + 190, by0 - 66, bx1 + 26, by0 + 26, t, 1.05,
                   0.45, RED, bend=50)
        if clicked:
            cpr = clamp((t - click_at) / 0.4)
            d = ImageDraw.Draw(img)
            d.arc([bx0 - 16, by0 - 14, bx1 + 16, by1 + 14], start=-70,
                  end=-70 + 340 * cpr, fill=RED + (255,), width=5)
    if p["side_text"]:
        hand_text(img, p["side_text"], bx1 + 40, 592, 40, INK_SOFT,
                  clamp((t - 1.25) / 0.6), seed=25)
    return img
