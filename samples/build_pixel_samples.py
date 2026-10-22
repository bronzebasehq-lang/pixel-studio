#!/usr/bin/env python3
"""
BANG MAU PIXEL: 8-BIT vs 16-BIT — cung 1 canh ve o 2 phong cach de chon.

Ky thuat:
- Moi canh duoc ve tren luoi THAP (8-bit: 160x90, 16-bit: 320x180),
  roi phong to len 960x540 bang Image.NEAREST -> pixel vuong sac net.
- 8-bit: bang mau hep kieu NES (~16 mau), mau phang, khong do bong muot.
- 16-bit: bang mau rong hon, do bong 2-3 tong + dithering nhe (cham xen ke)
  kieu game SNES.
- Ca 2 ban cua 1 canh dung CHUNG bo cuc (toa do chuan hoa 0..1) de so sanh
  cong bang.

Du an: tool video ve bang code MOI (kenh moi) — KHONG lien quan tool videos cu.

Chay: python3 build_pixel_samples.py
San pham: scene-a-8bit.png, scene-a-16bit.png, scene-b-8bit.png,
          scene-b-16bit.png, board.png
"""

import random
from PIL import Image, ImageDraw, ImageFont

OUT_W, OUT_H = 960, 540

# ---------------------------------------------------------------- bo cuc dung chung
# Sao: sinh 1 lan bang toa do chuan hoa -> ca 2 phong cach dung chung vi tri.
_rng = random.Random(42)
STARS = [(_rng.uniform(0.01, 0.99), _rng.uniform(0.01, 0.82), _rng.random())
         for _ in range(110)]
STARS_B = [(_rng.uniform(0.01, 0.99), _rng.uniform(0.01, 0.84), _rng.random())
           for _ in range(80)]

# ---------------------------------------------------------------- bang mau
PAL_8 = {  # kieu NES: it mau, phang
    "sky":      (20, 16, 46),
    "ground":   (12, 10, 32),
    "sphere":   (5, 5, 12),
    "sph_out":  (74, 63, 143),
    "sph_dot":  (58, 49, 112),
    "orange":   (242, 164, 19),
    "bldg":     (42, 35, 80),
    "bldg2":    (34, 28, 66),
    "window":   (245, 197, 66),
    "star":     (185, 194, 240),
    "star_dim": (110, 118, 180),
    "shadow":   (3, 3, 8),
    "skin":     (242, 193, 136),
    "hair":     (58, 45, 96),
    "shirt":    (29, 157, 180),
    "pants":    (30, 26, 54),
    "desk":     (90, 67, 144),
    "chair":    (44, 36, 84),
    "bubble":   (244, 244, 250),
    "win_in":   (27, 23, 64),
    "win_fr":   (58, 54, 112),
    "moon":     (245, 230, 184),
    "lamp":     (245, 158, 11),
    "lamp_pole": (230, 220, 200),
    "lap_fr":   (22, 22, 40),
    "lap_ln1":  (56, 200, 220),
    "lap_ln2":  (80, 220, 140),
    "black":    (0, 0, 0),
}

PAL_16 = {  # rong hon: moi mau chinh co them tong sang/toi
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
    "hair_d":   (46, 36, 78),
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
    "moon_d":   (226, 205, 150),
    "lamp":     (248, 166, 20),
    "lamp_hi":  (255, 214, 110),
    "lamp_pole": (236, 228, 208),
    "lap_fr":   (26, 26, 46),
    "lap_in":   (14, 16, 34),
    "lap_ln1":  (72, 210, 230),
    "lap_ln2":  (96, 228, 152),
    "black":    (0, 0, 0),
}


