#!/usr/bin/env python3
"""
PIXEL VIDEO - lop ve luoi pixel 320x180 (chuan PIXEL 16-BIT da khoa).

Ke thua tu pixel-tool-mockup/build_pixel_tool_mockup.py (ban mockup da duyet),
bo sung: sao nhap nhay theo thoi gian (tm), pulse phat sang, cac ham easing
dung chung cho chuyen dong. Moi canh deu ve qua lop nay de giu 1 chat pixel.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
FONTS = os.path.join(TOOL_DIR, "fonts")
FPIX = os.path.join(FONTS, "PressStart2P.ttf")
FVT = os.path.join(FONTS, "VT323.ttf")

GW, GH = 320, 180  # luoi ve 16-bit

# ---------------------------------------------------------------- bang mau khoa
PAL = {
    "sky_top":  (26, 21, 58),
    "sky":      (20, 16, 46),
    "sky_low":  (17, 14, 41),
    "ground":   (13, 11, 34),
    "ground_hi": (24, 20, 52),
    "sphere":   (6, 6, 14),
    "sph_out":  (88, 76, 168),
    "sph_out_d": (56, 47, 104),
    "sph_dot":  (64, 55, 124),
    "orange":   (246, 174, 32),
    "orange_d": (214, 132, 10),
    "bldg":     (46, 38, 88),
    "bldg2":    (38, 31, 72),
    "bldg_d":   (33, 27, 63),
    "window":   (248, 205, 84),
    "window_d": (196, 150, 44),
    "star":     (200, 208, 248),
    "star_dim": (120, 128, 190),
    "shadow":   (3, 3, 8),
    "skin":     (244, 199, 143),
    "skin_d":   (219, 164, 105),
    "hair":     (66, 52, 110),
    "shirt":    (33, 166, 190),
    "shirt_d":  (22, 122, 142),
    "pants":    (34, 29, 60),
    "desk":     (98, 74, 156),
    "desk_d":   (70, 52, 112),
    "chair":    (50, 41, 94),
    "bubble":   (246, 246, 252),
    "bubble_d": (206, 208, 226),
    "win_in":   (30, 25, 70),
    "win_fr":   (66, 61, 124),
    "moon":     (248, 234, 192),
    "lamp":     (248, 166, 20),
    "lamp_hi":  (255, 214, 110),
    "lamp_pole": (236, 228, 208),
    "lap_fr":   (26, 26, 46),
    "lap_in":   (14, 16, 34),
    "lap_ln1":  (72, 210, 230),
    "lap_ln2":  (96, 228, 152),
    "black":    (0, 0, 0),
    "cyan":     (46, 224, 255),
    "cyan_d":   (28, 156, 190),
    "green":    (52, 245, 165),
    "green_d":  (30, 178, 116),
    "pink":     (255, 93, 115),
    "pink_d":   (206, 62, 88),
    "red":      (255, 77, 94),
    "red_d":    (198, 48, 64),
    "mint":     (62, 207, 142),
    "skyblue":  (42, 168, 224),
    "skyblue_d": (30, 122, 178),
    "cream":    (255, 236, 200),
    "violet":   (124, 58, 237),
    "violet_d": (92, 40, 182),
    "edge_dim": (52, 58, 110),
    "axis":     (90, 96, 150),
    "halo_teal": (16, 48, 62),
    "halo_red": (64, 22, 34),
    "white":    (245, 248, 255),
}


def lite(c, f=0.30):
    return tuple(int(v + (255 - v) * f) for v in c)


def dark(c, f=0.72):
    return tuple(int(v * f) for v in c)


def lerp(a, b, k):
    return a + (b - a) * k


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


def window(t, start, dur):
    """Tien trinh cuc bo 0..1 cua 1 phan tu bat dau tai 'start', keo dai 'dur'."""
    return clamp((t - start) / dur)


def stars_for(seed, n=95):
    rng = random.Random(seed)
    return [(rng.uniform(0.01, 0.99), rng.uniform(0.01, 0.82), rng.random(),
             rng.uniform(0, 6.28)) for _ in range(n)]


# ---------------------------------------------------------------- lop ve luoi
class Painter:
    """Ve bang toa do chuan hoa (0..1) len luoi 320x180."""

    def __init__(self, pal=PAL):
        self.w, self.h = GW, GH
        self.pal = pal
        self.img = Image.new("RGB", (GW, GH), pal["sky"])
        self.d = ImageDraw.Draw(self.img)

    def px(self, x, y, c):
        self.d.point((int(x * self.w), int(y * self.h)), fill=c)

    def rect(self, x0, y0, x1, y1, c):
        self.d.rectangle([x0 * self.w, y0 * self.h, x1 * self.w, y1 * self.h],
                         fill=c)

    def rect_px(self, x0, y0, x1, y1, c):
        self.d.rectangle([x0, y0, x1, y1], fill=c)

    def ellipse(self, x0, y0, x1, y1, c, outline=None, ow=1):
        self.d.ellipse([x0 * self.w, y0 * self.h, x1 * self.w, y1 * self.h],
                       fill=c, outline=outline, width=max(1, int(ow)))

    def circle(self, cx, cy, r, c, outline=None, ow=1):
        ry = r * self.w / self.h
        self.ellipse(cx - r, cy - ry, cx + r, cy + ry, c, outline, ow)

    def line(self, x0, y0, x1, y1, c, wpx=1):
        self.d.line([x0 * self.w, y0 * self.h, x1 * self.w, y1 * self.h],
                    fill=c, width=wpx)

    def poly(self, pts, c):
        self.d.polygon([(x * self.w, y * self.h) for x, y in pts], fill=c)

    def arc(self, x0, y0, x1, y1, a0, a1, c, wpx=2):
        self.d.arc([x0 * self.w, y0 * self.h, x1 * self.w, y1 * self.h],
                   a0, a1, fill=c, width=wpx)

    def dither(self, x0, y0, x1, y1, c, phase=0):
        xa, ya = int(x0 * self.w), int(y0 * self.h)
        xb, yb = int(x1 * self.w), int(y1 * self.h)
        for yy in range(ya, yb):
            for xx in range(xa + ((yy + phase) % 2), xb, 2):
                self.d.point((xx, yy), fill=c)

    def text_vt(self, x, y, text, size, c):
        fnt = ImageFont.truetype(FVT, size)
        self.d.text((int(x * self.w), int(y * self.h)), text, font=fnt, fill=c)

    def upscale(self, w, h):
        return self.img.resize((w, h), Image.NEAREST)


# ---------------------------------------------------------------- nen + vat the
def draw_background(p, stars, tm=0.0, ground=True):
    """Nen troi sao + dat. Sao nhap nhay theo thoi gian tm (giay)."""
    pal = p.pal
    bands = [(0.0, 0.30, pal["sky_top"]), (0.30, 0.58, pal["sky"]),
             (0.58, 0.85, pal["sky_low"])]
    for y0, y1, c in bands:
        p.rect(0, y0, 1, y1, c)
    p.dither(0, 0.285, 1, 0.315, pal["sky"])
    p.dither(0, 0.565, 1, 0.595, pal["sky_low"])
    if ground:
        p.rect(0, 0.85, 1, 1, pal["ground"])
        p.rect(0, 0.85, 1, 0.862, pal["ground_hi"])
        p.dither(0, 0.862, 1, 0.885, pal["ground_hi"])
    for (x, y, b, ph) in stars:
        v = b * (0.68 + 0.32 * math.sin(tm * 2.1 + ph))
        c = pal["star"] if v > 0.42 else pal["star_dim"]
        s = 2 if v > 0.80 else 1
        gx, gy = int(x * p.w), int(y * p.h)
        p.rect_px(gx, gy, gx + s - 1, gy + s - 1, c)


def draw_orb(p, cx, cy, rw, rh, with_dot=True):
    pal = p.pal
    p.ellipse(cx - rw, cy - rh, cx + rw, cy + rh, pal["sphere"],
              outline=pal["sph_out"], ow=2)
    p.arc(cx - rw, cy - rh, cx + rw, cy + rh, 35, 145, pal["sph_out_d"], wpx=2)
    if with_dot:
        p.ellipse(cx - rw * 0.60, cy - rh * 0.52,
                  cx - rw * 0.22, cy - rh * 0.14, pal["sph_dot"])


def cube(p, x, y, w, h, c, cd, cl):
    """Khoi hop pixel: mat phang + dai sang tren + dai toi ben phai."""
    p.rect(x, y, x + w, y + h, c)
    p.rect(x, y, x + w, y + h * 0.30, cl)
    p.rect(x + w * 0.80, y, x + w, y + h, cd)


def gear(p, cx, cy, r, teeth, color, phase=0.0):
    """Banh rang pixel, xoay theo 'phase' (radian)."""
    pal = p.pal
    pts = []
    w = 2 * math.pi / teeth
    asp = p.w / p.h
    for i in range(teeth):
        a = phase + i * w
        for da, rr in [(-0.42 * w, r * 0.78), (-0.16 * w, r),
                       (0.16 * w, r), (0.42 * w, r * 0.78)]:
            pts.append((cx + rr * math.cos(a + da),
                        cy + rr * math.sin(a + da) * asp))
    p.poly(pts, color)
    p.circle(cx, cy, r * 0.46, color)
    p.circle(cx, cy, r * 0.24, pal["ground"])
    p.circle(cx, cy, r * 0.10, pal["cream"])
