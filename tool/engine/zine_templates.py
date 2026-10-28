#!/usr/bin/env python3
"""ZINE TEMPLATES - goi phong cach "ZINE" (cat dan tap chi).

Theo mock zine-c1..c3: chu = cac O CAT DAN - moi tu 1 o rieng, nen o
luan phien (den/trang bao/do/vang/xanh duong), font luan phien (Noto
Sans Black / Noto Serif Black / JetBrains Mono / Itim), moi o nghieng
ngau nhien +-3 do, bong giay, vai o co bang dinh/ghim do. Nen giay bao
mo tong xam kem. O tu xao font/mau/goc theo SEED cua job (p["_seed"]
do zine_scenes tiem): cung job render lai = cung ket qua, job khac =
to hop khac - day la bien the ruot cua goi.

Hieu ung rieng: o dan vao tung cai (bay vao + dap lech + rung rat nhe),
xe giay chuyen canh o dau shot, ghim/bang dinh xuat hien theo o.
Moi ham fn(t, dur, p) -> RGBA 1280x720.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")
SERIF = str(_FONT_DIR / "NotoSerif-Black.ttf")
JB = str(_FONT_DIR / "JetBrainsMono-Bold.ttf")
ITIM = str(_FONT_DIR / "Itim-Regular.ttf")
FALLBACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"

W, H = 1280, 720
PAPER_BG = (232, 226, 212)
INK = (18, 18, 18)
WHITE_P = (247, 244, 236)
RED = (217, 43, 31)
YELLOW = (255, 200, 0)
BLUE = (36, 86, 200)
NEWS_INK = (105, 96, 82)

# (nen o, mau chu, font) - luan phien theo seed
STYLES = [
    (INK, (255, 255, 255), SANS),
    (WHITE_P, INK, SERIF),
    (RED, (255, 255, 255), SANS),
    (YELLOW, INK, SANS),
    (BLUE, (255, 255, 255), JB),
    (WHITE_P, INK, ITIM),
    (WHITE_P, RED, SANS),
    (INK, YELLOW, JB),
]
GREY_STYLES = [
    ((120, 118, 110), (235, 232, 224), SANS),
    ((210, 206, 196), (110, 108, 100), SERIF),
    ((150, 148, 140), (240, 238, 230), JB),
    ((190, 186, 176), (90, 88, 82), ITIM),
]


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


def ease_out_back(k, s=1.4):
    k = clamp(k)
    return 1 + (s + 1) * (k - 1) ** 3 + s * (k - 1) ** 2


# ------------------------------------------------------------------ nen bao
_BG = None

_NEWS_FRAGS = [
    "the quick brown fox jumps over the lazy dog while the editor",
    "watches the deadline approaching and the whole newsroom holds",
    "its breath waiting for the final numbers to come in tonight",
    "tat ca va noi dung phai giu chan nguoi xem den tan giay cuoi",
    "cung cua video khong ai cho doi mot video cham chan ba giay",
    "dau tien quyet dinh tat ca va noi dung phai giu chan nguoi",
]


def bg():
    global _BG
    if _BG is not None:
        return _BG.copy()
    img = Image.new("RGBA", (W, H), PAPER_BG + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(17)
    for _ in range(900):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        d.point((x, y), fill=(120, 105, 80, rng.randint(5, 12)))
    col_w = 236
    f = _font(SERIF, 14)
    words = []
    for frag in _NEWS_FRAGS:
        words += frag.split()
    lines, cur = [], ""
    for w_ in words * 8:                       # cat dong vua chieu rong cot
        trial = (cur + " " + w_).strip()
        if _tw(trial, f) <= col_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    for ci in range(5):
        x0 = 26 + ci * (col_w + 18)
        head = "TIN TỨC" if ci % 2 == 0 else "THE NEWS"
        d.text((x0, 26), head, font=_font(SERIF, 30),
               fill=NEWS_INK + (64,))
        d.line([(x0, 66), (x0 + col_w, 66)], fill=NEWS_INK + (70,),
               width=2)
        y = 80
        li = ci * 3
        while y < H - 20:
            d.text((x0, y), lines[li % len(lines)], font=f,
                   fill=NEWS_INK + (52,))
            y += 21
            li += 1
    _BG = img
    return _BG.copy()


def tape_wipe(img, t, dur_in=0.50):
    """Dai bang dinh keo ngang LAU canh (fx=tape): dai bang dinh ban
    trong vang nhat, nghieng nhe, quet trai -> phai trong dur_in dau
    shot; mep dan co vet sang. Sau khi quet xong thi bien mat."""
    if t >= dur_in:
        return img
    pr = ease_out_cubic(t / dur_in)
    cx = -260 + (W + 520) * pr
    lay = Image.new("RGBA", (360, H + 320), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([30, 0, 330, H + 320], fill=(246, 231, 183, 150))
    ld.rectangle([30, 0, 52, H + 320], fill=(255, 246, 214, 190))
    ld.rectangle([308, 0, 330, H + 320], fill=(214, 196, 148, 150))
    for yy in range(40, H + 320, 90):       # vet mo ngang cua bang dinh
        ld.line([(36, yy), (324, yy)], fill=(255, 255, 255, 36), width=3)
    lay = lay.rotate(-7, expand=True, resample=Image.BICUBIC)
    out = img.copy()
    out.alpha_composite(lay, (int(cx - lay.width / 2), -160))
    return out


def tear_in(img, t, dur_in=0.30):
    """Xe giay dau shot: tam bao phu truot len tren, mep duoi rang cua."""
    if t >= dur_in:
        return img
    pr = ease_out_cubic(t / dur_in)
    cover = bg()
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    edge = int(H * (1 - pr))
    pts = [(0, 0), (W, 0)]
    x = W
    rng = random.Random(3)
    while x > 0:
        pts.append((x, edge + rng.randint(-9, 9)))
        x -= rng.randint(36, 70)
    pts.append((0, edge))
    md.polygon(pts, fill=255)
    out = img.copy()
    out.paste(cover, (0, 0), mask)
    return out


# ------------------------------------------------------------------ o dan
def make_tile(text, style, size, rng, pad_x=26, pad_y=14):
    """1 o cat dan (chua xoay): nen + chu + bong nhe o trong layer."""
    bgc, fgc, path = style
    f = _font(path, size)
    tw = int(_tw(text, f))
    wdt, hgt = tw + pad_x * 2, int(size * 1.32) + pad_y * 2
    lay = Image.new("RGBA", (wdt + 14, hgt + 14), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([7 + 5, 7 + 6, 7 + wdt + 5, 7 + hgt + 6],
                 fill=(40, 32, 20, 66))
    ld.rectangle([7, 7, 7 + wdt, 7 + hgt], fill=bgc + (255,))
    ld.text((7 + pad_x, 7 + pad_y - size * 0.06), text, font=f,
            fill=fgc + (255,))
    return lay


def paste_tile(img, lay, cx, cy, ang):
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2),
                              int(cy - lay.height / 2)))
    return lay.width, lay.height


def pin(img, cx, cy, r=13):
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - r + 3, cy - r + 4, cx + r + 3, cy + r + 4],
              fill=(40, 30, 20, 70))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED + (255,))
    d.ellipse([cx - r // 2, cy - r // 2 - 2, cx - 1, cy - 3],
              fill=(255, 170, 160, 255))


def tape(img, cx, cy, wdt=110, ang=-12):
    lay = Image.new("RGBA", (wdt + 16, 46), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([8, 10, wdt + 8, 36], fill=(246, 231, 183, 175))
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2),
                              int(cy - lay.height / 2)))


def slam_scale(t, at, dur=0.13):
    """He so phong khi o dap xuong: 1.3 -> 1 (ease-out), 0 neu chua toi."""
    if t < at:
        return 0.0
    k = clamp((t - at) / dur)
    return 1.3 - 0.3 * ease_out_cubic(k)


def place_tile(img, text, style, size, cx, cy, t, at, rng, with_pin=False,
               with_tape=False):
    """Dan 1 o tai (cx, cy) khi t >= at, kem goc nghieng tu rng.
    Tra (w, h) cua o (da xoay) hoac (0, 0) neu chua dan."""
    sc = slam_scale(t, at)
    if sc <= 0:
        return (0, 0)
    lay = make_tile(text, style, size, rng)
    if sc != 1.0:
        lay = lay.resize((max(2, int(lay.width * sc)),
                          max(2, int(lay.height * sc))), Image.LANCZOS)
    ang = rng.uniform(-3, 3)
    wdt, hgt = paste_tile(img, lay, cx, cy + int((1 - sc) * -26), ang)
    if with_pin and t >= at + 0.05:
        pin(img, cx, cy - hgt / 2 + 8)
    if with_tape and t >= at + 0.05:
        tape(img, cx - wdt // 4, cy - hgt / 2 + 4, 100, ang - 10)
    return (wdt, hgt)


def word_tiles(img, text, cy, size, t, start_at, step, seed, styles=None,
               align="c", x_left=90, max_w=1180, jitter=False):
    """Dan tung TU cua 1 cau thanh o (xep 1-2 dong theo chieu rong).
    Tra (so o da dan, y dong cuoi)."""
    rng = random.Random(seed)
    styles = styles or STYLES
    words = [w for w in text.split() if w]
    if not words:
        return (0, cy)
    off = rng.randrange(len(styles))
    # do rong tung tu theo font cua style tuong ung
    rows, cur, cur_w = [], [], 0
    for i, w_ in enumerate(words):
        st = styles[(off + i) % len(styles)]
        f = _font(st[2], size)
        wdt = _tw(w_, f) + 52 + 22
        if cur and cur_w + wdt > max_w:
            rows.append(cur)
            cur, cur_w = [], 0
        cur.append((w_, st, wdt))
        cur_w += wdt
    if cur:
        rows.append(cur)
    idx = 0
    yy = cy
    for row in rows[:2]:
        total = sum(w for _t, _s, w in row)
        x = (W - total) / 2 + (row[0][2]) / 2 if align == "c" \
            else x_left + row[0][2] / 2
        for (w_, st, wdt) in row:
            at = start_at + idx * step
            jx = jy = 0
            if jitter and t >= at:
                # fx=jitter: o chu RUNG +-2px theo nhip ~9 lan/giay
                ph = int(t * 9)
                jx = 2 if ph % 2 == 0 else -2
                jy = -1 if ph % 3 == 0 else 1
            place_tile(img, w_, st, size, x + jx, yy + jy, t, at, rng,
                       with_tape=(idx % 4 == 2))
            x += wdt
            idx += 1
        yy += int(size * 1.32) + 34
    return (idx, yy)


def starburst(img, lines, cx, cy, t, at, col=RED, txt_col=(255, 255, 255),
              size=40, radius=150, ang=-10, fit=False):
    """Nhan sao bung (starburst) kieu nhan gia: dan vao + xoay.

    fit=True: tu co co chu cho dong dai nhat nam gon trong vung phang
    cua sao (<= 1.32 * radius) thay vi tran ra mep."""
    sc = slam_scale(t, at, 0.14)
    if sc <= 0:
        return
    lay = Image.new("RGBA", (radius * 2 + 30, radius * 2 + 30),
                    (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ccx, ccy = radius + 15, radius + 15
    pts = []
    rng = random.Random(9)
    for i in range(32):
        a = i * math.pi / 16
        r = radius if i % 2 == 0 else radius * (0.78 + rng.uniform(0, 0.06))
        pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    ld.polygon(pts, fill=col + (255,))
    if fit and lines:
        while size > 18:
            f0 = _font(SANS, size)
            if max(_tw(ln, f0) for ln in lines) <= radius * 1.32:
                break
            size -= 2
    f = _font(SANS, size)
    ty = ccy - len(lines) * size * 0.62
    for ln in lines:
        ld.text((ccx - _tw(ln, f) / 2, ty), ln, font=f,
                fill=txt_col + (255,))
        ty += size * 1.24
    lay = lay.resize((max(2, int(lay.width * sc)),
                      max(2, int(lay.height * sc))), Image.LANCZOS)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2),
                              int(cy - lay.height / 2)))


def hand_arrow(img, x0, y0, x1, y1, col=RED):
    d = ImageDraw.Draw(img)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 46
    pts = []
    for i in range(21):
        k = i / 20.0
        px = (1 - k) ** 2 * x0 + 2 * (1 - k) * k * mx + k * k * x1
        py = (1 - k) ** 2 * y0 + 2 * (1 - k) * k * my + k * k * y1
        pts.append((px, py))
    d.line(pts, fill=col + (255,), width=6, joint="curve")
    ang = math.atan2(y1 - pts[-2][1], x1 - pts[-2][0])
    for da in (2.7, -2.7):
        hx = x1 - 30 * math.cos(ang + da * 0.22)
        hy = y1 - 30 * math.sin(ang + da * 0.22)
        d.line([(x1, y1), (hx, hy)], fill=col + (255,), width=6)


def fit_size(text, max_w, start, min_size, path=SANS):
    size = start
    while size > min_size:
        if _tw(text, _font(path, size)) <= max_w:
            return size
        size -= 4
    return min_size


def _lay(p):
    return int(p.get("_layout", 0))


def _seed(p, salt=0):
    return int(p.get("_seed", 12345)) + salt


def plain_text(img, text, cx, cy, size, col=INK, path=SANS):
    f = _font(path, size)
    tw = _tw(text, f)
    d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, cy - size / 2), text, font=f, fill=col + (255,))
    return tw


# =====================================================================
# 1. TILE HOOK - note xe ghim + headline o chu 2 dong (mock c1)
# =====================================================================
def tile_hook(t, dur, p):
    img = bg()
    lay = _lay(p)
    # note xe: giay trang lech, chu Itim, ghim do
    note_w, note_h = 520, 190
    nx = 150 if lay == 0 else W - 150 - note_w
    ny = 64
    if t >= 0.12:
        note = Image.new("RGBA", (note_w + 24, note_h + 24), (0, 0, 0, 0))
        nd = ImageDraw.Draw(note)
        pts = [(12, 12), (12 + note_w, 12), (12 + note_w, 12 + note_h)]
        rngj = random.Random(4)
        x = 12 + note_w
        while x > 12:                                # mep duoi rang cua
            pts.append((x, 12 + note_h - rngj.randint(0, 10)))
            x -= rngj.randint(30, 60)
        pts.append((12, 12 + note_h))
        nd.polygon([(px + 5, py + 6) for (px, py) in pts],
                   fill=(40, 32, 20, 60))
        nd.polygon(pts, fill=WHITE_P + (255,))
        # chu note: tu xuong dong theo tu + co co chu cho vua chieu
        # rong to giay (ban cu ve thang 1 dong -> tran ra ngoai giay)
        size = 50
        while size > 30:
            f = _font(ITIM, size)
            lines, cur = [], ""
            for w_ in p["note"].replace("\n", " ").split():
                trial = (cur + " " + w_).strip()
                if _tw(trial, f) <= note_w - 44 or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = w_
            if cur:
                lines.append(cur)
            if len(lines) <= 2:
                break
            size -= 4
        ty = 12 + (note_h - len(lines) * int(size * 1.24)) // 2 + 6
        for ln in lines[:2]:
            nd.text((12 + note_w / 2 - _tw(ln, f) / 2, ty), ln, font=f,
                    fill=INK + (255,))
            ty += int(size * 1.24)
        note = note.rotate(-2 if lay == 0 else 2, expand=True,
                           resample=Image.BICUBIC)
        img.alpha_composite(note, (nx - 12, ny - 12))
        pin(img, nx + note_w // 2, ny + 16, 14)
    align = "c" if lay == 0 else "l"
    word_tiles(img, p["head"], 356, 96, t, 0.45, 0.13, _seed(p, 1),
               align=align, x_left=110,
               jitter=("jitter" in str(p.get("fx", "") or "").lower()))
    if p["sub"]:
        word_tiles(img, p["sub"], 592, 44, t, 1.5, 0.09, _seed(p, 2),
                   align=align, x_left=110)
    return img


# =====================================================================
# 2. VERDICT TAG - headline o + nhan sao bung phan quyet
# =====================================================================
def verdict_tag(t, dur, p):
    img = bg()
    lay = _lay(p)
    word_tiles(img, p["head"], 268, 100, t, 0.25, 0.12, _seed(p, 3),
               align="c" if lay == 0 else "l", x_left=110)
    lines = [x.strip() for x in p["tag"].split("|") if x.strip()]
    cx = 1000 if lay == 0 else 250
    starburst(img, lines[:2], cx, 500, t, float(p["_tag_at"]), col=RED,
              size=44, radius=158, ang=-10 if lay == 0 else 10)
    if p["sub"]:
        word_tiles(img, p["sub"], 616, 42, t, float(p["_tag_at"]) + 0.35,
                   0.08, _seed(p, 4), align="c" if lay == 0 else "l",
                   x_left=110)
    return img


# =====================================================================
# 3. CLIPPING WINDOW - mau bao cat + dong viet tay
# =====================================================================
def clipping_window(t, dur, p):
    img = bg()
    lay = _lay(p)
    x0, y0, x1, y1 = (170, 130, 1110, 620) if lay == 0 else \
        (80, 130, 950, 620)
    if t >= 0.15:
        clip = Image.new("RGBA", (x1 - x0 + 24, y1 - y0 + 24),
                         (0, 0, 0, 0))
        cd = ImageDraw.Draw(clip)
        cd.rectangle([17, 18, x1 - x0 + 17, y1 - y0 + 18],
                     fill=(40, 32, 20, 55))
        cd.rectangle([12, 12, x1 - x0 + 12, y1 - y0 + 12],
                     fill=WHITE_P + (255,))
        clip = clip.rotate(-1, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(clip, (x0 - 12, y0 - 12))
        tape(img, x0 + 60, y0 + 8, 110, -16)
        tape(img, x1 - 60, y0 + 8, 110, 14)
    word_tiles(img, p["title"], y0 + 66, 54, t, 0.35, 0.08, _seed(p, 5))
    lines = [x for x in p["lines"].split("|")]
    starts = p["_line_starts"]
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines[:5]):
        st, en = starts[i]
        if t < st:
            break
        prog = clamp((t - st) / max(0.05, en - st))
        n = max(0, int(len(ln) * prog))
        d.text((x0 + 56, y0 + 128 + i * 66), ln[:n], font=_font(ITIM, 44),
               fill=INK + (255,))
    if lay == 1 and p["side"]:
        word_tiles(img, p["side"], 330, 46, t, 1.2, 0.1, _seed(p, 6),
                   align="l", x_left=990)
    return img


# =====================================================================
# 4. AB CLIPPINGS - 2 mau dan: trai xam mo vs phai song dong
# =====================================================================
def _clipping(img, x0, y0, x1, y1, dull, label, seed, t, at):
    if t < at:
        return
    clip = Image.new("RGBA", (x1 - x0 + 24, y1 - y0 + 24), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clip)
    cd.rectangle([17, 18, x1 - x0 + 17, y1 - y0 + 18], fill=(40, 32, 20, 55))
    cd.rectangle([12, 12, x1 - x0 + 12, y1 - y0 + 12], fill=WHITE_P + (255,))
    img.alpha_composite(clip, (x0 - 12, y0 - 12))
    styles = GREY_STYLES if dull else STYLES
    word_tiles(img, label, y0 + 120, 52, t, at + 0.1, 0.1, seed,
               styles=styles, max_w=x1 - x0 - 30)
    rng = random.Random(seed + 50)
    d = ImageDraw.Draw(img)
    for i in range(4):
        yy = y0 + 200 + i * 52
        wdt = rng.randint(200, 380)
        col = (170, 166, 156) if dull else (30, 30, 30)
        d.line([(x0 + 40, yy), (x0 + 40 + wdt, yy)], fill=col + (255,),
               width=7)


def ab_clippings(t, dur, p):
    img = bg()
    lay = _lay(p)
    word_tiles(img, p["head"], 84, 50, t, 0.15, 0.07, _seed(p, 7))
    lx, rx = (70, 680) if lay == 0 else (680, 70)
    _clipping(img, lx, 150, lx + 530, 540, dull=(lay == 0),
              label=p["label_a"], seed=_seed(p, 8), t=t, at=0.4)
    _clipping(img, rx, 150, rx + 530, 540, dull=(lay == 1),
              label=p["label_b"], seed=_seed(p, 9), t=t, at=0.75)
    if t >= 1.1:
        lay_tile = make_tile("VS", (YELLOW, INK, SANS), 40, random.Random(1))
        paste_tile(img, lay_tile, 640, 345, -6)
    return img


# =====================================================================
# 5. PINNED LIST - bang ghim, mau giay ghim dan tung cai
# =====================================================================
def pinned_list(t, dur, p):
    img = bg()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([56, 56, W - 56, H - 56], fill=(146, 108, 70, 255))  # bang
    rng = random.Random(21)
    for _ in range(1600):
        x, y = rng.randint(56, W - 56), rng.randint(56, H - 56)
        d.point((x, y), fill=(110, 80, 48, rng.randint(30, 80)))
    d.rectangle([56, 56, W - 56, H - 56], outline=(96, 70, 40, 255),
                width=8)
    lay = _lay(p)
    word_tiles(img, p["title"], 116, 48, t, 0.2, 0.07, _seed(p, 10))
    items = [x.strip() for x in p["items"].split("|") if x.strip()]
    starts = p["_starts"]
    for i, it in enumerate(items[:6]):
        if t < starts[i]:
            continue
        parts = it.split("::")
        body = parts[1] if len(parts) > 1 else parts[0]
        tag = parts[0] if len(parts) > 1 else "BƯỚC %d" % (i + 1)
        if lay == 0:
            sx = 120 + (i % 2) * 560
            sy = 190 + (i // 2) * 158
        else:
            sx = 120 + (i % 3) * 360
            sy = 190 + (i // 3) * 240
        sw, sh = (520, 132) if lay == 0 else (330, 200)
        slip = Image.new("RGBA", (sw + 20, sh + 20), (0, 0, 0, 0))
        sd = ImageDraw.Draw(slip)
        sd.rectangle([15, 16, sw + 15, sh + 16], fill=(40, 32, 20, 55))
        sd.rectangle([10, 10, sw + 10, sh + 10],
                     fill=(WHITE_P if i % 2 == 0 else NOTE_Y) + (255,))
        sd.text((30, 26), tag, font=_font(SANS, 26), fill=RED + (255,))
        sd.text((30, 66), body, font=_font(ITIM, 42), fill=INK + (255,))
        slip = slip.rotate(-2 if i % 2 == 0 else 2, expand=True,
                           resample=Image.BICUBIC)
        img.alpha_composite(slip, (sx - 10, sy - 10))
        if t >= starts[i] + 0.06:
            pin(img, sx + sw // 2, sy + 12, 12)
    return img


NOTE_Y = (255, 232, 140)


# =====================================================================
# 6. PRICE NUMBER - the gia vang kho lon + so chay
# =====================================================================
def price_number(t, dur, p):
    img = bg()
    lay = _lay(p)
    # the gia: hinh chu nhat vang, lo tron + day treo goc trai tren
    tw_, th_ = 760, 400
    tx = (W - tw_) // 2 if lay == 0 else 90
    ty = 130
    if t >= 0.2:
        tag = Image.new("RGBA", (tw_ + 30, th_ + 30), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rectangle([20, 21, tw_ + 20, th_ + 21], fill=(40, 32, 20, 60))
        td.rounded_rectangle([15, 15, tw_ + 15, th_ + 15], radius=26,
                             fill=YELLOW + (255,))
        td.ellipse([45, 45, 85, 85], outline=INK + (255,), width=5)
        tag = tag.rotate(-2, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(tag, (tx - 15, ty - 15))
        d = ImageDraw.Draw(img)
        d.line([(tx + 62, ty + 62), (tx - 30, ty - 34)], fill=INK + (255,),
               width=4)
        d.line([(tx + 62, ty + 62), (tx + 130, ty - 40)], fill=INK + (255,),
               width=4)
    target = float(p["_target"])
    cd = float(p["_count_dur"])
    pr = ease_out_cubic((t - 0.35) / max(0.05, cd))
    txt = "{:,.0f}".format(target * pr).replace(",", ".")
    size = fit_size(txt, 640, 190, 70)
    if t >= 0.3:
        plain_text(img, txt, tx + tw_ // 2, ty + 190, size, INK, SANS)
    if t >= 0.35 + cd * 0.55:
        word_tiles(img, p["label"], ty + th_ + 78, 54, t, 0.35 + cd * 0.55,
                   0.09, _seed(p, 11), align="c" if lay == 0 else "l",
                   x_left=110)
    starburst(img, [x.strip() for x in p["burst"].split("|")][:2], 1050, 140,
              t, 0.5, col=RED, size=34, radius=104, ang=12)
    return img


# =====================================================================
# 7. TILE GRID - luoi o dan danh so
# =====================================================================
def tile_grid(t, dur, p):
    img = bg()
    lay = _lay(p)
    word_tiles(img, p["title"], 82, 50, t, 0.15, 0.07, _seed(p, 12))
    total = int(p["_total"])
    cols = int(p["_cols"])
    step = float(p["_step"])
    cell, gap = 128, 18
    gw = cols * cell + (cols - 1) * gap
    rows = int(math.ceil(total / float(cols)))
    gh = rows * cell + (rows - 1) * gap
    x0 = (W - gw) // 2 if lay == 0 else 100
    y0 = (H - gh) // 2 + 40
    rng = random.Random(_seed(p, 13))
    off = rng.randrange(len(STYLES))
    for i in range(total):
        at = 0.45 + i * step
        if t < at:
            continue
        r, c = divmod(i, cols)
        cx = x0 + c * (cell + gap) + cell // 2
        cy = y0 + r * (cell + gap) + cell // 2
        st = STYLES[(off + i) % len(STYLES)]
        lay_tile = make_tile(str(i + 1), st, 52, rng, pad_x=18, pad_y=10)
        # o vuong: ve lai nen o theo kich thuoc cell
        tile_sq = Image.new("RGBA", (cell + 14, cell + 14), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile_sq)
        td.rectangle([12, 13, cell + 12, cell + 13], fill=(40, 32, 20, 60))
        td.rectangle([7, 7, cell + 7, cell + 7], fill=st[0] + (255,))
        f = _font(st[2], 52)
        td.text((7 + cell / 2 - _tw(str(i + 1), f) / 2, 7 + cell / 2 - 30),
                str(i + 1), font=f, fill=st[1] + (255,))
        sc = slam_scale(t, at, 0.12)
        tile_sq = tile_sq.resize((max(2, int(tile_sq.width * sc)),
                                  max(2, int(tile_sq.height * sc))),
                                 Image.LANCZOS)
        paste_tile(img, tile_sq, cx, cy, rng.uniform(-3, 3))
    if p["caption"]:
        word_tiles(img, p["caption"], y0 + gh + 52, 40, t,
                   0.45 + total * step + 0.15, 0.07, _seed(p, 14))
    return img


# =====================================================================
# 8. RULER PROGRESS - dai thuoc giay, o dan chong dan toi %
# =====================================================================
def ruler_progress(t, dur, p):
    img = bg()
    lay = _lay(p)
    pct = float(p["_pct"])
    fill_dur = float(p["_fill_dur"])
    t_lines = float(p["_t_lines"])
    pr = ease_out_cubic((t - 0.3) / max(0.05, fill_dur))
    cur = pct * pr
    strip_y = 470 if lay == 0 else 190
    txt_y = 150 if lay == 0 else 330
    d = ImageDraw.Draw(img)
    d.rectangle([102, strip_y + 8, W - 92, strip_y + 96],
                fill=(40, 32, 20, 50))
    d.rectangle([96, strip_y, W - 96, strip_y + 88], fill=WHITE_P + (255,),
                outline=INK + (255,), width=3)
    nseg = 12
    seg_w = (W - 192) / float(nseg)
    lit = int(round(nseg * cur / 100.0))
    rng = random.Random(_seed(p, 15))
    cols_cycle = [RED, YELLOW, BLUE, INK]
    for i in range(lit):
        sx0 = 96 + i * seg_w
        d.rectangle([sx0 + 4, strip_y + 8, sx0 + seg_w - 4, strip_y + 80],
                    fill=cols_cycle[(i + rng.randrange(2)) % 4] + (255,))
    for i in range(nseg + 1):
        sx0 = 96 + i * seg_w
        d.line([(sx0, strip_y), (sx0, strip_y + 20)], fill=INK + (255,),
               width=3)
    plain_text(img, "%d%%" % int(round(cur)), 190, strip_y - 66, 76, INK,
               SANS)
    entries = [(p["line1"], t_lines), (p["question"], t_lines + 0.55),
               (p["answer"], t_lines + 1.10)]
    yy = txt_y
    for txt, at in entries:
        if txt and t >= at:
            word_tiles(img, txt, yy, 50, t, at, 0.07, _seed(p, 16 + yy),
                       align="l", x_left=110)
        yy += 104
    return img


# =====================================================================
# 9. STACK COMBO - o so xN dan chong leo thang (mock c3)
# =====================================================================
def stack_combo(t, dur, p):
    img = bg()
    lay = _lay(p)
    sx = int(p["_start_x"])
    mx = int(p["_max_x"])
    step = float(p["_step"])
    rng = random.Random(_seed(p, 17))
    cols = [(WHITE_P, INK, SANS), (YELLOW, INK, SANS), (RED, WHITE_TXT, SANS),
            (BLUE, WHITE_TXT, JB), (INK, YELLOW, SANS)]
    n_steps = mx - sx + 1
    # --- Bo cuc theo chieu rong DO THAT cua tung o:
    # sao bung neo goc tren (phai voi lay 0, trai voi lay 1), vung dat o
    # so la phan ngang con lai -> o khong bao gio cham sao, ke ca muc x5.
    burst_r = 140
    burst_cx = W - 195 if lay == 0 else 195
    burst_cy = 192
    # hop bao cua sao sau xoay ~ (2r+30)*1.16/2 = 180px quanh tam
    if lay == 0:
        zone_l, zone_r = 56, burst_cx - 180 - 16
    else:
        zone_l, zone_r = burst_cx + 180 + 16, W - 56
    zone_w = zone_r - zone_l
    tiles = []
    for i, n in enumerate(range(sx, mx + 1)):
        size = 54 + i * 16
        tiles.append(make_tile("×%d" % n, cols[i % len(cols)], size, rng))
    gap = 16
    # chieu rong chiem cho = rong o * 1.22 (chua ca dap phong 1.3 + xoay)
    eff = [tl.width * 1.22 for tl in tiles]
    total = sum(eff) + gap * max(0, n_steps - 1)
    fit_sc = min(1.0, zone_w / total) if total > 0 else 1.0
    if fit_sc < 1.0:
        tiles = [tl.resize((max(2, int(tl.width * fit_sc)),
                            max(2, int(tl.height * fit_sc))),
                           Image.LANCZOS) for tl in tiles]
        eff = [e * fit_sc for e in eff]
        total = sum(eff) + gap * max(0, n_steps - 1)
    # tam o: lay 0 tang trai->phai, lay 1 guong phai->trai
    centers = []
    if lay == 0:
        cur = zone_l + (zone_w - total) / 2
        for e in eff:
            centers.append(cur + e / 2)
            cur += e + gap
    else:
        cur = zone_r - (zone_w - total) / 2
        for e in eff:
            centers.append(cur - e / 2)
            cur -= e + gap
    for i in range(n_steps):
        at = 0.35 + i * step
        if t < at:
            continue
        cy = 215 - i * 10
        sc = slam_scale(t, at, 0.13)
        lay_tile = tiles[i]
        if sc != 1.0:
            lay_tile = lay_tile.resize(
                (max(2, int(lay_tile.width * sc)),
                 max(2, int(lay_tile.height * sc))), Image.LANCZOS)
        paste_tile(img, lay_tile, centers[i], cy, rng.uniform(-3, 3))
    cur_max_at = 0.35 + (n_steps - 1) * step
    lines = [x.strip() for x in p["burst"].split("|") if x.strip()]
    starburst(img, lines[:2], burst_cx, burst_cy, t, cur_max_at + 0.15,
              col=RED, size=40, radius=burst_r, ang=10, fit=True)
    # dai nang luong: o nho dan day theo combo
    d = ImageDraw.Draw(img)
    seg_n = 10
    lit = int(round(seg_n * clamp((t - 0.3) / max(0.5, dur - 1.2))))
    for i in range(seg_n):
        x = 180 + i * 92
        colr = (53, 208, 186) if i < lit else (200, 194, 180)
        d.rectangle([x, 360, x + 80, 392], fill=colr + (255,))
    if p["caption"]:
        word_tiles(img, p["caption"], 470, 46, t, cur_max_at + 0.4, 0.08,
                   _seed(p, 18))
    return img


WHITE_TXT = (255, 255, 255)


# =====================================================================
# 10. POSTER END - poster PHAN 2 + nut THEO DOI o giay (mock c3)
# =====================================================================
def poster_end(t, dur, p):
    img = bg()
    lay = _lay(p)
    click_at = float(p["_click_at"])
    # poster lon giua: 1 o trang kho lon + bang dinh 2 goc
    big = p["big"]
    size = fit_size(big, 1000, 210, 90)
    f = _font(SANS, size)
    tw = int(_tw(big, f))
    pw, ph = tw + 120, int(size * 1.32) + 70
    pcx, pcy = (W / 2, 300) if lay == 0 else (620, 300)
    if t >= 0.25:
        poster = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
        pd = ImageDraw.Draw(poster)
        pd.rectangle([17, 18, pw + 17, ph + 18], fill=(40, 32, 20, 60))
        pd.rectangle([12, 12, pw + 12, ph + 12], fill=WHITE_P + (255,))
        pd.text((12 + 60, 12 + 30), big, font=f, fill=INK + (255,))
        poster = poster.rotate(-1, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(poster, (int(pcx - poster.width / 2),
                                     int(pcy - poster.height / 2)))
        tape(img, pcx - pw // 4, pcy - ph // 2 + 2, 120, -14)
        tape(img, pcx + pw // 4, pcy - ph // 2 + 2, 120, 12)
    clicked = t >= click_at
    bx0, by0, bx1, by1 = (390, 520, 720, 606) if lay == 0 else \
        (140, 520, 470, 606)
    if t >= 0.8:
        btn_style = (INK, (255, 255, 255), SANS) if clicked else \
            (WHITE_P, INK, SANS)
        txt = p["done_text"] if clicked else p["button"]
        lay_btn = make_tile(txt, btn_style, 42, random.Random(2),
                            pad_x=34, pad_y=16)
        cx_btn, cy_btn = (bx0 + bx1) // 2, (by0 + by1) // 2
        paste_tile(img, lay_btn, cx_btn, cy_btn, -1)
        d = ImageDraw.Draw(img)
        d.rectangle([bx0 - 6, by0 - 6, bx1 + 6, by1 + 6],
                    outline=INK + (255,), width=4)
        if p["side"]:
            plain_text(img, p["side"], bx1 + 215, cy_btn + 34, 38, INK, ITIM)
            hand_arrow(img, bx1 + 330, cy_btn - 60, bx1 + 44, cy_btn - 8)
    if p["main"]:
        word_tiles(img, p["main"], 108, 46, t, 0.3, 0.07, _seed(p, 19),
                   align="c" if lay == 0 else "l", x_left=110)
    return img