# ---------------------------------------------------------------- lop ve
class Painter:
    """Ve bang toa do chuan hoa (0..1) len luoi pixel thap."""

    def __init__(self, w, h, pal, style):
        self.w, self.h = w, h
        self.pal = pal
        self.style = style  # "8" hoac "16"
        self.img = Image.new("RGB", (w, h), pal.get("sky", (0, 0, 0)))
        self.d = ImageDraw.Draw(self.img)

    def px(self, x, y, c):
        self.d.point((int(x * self.w), int(y * self.h)), fill=c)

    def rect(self, x0, y0, x1, y1, c):
        self.d.rectangle([x0 * self.w, y0 * self.h, x1 * self.w, y1 * self.h],
                         fill=c)

    def rect_px(self, x0, y0, x1, y1, c):
        """Hinh chu nhat theo toa do pixel luoi (de ve cua so, chi tiet nho)."""
        self.d.rectangle([x0, y0, x1, y1], fill=c)

    def ellipse(self, x0, y0, x1, y1, c, outline=None, ow=1):
        self.d.ellipse([x0 * self.w, y0 * self.h, x1 * self.w, y1 * self.h],
                       fill=c, outline=outline, width=max(1, int(ow)))

    def circle(self, cx, cy, r, c, outline=None, ow=1):
        """r tinh theo chieu rong."""
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
        """Cham xen ke kieu ban co (checkerboard) — chi dung cho 16-bit."""
        xa, ya = int(x0 * self.w), int(y0 * self.h)
        xb, yb = int(x1 * self.w), int(y1 * self.h)
        for yy in range(ya, yb):
            for xx in range(xa + ((yy + phase) % 2), xb, 2):
                self.d.point((xx, yy), fill=c)

    def upscale(self):
        return self.img.resize((OUT_W, OUT_H), Image.NEAREST)


# ---------------------------------------------------------------- nen chung
def draw_background(p, stars):
    pal = p.pal
    if p.style == "8":
        p.rect(0, 0, 1, 1, pal["sky"])
        p.rect(0, 0.85, 1, 1, pal["ground"])
        p.line(0, 0.85, 1, 0.85, pal["ground"], 1)
    else:
        # troi chuyen 4 dai mau + dithering o ria chuyen
        bands = [(0.0, 0.30, pal["sky_top"]), (0.30, 0.58, pal["sky"]),
                 (0.58, 0.85, pal["sky_low"])]
        for y0, y1, c in bands:
            p.rect(0, y0, 1, y1, c)
        p.dither(0, 0.285, 1, 0.315, pal["sky"])
        p.dither(0, 0.565, 1, 0.595, pal["sky_low"])
        p.rect(0, 0.85, 1, 1, pal["ground"])
        p.rect(0, 0.85, 1, 0.862, pal["ground_hi"])
        p.dither(0, 0.862, 1, 0.885, pal["ground_hi"])
    # sao
    for x, y, b in stars:
        c = pal["star"] if b > 0.45 else pal["star_dim"]
        if p.style == "8":
            p.d.point((int(x * p.w), int(y * p.h)), fill=c)
            if b > 0.9:  # vai sao to 2px
                p.d.point((int(x * p.w) + 1, int(y * p.h)), fill=c)
        else:
            s = 2 if b > 0.82 else 1
            p.rect_px(int(x * p.w), int(y * p.h),
                      int(x * p.w) + s - 1, int(y * p.h) + s - 1, c)


def draw_orb(p, cx, cy, rw, rh, with_dot=True):
    """Qua cau den vien tim — ve bang ellipse (ban kinh ngang/doc rieng)
    de khop ti le anh tham chieu. Phan tu chu dao cua ca 2 canh."""
    pal = p.pal
    ow = 1 if p.style == "8" else 2
    p.ellipse(cx - rw, cy - rh, cx + rw, cy + rh, pal["sphere"],
              outline=pal["sph_out"], ow=ow)
    if p.style == "16":
        # ven sang mo o day cau (do bong them 1 tong)
        p.arc(cx - rw, cy - rh, cx + rw, cy + rh, 35, 145,
              pal["sph_out_d"], wpx=ow)
    if with_dot:
        p.ellipse(cx - rw * 0.60, cy - rh * 0.52,
                  cx - rw * 0.22, cy - rh * 0.14, pal["sph_dot"])


