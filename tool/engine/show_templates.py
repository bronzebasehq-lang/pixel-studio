#!/usr/bin/env python3
"""SHOW TEMPLATES - goi phong cach "SHOW" (gameshow truyen hinh) cho
Pixel Studio. Theo mock show-c1..c3 (~/workspace/pixel-tool-mockup/
pack-ideas-v3/) da duyet: studio TV tim -> xanh (#2B1055 -> #1B2A6B),
san phan chieu mo; bien marquee vien bong den vang PHAT SANG NHAP
NHAY DUOI NHAU (hieu ung chu ky - bong sang luân phien 2 trang thai
theo nhip frame); vong quay 8 mui mau co kim chi; bang diem LED den
chu JetBrains Mono vang; buc 2-1-3 leo thang; man cuoi phao giay roi
+ bien marquee. Mau nhan: vang #FFD23F, hong #FF5D8F, cyan #4CC9F0.

Module ve thuan (chi PIL): moi ham fn(t, dur, p) -> RGBA 1280x720.
p = dict tham so CHUOI da merge + khoa tinh toan "_" o show_scenes
(_layout: 0 = bien the A, 1 = bien the B).
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SANS = str(_FONT_DIR / "NotoSans-Black.ttf")
MONO = str(_FONT_DIR / "JetBrainsMono-Bold.ttf")
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 1280, 720
TOP = (43, 16, 85)            # #2B1055
BOT = (27, 42, 107)           # #1B2A6B
YEL = (255, 210, 63)          # #FFD23F
PINK = (255, 93, 143)         # #FF5D8F
CYAN = (76, 201, 240)         # #4CC9F0
PURPLE = (123, 44, 191)
WHITE = (255, 255, 255)
PANEL = (61, 26, 120)
DARK = (20, 12, 46)
LED_BG = (8, 8, 14)
GREEN_L = (74, 240, 138)
WHEEL_COLS = [YEL, PINK, CYAN, PURPLE, YEL, PINK, CYAN, PURPLE]


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


# ------------------------------------------------------------------ nen
_BG = None


def bg():
    """Nen studio: gradient tim->xanh + san phan chieu mo (cache)."""
    global _BG
    if _BG is not None:
        return _BG.copy()
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / float(H - 1)
        c = tuple(int(TOP[i] + (BOT[i] - TOP[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c + (255,))
    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fl)
    fd.rectangle([0, H - 150, W, H], fill=(255, 255, 255, 13))
    fd.line([(0, H - 150), (W, H - 150)], fill=(255, 255, 255, 38),
            width=2)
    img.alpha_composite(fl)
    _BG = img
    return _BG.copy()


def spotlight(img, apex_x, target_x, spread, alpha=26):
    """Chum den roi mem tu dinh xuong san (lop mo rieng)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(apex_x, 0), (target_x - spread, H),
               (target_x + spread, H)], fill=(255, 240, 190, alpha))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(28)))


def text_c(img, text, cy, size, col, cx=W / 2, path=SANS):
    f = _font(path, size)
    tw = _tw(text, f)
    bb = _DUMMY.textbbox((0, 0), text, font=f)
    d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f,
           fill=col + (255,))
    return tw


