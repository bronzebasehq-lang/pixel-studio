#!/usr/bin/env python3
"""FLAT TEMPLATES - goi phong cach "FLAT" (do hoa phang hien dai) cho
Pixel Studio. Theo mock flat-b1..b3 (~/workspace/pixel-tool-mockup/
pack-ideas-v3/) da duyet: PHANG TUYET DOI - khong texture, khong
gradient, khong do bong (chi cho phep bong dai 1 tong rat nhe o vai
khoi lon); nen tron luan phien san ho #FF6B5B / ngoc #0FA3A3 / vang
#FFB703 / navy #1D3557; khoi hinh hoc sac net; chu Noto Sans Black
trang/navy, nhieu khoang tho.

Module ve thuan (chi PIL): moi ham fn(t, dur, p) -> RGBA 1280x720.
p = dict tham so CHUOI da merge + khoa tinh toan "_" o flat_scenes
(_layout: 0 = bien the A, 1 = bien the B).
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 1280, 720
CORAL = (255, 107, 91)        # #FF6B5B
TEAL = (15, 163, 163)         # #0FA3A3
YEL = (255, 183, 3)           # #FFB703
NAVY = (29, 53, 87)           # #1D3557
NAVY_D = (18, 33, 56)
WHITE = (255, 255, 255)
GREY = (154, 165, 177)
GREY_D = (128, 140, 155)
PAPER_W = (250, 250, 248)
PALETTE = [CORAL, TEAL, YEL, NAVY]


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


def pop_scale(t, at, dur=0.22):
    """He so phong pop-in tai 'at' (0 neu chua toi)."""
    if t < at:
        return 0.0
    return ease_out_back((t - at) / dur)


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


def bg(col):
    return Image.new("RGBA", (W, H), col + (255,))


def text_l(img, text, x, cy, size, col, path=SANS):
    """Chu canh trai: x = mep trai, cy = tam doc."""
    f = _font(path, size)
    bb = _DUMMY.textbbox((0, 0), text, font=f)
    d = ImageDraw.Draw(img)
    d.text((x, cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f,
           fill=col + (255,))
    return _tw(text, f)


def text_c(img, text, cy, size, col, cx=W / 2, path=SANS):
    f = _font(path, size)
    tw = _tw(text, f)
    bb = _DUMMY.textbbox((0, 0), text, font=f)
    d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f,
           fill=col + (255,))
    return tw


def scaled_rect(img, box, col, sc, radius=0):
    """Hinh chu nhat phong theo he so sc quanh tam (pop-in phang)."""
    if sc <= 0.01:
        return
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2 * sc, (y1 - y0) / 2 * sc
    d = ImageDraw.Draw(img)
    if radius:
        d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh],
                            radius=int(radius * sc), fill=col + (255,))
    else:
        d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=col + (255,))


def scaled_circle(img, cx, cy, r, col, sc):
    if sc <= 0.01:
        return
    rr = r * sc
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (255,))


def col_of(name, default=CORAL):
    cols = {"coral": CORAL, "teal": TEAL, "yel": YEL, "navy": NAVY,
            "white": WHITE, "grey": GREY}
    return cols.get(str(name or "").strip().lower(), default)


def _lay(p):
    return int(p.get("_layout", 0))


# =====================================================================
# 1. FLAT HOOK - vong tron lon chua he so xN (mock b1)
# =====================================================================
def flat_hook(t, dur, p):
    img = bg(col_of(p["bgc"]))
    lay = _lay(p)
    ccx = 950 if lay == 0 else 330
    tx = 110 if lay == 0 else 560
    sc = pop_scale(t, 0.15)
    scaled_circle(img, ccx, 360, 218, WHITE, sc)
    if t >= 0.3:
        text_c(img, p["mult"], 366, fit_size(p["mult"], 330, 210, 80),
               NAVY, cx=ccx)
    if t >= 0.4:
        s1 = fit_size(p["head1"], 560, 120, 48)
        text_l(img, p["head1"], tx, 268, s1, WHITE)
        s2 = fit_size(p["head2"], 560, 120, 48)
        text_l(img, p["head2"], tx, 268 + int(s1 * 1.25), s2, WHITE)
        d = ImageDraw.Draw(img)
        d.rectangle([tx + 4, 268 + int(s1 * 1.25) + int(s2 * 0.85),
                     tx + 284, 268 + int(s1 * 1.25) + int(s2 * 0.85) + 15],
                    fill=YEL + (255,))
    return img


# =====================================================================
# 2. VERDICT BLOCK - khoi mau phan quyet dap xuong
# =====================================================================
def verdict_block(t, dur, p):
    img = bg(NAVY)
    lay = _lay(p)
    if t >= 0.15:
        text_c(img, p["head"], 130, fit_size(p["head"], 1140, 58, 30),
               WHITE)
    flip_at = float(p["_stamp_at"])
    if t >= flip_at:
        sc = pop_scale(t, flip_at, 0.2)
        box = (240, 230, 1040, 500) if lay == 0 else (140, 250, 900, 520)
        scaled_rect(img, box, col_of(p["color"], TEAL), sc, radius=6)
        if sc > 0.6:
            vs = fit_size(p["verdict"], 700, 110, 44)
            text_c(img, p["verdict"], (box[1] + box[3]) / 2, vs,
                   NAVY if col_of(p["color"], TEAL) == YEL else WHITE,
                   cx=(box[0] + box[2]) / 2)
    if p["sub"] and t >= flip_at + 0.5:
        text_c(img, p["sub"], 606, 38, GREY)
    return img


# =====================================================================
# 3. FLAT WINDOW - cua so phang chua dong noi dung
# =====================================================================
def flat_window(t, dur, p):
    img = bg(TEAL)
    lay = _lay(p)
    box = (140, 80, 1140, 640) if lay == 0 else (240, 80, 1220, 640)
    if t >= 0.12:
        sc = pop_scale(t, 0.12, 0.25)
        scaled_rect(img, (box[0], box[1], box[2], box[3]), PAPER_W, sc)
        scaled_rect(img, (box[0], box[1], box[2], box[1] + 76), NAVY,
                    sc)
    d = ImageDraw.Draw(img)
    if t >= 0.3:
        text_l(img, p["title"], box[0] + 34, box[1] + 40, 38, WHITE)
        for i, c in enumerate([CORAL, YEL, TEAL]):
            cx = box[2] - 46 - (2 - i) * 44
            d.ellipse([cx - 11, box[1] + 27, cx + 11, box[1] + 49],
                      fill=c + (255,))
    lines = [x.strip() for x in p["lines"].split("|") if x.strip()]
    starts = p["_starts"]
    for i, ln in enumerate(lines[:5]):
        if t < starts[i]:
            continue
        y = box[1] + 116 + i * 92
        d.rectangle([box[0] + 34, y, box[0] + 86, y + 52],
                    fill=PALETTE[i % 4] + (255,))
        text_l(img, ln, box[0] + 112, y + 28,
               fit_size(ln, box[2] - box[0] - 150, 40, 24), NAVY)
    return img


# =====================================================================
# 4. FLAT AB - chia doi 2 nen (mock b3)
# =====================================================================
def flat_ab(t, dur, p):
    img = bg(YEL)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W / 2, H], fill=NAVY + (255,))
    swapped = (_lay(p) == 1)
    a_side = W / 2 if swapped else 0          # nua chua CACH CU (navy)
    b_side = 0 if swapped else W / 2
    if t >= 0.15:
        text_c(img, p["label_a"], 120, 54, WHITE, cx=a_side + W / 4)
        d.rectangle([a_side + W / 4 - 90, 164, a_side + W / 4 + 90, 180],
                    fill=CORAL + (255,))
        text_c(img, p["label_b"], 120, 54, NAVY, cx=b_side + W / 4)
        d.rectangle([b_side + W / 4 - 90, 164, b_side + W / 4 + 90, 180],
                    fill=NAVY + (255,))
    if t >= 0.4:  # dong khoi vuong xam lon xon ben cu
        pile = [(70, 300, 130), (215, 260, 105), (130, 430, 105),
                (300, 380, 140), (395, 290, 95), (240, 180, 78)]
        for i, (px, py, s) in enumerate(pile):
            d.rectangle([a_side + px, py, a_side + px + s, py + s],
                        fill=(GREY if i % 2 == 0 else GREY_D) + (255,))
    if t >= 0.65:  # 1 khoi tron trang gon ben moi
        sc = pop_scale(t, 0.65, 0.25)
        scaled_circle(img, b_side + W / 4, 400, 118, WHITE, sc)
    strip_y = 618
    d.rectangle([0, strip_y, W, H], fill=NAVY_D + (255,))
    if t >= 0.95:
        text_c(img, p["question"], (strip_y + H) / 2, 44, WHITE)
    return img


# =====================================================================
# 5. FLAT LIST - hang phang truot vao
# =====================================================================
def flat_list(t, dur, p):
    img = bg(PAPER_W)
    lay = _lay(p)
    if t >= 0.1:
        if lay == 0:
            text_l(img, p["title"], 90, 84,
                   fit_size(p["title"], 1100, 58, 30), NAVY)
        else:
            text_c(img, p["title"], 84,
                   fit_size(p["title"], 1100, 58, 30), NAVY)
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    starts = p["_starts"]
    x0 = 90 if lay == 0 else 190
    wdt = 1100 if lay == 0 else 1000
    d = ImageDraw.Draw(img)
    for i, it in enumerate(items[:5]):
        if t < starts[i]:
            continue
        y = 150 + i * 106
        k = ease_out_cubic((t - starts[i]) / 0.3)
        off = int((1 - k) * -130) if lay == 0 else int((1 - k) * 130)
        col = PALETTE[i % 4]
        d.rectangle([x0 + off, y, x0 + off + wdt, y + 84],
                    fill=col + (255,))
        tcol = NAVY if col == YEL else WHITE
        text_l(img, it, x0 + off + 36, y + 44,
               fit_size(it, wdt - 80, 44, 24), tcol)
    return img


# =====================================================================
# 6. FLAT DATA - cot phang + so khong lo (mock b2)
# =====================================================================
def flat_data(t, dur, p):
    img = bg(PAPER_W)
    lay = _lay(p)
    vals = []
    for x in p["values"].split(","):
        try:
            vals.append(float(x.strip()))
        except ValueError:
            pass
    vals = (vals + [25, 40, 65, 90])[:4]
    mx = max(vals) or 1.0
    base_y = 590
    chart_x = 110 if lay == 0 else 600
    step = 160 if lay == 0 else 140
    bw = 110 if lay == 0 else 100
    d = ImageDraw.Draw(img)
    d.rectangle([chart_x, base_y, chart_x + 640, base_y + 8],
                fill=(210, 216, 224, 255))
    for i, v in enumerate(vals):
        at = 0.3 + i * 0.22
        if t < at:
            continue
        k = ease_out_cubic((t - at) / 0.45)
        hgt = int(430 * (v / mx) * k)
        x = chart_x + 20 + i * step
        d.rectangle([x, base_y - hgt, x + bw, base_y],
                    fill=PALETTE[i % 4] + (255,))
        if k > 0.85:
            lab = ("%g" % v)
            text_c(img, lab, base_y - hgt - 42, 46, NAVY, cx=x + bw // 2)
    big_x = 830 if lay == 0 else 130
    if t >= 0.7:
        bs = fit_size(p["big"], 420, 150, 54)
        text_l(img, p["big"], big_x, 268, bs, NAVY)
        text_l(img, p["big_label"], big_x + 4, 268 + int(bs * 0.85), 52,
               TEAL)
        d.rectangle([big_x + 4, 268 + int(bs * 0.85) + 48,
                     big_x + 190, 268 + int(bs * 0.85) + 62],
                    fill=YEL + (255,))
    if p["note"] and t >= 1.5:
        text_l(img, p["note"], chart_x + 4, 660, 30, GREY_D)
    return img


# =====================================================================
# 7. FLAT GRID - luoi o phang
# =====================================================================
def flat_grid(t, dur, p):
    img = bg(NAVY)
    lay = _lay(p)
    if t >= 0.1:
        text_c(img, p["title"], 72, fit_size(p["title"], 1140, 52, 28),
               WHITE)
    total, cols = int(p["_total"]), int(p["_cols"])
    step = float(p["_step"])
    rows = int(math.ceil(total / float(cols)))
    cell, gap = 132, 22
    gw = cols * cell + (cols - 1) * gap
    gh = rows * cell + (rows - 1) * gap
    x0 = (W - gw) / 2
    y0 = 140 if lay == 0 else (H - gh) / 2 + 26
    for i in range(total):
        at = 0.4 + i * step
        sc = pop_scale(t, at, 0.18)
        r, c = divmod(i, cols)
        box = (x0 + c * (cell + gap), y0 + r * (cell + gap),
               x0 + c * (cell + gap) + cell, y0 + r * (cell + gap) + cell)
        col = CORAL if i == total - 1 else PALETTE[i % 4]
        scaled_rect(img, box, col, sc)
        if sc > 0.7:
            text_c(img, str(i + 1), (box[1] + box[3]) / 2, 44,
                   NAVY if col == YEL else WHITE, cx=(box[0] + box[2]) / 2)
    if p["caption"] and t >= 0.4 + total * step + 0.15:
        text_c(img, p["caption"], 668, 34, YEL)
    return img


# =====================================================================
# 8. FLAT PROGRESS - thanh phang + % lon
# =====================================================================
def flat_progress(t, dur, p):
    img = bg(PAPER_W)
    lay = _lay(p)
    pct = float(p["_pct"])
    fill_dur = float(p["_fill_dur"])
    t_lines = float(p["_t_lines"])
    pr = ease_out_cubic((t - 0.3) / max(0.05, fill_dur))
    cur = pct * pr
    bar_y = 170 if lay == 0 else 470
    txt_y = 330 if lay == 0 else 130
    text_l(img, "%d%%" % int(round(cur)), 100, bar_y - 58, 96, NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([100, bar_y, 1180, bar_y + 64], fill=(226, 230, 236, 255))
    if cur > 0:
        d.rectangle([100, bar_y, 100 + int(1080 * cur / 100.0),
                     bar_y + 64], fill=CORAL + (255,))
    entries = [(p["line1"], 44, NAVY, t_lines),
               (p["question"], 54, CORAL, t_lines + 0.55),
               (p["answer"], 46, TEAL, t_lines + 1.10)]
    for txt, size, colr, at in entries:
        if txt and t >= at:
            text_l(img, txt, 100, txt_y, fit_size(txt, 1080, size, 26),
                   colr)
        txt_y += 82
    return img


# =====================================================================
# 9. FLAT STEPS - bac phang leo thang + huy hieu xN
# =====================================================================
def flat_steps(t, dur, p):
    img = bg(TEAL)
    lay = _lay(p)
    if t >= 0.1:
        text_c(img, p["head"], 74, fit_size(p["head"], 1140, 54, 28),
               WHITE)
    labels = [x.strip() for x in p["labels"].split("|")]
    while len(labels) < 3:
        labels.append("")
    base_y = 620
    heights = [180, 300, 420]
    cols3 = [NAVY, YEL, CORAL]
    xs = [110, 480, 850] if lay == 0 else [850, 480, 110]
    for k in range(3):
        at = 0.35 + k * 0.35
        if t < at:
            continue
        grow = ease_out_cubic((t - at) / 0.35)
        hgt = int(heights[k] * grow)
        d = ImageDraw.Draw(img)
        d.rectangle([xs[k], base_y - hgt, xs[k] + 320, base_y],
                    fill=cols3[k] + (255,))
        if labels[k] and grow > 0.9:
            text_c(img, labels[k], base_y - hgt + 44, 40,
                   NAVY if cols3[k] == YEL else WHITE, cx=xs[k] + 160)
    top_i = 2 if lay == 0 else 0
    if t >= 1.55:
        sc = pop_scale(t, 1.55, 0.22)
        scaled_circle(img, xs[top_i] + 160, base_y - heights[2] - 78, 62,
                      WHITE, sc)
        if sc > 0.6:
            text_c(img, p["mult"], base_y - heights[2] - 76,
                   fit_size(p["mult"], 110, 52, 28), NAVY,
                   cx=xs[top_i] + 160)
    return img


# =====================================================================
# 10. FLAT END - man cuoi phang: vong tron + nut
# =====================================================================
def flat_end(t, dur, p):
    img = bg(NAVY)
    click_at = float(p["_click_at"])
    lay = _lay(p)
    sc = pop_scale(t, 0.15, 0.3)
    scaled_circle(img, W / 2 if lay == 0 else 300, 215, 92, YEL, sc)
    tx = W / 2 if lay == 0 else 760
    if t >= 0.35:
        for j, ln in enumerate(wrap_lines(p["main"], 1080, 58)):
            text_c(img, ln, 368 + j * 70, fit_size(ln, 1080, 58, 30),
                   WHITE, cx=tx)
    if p["sub"] and t >= 0.8:
        text_c(img, p["sub"], 492, fit_size(p["sub"], 1000, 44, 24),
               YEL, cx=tx)
    if t >= 1.1:
        clicked = t >= click_at
        label = p["done_text"] if clicked else p["button"]
        f = _font(SANS, 42)
        bw = int(_tw(label, f)) + 72
        bx0, by0 = tx - bw / 2, 548
        d = ImageDraw.Draw(img)
        if clicked:
            d.rectangle([bx0, by0, bx0 + bw, by0 + 76], fill=CORAL + (255,))
            text_c(img, label, by0 + 40, 42, WHITE, cx=tx)
        else:
            d.rectangle([bx0, by0, bx0 + bw, by0 + 76],
                        outline=WHITE + (255,), width=4)
            text_c(img, label, by0 + 40, 42, WHITE, cx=tx)
    return img