# ---------------------------------------------------------------- CANH A
def scene_a(style):
    if style == "8":
        p = Painter(160, 90, PAL_8, "8")
    else:
        p = Painter(320, 180, PAL_16, "16")
    pal = p.pal
    draw_background(p, STARS)

    # mui ten cong cam phia tren (ve truoc, cau de len phan duoi)
    aw = 2 if style == "8" else 3
    p.arc(0.115, 0.03, 0.545, 0.37, 180, 338, pal["orange"], wpx=aw)
    p.poly([(0.566, 0.190), (0.498, 0.106), (0.512, 0.182)], pal["orange"])

    # bong duoi cau lon
    p.ellipse(0.115, 0.845, 0.575, 0.890, pal["shadow"])

    # toa nha ben phai (cua so ve theo pixel luoi cho nho gon)
    win_px = 2 if style == "8" else 3

    def building(x0, y0, x1, y1, c, cd=None, win_rows=4):
        p.rect(x0, y0, x1, y1, c)
        if style == "16" and cd:  # nua phai toi hon (do bong)
            p.rect((x0 + x1) / 2, y0, x1, y1, cd)
        bx0, bx1 = int(x0 * p.w), int(x1 * p.w)
        by0, by1 = int(y0 * p.h), int(y1 * p.h)
        wx = bx0 + (bx1 - bx0 - win_px) // 2
        for i in range(win_rows):
            wy = by0 + int((by1 - by0) * (0.13 + 0.235 * i))
            wc = pal["window"]
            if style == "16" and i % 3 == 2:
                wc = pal["window_d"]  # vai o cua mo hon
            p.rect_px(wx, wy, wx + win_px - 1, wy + win_px - 1, wc)

    bldg_c = pal["bldg"]
    bldg_cd = pal.get("bldg_d") if style == "16" else None
    building(0.700, 0.665, 0.758, 0.85, pal["bldg2"], bldg_cd, 2)
    building(0.775, 0.545, 0.837, 0.85, bldg_c, bldg_cd, 4)
    building(0.845, 0.665, 0.917, 0.85, pal["bldg2"], bldg_cd, 2)
    building(0.925, 0.585, 0.977, 0.85, bldg_c, bldg_cd, 4)

    # cau nho giua + cau rat nho truoc khoi nha
    draw_orb(p, 0.685, 0.740, 0.068, 0.105)
    draw_orb(p, 0.880, 0.775, 0.043, 0.070)

    # cau lon ben trai
    draw_orb(p, 0.345, 0.540, 0.225, 0.300)
    return p.upscale()


