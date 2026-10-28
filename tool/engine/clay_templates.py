#!/usr/bin/env python3
"""CLAY TEMPLATES - goi phong cach "DAT SET" (clay stop-motion) cho
Pixel Studio. Theo mock clay-a1..a3 (~/workspace/pixel-tool-mockup/
pack-ideas-v3/) da duyet: nen kem dao #F7E3C3, khoi bo tron lon do
bong mem 1 lop, be mat nhieu hat nhe, mau keo: san ho #FF6B57, ngoc
#2EC4B6, mu tat #FFC53D, troi #4EA8FF; chu Noto Sans Black tren phien
dat set. Hieu ung chu ky: SQUASH (ep det nay phong) khi vat/chu xuat
hien; tien trinh = con sau dat set uon khuc lap ranh; leo thang = bac
thang nan; man cuoi = nut dat set lon.

Module ve thuan (chi PIL): moi ham fn(t, dur, p) -> RGBA 1280x720.
p = dict tham so CHUOI da merge + khoa tinh toan "_" o clay_scenes
(_layout: 0 = bien the A, 1 = bien the B).
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 1280, 720
BG = (247, 227, 195)          # #F7E3C3 kem dao
CORAL = (255, 107, 87)        # #FF6B57
TEAL = (46, 196, 182)         # #2EC4B6
MUST = (255, 197, 61)         # #FFC53D
SKY = (78, 168, 255)          # #4EA8FF
INK = (38, 32, 26)
WHITE = (255, 255, 255)
CREAM = (255, 248, 232)
GREY = (168, 158, 148)
DULL = (196, 178, 158)
TRACK = (233, 203, 152)
PALETTE = [CORAL, TEAL, MUST, SKY]


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


def ease_out_back(k, s=1.9):
    k = clamp(k)
    return 1 + (s + 1) * (k - 1) ** 3 + s * (k - 1) ** 2


def fit_size(text, max_w, start, min_size, path=SANS):
    size = start
    while size > min_size:
        if _tw(text, _font(path, size)) <= max_w:
            return size
        size -= 4
    return min_size


def wrap_lines(text, max_w, size, path=SANS, max_lines=3):
    f = _font(path, size)
    lines, cur = [], ""
    for w_ in str(text).split():
        trial = (cur + " " + w_).strip()
        if _tw(trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines[:max_lines]


# ------------------------------------------------------------------ nen
_BG = None


def bg():
    """Nen kem dao + vet mo mem (cache 1 lan)."""
    global _BG
    if _BG is not None:
        return _BG.copy()
    img = Image.new("RGBA", (W, H), BG + (255,))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = random.Random(5)
    for _ in range(9):
        x, y = rng.randint(40, W - 280), rng.randint(40, H - 220)
        wdt, hgt = rng.randint(120, 280), rng.randint(50, 120)
        tone = rng.choice([(210, 180, 130, 15), (255, 246, 225, 17),
                           (190, 155, 105, 12)])
        d.ellipse([x, y, x + wdt, y + hgt], fill=tone)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
    _BG = img
    return _BG.copy()


# ------------------------------------------------------------- khoi dat set
_NOISE = None


def _noise_tex():
    global _NOISE
    if _NOISE is None:
        n = Image.effect_noise((W + 160, H + 160), 16).convert("L")
        _NOISE = n.point(lambda v: 128 + int((v - 128) * 0.4))
    return _NOISE


def squash_at(t, at, dur=0.30):
    """He so squash (sx, sy) tai thoi diem t cho vat xuat hien luc 'at':
    phong len -> ep det -> ve 1. (0, 0) neu chua xuat hien."""
    if t < at:
        return (0.0, 0.0)
    k = clamp((t - at) / dur)
    if k >= 1.0:
        return (1.0, 1.0)
    sy = 1.0 + 0.38 * math.sin(k * math.pi * 1.35) * (1 - k * 0.55)
    sx = 1.0 - (sy - 1.0) * 0.62
    return (sx, sy)


def clay_blob(img, box, col, radius=None, sx=1.0, sy=1.0, shadow=True):
    """Ve 1 khoi dat set bo tron: bong mem + hat nhieu trong mat na +
    vet sang goc tren-trai. (sx, sy) = squash quanh tam-day cua khoi."""
    if sx <= 0.01 or sy <= 0.01:
        return
    x0, y0, x1, y1 = [int(v) for v in box]
    wdt, hgt = x1 - x0, y1 - y0
    if radius is None:
        radius = min(wdt, hgt) // 3
    pad = 30
    lw, lh = wdt + pad * 2, hgt + pad * 2
    core = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(core)
    d.rounded_rectangle([pad, pad, pad + wdt, pad + hgt], radius=radius,
                        fill=col + (255,))
    mask = core.split()[3]
    noise = _noise_tex().crop((x0 - pad + 80, y0 - pad + 80,
                               x0 - pad + 80 + lw, y0 - pad + 80 + lh))
    noisy = ImageChops.add(core.convert("RGB"),
                           Image.merge("RGB", (noise, noise, noise)),
                           1.0, -128).convert("RGBA")
    noisy.putalpha(mask)
    core = Image.blend(core, noisy, 0.30)
    hl = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.ellipse([pad + wdt * 0.07, pad + hgt * 0.05,
                pad + wdt * 0.60, pad + hgt * 0.50],
               fill=(255, 255, 255, 32))
    hl = hl.filter(ImageFilter.GaussianBlur(16))
    hl.putalpha(ImageChops.multiply(hl.split()[3], mask))
    core.alpha_composite(hl)
    lay = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    if shadow:
        sh = Image.composite(Image.new("RGBA", (lw, lh), (0, 0, 0, 100)),
                             Image.new("RGBA", (lw, lh), (0, 0, 0, 0)),
                             mask.filter(ImageFilter.GaussianBlur(9)))
        lay.alpha_composite(sh, (0, 13))
    lay.alpha_composite(core)
    nw, nh = max(2, int(lw * sx)), max(2, int(lh * sy))
    lay = lay.resize((nw, nh), Image.LANCZOS)
    cx = (x0 + x1) / 2.0
    img.alpha_composite(lay, (int(cx - nw / 2), int(y1 + pad - nh)))


def clay_ball(img, cx, cy, r, col, sx=1.0, sy=1.0, shadow=True):
    clay_blob(img, (cx - r, cy - r, cx + r, cy + r), col,
              radius=int(r), sx=sx, sy=sy, shadow=shadow)


def text_on(img, text, cx, cy, size, col, path=SANS):
    """Chu canh giua tai (cx, cy) - tam chu theo ca 2 truc."""
    f = _font(path, size)
    tw = _tw(text, f)
    bb = _DUMMY.textbbox((0, 0), text, font=f)
    d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f,
           fill=col + (255,))
    return tw


def _lay(p):
    return int(p.get("_layout", 0))


def col_of(name, default=CORAL):
    cols = {"coral": CORAL, "teal": TEAL, "must": MUST, "sky": SKY,
            "ink": INK, "white": WHITE}
    return cols.get(str(name or "").strip().lower(), default)


# =====================================================================
# 1. CLAY HOOK - phien dat set lon + chu (mock a1)
# =====================================================================
def clay_hook(t, dur, p):
    img = bg()
    lay = _lay(p)
    sx, sy = squash_at(t, 0.15, 0.34)
    if lay == 0:
        box = (150, 150, 1130, 570)
    else:
        box = (90, 170, 950, 590)
    clay_blob(img, box, col_of(p["color"]), sx=sx, sy=sy)
    if t >= 0.30:
        cx = (box[0] + box[2]) / 2
        size = fit_size(max(p["head1"], p["head2"], key=len), box[2] - box[0] - 130, 118, 48)
        text_on(img, p["head1"], cx, (box[1] + box[3]) / 2 - size * 0.62,
                size, WHITE)
        text_on(img, p["head2"], cx, (box[1] + box[3]) / 2 + size * 0.62,
                size, WHITE)
    balls = [(70, 110, 52, TEAL), (1196, 96, 46, MUST),
             (1210, 620, 40, SKY)] if lay == 0 else \
            [(1050, 120, 48, TEAL), (1120, 330, 40, MUST),
             (1040, 560, 52, SKY)]
    for i, (bx, by, br, bc) in enumerate(balls):
        bsx, bsy = squash_at(t, 0.55 + i * 0.16, 0.3)
        clay_ball(img, bx, by, br, bc, sx=bsx, sy=bsy)
    if p["sub"] and t >= 1.25:
        text_on(img, p["sub"], W / 2, 656, 40, INK)
    return img


# =====================================================================
# 2. STAMP VERDICT - con dau dat set dap xuong phien
# =====================================================================
def stamp_verdict(t, dur, p):
    img = bg()
    lay = _lay(p)
    # phien nen trang kem
    sx, sy = squash_at(t, 0.12, 0.3)
    box = (240, 210, 1040, 560) if lay == 0 else (140, 190, 940, 540)
    clay_blob(img, box, CREAM, sx=sx, sy=sy)
    if t >= 0.3:
        size = fit_size(p["head"], box[2] - box[0] - 120, 84, 40)
        for j, ln in enumerate(wrap_lines(p["head"], box[2] - box[0] - 120, size)):
            text_on(img, ln, (box[0] + box[2]) / 2,
                    box[1] + 84 + j * int(size * 1.2), size, INK)
    stamp_at = float(p["_stamp_at"])
    if t >= stamp_at:
        k = clamp((t - stamp_at) / 0.16)
        sc = 1.45 - 0.45 * ease_out_cubic(k)
        # dau dong o GOC DUOI PHAI cua phien, nua ngoai mep - khong de
        # len dong chu headline o phia tren
        dcx = box[2] - 128
        dcy = box[3] - 18
        r = int(96 * sc)
        clay_ball(img, dcx, dcy, r, col_of(p["stamp_col"], TEAL),
                  sx=1.0 + (1 - k) * 0.1, sy=1.0 - (1 - k) * 0.22)
        if k >= 0.55:
            vs = fit_size(p["verdict"], r * 1.55, 54, 26)
            text_on(img, p["verdict"], dcx, dcy, vs, WHITE)
        if k >= 1.0:  # tia dat set ban quanh dau khi dap
            d = ImageDraw.Draw(img)
            rng = random.Random(8)
            for _ in range(7):
                ang = rng.uniform(0, math.tau)
                rr = r + rng.randint(14, 44)
                d.ellipse([dcx + rr * math.cos(ang) - 7,
                           dcy + rr * math.sin(ang) * 0.6 - 7,
                           dcx + rr * math.cos(ang) + 7,
                           dcy + rr * math.sin(ang) * 0.6 + 7],
                          fill=col_of(p["stamp_col"], TEAL) + (255,))
    if p["sub"] and t >= stamp_at + 0.45:
        text_on(img, p["sub"], W / 2, 648, 38, INK)
    return img


# =====================================================================
# 3. CLAY WINDOW - cua so/vien dat set chua dong noi dung
# =====================================================================
def clay_window(t, dur, p):
    img = bg()
    lay = _lay(p)
    sx, sy = squash_at(t, 0.12, 0.3)
    if lay == 0:
        box = (150, 90, 1130, 630)
    else:
        box = (330, 90, 1190, 630)
    clay_blob(img, box, SKY, radius=54, sx=sx, sy=sy)
    inner = (box[0] + 26, box[1] + 96, box[2] - 26, box[3] - 26)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(inner, radius=36, fill=CREAM + (255,))
    if t >= 0.3:
        ts = fit_size(p["title"], box[2] - box[0] - 90, 46, 26)
        text_on(img, p["title"], (box[0] + box[2]) / 2, box[1] + 50, ts,
                WHITE)
    lines = [x.strip() for x in p["lines"].split("|") if x.strip()]
    starts = p["_starts"]
    cols = [CORAL, TEAL, MUST]
    for i, ln in enumerate(lines[:5]):
        if t < starts[i]:
            continue
        y = inner[1] + 34 + i * 84
        bsx, bsy = squash_at(t, starts[i], 0.26)
        clay_blob(img, (inner[0] + 26, y, inner[0] + 92, y + 56),
                  cols[i % 3], radius=26, sx=bsx, sy=bsy, shadow=False)
        fs = fit_size(ln, inner[2] - inner[0] - 160, 40, 24)
        f = _font(SANS, fs)
        d = ImageDraw.Draw(img)
        d.text((inner[0] + 118, y + 28 - fs * 0.62), ln, font=f,
               fill=INK + (255,))
    if lay == 1 and t >= 0.3:
        text_on(img, "DEMO", 165, 300, 54, CORAL)
        text_on(img, "THẬT", 165, 366, 54, TEAL)
    return img


# =====================================================================
# 4. CLAY AB - 2 phien dat set so sanh + bong VS
# =====================================================================
def clay_ab(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.1:
        text_on(img, p["head"], W / 2, 74, fit_size(p["head"], 1160, 56, 30),
                INK)
    if lay == 0:
        box_a, box_b = (80, 170, 560, 580), (720, 150, 1200, 600)
    else:
        box_a, box_b = (240, 150, 1040, 380), (240, 420, 1040, 660)
    sax, say = squash_at(t, 0.35, 0.3)
    clay_blob(img, box_a, DULL, sx=sax, sy=say)
    sbx, sby = squash_at(t, 0.6, 0.3)
    clay_blob(img, box_b, col_of(p["color_b"]), sx=sbx, sy=sby)
    if t >= 0.55:
        text_on(img, p["label_a"], (box_a[0] + box_a[2]) / 2,
                box_a[1] + 66, fit_size(p["label_a"], 420, 52, 28), INK)
        if p["note_a"]:
            text_on(img, p["note_a"], (box_a[0] + box_a[2]) / 2,
                    (box_a[1] + box_a[3]) / 2 + 30, 38, INK)
    if t >= 0.8:
        text_on(img, p["label_b"], (box_b[0] + box_b[2]) / 2,
                box_b[1] + 66, fit_size(p["label_b"], 420, 52, 28), WHITE)
        if p["note_b"]:
            text_on(img, p["note_b"], (box_b[0] + box_b[2]) / 2,
                    (box_b[1] + box_b[3]) / 2 + 30, 38, WHITE)
    vsx, vsy = squash_at(t, 1.0, 0.3)
    vcx = W / 2 if lay == 0 else W / 2
    vcy = 375 if lay == 0 else 400
    clay_ball(img, vcx, vcy, 52, MUST, sx=vsx, sy=vsy)
    if t >= 1.1:
        text_on(img, "VS", vcx, vcy, 44, INK)
    return img


# =====================================================================
# 5. CLAY LIST - vien dat set xep chong (mock a2 trai)
# =====================================================================
def clay_list(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.1:
        if lay == 0:
            text_on(img, p["title"], W / 2, 76,
                    fit_size(p["title"], 1160, 58, 30), INK)
        else:
            text_on(img, p["title"], 300, 360, 54, INK)
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    starts = p["_starts"]
    x0 = 110 if lay == 0 else 520
    wdt = 1060 if lay == 0 else 700
    for i, it in enumerate(items[:5]):
        if t < starts[i]:
            continue
        y = 150 + i * 108 if lay == 0 else 130 + i * 108
        col = PALETTE[i % 4]
        sx, sy = squash_at(t, starts[i], 0.28)
        clay_blob(img, (x0, y, x0 + wdt, y + 88), col, radius=44,
                  sx=sx, sy=sy)
        tcol = INK if col == MUST else WHITE
        fs = fit_size(it, wdt - 120, 46, 26)
        text_on(img, it, x0 + wdt / 2, y + 44, fs, tcol)
    return img


# =====================================================================
# 6. BIG NUMBER - so dat set khong lo dem tang
# =====================================================================
def big_number(t, dur, p):
    img = bg()
    lay = _lay(p)
    target = float(p["_target"])
    cd = float(p["_count_dur"])
    pr = ease_out_cubic((t - 0.25) / max(0.05, cd))
    val = target * pr
    txt = "{:,.0f}".format(val).replace(",", ".")
    box = (190, 120, 1090, 480) if lay == 0 else (110, 150, 1010, 510)
    sx, sy = squash_at(t, 0.12, 0.3)
    clay_blob(img, box, col_of(p["color"], MUST), sx=sx, sy=sy)
    if t >= 0.25:
        bounce = 1.0
        if pr >= 1.0 and t < 0.25 + cd + 0.3:
            bounce = 1.0 + 0.06 * math.sin((t - 0.25 - cd) / 0.3 * math.pi)
        size = int(fit_size(txt, box[2] - box[0] - 110, 190, 70) * bounce)
        tcol = INK if col_of(p["color"], MUST) == MUST else WHITE
        text_on(img, txt, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2,
                size, tcol)
    if p["label"] and t >= 0.25 + cd * 0.55:
        text_on(img, p["label"], W / 2, 556,
                fit_size(p["label"], 1100, 52, 28), INK)
    if p["sub"] and t >= 0.25 + cd + 0.3:
        text_on(img, p["sub"], W / 2, 636, 36, INK)
    return img


# =====================================================================
# 7. CLAY GRID - luoi vien dat set
# =====================================================================
def clay_grid(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.1:
        text_on(img, p["title"], W / 2, 70,
                fit_size(p["title"], 1160, 54, 28), INK)
    total, cols = int(p["_total"]), int(p["_cols"])
    step = float(p["_step"])
    rows = int(math.ceil(total / float(cols)))
    cell = 128
    gap = 26
    gw = cols * cell + (cols - 1) * gap
    gh = rows * cell + (rows - 1) * gap
    x0 = (W - gw) / 2 if lay == 0 else 90
    y0 = 130 if lay == 0 else (H - gh) / 2 + 20
    for i in range(total):
        at = 0.45 + i * step
        if t < at:
            continue
        r, c = divmod(i, cols)
        cx = x0 + c * (cell + gap) + cell / 2
        cy = y0 + r * (cell + gap) + cell / 2
        col = PALETTE[i % 4] if i < total - 1 else CORAL
        sx, sy = squash_at(t, at, 0.26)
        clay_ball(img, cx, cy, cell / 2 - 4, col, sx=sx, sy=sy)
        if t >= at + 0.12:
            tcol = INK if col == MUST else WHITE
            text_on(img, str(i + 1), cx, cy, 44, tcol)
    if p["caption"] and t >= 0.45 + total * step + 0.15:
        text_on(img, p["caption"], W / 2, 664, 36, INK)
    return img


# =====================================================================
# 8. WORM PROGRESS - con sau dat set lap ranh (mock a2 phai)
# =====================================================================
def worm_progress(t, dur, p):
    img = bg()
    lay = _lay(p)
    pct = float(p["_pct"])
    fill_dur = float(p["_fill_dur"])
    t_lines = float(p["_t_lines"])
    pr = ease_out_cubic((t - 0.3) / max(0.05, fill_dur))
    tx0, ty0, tx1, ty1 = (90, 96, 1190, 300) if lay == 0 else \
        (90, 420, 1190, 624)
    clay_blob(img, (tx0, ty0, tx1, ty1), TRACK, radius=96, shadow=True)
    fill_to = tx0 + 70 + (tx1 - tx0 - 140) * (pct / 100.0) * pr
    cy_mid = (ty0 + ty1) / 2
    r = 62
    stepx = 52
    cx = tx0 + 84
    i = 0
    last_cy = cy_mid
    while cx < fill_to:
        cy = cy_mid + int(math.sin(i * 0.9) * 15)
        col = TEAL if i % 2 == 0 else (41, 178, 165)
        clay_ball(img, cx, cy, r, col, shadow=False)
        last_cy = cy
        cx += stepx
        i += 1
    if pr > 0.02:  # dau sau lon hon + vet sang
        hx = min(tx1 - 60, fill_to + 26)
        clay_ball(img, hx, last_cy, 78, (64, 205, 190), shadow=False)
        d = ImageDraw.Draw(img)
        d.arc([hx - 52, last_cy - 60, hx + 22, last_cy - 6], 180, 300,
              fill=(255, 255, 255, 230), width=13)
    text_on(img, "TIẾN ĐỘ: %d%%" % int(round(pct * pr)), W / 2,
            ty1 + 44, 42, INK)
    entries = [(p["line1"], 44, INK, t_lines),
               (p["question"], 54, CORAL, t_lines + 0.55),
               (p["answer"], 46, TEAL, t_lines + 1.10)]
    yy = 420 if lay == 0 else 150
    for txt, size, colr, at in entries:
        if txt and t >= at:
            text_on(img, txt, W / 2, yy, fit_size(txt, 1140, size, 26),
                    colr)
        yy += 78
    return img


# =====================================================================
# 9. STEPS UP - bac thang nan leo thang (mock a3)
# =====================================================================
def steps_up(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.1:
        text_on(img, p["head"], W / 2, 72,
                fit_size(p["head"], 1160, 56, 30), INK)
    labels = [x.strip() for x in p["labels"].split("|")]
    while len(labels) < 3:
        labels.append("")
    base_y = 640
    if lay == 0:
        steps = [(70, 470, 360, MUST), (460, 350, 360, TEAL),
                 (850, 230, 360, CORAL)]
    else:
        steps = [(850, 470, 360, MUST), (460, 350, 360, TEAL),
                 (70, 230, 360, CORAL)]
    order = [0, 1, 2]
    for k, si in enumerate(order):
        x, top, wdt, col = steps[si]
        at = 0.35 + k * 0.35
        sx, sy = squash_at(t, at, 0.3)
        clay_blob(img, (x, top, x + wdt, base_y), col, radius=42,
                  sx=sx, sy=sy)
        lab = labels[si]
        if lab and t >= at + 0.15:
            fs = fit_size(lab, wdt - 40, 42, 24)
            text_on(img, lab, x + wdt / 2, top + 52, fs,
                    INK if col == MUST else WHITE)
    # bong dat set nhay len tung bac
    hop_t = [0.75, 1.15, 1.55]
    pos = [(steps[0][0] + 180, steps[0][1] - 36),
           (steps[1][0] + 180, steps[1][1] - 36),
           (steps[2][0] + 180, steps[2][1] - 36)]
    cur = 0
    for k, ht in enumerate(hop_t):
        if t >= ht:
            cur = k
    if t >= hop_t[0] - 0.35:
        bx, by = pos[cur]
        if cur > 0 and t < hop_t[cur] + 0.22:  # dang nhay: phong len
            fr = (t - hop_t[cur]) / 0.22
            px, py = pos[cur - 1]
            bx = px + (bx - px) * fr
            by = py + (by - py) * fr - math.sin(fr * math.pi) * 90
        clay_ball(img, bx, by, 34, SKY)
    return img


# =====================================================================
# 10. CLAY BUTTON END - man cuoi nut dat set lon
# =====================================================================
def clay_button_end(t, dur, p):
    img = bg()
    click_at = float(p["_click_at"])
    lay = _lay(p)
    cy_main = 150 if lay == 0 else 130
    if t >= 0.15:
        for j, ln in enumerate(wrap_lines(p["main"], 1120, 62)):
            text_on(img, ln, W / 2, cy_main + j * 74,
                    fit_size(ln, 1120, 62, 32), INK)
    if p["sub"] and t >= 0.6:
        text_on(img, p["sub"], W / 2, cy_main + 158,
                fit_size(p["sub"], 1100, 46, 26), CORAL)
    bw, bh = 560, 170
    bx0, by0 = W / 2 - bw / 2, 420 if lay == 0 else 400
    clicked = t >= click_at
    if clicked:
        k = clamp((t - click_at) / 0.18)
        sy = 1.0 - 0.30 * math.sin(min(1.0, k) * math.pi)
        sx = 1.0 + 0.16 * math.sin(min(1.0, k) * math.pi)
    else:
        pulse = 1.0 + 0.02 * math.sin(t * 2.6)
        sx, sy = pulse, pulse
    if t >= 1.0:
        clay_blob(img, (bx0, by0, bx0 + bw, by0 + bh),
                  TEAL if clicked else CORAL, radius=80, sx=sx, sy=sy)
        label = p["done_text"] if clicked else p["button"]
        text_on(img, label, W / 2, by0 + bh / 2,
                fit_size(label, bw - 90, 56, 30), WHITE)
        if clicked:  # vong dat set lan ra sau khi bam
            k2 = clamp((t - click_at) / 0.7)
            if k2 < 1.0:
                d = ImageDraw.Draw(img)
                rr = int(120 + k2 * 260)
                d.ellipse([W / 2 - rr, by0 + bh / 2 - rr * 0.5,
                           W / 2 + rr, by0 + bh / 2 + rr * 0.5],
                          outline=TEAL + (int(160 * (1 - k2)),), width=7)
    return img