def text_l(img, text, x, cy, size, col, path=SANS):
    f = _font(path, size)
    bb = _DUMMY.textbbox((0, 0), text, font=f)
    d = ImageDraw.Draw(img)
    d.text((x, cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f,
           fill=col + (255,))
    return _tw(text, f)


# ------------------------------------------------------------------ marquee
def _bulb_points(box, r, step=64):
    """Diem bong den doc vien hinh chu nhat bo goc (goc + canh)."""
    x0, y0, x1, y1 = box
    pts = []
    x = x0 + r
    while x <= x1 - r:
        pts.append((x, y0))
        x += step
    y = y0 + r
    while y <= y1 - r:
        pts.append((x1, y))
        y += step
    x = x1 - r
    while x >= x0 + r:
        pts.append((x, y1))
        x -= step
    y = y1 - r
    while y >= y0 + r:
        pts.append((x0, y))
        y -= step
    for (ccx, ccy), a0 in [((x0 + r, y0 + r), 180), ((x1 - r, y0 + r), 270),
                           ((x1 - r, y1 - r), 0), ((x0 + r, y1 - r), 90)]:
        for a in range(a0, a0 + 91, 30):
            pts.append((ccx + r * math.cos(math.radians(a)),
                        ccy + r * math.sin(math.radians(a))))
    return pts


def marquee(img, box, t, chase=5.0, panel_col=PANEL, outline=YEL):
    """Bien marquee: tam nen + vien + bong den NHAP NHAY DUOI NHAU
    (bong chan/le sang luân phien theo nhip 'chase' lan/giay)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    r = 42
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=panel_col + (255,),
                        outline=outline + (255,), width=5)
    pts = _bulb_points((x0, y0, x1, y1), r)
    phase = int(t * chase) % 2
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, (bx, by) in enumerate(pts):
        if (i + phase) % 2 == 0:
            gd.ellipse([bx - 26, by - 26, bx + 26, by + 26],
                       fill=(255, 190, 60, 95))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(img)
    for i, (bx, by) in enumerate(pts):
        on = (i + phase) % 2 == 0
        rad = 10 if on else 8
        d.ellipse([bx - rad, by - rad, bx + rad, by + rad],
                  fill=(255, 208, 90, 255) if on else (146, 104, 40, 255))
        if on:
            d.ellipse([bx - 4, by - 4, bx + 4, by + 4],
                      fill=(255, 246, 200, 255))


def led_board(img, box, outline=(90, 90, 120)):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=22, fill=LED_BG + (255,),
                        outline=outline + (255,), width=4)


def confetti(img, t, t0, n=70, seed=9):
    """Phao giay roi: manh giay mau roi + xoay nhe, bat dau tu t0."""
    if t < t0:
        return
    rng = random.Random(seed)
    cols = [YEL, PINK, CYAN, WHITE]
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = rng.uniform(20, W - 20)
        speed = rng.uniform(120, 300)
        y = ((rng.uniform(0, H) + (t - t0) * speed) % (H + 60)) - 30
        s = rng.uniform(7, 14)
        sway = math.sin((t - t0) * 2.2 + i) * 16
        col = cols[i % 4]
        d.rectangle([x + sway, y, x + sway + s, y + s * 0.55],
                    fill=col + (235,))


def _lay(p):
    return int(p.get("_layout", 0))


def col_of(name, default=YEL):
    cols = {"yel": YEL, "pink": PINK, "cyan": CYAN, "white": WHITE}
    return cols.get(str(name or "").strip().lower(), default)


# =====================================================================
# 1. MARQUEE HOOK - bien marquee moc (mock c1)
# =====================================================================
def marquee_hook(t, dur, p):
    img = bg()
    spotlight(img, W / 2, W / 2, 620, 20)
    lay = _lay(p)
    box = (150, 130, 1130, 590) if lay == 0 else (150, 84, 1130, 520)
    if t >= 0.12:
        marquee(img, box, t)
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    if t >= 0.35:
        # dong 1: chu thuong + tu nhan mau hong (accent)
        line1 = p["line1"]
        acc = p["accent"]
        size = fit_size(line1, box[2] - box[0] - 150, 118, 46)
        f = _font(SANS, size)
        if acc and acc in line1:
            a, b = line1.split(acc, 1)
            tot = _tw(a, f) + _tw(acc, f) + _tw(b, f)
            x = cx - tot / 2
            bb = _DUMMY.textbbox((0, 0), line1, font=f)
            yy = cy - size * 0.72 - (bb[3] - bb[1]) / 2 - bb[1]
            d = ImageDraw.Draw(img)
            d.text((x, yy), a, font=f, fill=YEL + (255,))
            d.text((x + _tw(a, f), yy), acc, font=f, fill=PINK + (255,))
            d.text((x + _tw(a, f) + _tw(acc, f), yy), b, font=f,
                   fill=YEL + (255,))
        else:
            text_c(img, line1, cy - size * 0.72, size, YEL, cx=cx)
    if p["line2"] and t >= 0.8:
        text_c(img, p["line2"], cy + size * 0.85,
               fit_size(p["line2"], box[2] - box[0] - 150, 110, 44),
               YEL, cx=cx)
    if lay == 1 and t >= 1.3:
        led_board(img, (430, 566, 850, 648))
        text_c(img, "TRỰC TIẾP · LIVE", 608, 36, CYAN, path=MONO)
    return img


# =====================================================================
# 2. VERDICT SIGN - bien phan quyet + den bao dung/sai
# =====================================================================
def verdict_sign(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.12:
        text_c(img, p["head"], 96, fit_size(p["head"], 1140, 54, 28),
               WHITE)
    vat = float(p["_verdict_at"])
    box = (190, 170, 1090, 520) if lay == 0 else (120, 180, 940, 530)
    if t >= vat:
        marquee(img, box, t, chase=8.0)
        vs = fit_size(p["verdict"], box[2] - box[0] - 160, 120, 44)
        text_c(img, p["verdict"], (box[1] + box[3]) / 2, vs,
               col_of(p["verdict_col"]), cx=(box[0] + box[2]) / 2)
    # 2 den bao 2 ben: xanh = dung (sang sau verdict)
    d = ImageDraw.Draw(img)
    lamp_y = 345 if lay == 0 else 355
    lamp_xs = [110, 1170] if lay == 0 else [1010, 1100]
    for i, lx in enumerate(lamp_xs[:1] if lay == 1 else lamp_xs):
        on = t >= vat + 0.25
        col = GREEN_L if on else (52, 70, 58)
        d.ellipse([lx - 30, lamp_y - 30, lx + 30, lamp_y + 30],
                  fill=col + (255,))
        d.ellipse([lx - 11, lamp_y - 11, lx + 11, lamp_y + 11],
                  fill=(215, 255, 226, 255) if on else (90, 110, 96, 255))
    if p["sub"] and t >= vat + 0.55:
        text_c(img, p["sub"], 606, 38, CYAN)
    return img


# =====================================================================
# 3. SHOW WINDOW - bang LED chua dong noi dung
# =====================================================================
def show_window(t, dur, p):
    img = bg()
    lay = _lay(p)
    box = (130, 80, 1150, 640) if lay == 0 else (230, 80, 1210, 640)
    if t >= 0.12:
        led_board(img, box)
    if t >= 0.3:
        text_l(img, p["title"], box[0] + 40, box[1] + 52, 40, CYAN,
               path=MONO)
        d = ImageDraw.Draw(img)
        d.line([(box[0] + 40, box[1] + 92), (box[2] - 40, box[1] + 92)],
               fill=(60, 60, 90, 255), width=3)
    lines = [x.strip() for x in p["lines"].split("|") if x.strip()]
    starts = p["_starts"]
    for i, ln in enumerate(lines[:5]):
        if t < starts[i]:
            continue
        y = box[1] + 150 + i * 84
        text_l(img, "> " + ln, box[0] + 40, y,
               fit_size("> " + ln, box[2] - box[0] - 80, 38, 22), YEL,
               path=MONO)
    # vet quet sang chay doc bang theo nhip
    if t >= 0.4:
        sx = box[0] + int(((t * 130) % (box[2] - box[0] + 240))) - 120
        lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay2)
        ld.rectangle([sx, box[1] + 8, sx + 60, box[3] - 8],
                     fill=(255, 255, 255, 16))
        img.alpha_composite(lay2)
    return img


# =====================================================================
# 4. SHOW AB - 2 bien marquee so sanh
# =====================================================================
def show_ab(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.1:
        text_c(img, p["head"], 72, fit_size(p["head"], 1140, 52, 26),
               WHITE)
    if lay == 0:
        box_a, box_b = (70, 180, 580, 560), (700, 180, 1210, 560)
    else:
        box_a, box_b = (240, 150, 1040, 380), (240, 420, 1040, 650)
    if t >= 0.35:  # bien A mo (khong chase, bong tat)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box_a, radius=36, fill=(40, 30, 70, 255),
                            outline=(110, 100, 130, 255), width=4)
        text_c(img, p["label_a"], (box_a[1] + box_a[3]) / 2 - 30,
               fit_size(p["label_a"], 430, 56, 26), (168, 162, 198),
               cx=(box_a[0] + box_a[2]) / 2)
        if p["note_a"]:
            text_c(img, p["note_a"], (box_a[1] + box_a[3]) / 2 + 42, 32,
                   (140, 135, 175), cx=(box_a[0] + box_a[2]) / 2)
    if t >= 0.6:  # bien B sang + chase
        marquee(img, box_b, t)
        text_c(img, p["label_b"], (box_b[1] + box_b[3]) / 2 - 30,
               fit_size(p["label_b"], 430, 56, 26), YEL,
               cx=(box_b[0] + box_b[2]) / 2)
        if p["note_b"]:
            text_c(img, p["note_b"], (box_b[1] + box_b[3]) / 2 + 42, 32,
                   WHITE, cx=(box_b[0] + box_b[2]) / 2)
    if t >= 1.0:
        vcx = W / 2 if lay == 0 else W / 2
        vcy = 370 if lay == 0 else 400
        d = ImageDraw.Draw(img)
        d.ellipse([vcx - 44, vcy - 44, vcx + 44, vcy + 44],
                  fill=DARK + (255,), outline=YEL + (255,), width=4)
        text_c(img, "VS", vcy, 36, YEL, cx=vcx)
    return img


# =====================================================================
# 5. SCORE LIST - bang diem LED nhieu dong
# =====================================================================
def score_list(t, dur, p):
    img = bg()
    lay = _lay(p)
    box = (150, 90, 1130, 630) if lay == 0 else (90, 90, 1050, 630)
    if t >= 0.12:
        led_board(img, box)
    if t >= 0.3:
        text_l(img, p["title"], box[0] + 40, box[1] + 50, 38, CYAN,
               path=MONO)
    rows = []
    for raw in p["rows"].split("|"):
        raw = raw.strip()
        if not raw:
            continue
        if "::" in raw:
            nm, sc = [q.strip() for q in raw.split("::", 1)]
        else:
            nm, sc = raw, ""
        rows.append((nm, sc))
    starts = p["_starts"]
    for i, (nm, sc) in enumerate(rows[:5]):
        if t < starts[i]:
            continue
        y = box[1] + 128 + i * 82
        text_l(img, nm, box[0] + 40, y,
               fit_size(nm, 560, 40, 24), WHITE)
        if sc:
            f = _font(MONO, 44)
            tw = _tw(sc, f)
            d = ImageDraw.Draw(img)
            bb = _DUMMY.textbbox((0, 0), sc, font=f)
            d.text((box[2] - 40 - tw, y - (bb[3] - bb[1]) / 2 - bb[1]),
                   sc, font=f, fill=YEL + (255,))
        d = ImageDraw.Draw(img)
        d.line([(box[0] + 40, y + 40), (box[2] - 40, y + 40)],
               fill=(46, 46, 74, 255), width=2)
    if lay == 1 and t >= 0.3:
        text_c(img, "BẢNG ĐIỂM", 200, 44, PINK, cx=1130)
        text_c(img, "TUẦN NÀY", 262, 44, YEL, cx=1130)
    return img


# =====================================================================
# 6. BIG SCORE - so diem LED khong lo dem tang
# =====================================================================
def big_score(t, dur, p):
    img = bg()
    lay = _lay(p)
    box = (190, 110, 1090, 500) if lay == 0 else (110, 130, 1010, 520)
    if t >= 0.12:
        marquee(img, (box[0] - 26, box[1] - 26, box[2] + 26, box[3] + 26),
                t, chase=4.0, panel_col=LED_BG, outline=(90, 90, 120))
    target = float(p["_target"])
    cd = float(p["_count_dur"])
    pr = ease_out_cubic((t - 0.3) / max(0.05, cd))
    val = target * pr
    txt = "{:,.0f}".format(val).replace(",", ".")
    if t >= 0.3:
        text_c(img, "ĐIỂM SỐ", box[1] + 62, 38, CYAN,
               cx=(box[0] + box[2]) / 2, path=MONO)
        text_c(img, txt, (box[1] + box[3]) / 2 + 26,
               fit_size(txt, box[2] - box[0] - 110, 150, 54, path=MONO),
               YEL, cx=(box[0] + box[2]) / 2, path=MONO)
    if p["label"] and t >= 0.3 + cd * 0.55:
        text_c(img, p["label"], 566, fit_size(p["label"], 1100, 48, 26),
               WHITE)
    if p["sub"] and t >= 0.3 + cd + 0.3:
        text_c(img, p["sub"], 640, 34, CYAN)
    return img


# =====================================================================
# 7. LIGHT GRID - luoi den san khau sang dan
# =====================================================================
def light_grid(t, dur, p):
    img = bg()
    lay = _lay(p)
    if t >= 0.1:
        text_c(img, p["title"], 70, fit_size(p["title"], 1140, 52, 28),
               WHITE)
    total, cols = int(p["_total"]), int(p["_cols"])
    step = float(p["_step"])
    rows = int(math.ceil(total / float(cols)))
    cell, gap = 150, 30
    gw = cols * cell + (cols - 1) * gap
    x0 = (W - gw) / 2 if lay == 0 else 100
    y0 = 150
    d = ImageDraw.Draw(img)
    for i in range(total):
        at = 0.4 + i * step
        r, c = divmod(i, cols)
        cx = x0 + c * (cell + gap) + cell / 2
        cy = y0 + r * (cell + gap) + cell / 2
        on = t >= at
        col = WHEEL_COLS[i % 8] if on else (44, 38, 74)
        if on:  # hao quang
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.ellipse([cx - 86, cy - 86, cx + 86, cy + 86],
                       fill=col + (70,))
            img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
            d = ImageDraw.Draw(img)
        d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=col + (255,),
                  outline=(16, 10, 36, 255), width=5)
        d.ellipse([cx - 20, cy - 24, cx + 8, cy - 4],
                  fill=(255, 255, 255, 200) if on else (70, 64, 100, 255))
    if p["caption"] and t >= 0.4 + total * step + 0.15:
        text_c(img, p["caption"], 668, 36, YEL)
    return img


# =====================================================================
# 8. WHEEL PROGRESS - vong quay + bang % LED (mock c2)
# =====================================================================
def _draw_wheel(img, cx, cy, R, rot_deg):
    d = ImageDraw.Draw(img)
    start = -90 - 22.5 + rot_deg
    for i, col in enumerate(WHEEL_COLS):
        d.pieslice([cx - R, cy - R, cx + R, cy + R],
                   start + i * 45, start + (i + 1) * 45, fill=col + (255,))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=DARK + (255,),
              width=13)
    for i in range(8):
        a = math.radians(start + i * 45)
        d.line([cx, cy, cx + R * math.cos(a), cy + R * math.sin(a)],
               fill=DARK + (255,), width=8)
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=DARK + (255,),
              outline=YEL + (255,), width=7)


def wheel_progress(t, dur, p):
    img = bg()
    lay = _lay(p)
    spotlight(img, W / 2, 360, 480, 22)
    pct = float(p["_pct"])
    spin = float(p["_spin_dur"])
    # vong quay dung o mui theo %: mui dich = pct/100 * 8
    seg = int(pct / 100.0 * 8) % 8
    final_rot = 360.0 * 3 - seg * 45.0
    pr = ease_out_cubic((t - 0.25) / max(0.05, spin))
    rot = final_rot * pr
    cx, cy, R = (350, 370, 235) if lay == 0 else (930, 370, 235)
    _draw_wheel(img, cx, cy, R, rot)
    d = ImageDraw.Draw(img)  # kim chi co dinh o dinh
    d.polygon([(cx - 34, cy - R - 48), (cx + 34, cy - R - 48),
               (cx, cy - R + 16)], fill=YEL + (255,),
              outline=DARK + (255,))
    if pr >= 1.0:  # nhan he so tren mui dich (o dinh, duoi kim chi)
        text_c(img, p["mult"], cy - R + 62, 54, DARK, cx=cx)
    bx = (640, 190, 1210, 470) if lay == 0 else (70, 190, 640, 470)
    led_board(img, bx)
    cur = pct * pr
    text_c(img, "TIẾN ĐỘ", bx[1] + 66, 36, CYAN,
           cx=(bx[0] + bx[2]) / 2, path=MONO)
    text_c(img, "%d%%" % int(round(cur)), (bx[1] + bx[3]) / 2 + 22,
           fit_size("%d%%" % int(pct), 380, 110, 44, path=MONO), YEL,
           cx=(bx[0] + bx[2]) / 2, path=MONO)
    # 3 den xanh duoi bang sang dan khi quay gan xong
    for i in range(3):
        on = pr >= 0.45 + i * 0.2
        lx = (bx[0] + bx[2]) / 2 + (i - 1) * 110
        ly = bx[3] + 56
        d.ellipse([lx - 24, ly - 24, lx + 24, ly + 24],
                  fill=(GREEN_L if on else (52, 70, 58)) + (255,))
    if p["label"] and pr >= 1.0:
        text_c(img, p["label"], 622, fit_size(p["label"], 1100, 44, 24),
               WHITE)
    return img


# =====================================================================
# 9. PODIUM STEPS - buc 2-1-3 leo thang (mock c3)
# =====================================================================
def podium_steps(t, dur, p):
    img = bg()
    spotlight(img, W / 2, W / 2, 700, 26)
    lay = _lay(p)
    if t >= 0.1:
        text_c(img, p["head"], 70, fit_size(p["head"], 1140, 52, 28),
               WHITE)
    labels = [x.strip() for x in p["labels"].split("|")]
    while len(labels) < 3:
        labels.append("")
    base_y = 600
    pods = [(150, 390, 300, (192, 198, 208), "2", labels[1]),
            (490, 290, 300, (255, 196, 48), "1", labels[0]),
            (830, 440, 300, (205, 127, 50), "3", labels[2])]
    if lay == 1:
        pods = [(830, 390, 300, (192, 198, 208), "2", labels[1]),
                (490, 290, 300, (255, 196, 48), "1", labels[0]),
                (150, 440, 300, (205, 127, 50), "3", labels[2])]
    d = ImageDraw.Draw(img)
    order = [0, 2, 1]  # buc 2, 3 dung truoc; buc 1 (giua) dung sau cung
    for k, pi in enumerate(order):
        x, top, wdt, col, num, lab = pods[pi]
        at = 0.35 + k * 0.35
        if t < at:
            continue
        grow = ease_out_cubic((t - at) / 0.35)
        cur_top = base_y - int((base_y - top) * grow)
        d.polygon([(x - 14, cur_top), (x + wdt + 14, cur_top),
                   (x + wdt, cur_top + 26), (x, cur_top + 26)],
                  fill=tuple(min(255, c + 36) for c in col) + (255,))
        if base_y - (cur_top + 26) >= 2:
            d.rectangle([x, cur_top + 26, x + wdt, base_y],
                        fill=col + (255,))
        if grow > 0.9:
            text_c(img, num, (cur_top + 26 + base_y) / 2 + 6, 84,
                   (40, 30, 20), cx=x + wdt / 2)
            if lab:
                text_c(img, lab, cur_top - 34,
                       fit_size(lab, wdt + 60, 38, 22), WHITE,
                       cx=x + wdt / 2)
    # hop qua phat sang tren buc 1 sau khi buc dung xong
    if t >= 1.55:
        gx, gy = 640, 168
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([gx - 130, gy - 110, gx + 130, gy + 110],
                   fill=(255, 205, 70, 120))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(36)))
        d = ImageDraw.Draw(img)
        d.rectangle([gx - 62, gy - 40, gx + 62, gy + 48],
                    fill=(255, 214, 90, 255))
        d.rectangle([gx - 70, gy - 62, gx + 70, gy - 38],
                    fill=(255, 224, 130, 255))
        d.rectangle([gx - 11, gy - 62, gx + 11, gy + 48],
                    fill=PINK + (255,))
    return img


# =====================================================================
# 10. SHOW END - man cuoi marquee + phao giay
# =====================================================================
def show_end(t, dur, p):
    img = bg()
    spotlight(img, W / 2, W / 2, 640, 22)
    click_at = float(p["_click_at"])
    lay = _lay(p)
    box = (170, 110, 1110, 500) if lay == 0 else (170, 84, 1110, 460)
    if t >= 0.12:
        marquee(img, box, t, chase=6.0)
    cx = (box[0] + box[2]) / 2
    if t >= 0.35:
        for j, ln in enumerate(wrap_lines(p["main"], 900, 60)):
            text_c(img, ln, (box[1] + box[3]) / 2 - 52 + j * 68,
                   fit_size(ln, 900, 60, 30), WHITE, cx=cx)
    if p["sub"] and t >= 0.85:
        text_c(img, p["sub"], (box[1] + box[3]) / 2 + 62,
               fit_size(p["sub"], 880, 44, 24), YEL, cx=cx)
    if t >= 1.15:
        clicked = t >= click_at
        label = p["done_text"] if clicked else p["button"]
        f = _font(SANS, 42)
        bw = int(_tw(label, f)) + 76
        bx0, by0 = W / 2 - bw / 2, 548
        d = ImageDraw.Draw(img)
        if clicked:
            d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + 78], radius=16,
                                fill=PINK + (255,))
        else:
            d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + 78], radius=16,
                                outline=YEL + (255,), width=4)
        text_c(img, label, by0 + 41, 42, WHITE if clicked else YEL)
    confetti(img, t, click_at, n=80, seed=14)
    return img