# ---------------------------------------------------------------- CANH B
def scene_b(style):
    if style == "8":
        p = Painter(160, 90, PAL_8, "8")
    else:
        p = Painter(320, 180, PAL_16, "16")
    pal = p.pal
    draw_background(p, STARS_B)
    if style == "16":  # san nha co dai sang o ria tren
        p.rect(0, 0.845, 1, 0.856, pal["ground_hi"])
    p.rect(0, 0.845, 1, 1, pal["ground"] if style == "8" else pal["ground"])

    s16 = (style == "16")

    # ---- cua so ben phai
    fw = 2 if style == "8" else 3
    p.rect(0.695, 0.115, 0.945, 0.585, pal["win_fr"])
    p.rect(0.695 + fw / p.w * 1.0, 0.115 + fw / p.h * 1.6,
           0.945 - fw / p.w * 1.0, 0.585 - fw / p.h * 1.6, pal["win_in"])
    # trang khuyet: vong tron sang bi vong tron mau nen de len
    p.circle(0.862, 0.265, 0.052, pal["moon"])
    p.circle(0.880, 0.248, 0.046, pal["win_in"])
    # sao long lanh trong cua so
    for sx, sy in [(0.735, 0.20), (0.745, 0.44), (0.905, 0.47)]:
        c = pal["star"]
        cx, cy = int(sx * p.w), int(sy * p.h)
        r = 2 if s16 else 1
        p.rect_px(cx - r, cy, cx + r, cy, c)
        p.rect_px(cx, cy - r, cx, cy + r, c)

    # ---- bong bong suy nghi + qua cau nho trong bong bong
    p.circle(0.312, 0.378, 0.013, pal["bubble"])
    p.circle(0.352, 0.332, 0.019, pal["bubble"])
    bx0, by0, bx1, by1 = 0.405, 0.120, 0.665, 0.345
    p.rect(bx0, by0, bx1, by1, pal["bubble"])
    if s16:  # vien duoi bong bong toi nhe
        p.rect(bx0, by1 - 4 / p.h, bx1, by1, pal["bubble_d"])
    draw_orb(p, 0.556, 0.232, 0.066, 0.090)

    # ---- ghe
    p.rect(0.098, 0.560, 0.138, 0.865, pal["chair"])

    # ---- nhan vat (chi la phan tu trong canh)
    # chan / ghe ngoi
    p.rect(0.145, 0.745, 0.237, 0.885, pal["pants"])
    # than ao
    p.rect(0.122, 0.512, 0.248, 0.752, pal["shirt"])
    if s16:  # do bong ao: nua duoi + ria phai toi hon
        p.rect(0.122, 0.690, 0.248, 0.752, pal["shirt_d"])
        p.rect(0.228, 0.512, 0.248, 0.752, pal["shirt_d"])
    # dau
    p.circle(0.185, 0.402, 0.058, pal["skin"])
    if s16:  # bong nhe duoi cam
        p.arc(0.127, 0.315, 0.243, 0.49, 20, 160, pal["skin_d"], wpx=2)
    # toc: nua tren cua dau
    hx0, hy0 = 0.185 - 0.058, 0.402 - 0.058 * p.w / p.h
    hx1, hy1 = 0.185 + 0.058, 0.402 + 0.058 * p.w / p.h
    p.d.pieslice([hx0 * p.w, hy0 * p.h, hx1 * p.w, hy1 * p.h],
                 180, 360, fill=pal["hair"])
    # mat + mieng cuoi
    ey = 0.408
    for ex in (0.166, 0.204):
        if s16:
            p.rect_px(int(ex * p.w) - 1, int(ey * p.h) - 1,
                      int(ex * p.w) + 1, int(ey * p.h) + 1, pal["black"])
        else:
            p.px(ex, ey, pal["black"])
    p.arc(0.168, 0.415, 0.202, 0.455, 15, 165, pal["black"],
          wpx=2 if s16 else 1)
    # tay vuon toi laptop: ve bang polygon dac (line Bresenham bi dut net)
    p.poly([(0.198, 0.578), (0.415, 0.650), (0.418, 0.686), (0.205, 0.616)],
           pal["skin"])
    if s16:  # duong toi doc canh duoi cua tay
        p.line(0.205, 0.616, 0.418, 0.686, pal["skin_d"], wpx=1)

    # ---- ban
    p.rect(0.128, 0.735, 0.648, 0.768, pal["desk"])
    if s16:
        p.rect(0.128, 0.752, 0.648, 0.768, pal["desk_d"])
    p.rect(0.152, 0.768, 0.178, 0.895, pal["desk_d"] if s16 else pal["desk"])
    p.rect(0.598, 0.768, 0.624, 0.895, pal["desk_d"] if s16 else pal["desk"])

    # ---- laptop tren ban
    p.rect(0.435, 0.545, 0.577, 0.738, pal["lap_fr"])
    if not s16:  # 8-bit: them vien sang de laptop khong chim vao nen toi
        gx0, gy0 = int(0.435 * p.w), int(0.545 * p.h)
        gx1, gy1 = int(0.577 * p.w), int(0.738 * p.h)
        p.d.rectangle([gx0, gy0, gx1, gy1], outline=pal["sph_out"], width=1)
    if s16:
        p.rect(0.447, 0.557, 0.565, 0.726, pal["lap_in"])
        p.line(0.462, 0.665, 0.545, 0.600, pal["lap_ln1"], wpx=2)
        p.line(0.462, 0.695, 0.520, 0.648, pal["lap_ln2"], wpx=2)
    else:
        p.line(0.462, 0.665, 0.545, 0.600, pal["lap_ln1"], wpx=1)
        p.line(0.462, 0.695, 0.520, 0.648, pal["lap_ln2"], wpx=1)
    p.rect(0.420, 0.738, 0.592, 0.756, pal["lap_fr"])  # de laptop

    # ---- den ban
    p.line(0.636, 0.738, 0.617, 0.520, pal["lamp_pole"], wpx=2 if s16 else 1)
    p.poly([(0.584, 0.438), (0.652, 0.438), (0.636, 0.548), (0.600, 0.548)],
           pal["lamp"])
    if s16:  # bong den sang + quai sang mo quanh den
        p.circle(0.618, 0.500, 0.016, pal["lamp_hi"])
        for gx, gy in [(0.600, 0.475), (0.636, 0.475), (0.618, 0.545),
                       (0.594, 0.520), (0.642, 0.520)]:
            p.px(gx, gy, pal["lamp_hi"])
    else:
        p.circle(0.618, 0.500, 0.014, pal["moon"])
    return p.upscale()


