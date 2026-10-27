#!/usr/bin/env python3
"""TEST01 TEMPLATES - goi phong cach "test01" (kinetic / giu chan) cho Pixel Studio.

Theo SPEC v2 (~/workspace/pixel-tool-mockup/kinetic-pack-v1/SPEC.md, Minh duyet
27/10/2026): chu la dien vien chinh, KHONG linh vat, nen nau den, 2 he font
(sans nang co dau tieng Viet + pixel PressStart2P/VT323), hieu ung: pop nay,
dong dau + rung, nut tach mau RGB, vo pixel, go tung ky tu, so chay, hat pixel.

Module ve thuan (chi PIL + math/random nhu style2_templates):
  moi ham fn(t, dur, p) -> RGBA 1280x720 (khung goc cua goi theo spec muc 2;
  pipeline chinh phong NEAREST len 1920x1080 khi can).
  p = dict tham so dang CHUOI (da merge mac dinh o test01_scenes).
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")   # he A: sans nang, du dau TV
SANS_FALLBACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
PS = str(_FONT_DIR / "PressStart2P.ttf")       # he B: pixel so/ASCII
VT = str(_FONT_DIR / "VT323.ttf")              # he B: pixel chu (co dau TV)

W, H = 1280, 720
BG_TOP = (31, 13, 8)        # #1F0D08
BG_BOT = (13, 6, 4)         # #0D0604
CREAM = (245, 239, 230)     # #F5EFE6
RED = (232, 68, 46)         # #E8442E
TEAL = (53, 208, 186)       # #35D0BA
YELLOW = (245, 197, 66)     # #F5C542
GREY_TXT = (168, 156, 144)

COLS = {"cream": CREAM, "red": RED, "teal": TEAL, "yellow": YELLOW,
        "grey": GREY_TXT, "white": (255, 255, 255)}


def col_of(name, default=CREAM):
    return COLS.get(str(name or "").strip().lower(), default)


def _font(path, size):
    try:
        return ImageFont.truetype(path, int(size))
    except OSError:
        return ImageFont.truetype(SANS_FALLBACK, int(size))


def _tw(d, text, f):
    return d.textlength(text, font=f)


# ---------------------------------------------------------------- easing
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease_out_cubic(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def ease_in_quad(k):
    k = clamp(k)
    return k * k


def ease_out_back(k, s=1.70158):
    k = clamp(k)
    return 1 + (s + 1) * (k - 1) ** 3 + s * (k - 1) ** 2


def pop_scale(t, t0, dur=0.22):
    """He so phong cua hieu ung 'pop': 0 khi chua toi, nay qua 1 roi ve 1."""
    if t < t0:
        return 0.0
    return max(0.01, ease_out_back((t - t0) / max(0.05, dur)))


# ---------------------------------------------------------------- text fit
_DUMMY = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def fit_lines(text, max_w, start, min_size, path=SANS, max_lines=3):
    """Tim (size, [dong]) lon nhat sao cho moi dong <= max_w, toi da max_lines."""
    text = (text or "").strip()
    if not text:
        return min_size, []
    size = start
    while size > min_size:
        f = _font(path, size)
        if _tw(_DUMMY, text, f) <= max_w:
            return size, [text]
        size -= 4
    words = text.split()
    if len(words) < 2:
        return min_size, [text]
    best = None
    size = start
    while size > min_size:
        f = _font(path, size)
        # tham lam: xep tu vao toi da max_lines dong
        lines, cur = [], ""
        for w_ in words:
            trial = (cur + " " + w_).strip()
            if _tw(_DUMMY, trial, f) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w_
        lines.append(cur)
        if len(lines) <= max_lines and all(
                _tw(_DUMMY, l, f) <= max_w for l in lines):
            best = (size, lines)
            break
        size -= 4
    return best if best else (min_size, [text])


def draw_text_c(img, text, cy, size, colr, path=SANS, cx=W / 2, stroke=0,
                stroke_col=(0, 0, 0)):
    """Ve 1 dong chu canh giua tai tam doc cy. Tra chieu rong chu."""
    if not text:
        return 0
    d = ImageDraw.Draw(img)
    f = _font(path, size)
    tw = _tw(d, text, f)
    kw = dict(font=f, fill=colr)
    if stroke:
        kw.update(stroke_width=stroke, stroke_fill=stroke_col)
    d.text((cx - tw / 2, cy - size / 2), text, **kw)
    return tw


def draw_pop_text(img, text, cy, size, colr, t, t0, path=SANS, cx=W / 2,
                  pop_dur=0.22):
    """Chu bat vao voi scale pop (nay). Ve qua lop rieng de phong quanh tam."""
    sc = pop_scale(t, t0, pop_dur)
    if sc <= 0 or not text:
        return
    f = _font(path, size)
    tw = int(_tw(_DUMMY, text, f)) + 16
    th = int(size * 1.5) + 16
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.text((8, 8), text, font=f, fill=colr + (255,) if len(colr) == 3 else colr)
    nw, nh = max(2, int(tw * sc)), max(2, int(th * sc))
    lay = lay.resize((nw, nh), Image.LANCZOS if path == SANS else Image.NEAREST)
    img.alpha_composite(lay, (int(cx - nw / 2), int(cy - nh / 2)))


def draw_mixed_pop(img, segments, cy, size, t, t0, path=SANS):
    """1 dong gom nhieu doan mau [(text, color)...], pop chung 1 nhip."""
    sc = pop_scale(t, t0)
    if sc <= 0:
        return
    f = _font(path, size)
    widths = [_tw(_DUMMY, s, f) for s, _ in segments]
    total = sum(widths)
    th = int(size * 1.5) + 16
    lay = Image.new("RGBA", (int(total) + 16, th), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    x = 8
    for (s, c), wseg in zip(segments, widths):
        ld.text((x, 8), s, font=f,
                fill=c + (255,) if len(c) == 3 else c)
        x += wseg
    nw, nh = max(2, int(lay.width * sc)), max(2, int(lay.height * sc))
    lay = lay.resize((nw, nh), Image.LANCZOS if path == SANS else Image.NEAREST)
    img.alpha_composite(lay, (int(W / 2 - nw / 2), int(cy - nh / 2)))


# ---------------------------------------------------------------- effects
def fx_pixelate(img, block):
    """Vo pixel: ha do phan giai xuong block lan roi phong NEAREST."""
    block = int(block)
    if block <= 1:
        return img
    small = img.convert("RGB").resize(
        (max(1, W // block), max(1, H // block)), Image.NEAREST)
    return small.resize((W, H), Image.NEAREST).convert("RGBA")


def fx_rgb_split(img, amp=6):
    """Nut tach mau RGB: kenh R lech trai, B lech phai."""
    if amp <= 0:
        return img
    rgb = img.convert("RGB")
    r, g, b = rgb.split()
    r = ImageChops.offset(r, -amp, 0)
    b = ImageChops.offset(b, amp, 0)
    return Image.merge("RGB", (r, g, b)).convert("RGBA")


def fx_shake(img, t, t0, mag=7, dur=0.09):
    """Rung man hinh sau moc t0 (vd dong dau): lech +-mag giam dan."""
    if not (t0 <= t < t0 + dur):
        return img
    k = 1.0 - (t - t0) / dur
    dx = int(mag * k) * (1 if int((t - t0) * 60) % 2 == 0 else -1)
    out = Image.new("RGBA", (W, H), BG_BOT + (255,))
    out.alpha_composite(img, (dx, 0))
    return out


def fx_glitch_slices(img, t, t0, dur=0.22):
    """Xe ngang 3 dai anh trong cua so [t0, t0+dur] (phong cach style2)."""
    if not (t0 <= t <= t0 + dur):
        return img
    out = img.copy()
    for (y0, y1, dx) in [(150, 196, 22), (330, 372, -30), (520, 596, 16)]:
        strip = img.crop((0, y0, W, y1))
        out.paste(strip, (dx, y0))
    return out


# ---------------------------------------------------------------- nen
def bg_plain():
    """Nen phang: gradient nau den doc + cham mo rat nhe."""
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / float(H - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * k)
                  for i in range(3))
        d.line([(0, y), (W, y)], fill=c + (255,))
    rng = random.Random(7)
    for _ in range(260):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        a = rng.randint(6, 20)
        d.point((x, y), fill=(255, 230, 190, a))
    return img


_PARTICLES = None


def _particles():
    global _PARTICLES
    if _PARTICLES is None:
        rng = random.Random(31)
        _PARTICLES = [(rng.uniform(0.02, 0.98), rng.uniform(0.0, 1.0),
                       rng.uniform(6, 20), rng.choice([2, 3, 3, 4]),
                       rng.uniform(0, 6.28)) for _ in range(46)]
    return _PARTICLES


def draw_particles(img, t, strength=1.0):
    """Hat pixel bay cham len tren + nhap nhay (khong khi san khau)."""
    d = ImageDraw.Draw(img, "RGBA")
    for (fx, ph, sp, sz, ph2) in _particles():
        y = ((ph - t * sp / H) % 1.0) * H
        x = fx * W + math.sin(t * 0.6 + ph2) * 12
        a = int(120 * strength * (0.5 + 0.5 * math.sin(t * 2.0 + ph2 * 3)))
        if a > 10:
            d.rectangle([x, y, x + sz, y + sz],
                        fill=(255, 232, 190, a))


def stage_bg(t):
    """Set san khau: vach go, 2 khung tranh, ke sach, tham do, den roi, hat."""
    img = bg_plain()
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(56, 566, 46):                       # vach go ngang
        d.line([(0, y), (W, y)], fill=(0, 0, 0, 70), width=2)
    for bx in (70, 1010):                               # khung tranh
        d.rectangle([bx, 84, bx + 180, 224], outline=(112, 74, 42, 255),
                    width=6)
    for i, c in enumerate([(120, 70, 40), (60, 90, 80), (140, 110, 50),
                           (90, 50, 90)]):              # sach duoi trai
        d.rectangle([80 + i * 26, 566, 98 + i * 26, 626], fill=c + (255,))
    d.rectangle([66, 626, 220, 634], fill=(112, 74, 42, 255))
    d.rectangle([0, 560, W, H], fill=(16, 8, 5, 110))  # san toi
    d.polygon([(300, 720), (520, 585), (900, 585), (1120, 720)],
              fill=(122, 28, 24, 255))                  # tham do
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))       # con den roi
    od = ImageDraw.Draw(ov)
    od.polygon([(560, 0), (720, 0), (1060, 600), (220, 600)],
               fill=(255, 240, 210, 26))
    img.alpha_composite(ov)
    draw_particles(img, t)
    return img


# =====================================================================
# 1. HOOK-THE - 5 the xoe quat tu duoi len + cau hoi lon (mock-2)
# =====================================================================
CARD_COLS = [(96, 96, 104), (38, 92, 84), (198, 102, 44),
             (226, 214, 196), (172, 46, 36)]


def _one_card(colr, with_ai=False):
    card = Image.new("RGBA", (200, 270), colr + (255,))
    cd = ImageDraw.Draw(card)
    dark = tuple(max(0, v - 45) for v in colr)
    cd.rectangle([10, 10, 190, 260], outline=(10, 6, 4, 255), width=4)
    cd.rectangle([10, 10, 190, 66], fill=dark + (255,))
    if with_ai:
        f = _font(PS, 22)
        cd.text((100 - _tw(cd, "AI", f) / 2, 24), "AI", font=f,
                fill=(23, 11, 6, 255))
    return card


def hook_cards(t, dur, p):
    img = bg_plain()
    draw_pop_text(img, p["kicker"], 94, 40, CREAM, t, 0.10)
    f = _font(SANS, 92)
    segs = [(p["pre"], CREAM), (p["accent"], col_of(p["accent_col"], RED))]
    total = sum(_tw(_DUMMY, s, f) for s, _ in segs)
    size = 92
    while total > 1160 and size > 40:
        size -= 6
        f = _font(SANS, size)
        total = sum(_tw(_DUMMY, s, f) for s, _ in segs)
    draw_mixed_pop(img, segs, 186, size, t, 0.30)
    draw_pop_text(img, p["sub"], 272, 40, CREAM, t, 0.55)
    cx, cy = W // 2, 800
    for i, colr in enumerate(CARD_COLS):
        ang = math.radians(-34 + i * 17)
        start = 0.50 + i * 0.11
        pr = ease_out_cubic((t - start) / 0.45)
        if pr <= 0:
            continue
        rot = math.degrees(ang) * (0.35 + 0.65 * pr)
        card = _one_card(colr, with_ai=(i == 3)).rotate(
            rot, resample=Image.BICUBIC, expand=True)
        px = cx + int(math.sin(ang) * 300) - card.width // 2
        py = cy - int(math.cos(ang) * 300) - card.height // 2 + 60 \
            + int((1 - pr) * 420)
        img.alpha_composite(card, (px, py))
    return img


# =====================================================================
# 2. DONG DAU - chu lon + tem do dong xuong, rung (SPEC muc 6.2)
# =====================================================================
def stamp_big(t, dur, p):
    img = bg_plain()
    size, lines = fit_lines(p["big"], 1120, 108, 44, SANS, max_lines=2)
    cy = 268 if len(lines) > 1 else 300
    for j, ln in enumerate(lines):
        draw_pop_text(img, ln, cy + j * int(size * 1.18), size,
                      col_of(p["big_col"], CREAM), t, 0.12 + j * 0.1)
    stamp_at = float(p["_stamp_at"])
    if t >= stamp_at:
        sp = clamp((t - stamp_at) / 0.10)
        sc = 2.4 - 1.4 * ease_in_quad(sp)
        f = _font(PS, 54)
        tw = _tw(_DUMMY, p["stamp"], f)
        lay = Image.new("RGBA", (int(tw + 68), 128), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rectangle([4, 4, tw + 62, 122], outline=RED + (255,), width=8)
        ld.text((34, 36), p["stamp"], font=f, fill=RED + (255,))
        lay = lay.resize((max(2, int(lay.width * sc)),
                          max(2, int(lay.height * sc))), Image.NEAREST)
        lay = lay.rotate(-8, expand=True, resample=Image.NEAREST)
        stamp_cy = cy + len(lines) * int(size * 1.18) + 10
        img.alpha_composite(lay, (int(880 - lay.width / 2),
                                  int(stamp_cy - lay.height / 2)))
    if p["sub"]:
        draw_pop_text(img, p["sub"], 540, 38, TEAL, t, stamp_at + 0.28,
                      path=VT)
    return fx_shake(img, t, stamp_at, mag=7, dur=0.09)


# =====================================================================
# 3. CUA SO GIA - khung chat/file, go tung dong + con tro (mock-3)
# =====================================================================
def type_window(t, dur, p):
    img = bg_plain()
    lines = [x for x in p["lines"].split("|")]
    cols = [col_of(c) for c in p["colors"].split(",")] or [CREAM]
    has_head = bool(p["head_small"] or p["head_big"])
    if has_head:
        draw_pop_text(img, p["head_small"], 118, 44, CREAM, t, 0.10, cx=228)
        draw_pop_text(img, p["head_big"], 200, 72,
                      col_of(p["head_col"], TEAL), t, 0.30, cx=228)
        wx0, wy0, wx1, wy1 = 460, 90, 1210, 560
        lx = 500
    else:
        wx0, wy0, wx1, wy1 = 190, 80, 1090, 600
        lx = 235
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=14, fill=(18, 13, 18),
                        outline=(90, 80, 90), width=3)
    d.rounded_rectangle([wx0, wy0, wx1, wy0 + 50], radius=14,
                        fill=(36, 28, 38))
    d.rectangle([wx0, wy0 + 30, wx1, wy0 + 50], fill=(36, 28, 38))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([wx0 + 25 + i * 34, wy0 + 14, wx0 + 47 + i * 34,
                   wy0 + 36], fill=c)
    d.text((wx0 + 130, wy0 + 12), p["title"], font=_font(VT, 30), fill=CREAM)
    # lich go chu: moi dong 1 khoang, tinh tu beats da chuan bi o scenes
    starts = p["_line_starts"]
    f = _font(VT, 40)
    cur = None
    for i, ln in enumerate(lines):
        st, en = starts[i]
        if t < st:
            break
        prog = clamp((t - st) / max(0.05, en - st))
        n = int(prog * len(ln) + 0.5)
        y = wy0 + 84 + i * 56
        d.text((lx, y), ln[:n], font=f, fill=cols[i % len(cols)])
        cur = (lx + _tw(d, ln[:n], f) + 4, y)
        if prog >= 1.0:
            cur = (lx + _tw(d, ln, f) + 4, y)
    if cur is not None and int(t * 2.4) % 2 == 0:
        d.rectangle([cur[0], cur[1] + 4, cur[0] + 16, cur[1] + 34],
                    fill=CREAM)
    return img


# =====================================================================
# 4. SAN KHAU CHU - set phong + den roi + chu lon (mock-1 v2, KHONG linh vat)
# =====================================================================
def stage_text(t, dur, p):
    img = stage_bg(t)
    draw_pop_text(img, p["small"], 196, 46, CREAM, t, 0.15)
    draw_pop_text(img, p["big1"], 292, 104, CREAM, t, 0.45)
    draw_pop_text(img, p["big2"], 408, 104, col_of(p["big2_col"], RED),
                  t, 0.80)
    if p["sub"]:
        draw_pop_text(img, p["sub"], 566, 34, TEAL, t, 1.15, path=VT)
    glitch_at = float(p["_glitch_at"])
    if glitch_at <= t <= glitch_at + 0.25:
        img = fx_rgb_split(img, amp=6)
        img = fx_glitch_slices(img, t, glitch_at, 0.25)
    return img


# =====================================================================
# 5. SO SANH A/B - trai xam rong vs phai day du (SPEC muc 6.5)
# =====================================================================
def _panel_left(img, x0, y0, x1, y1, t):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0, y0, x1, y1], fill=(46, 46, 52, 255),
                outline=(90, 90, 98), width=4)
    rng = random.Random(5)
    for _ in range(240):
        x = rng.randint(x0 + 8, x1 - 8)
        y = rng.randint(y0 + 8, y1 - 8)
        v = rng.randint(52, 86)
        d.point((x, y), fill=(v, v, v + 6, 255))
    for yy in range(y0 + 26, y1 - 10, 34):          # scanline mo
        # alpha PHAI la 255: ImageDraw khong tron alpha, de 10 thi luc
        # phang hoa RGB se thanh soc trang sang (loi da thay o ban mau 1)
        d.line([(x0 + 10, yy), (x1 - 10, yy)], fill=(74, 74, 82, 255),
               width=2)


def _panel_right(img, x0, y0, x1, y1, t):
    d = ImageDraw.Draw(img)
    for yy in range(y0, y1):                        # troi gradient
        k = (yy - y0) / float(y1 - y0)
        c = (int(24 + 160 * k), int(70 + 60 * k), int(96 - 30 * k))
        d.line([(x0, yy), (x1, yy)], fill=c)
    sx, sy = x1 - 120, y0 + 74                      # mat troi pixel
    d.rectangle([sx - 26, sy - 26, sx + 26, sy + 26], fill=(255, 176, 66))
    d.rectangle([sx - 34, sy - 10, sx + 34, sy + 10], fill=(255, 176, 66, 0))
    d.polygon([(x0, y1 - 90), (x0 + 150, y0 + 130), (x0 + 300, y1 - 90)],
              fill=(30, 52, 74))                    # nui trai
    d.polygon([(x0 + 190, y1 - 70), (x0 + 360, y0 + 170), (x1, y1 - 70)],
              fill=(22, 40, 60))                    # nui phai
    d.rectangle([x0, y1 - 46, x1, y1], fill=(24, 66, 52))
    rng = random.Random(9)
    for _ in range(26):                             # sao/sang lap lanh
        x = rng.randint(x0 + 10, x1 - 10)
        y = rng.randint(y0 + 10, y0 + 130)
        if int(t * 2 + x) % 3:
            d.rectangle([x, y, x + 4, y + 4], fill=(255, 244, 200))
    d.rectangle([x0, y0, x1, y1], outline=TEAL, width=4)


def ab_compare(t, dur, p):
    img = bg_plain()
    draw_pop_text(img, p["head"], 84, 44, CREAM, t, 0.10)
    if t >= 0.35:
        _panel_left(img, 70, 150, 600, 560, t)
    if t >= 0.75:
        _panel_right(img, 680, 150, 1210, 560, t)
    if t >= 1.0:                                    # huy hieu VS
        d = ImageDraw.Draw(img)
        d.ellipse([592, 307, 688, 403], fill=(16, 10, 8),
                  outline=CREAM, width=3)
        f = _font(PS, 26)
        d.text((640 - _tw(d, "VS", f) / 2, 342), "VS", font=f, fill=YELLOW)
    draw_pop_text(img, p["label_a"], 606, 36, GREY_TXT, t, 1.10, cx=335)
    draw_pop_text(img, p["label_b"], 606, 36, TEAL, t, 1.25, cx=945)
    return img


# =====================================================================
# 6. HANG MUC HIEN DAN - cac muc pop lan luot (SPEC muc 6.6)
# =====================================================================
_GLYPHS = ["doc", "grid", "play", "bars", "wave", "star"]


def _glyph(d, kind, x, y, s, colr):
    if kind == "doc":
        d.rectangle([x + 12, y + 6, x + s - 12, y + s - 6], outline=colr,
                    width=4)
        for i in range(3):
            d.line([(x + 20, y + 18 + i * 12), (x + s - 20, y + 18 + i * 12)],
                   fill=colr, width=3)
    elif kind == "grid":
        d.rectangle([x + 8, y + 8, x + s - 8, y + s - 8], outline=colr,
                    width=4)
        d.line([(x + s / 2, y + 8), (x + s / 2, y + s - 8)], fill=colr,
               width=3)
        d.line([(x + 8, y + s / 2), (x + s - 8, y + s / 2)], fill=colr,
               width=3)
    elif kind == "play":
        d.polygon([(x + 18, y + 10), (x + 18, y + s - 10),
                   (x + s - 14, y + s / 2)], fill=colr)
    elif kind == "bars":
        for i, hh in enumerate([18, 30, 24, 38]):
            d.rectangle([x + 10 + i * 12, y + s - 8 - hh, x + 18 + i * 12,
                         y + s - 8], fill=colr)
    elif kind == "wave":
        pts = [(x + 6 + i * 6, y + s / 2 + int(14 * math.sin(i * 0.9)))
               for i in range(8)]
        d.line(pts, fill=colr, width=4)
    else:  # star
        cx, cy = x + s / 2, y + s / 2
        d.polygon([(cx, cy - 20), (cx + 6, cy - 6), (cx + 20, cy),
                   (cx + 6, cy + 6), (cx, cy + 20), (cx - 6, cy + 6),
                   (cx - 20, cy), (cx - 6, cy - 6)], fill=colr)


def item_rows(t, dur, p):
    img = bg_plain()
    draw_pop_text(img, p["title"], 92, 50, CREAM, t, 0.10)
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    starts = p["_starts"]
    d = ImageDraw.Draw(img)
    for i, it in enumerate(items):
        if t < starts[i]:
            continue
        sc = pop_scale(t, starts[i], 0.2)
        y = 168 + i * 86
        lay = Image.new("RGBA", (1100, 76), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 6, 64, 70], fill=(28, 17, 11, 255),
                     outline=TEAL, width=3)
        _glyph(ld, _GLYPHS[i % len(_GLYPHS)], 4, 10, 56, TEAL)
        ld.text((84, 22), "%02d" % (i + 1), font=_font(PS, 20), fill=TEAL)
        ld.text((170, 14), it, font=_font(SANS, 42), fill=CREAM)
        nw, nh = max(2, int(1100 * sc)), max(2, int(76 * sc))
        lay = lay.resize((nw, nh), Image.LANCZOS)
        img.alpha_composite(lay, (90, int(y - nh / 2 + 38)))
    return img


# =====================================================================
# 7. BO DEM LON - so pixel chay tang + song am (mock-4)
# =====================================================================
def big_counter(t, dur, p):
    img = bg_plain()
    target = float(p["_target"])
    count_dur = float(p["_count_dur"])
    pr = ease_out_cubic((t - 0.20) / max(0.05, count_dur))
    val = int(target * pr)
    txt = "{:,}".format(val).replace(",", ".")
    draw_text_c(img, txt, 150, 108, CREAM, path=PS)
    if t >= 0.20 + count_dur * 0.55:
        draw_pop_text(img, p["label"], 292, 58, col_of(p["label_col"], RED),
                      t, 0.20 + count_dur * 0.55)
    if t >= 0.20:                                   # song am nhay
        d = ImageDraw.Draw(img)
        rng = random.Random(7)
        base = [rng.randint(14, 74) for _ in range(48)]
        for i in range(48):
            wob = 0.72 + 0.28 * math.sin(t * 3.1 + i * 0.7)
            hb = int(base[i] * wob)
            x = 190 + i * 19
            d.rectangle([x, 400 - hb // 2, x + 9, 400 + hb // 2], fill=TEAL)
    if p["sub"]:
        draw_pop_text(img, p["sub"], 560, 36, YELLOW, t,
                      0.20 + count_dur + 0.3, path=VT)
    return img


# =====================================================================
# 8. LUOI O - o danh so hien dan (mock-4 phan duoi)
# =====================================================================
def cell_grid(t, dur, p):
    img = bg_plain()
    draw_pop_text(img, p["title"], 84, 52, CREAM, t, 0.10)
    cols = int(float(p["_cols"]))
    rows = int(float(p["_rows"]))
    total = int(float(p["_total"]))
    cell, gap = 92, 14
    gw = cols * cell + (cols - 1) * gap
    gh = rows * cell + (rows - 1) * gap
    x0 = (W - gw) // 2
    y0 = (H - gh) // 2 + 26
    step = float(p["_step"])
    d = ImageDraw.Draw(img)
    for i in range(total):
        at = 0.40 + i * step
        if t < at:
            continue
        sc = pop_scale(t, at, 0.16)
        r, c = divmod(i, cols)
        cx0 = x0 + c * (cell + gap)
        cy0 = y0 + r * (cell + gap)
        sz = int(cell * min(1.0, sc + 0.15))
        ox, oy = cx0 + (cell - sz) // 2, cy0 + (cell - sz) // 2
        outline = RED if i == total - 1 else TEAL
        d.rounded_rectangle([ox, oy, ox + sz, oy + sz], radius=10,
                            outline=outline, width=3)
        if sc > 0.55:
            f = _font(PS, 19)
            n = str(i + 1)
            d.text((cx0 + cell / 2 - _tw(d, n, f) / 2, cy0 + cell / 2 - 12),
                   n, font=f, fill=CREAM)
    if p["caption"]:
        draw_pop_text(img, p["caption"], y0 + gh + 44, 34, YELLOW, t,
                      0.40 + total * step + 0.15, path=VT)
    return img


# =====================================================================
# 9. THANH TIEN TRINH / THANH HP-MANA (mock-5 + bien the game)
# =====================================================================
def progress_bar(t, dur, p):
    img = bg_plain()
    pct = float(p["_pct"])
    fill_dur = float(p["_fill_dur"])
    t_lines = float(p["_t_lines"])
    variant = p["variant"].strip().lower()
    pr = ease_out_cubic((t - 0.25) / max(0.05, fill_dur))
    cur = pct * pr
    d = ImageDraw.Draw(img)
    if variant == "hp":
        f = _font(PS, 44)
        d.text((90, 84), "HP", font=f, fill=TEAL)
        seg_n = 12
        seg_w = (1100 - (seg_n - 1) * 8) / seg_n
        lit = int(round(seg_n * cur / 100.0))
        for i in range(seg_n):
            x = 90 + i * (seg_w + 8)
            colr = TEAL if i < lit else (60, 44, 34)
            d.rectangle([x, 168, x + seg_w, 214], fill=colr,
                        outline=CREAM, width=2)
        f2 = _font(PS, 30)
        d.text((90, 240), "%d%%" % int(round(cur)), font=f2, fill=YELLOW)
        ly = 330
    else:
        f = _font(PS, 58)
        d.text((90, 74), "%d%%" % int(round(cur)), font=f, fill=TEAL)
        d.rounded_rectangle([90, 168, 1190, 224], radius=26,
                            outline=CREAM, width=4)
        if cur > 0.5:
            fw = int((1190 - 98) * cur / 100.0)
            d.rounded_rectangle([98, 176, 98 + fw, 216], radius=18,
                                fill=TEAL)
        ly = 300
    # 3 dong text canh trai (le trai nhu mock-5), pop lan luot
    d = ImageDraw.Draw(img)
    entries = [(p["line1"], 50, CREAM, t_lines),
               (p["question"], 62, col_of(p["question_col"], YELLOW),
                t_lines + 0.55),
               (p["answer"], 52, CREAM, t_lines + 1.10)]
    yy = ly
    for txt, size, colr, at in entries:
        if t >= at and txt:
            sc = pop_scale(t, at, 0.2)
            f = _font(SANS, size)
            lay = Image.new("RGBA", (int(_tw(_DUMMY, txt, f)) + 16,
                                     int(size * 1.5) + 16), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.text((8, 8), txt, font=f, fill=colr + (255,))
            nw, nh = max(2, int(lay.width * sc)), max(2, int(lay.height * sc))
            lay = lay.resize((nw, nh), Image.LANCZOS)
            img.alpha_composite(lay, (82, int(yy - nh / 2 + size / 2)))
        yy += 92
    return img


# =====================================================================
# 10. MAN HINH CUOI - nut THEO DOI + con tro bam (mock-5 phan duoi)
# =====================================================================
def follow_end(t, dur, p):
    img = bg_plain()
    draw_pop_text(img, p["main"], 200, 56, CREAM, t, 0.15)
    if p["accent"] and p["accent"] in p["sub"]:
        a, b = p["sub"].split(p["accent"], 1)
        segs = [(a, CREAM), (p["accent"], col_of(p["accent_col"], RED)),
                (b, CREAM)]
        segs = [s for s in segs if s[0]]
        draw_mixed_pop(img, segs, 292, 60, t, 0.60)
    else:
        draw_pop_text(img, p["sub"], 292, 60, CREAM, t, 0.60)
    click_at = float(p["_click_at"])
    bx0, by0, bx1, by1 = 430, 500, 850, 580
    clicked = t >= click_at
    if t >= 1.0:
        sc = pop_scale(t, 1.0, 0.2)
        if clicked and t < click_at + 0.08:
            sc *= 0.93
        lay = Image.new("RGBA", (bx1 - bx0 + 40, by1 - by0 + 40),
                        (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        colr = TEAL if clicked else RED
        txt = p["done_text"] if clicked else p["button"]
        ld.rounded_rectangle([20, 20, bx1 - bx0 + 20, by1 - by0 + 20],
                             radius=38, fill=colr + (255,))
        f = _font(SANS, 36)
        ld.text(((lay.width - _tw(ld, txt, f)) / 2, 20 + (by1 - by0) / 2 - 24),
                txt, font=f, fill=(255, 255, 255, 255))
        nw, nh = max(2, int(lay.width * sc)), max(2, int(lay.height * sc))
        lay = lay.resize((nw, nh), Image.LANCZOS)
        img.alpha_composite(lay, (int(640 - nw / 2), int(540 - nh / 2)))
        if clicked and t < click_at + 0.30:         # vong click lan ra
            rr = (t - click_at) / 0.30 * 60
            d = ImageDraw.Draw(img, "RGBA")
            d.ellipse([790 - rr, 540 - rr, 790 + rr, 540 + rr],
                      outline=(255, 255, 255, int(160 * (1 - rr / 60))),
                      width=4)
    if p["side_text"]:
        draw_pop_text(img, p["side_text"], 540, 38, CREAM, t, 1.15, cx=1042)
    # con tro: bay vao tu goc duoi phai, dung lai o nut
    move = clamp((t - (click_at - 0.45)) / 0.45)
    if move > 0:
        me = ease_out_cubic(move)
        cxp = 1150 + (800 - 1150) * me
        cyp = 700 + (560 - 700) * me
        d = ImageDraw.Draw(img)
        d.polygon([(cxp, cyp), (cxp, cyp + 44), (cxp + 16, cyp + 32),
                   (cxp + 26, cyp + 52), (cxp + 34, cyp + 48),
                   (cxp + 24, cyp + 28), (cxp + 40, cyp + 28)],
                  fill=CREAM, outline=(10, 6, 4))
    return img


# =====================================================================
# 11. COMBO - x2 x3 x4... + thanh nang luong kieu game (mock-6)
# =====================================================================
def combo_chain(t, dur, p):
    img = bg_plain()
    draw_pop_text(img, p["label"], 92, 46, CREAM, t, 0.10, path=PS)
    start_x = int(float(p["_start_x"]))
    max_x = int(float(p["_max_x"]))
    step = float(p["_step"])
    cur = start_x
    last_at = 0.35
    for n in range(start_x, max_x + 1):
        at = 0.35 + (n - start_x) * step
        if t >= at:
            cur, last_at = n, at
    big = "x%d" % cur
    sc = pop_scale(t, last_at, 0.18) if t >= 0.35 else 0.0
    if sc > 0:
        draw_pop_text(img, big, 218, 104, RED, t, last_at, path=PS)
    seg_n = 10
    lit = int(round(seg_n * (cur - start_x + 1) / float(max_x - start_x + 1)))
    bw = (920 - (seg_n - 1) * 8) / seg_n
    x0 = (W - 920) // 2
    d = ImageDraw.Draw(img)
    for i in range(seg_n):
        x = x0 + i * (bw + 8)
        colr = TEAL if i < lit else (60, 44, 34)
        d.rectangle([x, 330, x + bw, 366], fill=colr, outline=CREAM, width=2)
    if t >= 0.35:
        draw_pop_text(img, p["plus_text"], 442, 54, YELLOW, t, last_at)
    base_y = 596
    n_steps = max_x - start_x + 1
    for i, n in enumerate(range(start_x, max_x + 1)):
        at = 0.35 + i * step
        if t < at:
            continue
        # bac thang trai deu trong khung 240..940 (keo ca duong ke 120px
        # van nam gon trong man hinh ke ca bac cao nhat)
        x = 240 + (i * 700 // max(1, n_steps - 1) if n_steps > 1 else 0)
        y = base_y - i * 34
        c = TEAL if n < max_x else RED
        d.text((x, y), "x%d" % n, font=_font(PS, 26), fill=c)
        d.rectangle([x, y + 46, x + 120, y + 53], fill=c)
    if p["caption"]:
        draw_pop_text(img, p["caption"], 676, 32, (200, 180, 160), t,
                      0.35 + (max_x - start_x) * step + 0.3, path=VT)
    return img
