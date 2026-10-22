#!/usr/bin/env python3
"""
MOCKUP TOOL "PIXEL STUDIO" — tool video ve bang code, phong cach khoa cung
PIXEL 16-BIT. Day la du an RIENG cho kenh moi, KHONG tich hop tool videos cu.
Trang thai: CHI LA MOCKUP de duyet — chua phai tool that.

Chuan phong cach 16-bit (da khoa):
- Ve moi canh tren luoi 320x180, phong len bang Image.NEAREST
  -> o pixel vuong 3x3, sac net, khong mo.
- Do bong 2-3 tong cho tung vat + dithering cham xen ke (ban co) o ria
  chuyen mau nen troi, kieu game SNES.
- Bang mau co dinh (PAL ben duoi) — moi video tu tool nay deu cung 1 chat.
- Chu trong video: font pixel VT323 / PressStart2P.

Ky thuat ke thua tu ~/workspace/pixel-studio-sample/build_pixel_samples.py
(luoi 320x180, Painter theo toa do chuan hoa, draw_orb, nen sao + dithering)
va bo cuc 8 mau canh tu ~/workspace/kurzgesagt-tool-mockup/.

Chay: python3 build_pixel_tool_mockup.py
San pham: scene-01.png ... scene-08.png (960x540, co thanh nhan),
          tool-mockup-pixel.png (2000x1280, mockup tool 3 cot).
100% PIL, khong AI sinh anh, khong icon emoji.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

DIR = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.expanduser("~/workspace/fonts")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FPIX = os.path.join(FONTS, "PressStart2P.ttf")   # chi dung cho chu ASCII
FVT = os.path.join(FONTS, "VT323.ttf")           # pixel + co tieng Viet

GW, GH = 320, 180          # luoi ve 16-bit
OUT_W, OUT_H = 960, 540    # anh canh xuat ra (gom ca thanh nhan 46px)

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
    # mau bo sung cho cac mau canh 02-07 (van theo cap sang/toi)
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
}


def stars_for(seed, n=95):
    rng = random.Random(seed)
    return [(rng.uniform(0.01, 0.99), rng.uniform(0.01, 0.82), rng.random())
            for _ in range(n)]


# ---------------------------------------------------------------- lop ve luoi
class Painter:
    """Ve bang toa do chuan hoa (0..1) len luoi 320x180, phong NEAREST."""

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
        """Chu pixel VT323 ve thang len luoi (phong NEAREST se giu chat pixel)."""
        fnt = ImageFont.truetype(FVT, size)
        self.d.text((int(x * self.w), int(y * self.h)), text, font=fnt, fill=c)

    def upscale(self):
        return self.img.resize((OUT_W, OUT_H), Image.NEAREST)


# ---------------------------------------------------------------- nen + qua cau
def draw_background(p, stars, ground=True):
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
    for x, y, b in stars:
        c = pal["star"] if b > 0.45 else pal["star_dim"]
        s = 2 if b > 0.82 else 1
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


def lite(c, f=0.30):
    return tuple(int(v + (255 - v) * f) for v in c)


def dark(c, f=0.72):
    return tuple(int(v * f) for v in c)


# ---------------------------------------------------------------- thanh nhan
def add_label(img, num, title, sub):
    d = ImageDraw.Draw(img)
    d.rectangle([0, OUT_H - 46, OUT_W, OUT_H], fill=(8, 7, 22))
    d.line([0, OUT_H - 46, OUT_W, OUT_H - 46], fill=PAL["sph_out_d"], width=2)
    f1 = ImageFont.truetype(FB, 21)
    f2 = ImageFont.truetype(FR, 19)
    d.text((18, OUT_H - 35), "%s · %s" % (num, title), font=f1,
           fill=(240, 240, 250))
    w2 = d.textlength(sub, font=f2)
    d.text((OUT_W - 18 - w2, OUT_H - 34), sub, font=f2, fill=(165, 165, 195))
    return img


# ================================================================= CANH 01
def scene01():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(101))
    aw = 3
    p.arc(0.115, 0.03, 0.545, 0.37, 180, 338, pal["orange"], wpx=aw)
    p.poly([(0.566, 0.190), (0.498, 0.106), (0.512, 0.182)], pal["orange"])
    p.ellipse(0.115, 0.845, 0.575, 0.890, pal["shadow"])

    def building(x0, y0, x1, y1, c, win_rows=4):
        p.rect(x0, y0, x1, y1, c)
        p.rect((x0 + x1) / 2, y0, x1, y1, pal["bldg_d"])
        bx0, bx1 = int(x0 * p.w), int(x1 * p.w)
        by0, by1 = int(y0 * p.h), int(y1 * p.h)
        wx = bx0 + (bx1 - bx0 - 3) // 2
        for i in range(win_rows):
            wy = by0 + int((by1 - by0) * (0.13 + 0.235 * i))
            wc = pal["window_d"] if i % 3 == 2 else pal["window"]
            p.rect_px(wx, wy, wx + 2, wy + 2, wc)

    building(0.700, 0.665, 0.758, 0.85, pal["bldg2"], 2)
    building(0.775, 0.545, 0.837, 0.85, pal["bldg"], 4)
    building(0.845, 0.665, 0.917, 0.85, pal["bldg2"], 2)
    building(0.925, 0.585, 0.977, 0.85, pal["bldg"], 4)
    draw_orb(p, 0.685, 0.740, 0.068, 0.105)
    draw_orb(p, 0.880, 0.775, 0.043, 0.070)
    draw_orb(p, 0.345, 0.540, 0.225, 0.300)
    return add_label(p.upscale(), "01", "QUẢ CẦU NUỐT CẢNH",
                     "tăng trưởng · nguy cơ phình to")


# ================================================================= CANH 02
def scene02():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(102))
    cx = 0.5
    # cot + de tam giac + truc
    p.rect(0.489, 0.30, 0.511, 0.80, pal["violet_d"])
    p.rect(0.489, 0.30, 0.500, 0.80, pal["violet"])
    p.poly([(cx, 0.76), (0.415, 0.885), (0.585, 0.885)], pal["violet"])
    p.poly([(cx, 0.76), (0.415, 0.885), (cx, 0.885)], pal["violet_d"])
    # thanh can nghieng: trai thap (nang), phai cao (nhe)
    lx, ly, rx, ry = 0.135, 0.315, 0.865, 0.205
    p.line(lx, ly, rx, ry, pal["cream"], wpx=3)
    # dia trai + khoi cam nang
    p.line(lx, ly, lx, 0.415, pal["cream"], wpx=1)
    p.line(lx - 0.045, 0.415, lx, 0.415, pal["cream"], wpx=1)
    p.poly([(lx - 0.088, 0.415), (lx + 0.088, 0.415),
            (lx + 0.052, 0.465), (lx - 0.052, 0.465)], pal["skyblue"])
    p.rect(lx - 0.088, 0.408, lx + 0.088, 0.418, pal["skyblue_d"])
    cube(p, lx - 0.062, 0.330, 0.058, 0.082, pal["orange"], pal["orange_d"],
         lite(pal["orange"]))
    cube(p, lx + 0.002, 0.330, 0.058, 0.082, pal["orange_d"],
         dark(pal["orange_d"]), pal["orange"])
    cube(p, lx - 0.031, 0.248, 0.058, 0.082, pal["window"], pal["window_d"],
         lite(pal["window"]))
    p.text_vt(lx - 0.075, 0.115, "A", 34, pal["cream"])
    # dia phai + qua cau cyan phat sang
    p.line(rx, ry, rx, 0.305, pal["cream"], wpx=1)
    p.poly([(rx - 0.088, 0.305), (rx + 0.088, 0.305),
            (rx + 0.052, 0.355), (rx - 0.052, 0.355)], pal["skyblue"])
    p.rect(rx - 0.088, 0.298, rx + 0.088, 0.308, pal["skyblue_d"])
    p.circle(rx, 0.262, 0.052, pal["halo_teal"])
    p.circle(rx, 0.262, 0.036, pal["cyan"])
    p.circle(rx - 0.012, 0.250, 0.011, (225, 252, 255))
    p.text_vt(rx - 0.018, 0.075, "B", 34, pal["cream"])
    p.circle(cx, 0.26, 0.017, pal["orange"])
    return add_label(p.upscale(), "02", "CÂN SO SÁNH A vs B",
                     "so sánh · bên nào nặng hơn")


# ================================================================= CANH 03
def scene03():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(103), ground=False)
    cx, cy = 0.5, 0.47
    sats = [(0.156, 0.204, pal["violet"]), (0.344, 0.122, pal["skyblue"]),
            (0.667, 0.111, pal["mint"]), (0.856, 0.219, pal["orange"]),
            (0.898, 0.556, pal["red"]), (0.729, 0.778, pal["violet"]),
            (0.260, 0.793, pal["pink"]), (0.112, 0.559, pal["skyblue"])]
    for (x, y, c) in sats:
        p.line(cx, cy, x, y, pal["edge_dim"], wpx=1)
    p.line(0.156, 0.204, 0.344, 0.122, pal["edge_dim"], wpx=1)
    p.line(0.856, 0.219, 0.898, 0.556, pal["edge_dim"], wpx=1)
    for i in (0, 3, 5, 6):  # duong dang sang + xung chay
        x, y, c = sats[i]
        p.line(cx, cy, x, y, pal["green_d"], wpx=1)
        mx, my = cx + (x - cx) * 0.55, cy + (y - cy) * 0.55
        gx, gy = int(mx * p.w), int(my * p.h)
        p.rect_px(gx - 2, gy - 2, gx + 2, gy + 2, pal["green"])
        p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, (225, 255, 245))
    for (x, y, c) in sats:
        p.circle(x, y, 0.021, c)
        p.circle(x, y, 0.008, (240, 245, 255))
    p.circle(cx, cy, 0.058, pal["halo_teal"])
    p.circle(cx, cy, 0.037, pal["cyan"])
    p.circle(cx, cy, 0.015, (235, 252, 255))
    return add_label(p.upscale(), "03", "MẠNG LƯỚI NODE",
                     "hệ thống · kết nối · lan truyền")


# ================================================================= CANH 04
def scene04():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(104), ground=False)
    y = 0.55
    p.line(0.07, y, 0.93, y, pal["axis"], wpx=2)
    p.poly([(0.945, y), (0.918, y - 0.024), (0.918, y + 0.024)], pal["star"])
    xs = [0.115, 0.307, 0.5, 0.692, 0.885]
    rs = [0.013, 0.017, 0.021, 0.027, 0.033]
    cols = [pal["skyblue"], pal["mint"], pal["cyan"], pal["orange"], pal["red"]]
    for i, (x, r, c) in enumerate(zip(xs, rs, cols)):
        up = (i % 2 == 0)
        sy = y - 0.215 if up else y + 0.215
        p.line(x, y, x, sy, pal["axis"], wpx=1)
        if i == 0:      # vong tron + cham giua
            p.ellipse(x - 0.024, sy - 0.024 * p.w / p.h, x + 0.024,
                      sy + 0.024 * p.w / p.h, None, outline=c, ow=2)
            p.circle(x, sy, 0.007, c)
        elif i == 1:    # the chu nhat
            p.rect(x - 0.030, sy - 0.034, x + 0.030, sy + 0.034, c)
            p.rect(x - 0.030, sy - 0.034, x + 0.030, sy - 0.012,
                   lite(c))
        elif i == 2:    # tam giac
            p.poly([(x, sy - 0.045), (x + 0.026, sy + 0.032),
                    (x - 0.026, sy + 0.032)], c)
            p.poly([(x, sy - 0.045), (x + 0.026, sy + 0.032), (x, sy + 0.032)],
                   dark(c))
        elif i == 3:    # vuong + cham giua
            p.rect(x - 0.026, sy - 0.046, x + 0.026, sy + 0.046, c)
            p.rect(x - 0.026, sy - 0.046, x + 0.026, sy - 0.016, lite(c))
            p.circle(x, sy, 0.008, pal["sky"])
        else:           # ngoi sao (moc cuoi, to nhat)
            p.circle(x, sy, 0.052, pal["halo_red"])
            pts = []
            for k in range(10):
                ang = -math.pi / 2 + k * math.pi / 5
                rr = 0.036 if k % 2 == 0 else 0.016
                pts.append((x + rr * math.cos(ang),
                            sy + rr * math.sin(ang) * p.w / p.h))
            p.poly(pts, c)
        p.circle(x, y, r, c)
        p.circle(x, y, r * 0.38, (245, 248, 255))
        p.text_vt(x - 0.012, y + 0.045, str(i + 1), 22, pal["star_dim"])
    return add_label(p.upscale(), "04", "DÒNG THỜI GIAN",
                     "lịch sử · tiến trình · các mốc")


# ================================================================= CANH 05
def scene05():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(105))
    p.ellipse(0.19, 0.845, 0.77, 0.885, pal["shadow"])
    W_, H_ = 0.115, 0.105
    cube(p, 0.315, 0.755, W_, H_, pal["orange"], pal["orange_d"], lite(pal["orange"]))
    cube(p, 0.440, 0.755, W_, H_, pal["violet"], pal["violet_d"], lite(pal["violet"]))
    cube(p, 0.565, 0.755, W_, H_, (38, 150, 190), (26, 104, 134), (86, 182, 214))
    cube(p, 0.377, 0.650, W_, H_, pal["mint"], pal["green_d"], lite(pal["mint"]))
    cube(p, 0.502, 0.650, W_, H_, pal["orange_d"], dark(pal["orange_d"]), pal["orange"])
    cube(p, 0.440, 0.545, W_, H_, pal["pink"], pal["pink_d"], lite(pal["pink"]))
    # 2 khoi dang roi + vet chuyen dong
    for (x, y, w2, c, cd) in [(0.470, 0.205, 0.100, pal["skyblue"], pal["skyblue_d"]),
                              (0.625, 0.105, 0.085, pal["orange"], pal["orange_d"])]:
        for k in range(3):
            lx = x + 0.018 + k * 0.026
            p.line(lx, y - 0.085, lx, y - 0.028, pal["star_dim"], wpx=1)
        cube(p, x, y, w2, 0.095, c, cd, lite(c))
    return add_label(p.upscale(), "05", "RƠI & XẾP CHỒNG",
                     "tích lũy · số lượng tăng dần")


# ================================================================= CANH 06
def scene06():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(106))
    p0, p1, p2, p3 = ((0.115, 0.778), (0.448, 0.926),
                      (0.583, 0.389), (0.854, 0.241))

    def bez(t):
        x = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0]
             + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0])
        y = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1]
             + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1])
        return x, y

    pts = [bez(t / 90.0) for t in range(91)]
    for i in range(0, 91, 3):  # duong dut net = cac o pixel nho
        x, y = pts[i]
        gx, gy = int(x * p.w), int(y * p.h)
        p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, pal["star"])
    for t, c in [(0.0, pal["green"]), (0.34, pal["skyblue"]),
                 (0.62, pal["orange"]), (0.83, pal["violet"])]:
        x, y = bez(t)
        p.circle(x, y, 0.017, c)
        p.circle(x, y, 0.006, (245, 248, 255))
    # co o chang giua (t = 0.62)
    fx, fy = bez(0.62)
    p.line(fx, fy - 0.010, fx, fy - 0.115, pal["cream"], wpx=1)
    p.poly([(fx, fy - 0.115), (fx + 0.038, fy - 0.092), (fx, fy - 0.068)],
           pal["orange"])
    # ghim dich den
    x, y = bez(1.0)
    p.circle(x, y - 0.038, 0.048, pal["halo_red"])
    p.circle(x, y - 0.038, 0.027, pal["red"])
    p.poly([(x - 0.016, y - 0.026), (x + 0.016, y - 0.026), (x, y + 0.012)],
           pal["red"])
    p.circle(x, y - 0.038, 0.010, (255, 235, 238))
    p.text_vt(0.030, 0.600, "START", 19, pal["star_dim"])
    p.text_vt(0.845, 0.075, "END", 20, pal["red"])
    return add_label(p.upscale(), "06", "BẢN ĐỒ HÀNH TRÌNH",
                     "quá trình · từng bước một")


# ================================================================= CANH 07
def gear(p, cx, cy, r, teeth, color, cd, phase=0.0):
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
    p.circle(cx, cy, r * 0.24, pal_hole(p))
    p.circle(cx, cy, r * 0.10, p.pal["cream"])


def pal_hole(p):
    return p.pal["ground"]


def scene07():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(107))
    gear(p, 0.330, 0.340, 0.105, 9, pal["violet"], pal["violet_d"], 0.1)
    gear(p, 0.495, 0.470, 0.072, 8, pal["skyblue"], pal["skyblue_d"], 0.35)
    gear(p, 0.240, 0.575, 0.058, 8, pal["orange"], pal["orange_d"], 0.2)
    for (x, y, r) in [(0.330, 0.085, 0.014), (0.360, 0.055, 0.009),
                      (0.500, 0.225, 0.010)]:
        p.circle(x, y, r, pal["star_dim"])
    # bang chuyen
    p.rect(0.470, 0.690, 0.940, 0.752, (40, 36, 84))
    p.rect(0.470, 0.690, 0.940, 0.700, pal["axis"])
    p.rect(0.470, 0.742, 0.940, 0.752, pal["sph_out_d"])
    x = 0.492
    while x < 0.925:
        p.circle(x, 0.721, 0.011, pal["axis"])
        x += 0.056
    cube(p, 0.575, 0.585, 0.075, 0.105, pal["mint"], pal["green_d"], lite(pal["mint"]))
    cube(p, 0.715, 0.585, 0.075, 0.105, pal["pink"], pal["pink_d"], lite(pal["pink"]))
    cube(p, 0.845, 0.585, 0.075, 0.105, pal["green"], pal["green_d"], lite(pal["green"]))
    return add_label(p.upscale(), "07", "CỖ MÁY VẬN HÀNH",
                     "cơ chế · bên trong nó chạy thế nào")


# ================================================================= CANH 08
def scene08():
    p = Painter()
    pal = p.pal
    draw_background(p, stars_for(108, 80))
    p.rect(0, 0.845, 1, 0.856, pal["ground_hi"])
    p.rect(0, 0.845, 1, 1, pal["ground"])
    # cua so ben phai
    p.rect(0.695, 0.115, 0.945, 0.585, pal["win_fr"])
    p.rect(0.703, 0.139, 0.937, 0.561, pal["win_in"])
    p.circle(0.862, 0.265, 0.052, pal["moon"])
    p.circle(0.880, 0.248, 0.046, pal["win_in"])
    for sx, sy in [(0.735, 0.20), (0.745, 0.44), (0.905, 0.47)]:
        cx, cy = int(sx * p.w), int(sy * p.h)
        p.rect_px(cx - 2, cy, cx + 2, cy, pal["star"])
        p.rect_px(cx, cy - 2, cx, cy + 2, pal["star"])
    # bong bong suy nghi + qua cau nho
    p.circle(0.312, 0.378, 0.013, pal["bubble"])
    p.circle(0.352, 0.332, 0.019, pal["bubble"])
    bx0, by0, bx1, by1 = 0.405, 0.120, 0.665, 0.345
    p.rect(bx0, by0, bx1, by1, pal["bubble"])
    p.rect(bx0, by1 - 4 / p.h, bx1, by1, pal["bubble_d"])
    draw_orb(p, 0.556, 0.232, 0.066, 0.090)
    # ghe + nhan vat (chi la phan tu trong canh)
    p.rect(0.098, 0.560, 0.138, 0.865, pal["chair"])
    p.rect(0.145, 0.745, 0.237, 0.885, pal["pants"])
    p.rect(0.122, 0.512, 0.248, 0.752, pal["shirt"])
    p.rect(0.122, 0.690, 0.248, 0.752, pal["shirt_d"])
    p.rect(0.228, 0.512, 0.248, 0.752, pal["shirt_d"])
    p.circle(0.185, 0.402, 0.058, pal["skin"])
    p.arc(0.127, 0.315, 0.243, 0.49, 20, 160, pal["skin_d"], wpx=2)
    hx0, hy0 = 0.185 - 0.058, 0.402 - 0.058 * p.w / p.h
    hx1, hy1 = 0.185 + 0.058, 0.402 + 0.058 * p.w / p.h
    p.d.pieslice([hx0 * p.w, hy0 * p.h, hx1 * p.w, hy1 * p.h],
                 180, 360, fill=pal["hair"])
    for ex in (0.166, 0.204):
        gx, gy = int(ex * p.w), int(0.408 * p.h)
        p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, pal["black"])
    p.arc(0.168, 0.415, 0.202, 0.455, 15, 165, pal["black"], wpx=2)
    p.poly([(0.198, 0.578), (0.415, 0.650), (0.418, 0.686), (0.205, 0.616)],
           pal["skin"])
    p.line(0.205, 0.616, 0.418, 0.686, pal["skin_d"], wpx=1)
    # ban + laptop + den ban
    p.rect(0.128, 0.735, 0.648, 0.768, pal["desk"])
    p.rect(0.128, 0.752, 0.648, 0.768, pal["desk_d"])
    p.rect(0.152, 0.768, 0.178, 0.895, pal["desk_d"])
    p.rect(0.598, 0.768, 0.624, 0.895, pal["desk_d"])
    p.rect(0.435, 0.545, 0.577, 0.738, pal["lap_fr"])
    p.rect(0.447, 0.557, 0.565, 0.726, pal["lap_in"])
    p.line(0.462, 0.665, 0.545, 0.600, pal["lap_ln1"], wpx=2)
    p.line(0.462, 0.695, 0.520, 0.648, pal["lap_ln2"], wpx=2)
    p.rect(0.420, 0.738, 0.592, 0.756, pal["lap_fr"])
    p.line(0.636, 0.738, 0.617, 0.520, pal["lamp_pole"], wpx=2)
    p.poly([(0.584, 0.438), (0.652, 0.438), (0.636, 0.548), (0.600, 0.548)],
           pal["lamp"])
    p.circle(0.618, 0.500, 0.016, pal["lamp_hi"])
    for gx, gy in [(0.600, 0.475), (0.636, 0.475), (0.618, 0.545),
                   (0.594, 0.520), (0.642, 0.520)]:
        p.px(gx, gy, pal["lamp_hi"])
    return add_label(p.upscale(), "08", "NGƯỜI TRONG CẢNH",
                     "con người · bị công nghệ tác động")


SCENES = [scene01, scene02, scene03, scene04, scene05, scene06, scene07,
          scene08]


# ================================================================= MOCKUP TOOL
MW, MH = 2000, 1280
MBG = (10, 9, 26)
MPANEL = (24, 22, 46)
MCARD = (34, 31, 62)
MTXT = (238, 238, 248)
MSUB = (168, 168, 200)
MACC = (64, 200, 220)
MGRN = (70, 200, 120)
MYEL = (255, 218, 92)
MBORD = (88, 76, 168)


def make_mockup():
    img = Image.new("RGB", (MW, MH), MBG)
    d = ImageDraw.Draw(img)

    def f(sz, bold=False):
        return ImageFont.truetype(FB if bold else FR, sz)

    def fpix(sz):
        return ImageFont.truetype(FPIX, sz)

    def fvt(sz):
        return ImageFont.truetype(FVT, sz)

    def wrap(text, font, maxw):
        words, lines, cur = text.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if d.textlength(t, font=font) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def panel(x, y, w, h, title):
        d.rectangle([x, y, x + w, y + h], fill=MPANEL, outline=MBORD, width=3)
        for (cx_, cy_) in [(x, y), (x + w - 10, y), (x, y + h - 10),
                           (x + w - 10, y + h - 10)]:
            d.rectangle([cx_, cy_, cx_ + 10, cy_ + 10], fill=MACC)
        d.text((x + 24, y + 14), title, font=fvt(37), fill=MACC)

    def tri(x, y, s=11, c=MSUB):
        d.polygon([(x, y), (x + s, y), (x + s // 2, y + s - 2)], fill=c)

    def dropdown(x, y, w, h, text, font_sz=21):
        d.rectangle([x, y, x + w, y + h], fill=MCARD, outline=MSUB, width=2)
        d.text((x + 14, y + (h - font_sz) // 2 - 2), text, font=f(font_sz),
               fill=MTXT)
        tri(x + w - 30, y + h // 2 - 4)

    def thumb(name, w, h):
        s = Image.open(os.path.join(DIR, name)).convert("RGB")
        return s.resize((w, h))

    # ---- logo pixel nho: qua cau ve tren luoi 48x48, phong NEAREST
    lp = Painter()
    lp.img = Image.new("RGB", (48, 48), MPANEL)
    lp.d = ImageDraw.Draw(lp.img)
    lp.w, lp.h = 48, 48
    draw_orb(lp, 0.5, 0.56, 0.33, 0.33)
    lp.arc(0.14, 0.02, 0.86, 0.62, 180, 330, PAL["orange"], wpx=3)
    img.paste(lp.img.resize((72, 72), Image.NEAREST), (40, 22))

    # ---- header
    d.text((128, 30), "PIXEL STUDIO", font=fpix(33), fill=MTXT)
    tw = d.textlength("PIXEL STUDIO", font=fpix(33))
    d.text((128 + tw + 22, 22), "— MOCKUP (chưa phải tool thật)",
           font=fvt(46), fill=MYEL)
    d.text((44, 104),
           "Dán kịch bản → mỗi câu chọn 1 mẫu cảnh pixel vẽ bằng code → "
           "giọng cố định → Render. Không cần biết code.",
           font=f(23), fill=MSUB)
    # bang khoa phong cach (2 dong bat buoc ghi ro)
    d.rectangle([40, 142, 1960, 206], fill=(30, 26, 56), outline=MBORD,
                width=2)
    d.text((60, 152),
           "PHONG CÁCH ĐÃ KHÓA: PIXEL 16-BIT — lưới 320×180, phóng NEAREST, "
           "đổ bóng 2–3 tông + dithering. Mọi video từ tool này đều cùng "
           "1 chất pixel.",
           font=f(21, True), fill=MYEL)
    d.text((60, 179),
           "DỰ ÁN RIÊNG CHO KÊNH MỚI — tách biệt hẳn tool videos hiện tại, "
           "không dùng chung code.",
           font=f(21, True), fill=MACC)

    PY, PH = 222, 1024

    # ---------------------------------------------------------- cot trai
    panel(40, PY, 588, PH, "1 · KỊCH BẢN (dán chữ vào)")
    script_lines = [
        "You've seen the terms. LLM. RAG.",
        "AI Agent. MCP. System Prompt.",
        "Sounds like a PhD thesis.",
        "Sounds complicated. Sounds like",
        "they're trying to confuse you.",
        "They're not. They're just",
        "describing... you.",
        "Every single AI concept is copied",
        "from your own body.",
        "Let me prove it.",
    ]
    d.rectangle([64, PY + 58, 604, PY + 424], fill=MCARD, outline=MBORD,
                width=2)
    y = PY + 78
    for ln in script_lines:
        d.text((86, y), ln, font=f(23), fill=MTXT)
        y += 35
    d.line([64, PY + 444, 604, PY + 444], fill=MSUB, width=2)
    notes_l = [
        "Tool tự cắt kịch bản theo từng câu.",
        "Mỗi câu = 1 cảnh. Câu nào chưa chọn",
        "cảnh, tool sẽ nhắc trước khi Render.",
        "",
        "Kịch bản mẫu trong hình: mở đầu",
        "Long #5 (LLM, RAG, Agent, MCP).",
        "",
        "Chữ trong video: font pixel VT323 /",
        "PressStart2P (đúng chất 16-bit).",
    ]
    y = PY + 462
    for ln in notes_l:
        d.text((64, y), ln, font=f(22), fill=MSUB)
        y += 31
    for i, t in enumerate(["6 câu thoại", "4 / 6 đã gán cảnh"]):
        x = 64 + i * 268
        d.rectangle([x, PY + 782, x + 252, PY + 834], outline=MACC, width=2)
        tw2 = d.textlength(t, font=f(21, True))
        d.text((x + (252 - tw2) / 2, PY + 796), t, font=f(21, True),
               fill=MACC)
    d.text((64, PY + 866), "Thư viện mẫu cảnh hiện có: 8 mẫu.",
           font=f(22, True), fill=MTXT)
    lib = ["Quả cầu nuốt cảnh · Cân so sánh",
           "Mạng lưới node · Dòng thời gian",
           "Rơi & xếp chồng · Bản đồ hành trình",
           "Cỗ máy vận hành · Người trong cảnh"]
    y = PY + 898
    for ln in lib:
        d.text((64, y), ln, font=f(21), fill=MSUB)
        y += 29

    # ---------------------------------------------------------- cot giua
    panel(656, PY, 660, PH, "2 · TỪNG CÂU — CHỌN MẪU CẢNH")
    rows = [
        ("scene-03.png", "You've seen the terms. LLM. RAG. AI Agent. MCP. "
         "System Prompt.", "Mạng lưới node", "0:00 – 0:06"),
        ("scene-08.png", "Sounds like a PhD thesis. Sounds complicated.",
         "Người trong cảnh", "0:06 – 0:11"),
        ("scene-02.png", "They're not. They're just describing... you.",
         "Cân so sánh A vs B", "0:11 – 0:16"),
        ("scene-07.png", "Start with the brain. In AI, that's the LLM.",
         "Cỗ máy vận hành", "0:16 – 0:22"),
    ]
    ry = PY + 62
    for name, sentence, dd, tcode in rows:
        d.rectangle([680, ry, 1292, ry + 226], fill=MCARD, outline=MBORD,
                    width=2)
        img.paste(thumb(name, 250, 141), (700, ry + 12))
        d.text((700, ry + 162), tcode, font=f(19), fill=MSUB)
        d.text((700, ry + 190), "Cảnh vẽ bằng code · pixel 16-bit",
               font=f(16), fill=MSUB)
        sy = ry + 14
        for ln in wrap(sentence, f(21, True), 296):
            d.text((970, sy), ln, font=f(21, True), fill=MTXT)
            sy += 29
        d.text((970, ry + 96), "MẪU CẢNH:", font=f(16, True), fill=MSUB)
        dropdown(970, ry + 118, 302, 46, dd, 20)
        d.text((970, ry + 180), "Hiệu ứng: hiện dần", font=f(19), fill=MSUB)
        tri(1158, ry + 188, 10)
        ry += 240

    # ---------------------------------------------------------- cot phai
    panel(1344, PY, 616, PH, "3 · XEM TRƯỚC + RENDER")
    img.paste(thumb("scene-01.png", 568, 320), (1368, PY + 58))
    d.rectangle([1368, PY + 58, 1936, PY + 378], outline=MBORD, width=3)
    d.rectangle([1368, PY + 326, 1936, PY + 378], fill=(0, 0, 0))
    d.text((1382, PY + 341), "Every AI concept is copied from your own body.",
           font=f(20, True), fill=MYEL)
    yy = PY + 390
    d.text((1368, yy), "Giọng đọc (cố định):", font=fvt(31), fill=MACC)
    dropdown(1368, yy + 32, 568, 48, "am_adam — giọng cố định của kênh", 22)
    yy = PY + 486
    d.text((1368, yy), "Định dạng:", font=fvt(31), fill=MACC)
    dropdown(1368, yy + 32, 276, 48, "Ngang 16:9 (Long)", 21)
    dropdown(1660, yy + 32, 276, 48, "Nhạc nền: Có", 21)
    yy = PY + 584
    d.rectangle([1368, yy, 1936, yy + 84], fill=MGRN)
    t = "RENDER VIDEO"
    tw3 = d.textlength(t, font=fpix(20))
    tx = 1368 + (568 - tw3 - 34) / 2
    d.polygon([(tx, yy + 29), (tx, yy + 55), (tx + 24, yy + 42)],
              fill=(8, 30, 18))
    d.text((tx + 34, yy + 29), t, font=fpix(20), fill=(8, 30, 18))
    yy = PY + 684
    # thanh tien trinh dang o pixel (cac o vuong lien tiep)
    seg, filled = 28, 17
    sw_ = 568 // seg
    for i in range(seg):
        c = MACC if i < filled else MCARD
        d.rectangle([1368 + i * sw_ + 1, yy, 1368 + (i + 1) * sw_ - 1,
                     yy + 14], fill=c)
    d.text((1368, yy + 22), "Đang vẽ cảnh 4/6 bằng code... (minh họa)",
           font=f(20), fill=MSUB)
    yy = PY + 748
    notes_r = [
        "Mẫu cảnh vẽ sẵn bằng code trong thư viện —",
        "bạn chỉ bấm chọn, không gõ một dòng code nào.",
        "",
        "Phong cách pixel 16-bit khóa cứng trong tool:",
        "video nào cũng cùng 1 chất pixel, không lệch tay.",
        "",
        "Không nhân vật chính cố định — nhân vật chỉ",
        "là phần tử trong cảnh, thay đổi theo từng câu.",
        "",
        "Muốn mẫu cảnh mới? Rio nạp thêm, tool tự hiện.",
    ]
    for ln in notes_r:
        d.text((1368, yy), ln, font=f(21), fill=MSUB)
        yy += 27
    return img


# ================================================================= main
def main():
    os.chdir(DIR)
    for i, fn in enumerate(SCENES, 1):
        im = fn()
        name = "scene-%02d.png" % i
        im.save(name)
        print("saved", name, im.size)
    mock = make_mockup()
    mock.save("tool-mockup-pixel.png")
    print("saved tool-mockup-pixel.png", mock.size)


if __name__ == "__main__":
    main()