# ---------------------------------------------------------------- bang tong
def load_font(size, bold=True):
    path = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(path, size)


def centered(d, cx, y, text, font, fill):
    box = d.textbbox((0, 0), text, font=font)
    d.text((cx - (box[2] - box[0]) / 2, y), text, font=font, fill=fill)


def make_board(panels):
    W = 2000
    MARGIN, GAP = 30, 20
    TITLE_H, COLH_H, ROWL_H, FOOT_H = 104, 58, 46, 54
    PH = 540
    H = TITLE_H + COLH_H + (ROWL_H + PH) * 2 + FOOT_H
    board = Image.new("RGB", (W, H), (13, 11, 32))
    d = ImageDraw.Draw(board)
    f_title = load_font(52)
    f_col = load_font(35)
    f_row = load_font(32)
    f_foot = load_font(26, bold=False)

    centered(d, W / 2, 22, "BẢNG MẪU PIXEL — CHỌN 1 PHONG CÁCH",
             f_title, (240, 240, 250))
    y = TITLE_H
    col_x = [MARGIN, MARGIN + 960 + GAP]
    centered(d, col_x[0] + 480, y + 6, "8-BIT  (lưới 160×90 · ít màu · phẳng)",
             f_col, (120, 220, 255))
    centered(d, col_x[1] + 480, y + 6, "16-BIT  (lưới 320×180 · đổ bóng + dithering)",
             f_col, (255, 190, 90))
    y += COLH_H
    rows = [("CẢNH A · QUẢ CẦU NUỐT CẢNH", panels["a8"], panels["a16"]),
            ("CẢNH B · NGƯỜI NGỒI MÁY TÍNH", panels["b8"], panels["b16"])]
    for label, left, right in rows:
        d.text((MARGIN + 4, y + 6), label, font=f_row, fill=(200, 200, 230))
        y += ROWL_H
        for x, img in zip(col_x, (left, right)):
            board.paste(img, (x, y))
            d.rectangle([x, y, x + 959, y + 539], outline=(74, 63, 143),
                        width=3)
        y += PH
    centered(d, W / 2, y + 12,
             "Cùng một cảnh, cùng bố cục — chỉ khác độ mịn pixel và độ giàu màu/bóng.",
             f_foot, (150, 150, 180))
    return board


# ---------------------------------------------------------------- main
def main():
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    a8, a16 = scene_a("8"), scene_a("16")
    b8, b16 = scene_b("8"), scene_b("16")
    a8.save("scene-a-8bit.png")
    a16.save("scene-a-16bit.png")
    b8.save("scene-b-8bit.png")
    b16.save("scene-b-16bit.png")
    board = make_board({"a8": a8, "a16": a16, "b8": b8, "b16": b16})
    board.save("board.png")
    print("OK:", board.size)


if __name__ == "__main__":
    main()
