#!/usr/bin/env python3
"""
PIXEL STUDIO - 8 mau canh VE BANG CODE, TAT CA DEU CO CHUYEN DONG + HIEU UNG.

Moi ham canh nhan:
  p  : Painter (luoi 320x180, ve bang toa do chuan hoa 0..1)
  t  : tien trinh cua canh 0..1 (theo thoi luong giong doc)
  tm : thoi gian that trong canh (giay) - cho chuyen dong lien tuc
       (banh rang quay, sao nhap nhay, xung chay...)

Hieu ung dung chung: sao nhap nhay (trong draw_background), fade-in/out
(rap o render.py), pop-in (ease_out_back), pulse phat sang (halo dao dong).
Chuyen canh = HARD CUT. Cam zoompan tren anh tinh.
"""
import math

from PIL import Image, ImageFont

from painter import (FVT, PAL, Painter, clamp, dark, draw_background,
                     draw_orb, cube, ease_in_quad, ease_out_back,
                     ease_out_cubic, gear, lerp, lite, stars_for, window)

_FONT_CACHE = {}


def _vt_font(size):
    size = int(size)
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(FVT, size)
    return _FONT_CACHE[size]


def _text_centered_x(p, cx, y, text, size, color):
    """Ve chu VT323 can giua theo chieu ngang quanh cx (y = mep tren, 0..1)."""
    w_px = p.d.textlength(text, font=_vt_font(size))
    p.text_vt(cx - (w_px / 2.0) / p.w, y, text, size, color)


def _text_centered_xy(p, cx, cy, text, size, color):
    """Ve chu VT323 can giua ca ngang + doc quanh diem (cx, cy) 0..1."""
    fnt = _vt_font(size)
    w_px = p.d.textlength(text, font=fnt)
    bb = p.d.textbbox((0, 0), text, font=fnt)
    glyph_cy_px = (bb[1] + bb[3]) / 2.0
    x_px = cx * p.w - w_px / 2.0
    y_px = cy * p.h - glyph_cy_px
    p.text_vt(x_px / p.w, y_px / p.h, text, size, color)


def _params(params):
    return params if isinstance(params, dict) else {}

# ================================================================= CANH 01
def scene01(p, t, tm, params=None):
    """Qua cau nuot canh: mui ten ve dan, qua cau lon dan nuot dan canh vat."""
    prm = _params(params)
    pal = p.pal
    draw_background(p, stars_for(101), tm)
    # mui ten cong ve dan theo t
    sweep = ease_out_cubic(window(t, 0.0, 0.45))
    if sweep > 0.02:
        p.arc(0.115, 0.03, 0.545, 0.37, 180, 180 + 158 * sweep,
              pal["orange"], wpx=3)
    if sweep > 0.9:  # dau mui ten pop-in khi cung gan tron
        s = ease_out_back((sweep - 0.9) / 0.1)
        cx, cy = 0.512, 0.182
        p.poly([(cx + 0.054 * s, cy + 0.008 * s), (cx - 0.014 * s, cy - 0.076 * s),
                (cx, cy)], pal["orange"])
    # bong duoi qua cau lon theo kich thuoc cau
    grow = ease_out_cubic(window(t, 0.10, 0.75))
    if prm.get("percent") is not None:
        r_final = min(0.45 * (1 + float(prm["percent"]) / 100.0), 1.35)
    else:
        r_final = 1.0
    r_scale = lerp(0.45, r_final, grow) * (1 + 0.012 * math.sin(tm * 1.6))
    p.ellipse(0.345 - 0.23 * r_scale, 0.845, 0.345 + 0.23 * r_scale, 0.890,
              pal["shadow"])

    def building(x0, y0, x1, y1, c, win_rows=4):
        p.rect(x0, y0, x1, y1, c)
        p.rect((x0 + x1) / 2, y0, x1, y1, pal["bldg_d"])
        bx0, bx1 = int(x0 * p.w), int(x1 * p.w)
        by0, by1 = int(y0 * p.h), int(y1 * p.h)
        wx = bx0 + (bx1 - bx0 - 3) // 2
        for i in range(win_rows):
            wy = by0 + int((by1 - by0) * (0.13 + 0.235 * i))
            # cua so lan luot tat khi qua cau nuot toi gan (theo t)
            lit = (i * 0.21 + (x0 - 0.7)) < (1.05 - grow)
            wc = pal["window"] if lit else pal["bldg_d"]
            if i % 3 == 2 and lit:
                wc = pal["window_d"]
            p.rect_px(wx, wy, wx + 2, wy + 2, wc)

    building(0.700, 0.665, 0.758, 0.85, pal["bldg2"], 2)
    building(0.775, 0.545, 0.837, 0.85, pal["bldg"], 4)
    building(0.845, 0.665, 0.917, 0.85, pal["bldg2"], 2)
    building(0.925, 0.585, 0.977, 0.85, pal["bldg"], 4)
    # 2 qua cau nho: pulse phat sang nhe
    pu = 1 + 0.05 * math.sin(tm * 2.2)
    draw_orb(p, 0.685, 0.740, 0.068 * pu, 0.105 * pu)
    draw_orb(p, 0.880, 0.775, 0.043 * pu, 0.070 * pu)
    # qua cau chinh lon dan
    draw_orb(p, 0.345, 0.540, 0.225 * r_scale, 0.300 * r_scale)
    # chu % ngay giua cau (chi khi co du kien percent), hien khi cau du lon
    if prm.get("percent") is not None and grow > 0.45:
        pv = prm["percent"]
        txt = ("%d%%" % pv) if float(pv) == int(float(pv)) else ("%s%%" % pv)
        _text_centered_xy(p, 0.345, 0.540, txt, 30, pal["window"])
    # span_text (vd "5 years"): dong phu trong cau, duoi chu % neu co
    if prm.get("span_text") and grow > 0.45:
        span_y = 0.635 if prm.get("percent") is not None else 0.540
        _text_centered_xy(p, 0.345, span_y, str(prm["span_text"]), 16,
                          pal["window_d"])


# ================================================================= CANH 02
def scene02(p, t, tm, params=None):
    """Can so sanh: can tu ngang nghieng dan ve ben nang (co nay qua lai)."""
    prm = _params(params)
    pal = p.pal
    draw_background(p, stars_for(102), tm)
    cx = 0.5
    p.rect(0.489, 0.30, 0.511, 0.80, pal["violet_d"])
    p.rect(0.489, 0.30, 0.500, 0.80, pal["violet"])
    p.poly([(cx, 0.76), (0.415, 0.885), (0.585, 0.885)], pal["violet"])
    p.poly([(cx, 0.76), (0.415, 0.885), (cx, 0.885)], pal["violet_d"])
    # goc xoay: bat dau +0.149 (can NGANG) -> a_final (vi tri nghieng da duyet);
    # winner="b" -> a_final=0.298 (nghieng nguoc: dia B thap hon, guong cua v1);
    # ease_out_back vuot qua 1 mot chut -> can nay qua muc roi moi yen (wobble)
    a_final = 0.298 if prm.get("winner") == "b" else 0.0
    a = lerp(0.149, a_final, ease_out_back(window(t, 0.08, 0.62)))
    a += 0.008 * math.sin(tm * 1.7) * window(t, 0.7, 0.3)  # rung nhe khi da yen
    piv = (0.5, 0.26)
    L0, R0 = (-0.365, 0.055), (0.365, -0.055)   # vector toi 2 dau can (ban duyet)
    def rot(vx, vy, a):
        return (vx * math.cos(a) - vy * math.sin(a),
                vx * math.sin(a) + vy * math.cos(a))
    lx_, ly_ = rot(L0[0], L0[1], a)
    rx_, ry_ = rot(R0[0], R0[1], a)
    lx, ly = piv[0] + lx_, piv[1] + ly_
    rx, ry = piv[0] + rx_, piv[1] + ry_
    p.line(lx, ly, rx, ry, pal["cream"], wpx=3)
    # ---- dia trai + khoi nang (chuyen dong cung dau can)
    p.line(lx, ly, lx, ly + 0.100, pal["cream"], wpx=1)
    ptop = ly + 0.100
    p.poly([(lx - 0.088, ptop), (lx + 0.088, ptop),
            (lx + 0.052, ptop + 0.050), (lx - 0.052, ptop + 0.050)],
           pal["skyblue"])
    p.rect(lx - 0.088, ptop - 0.007, lx + 0.088, ptop + 0.003, pal["skyblue_d"])
    cube(p, lx - 0.062, ptop - 0.085, 0.058, 0.082, pal["orange"],
         pal["orange_d"], lite(pal["orange"]))
    cube(p, lx + 0.002, ptop - 0.085, 0.058, 0.082, pal["orange_d"],
         dark(pal["orange_d"]), pal["orange"])
    cube(p, lx - 0.031, ptop - 0.167, 0.058, 0.082, pal["window"],
         pal["window_d"], lite(pal["window"]))
    if prm.get("label_a"):
        _text_centered_x(p, lx, ptop - 0.300, str(prm["label_a"]), 18,
                         pal["cream"])
    else:
        p.text_vt(lx - 0.075, ptop - 0.300, "A", 34, pal["cream"])
    # ---- dia phai + qua cau cyan pulse phat sang
    p.line(rx, ry, rx, ry + 0.100, pal["cream"], wpx=1)
    ptop_r = ry + 0.100
    p.poly([(rx - 0.088, ptop_r), (rx + 0.088, ptop_r),
            (rx + 0.052, ptop_r + 0.050), (rx - 0.052, ptop_r + 0.050)],
           pal["skyblue"])
    p.rect(rx - 0.088, ptop_r - 0.007, rx + 0.088, ptop_r + 0.003,
           pal["skyblue_d"])
    ocy = ptop_r - 0.043
    pu = 1 + 0.10 * math.sin(tm * 2.6)
    p.circle(rx, ocy, 0.052 * pu, pal["halo_teal"])
    p.circle(rx, ocy, 0.036, pal["cyan"])
    p.circle(rx - 0.012, ocy - 0.012, 0.011, (225, 252, 255))
    if prm.get("label_b"):
        _text_centered_x(p, rx, ptop_r - 0.230, str(prm["label_b"]), 18,
                         pal["cream"])
    else:
        p.text_vt(rx - 0.018, ptop_r - 0.230, "B", 34, pal["cream"])
    p.circle(cx, 0.26, 0.017, pal["orange"])


# ================================================================= CANH 03
def scene03(p, t, tm, params=None):
    """Mang luoi node: node sang lan luot, xung chay doc duong noi."""
    pal = p.pal
    draw_background(p, stars_for(103), tm, ground=False)
    cx, cy = 0.5, 0.47
    sats = [(0.156, 0.204, pal["violet"]), (0.344, 0.122, pal["skyblue"]),
            (0.667, 0.111, pal["mint"]), (0.856, 0.219, pal["orange"]),
            (0.898, 0.556, pal["red"]), (0.729, 0.778, pal["violet"]),
            (0.260, 0.793, pal["pink"]), (0.112, 0.559, pal["skyblue"])]
    for (x, y, c) in sats:
        p.line(cx, cy, x, y, pal["edge_dim"], wpx=1)
    p.line(0.156, 0.204, 0.344, 0.122, pal["edge_dim"], wpx=1)
    p.line(0.856, 0.219, 0.898, 0.556, pal["edge_dim"], wpx=1)
    active = [window(t, 0.06 + i * 0.085, 0.22) for i in range(8)]
    for i, (x, y, c) in enumerate(sats):
        if active[i] > 0:  # duong noi sang xanh khi node kich hoat
            p.line(cx, cy, x, y, pal["green_d"], wpx=1)
            # xung chay tu tam ra node, lap lai
            fr = (tm * 0.55 + i * 0.17) % 1.0
            mx, my = cx + (x - cx) * fr, cy + (y - cy) * fr
            gx, gy = int(mx * p.w), int(my * p.h)
            p.rect_px(gx - 2, gy - 2, gx + 2, gy + 2, pal["green"])
            p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, (225, 255, 245))
    for i, (x, y, c) in enumerate(sats):
        a = active[i]
        if a <= 0:
            p.circle(x, y, 0.012, pal["edge_dim"])
        else:
            s = ease_out_back(a)
            p.circle(x, y, 0.021 * s, c)
            if a > 0.6:
                p.circle(x, y, 0.008, (240, 245, 255))
    # tam: pulse phat sang lien tuc
    pu = 1 + 0.09 * math.sin(tm * 2.4)
    p.circle(cx, cy, 0.058 * pu, pal["halo_teal"])
    p.circle(cx, cy, 0.037, pal["cyan"])
    p.circle(cx, cy, 0.015, (235, 252, 255))


# ================================================================= CANH 04
def scene04(p, t, tm, params=None):
    """Dong thoi gian: truc ve dan, cac moc pop-in lan luot trai -> phai."""
    prm = _params(params)
    pal = p.pal
    draw_background(p, stars_for(104), tm, ground=False)
    y = 0.55
    xs = [0.115, 0.307, 0.5, 0.692, 0.885]
    rs = [0.013, 0.017, 0.021, 0.027, 0.033]
    cols = [pal["skyblue"], pal["mint"], pal["cyan"], pal["orange"], pal["red"]]
    years = prm.get("years") or None
    if years:
        years = list(years)[:5]
        n_yr = len(years)
        if n_yr == 1:
            xs = [0.5]
        else:
            xs = [0.115 + (0.885 - 0.115) * i / (n_yr - 1)
                  for i in range(n_yr)]
        rs = [lerp(0.013, 0.033, i / (n_yr - 1) if n_yr > 1 else 0.0)
              for i in range(n_yr)]
        cols = [cols[i % len(cols)] for i in range(n_yr)]
    prog = ease_out_cubic(window(t, 0.0, 0.9))
    x_end = lerp(0.07, 0.93, prog)
    p.line(0.07, y, x_end, y, pal["axis"], wpx=2)
    if prog > 0.97:
        p.poly([(0.945, y), (0.918, y - 0.024), (0.918, y + 0.024)], pal["star"])
    for i, (x, r, c) in enumerate(zip(xs, rs, cols)):
        lt = window(t, 0.08 + i * 0.155, 0.20)
        if lt <= 0:
            continue
        s = ease_out_back(lt)
        up = (i % 2 == 0)
        sy = y - 0.215 if up else y + 0.215
        stem = lerp(y, sy, ease_out_cubic(lt))
        p.line(x, y, x, stem, pal["axis"], wpx=1)
        # bieu tuong moc, phong to theo s quanh tam (x, sy)
        def sc(v):
            return v * s
        if i == 0:
            p.ellipse(x - sc(0.024), sy - sc(0.024) * p.w / p.h,
                      x + sc(0.024), sy + sc(0.024) * p.w / p.h,
                      None, outline=c, ow=2)
            p.circle(x, sy, sc(0.007), c)
        elif i == 1:
            p.rect(x - sc(0.030), sy - sc(0.034), x + sc(0.030), sy + sc(0.034), c)
            p.rect(x - sc(0.030), sy - sc(0.034), x + sc(0.030), sy - sc(0.012),
                   lite(c))
        elif i == 2:
            p.poly([(x, sy - sc(0.045)), (x + sc(0.026), sy + sc(0.032)),
                    (x - sc(0.026), sy + sc(0.032))], c)
            p.poly([(x, sy - sc(0.045)), (x + sc(0.026), sy + sc(0.032)),
                    (x, sy + sc(0.032))], dark(c))
        elif i == 3:
            p.rect(x - sc(0.026), sy - sc(0.046), x + sc(0.026), sy + sc(0.046), c)
            p.rect(x - sc(0.026), sy - sc(0.046), x + sc(0.026), sy - sc(0.016),
                   lite(c))
            p.circle(x, sy, sc(0.008), pal["sky"])
        else:
            pu = 1 + 0.07 * math.sin(tm * 3.0)
            p.circle(x, sy, sc(0.052) * pu, pal["halo_red"])
            pts = []
            for k in range(10):
                ang = -math.pi / 2 + k * math.pi / 5
                rr = sc(0.036 if k % 2 == 0 else 0.016)
                pts.append((x + rr * math.cos(ang),
                            sy + rr * math.sin(ang) * p.w / p.h))
            p.poly(pts, c)
        p.circle(x, y, r * s, c)
        if lt > 0.5:
            p.circle(x, y, r * 0.38 * s, (245, 248, 255))
            if years:
                _text_centered_x(p, x, y + 0.045, str(years[i]), 15,
                                 pal["star_dim"])
            else:
                p.text_vt(x - 0.012, y + 0.045, str(i + 1), 22,
                          pal["star_dim"])


# ================================================================= CANH 05
def scene05(p, t, tm, params=None):
    """Roi & xep chong: cac khoi roi lan luot xep thanh dong ngay cang cao."""
    prm = _params(params)
    pal = p.pal
    draw_background(p, stars_for(105), tm)
    p.ellipse(0.19, 0.845, 0.77, 0.885, pal["shadow"])
    W_, H_ = 0.115, 0.105
    # (x, y_dich, mau, mau_toi, mau_sang) theo thu tu xep tu duoi len
    blocks = [
        (0.315, 0.755, pal["orange"], pal["orange_d"], lite(pal["orange"])),
        (0.440, 0.755, pal["violet"], pal["violet_d"], lite(pal["violet"])),
        (0.565, 0.755, (38, 150, 190), (26, 104, 134), (86, 182, 214)),
        (0.377, 0.650, pal["mint"], pal["green_d"], lite(pal["mint"])),
        (0.502, 0.650, pal["orange_d"], dark(pal["orange_d"]), pal["orange"]),
        (0.440, 0.545, pal["pink"], pal["pink_d"], lite(pal["pink"])),
        (0.470, 0.440, pal["skyblue"], pal["skyblue_d"], lite(pal["skyblue"])),
        (0.625, 0.650, pal["orange"], pal["orange_d"], lite(pal["orange"])),
    ]
    if prm.get("quantity_value") is not None:
        # 6 vi tri mo rong: 2 hang day (2 ben), 2 hang 2, 2 hang 3
        extra = [
            (0.190, 0.755, pal["skyblue"], pal["skyblue_d"],
             lite(pal["skyblue"])),
            (0.690, 0.755, pal["pink"], pal["pink_d"], lite(pal["pink"])),
            (0.252, 0.650, (38, 150, 190), (26, 104, 134), (86, 182, 214)),
            (0.750, 0.650, pal["violet"], pal["violet_d"],
             lite(pal["violet"])),
            (0.315, 0.545, pal["mint"], pal["green_d"], lite(pal["mint"])),
            (0.565, 0.545, pal["orange"], pal["orange_d"],
             lite(pal["orange"])),
        ]
        qv = float(prm["quantity_value"])
        n_blocks = int(clamp(4 + int(2.0 * math.log10(max(qv, 1.0))),
                             4, 14))
        blocks = (blocks + extra)[:n_blocks]
    # nhieu khoi hon 8: nen khoang cach roi de khoi cuoi van cham dat ~0.945
    step = 0.105 if len(blocks) <= 8 else 0.735 / (len(blocks) - 1)
    for k, (x, y_land, c, cd, cl) in enumerate(blocks):
        lt = window(t, 0.04 + k * step, 0.17)
        if lt <= 0:
            continue
        if lt < 1:  # dang roi: nhanh dan (ease-in) + vet chuyen dong
            y = lerp(y_land - 0.62, y_land, ease_in_quad(lt))
            for j in range(3):
                lx = x + 0.018 + j * 0.030
                p.line(lx, y - 0.085, lx, y - 0.028, pal["star_dim"], wpx=1)
        else:  # da cham dat: nay nhe 1 nhip ngay khi tiep dat
            y = y_land
        cube(p, x, y, W_, H_, c, cd, cl)
    if prm.get("quantity_text") and t > 0.85:
        _text_centered_x(p, 0.5, 0.06, str(prm["quantity_text"]), 22,
                         pal["cream"])


# ================================================================= CANH 06
def scene06(p, t, tm, params=None):
    """Ban do hanh trinh: duong dut net ve dan, chang sang lan luot, ghim pulse."""
    prm = _params(params)
    pal = p.pal
    draw_background(p, stars_for(106), tm)
    p0, p1, p2, p3 = ((0.115, 0.778), (0.448, 0.926),
                      (0.583, 0.389), (0.854, 0.241))

    def bez(tt):
        x = ((1 - tt) ** 3 * p0[0] + 3 * (1 - tt) ** 2 * tt * p1[0]
             + 3 * (1 - tt) * tt * tt * p2[0] + tt ** 3 * p3[0])
        y = ((1 - tt) ** 3 * p0[1] + 3 * (1 - tt) ** 2 * tt * p1[1]
             + 3 * (1 - tt) * tt * tt * p2[1] + tt ** 3 * p3[1])
        return x, y

    pts = [bez(i / 90.0) for i in range(91)]
    prog = ease_out_cubic(window(t, 0.0, 0.92))
    n_show = int(91 * prog)
    for i in range(0, n_show, 3):
        x, y = pts[i]
        gx, gy = int(x * p.w), int(y * p.h)
        p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, pal["star"])
    if 0 < n_show <= 90:  # dau di chuyen phat sang o dau duong dang ve
        x, y = pts[min(n_show, 90)]
        p.circle(x, y, 0.010, pal["green"])
        p.circle(x, y, 0.004, (240, 255, 250))
    stages = prm.get("stages") or None
    if stages:
        stages = int(clamp(int(stages), 2, 5))
        mid_cols = [pal["skyblue"], pal["orange"], pal["violet"],
                    pal["skyblue"]]
        nodes = [(0.0, pal["green"])] + [
            (i / stages, mid_cols[(i - 1) % len(mid_cols)])
            for i in range(1, stages)]
        flag_tt = (stages - 1) / stages
    else:
        nodes = [(0.0, pal["green"]), (0.34, pal["skyblue"]),
                 (0.62, pal["orange"]), (0.83, pal["violet"])]
        flag_tt = 0.62
    for tt, c in nodes:
        if prog >= tt - 0.01:
            s = ease_out_back(window(prog, tt, 0.10))
            x, y = bez(tt)
            p.circle(x, y, 0.017 * s, c)
            if s > 0.7:
                p.circle(x, y, 0.006, (245, 248, 255))
    flag_start = flag_tt - 0.02
    if prog >= flag_start:  # co o chang trung gian cuoi
        fx, fy = bez(flag_tt)
        s = ease_out_back(window(prog, flag_start, 0.10))
        p.line(fx, fy - 0.010, fx, fy - 0.115 * s, pal["cream"], wpx=1)
        p.poly([(fx, fy - 0.115 * s), (fx + 0.038 * s, fy - 0.092 * s),
                (fx, fy - 0.068 * s)], pal["orange"])
    x, y = bez(1.0)
    if prog > 0.965:  # ghim dich: pop-in + pulse lien tuc
        s = ease_out_back(window(prog, 0.965, 0.035))
        pu = (1 + 0.08 * math.sin(tm * 4.0)) * s
        p.circle(x, y - 0.038, 0.048 * pu, pal["halo_red"])
        p.circle(x, y - 0.038, 0.027 * s, pal["red"])
        p.poly([(x - 0.016 * s, y - 0.026), (x + 0.016 * s, y - 0.026),
                (x, y + 0.012 * s)], pal["red"])
        if s > 0.7:
            p.circle(x, y - 0.038, 0.010, (255, 235, 238))
        p.text_vt(0.845, 0.075, "END", 20, pal["red"])
    p.text_vt(0.030, 0.600, "START", 19, pal["star_dim"])


# ================================================================= CANH 07
def scene07(p, t, tm, params=None):
    """Co may van hanh: banh rang quay an khop, bang chuyen chay, khoi di chuyen."""
    pal = p.pal
    draw_background(p, stars_for(107), tm)
    # banh rang quay lien tuc (nguoc chieu nhau nhu an khop)
    gear(p, 0.330, 0.340, 0.105, 9, pal["violet"], phase=tm * 0.55)
    gear(p, 0.495, 0.470, 0.072, 8, pal["skyblue"], phase=-tm * 0.78 + 0.35)
    gear(p, 0.240, 0.575, 0.058, 8, pal["orange"], phase=-tm * 0.95 + 0.2)
    # bong bong khi bay len tu co may
    for (bx, sp, ph) in [(0.330, 0.045, 0.0), (0.360, 0.035, 0.4),
                         (0.500, 0.05, 0.7)]:
        yy = 0.24 - ((tm * sp + ph) % 0.17)
        p.circle(bx + 0.01 * math.sin(tm + ph * 9), yy, 0.010, pal["star_dim"])
    # bang chuyen
    belt_x0, belt_x1 = 0.470, 0.940
    p.rect(belt_x0, 0.690, belt_x1, 0.752, (40, 36, 84))
    p.rect(belt_x0, 0.690, belt_x1, 0.700, pal["axis"])
    p.rect(belt_x0, 0.742, belt_x1, 0.752, pal["sph_out_d"])
    # con lan xoay: diem sang tren con lan di chuyen theo goc
    rx = belt_x0 + 0.022
    while rx < 0.925:
        p.circle(rx, 0.721, 0.011, pal["axis"])
        da = tm * 3.0 + rx * 7.0
        p.px(rx + 0.006 * math.cos(da), 0.721 + 0.006 * math.sin(da),
             pal["cream"])
        rx += 0.056
    # 3 khoi chay tren bang chuyen, vong lap
    span = belt_x1 - belt_x0 - 0.10
    cube_cols = [(pal["mint"], pal["green_d"], lite(pal["mint"])),
                 (pal["pink"], pal["pink_d"], lite(pal["pink"])),
                 (pal["green"], pal["green_d"], lite(pal["green"]))]
    for k, (c, cd, cl) in enumerate(cube_cols):
        fx = (tm * 0.055 + k * 0.34) % 1.0
        x = belt_x0 + 0.012 + fx * span
        cube(p, x, 0.585, 0.075, 0.105, c, cd, cl)


# ================================================================= CANH 08
def scene08(p, t, tm, params=None):
    """Nguoi trong canh: nhan vat go may, bong bong suy nghi hien dan + qua cau."""
    pal = p.pal
    draw_background(p, stars_for(108, 80), tm)
    p.rect(0, 0.845, 1, 0.856, pal["ground_hi"])
    p.rect(0, 0.845, 1, 1, pal["ground"])
    # cua so ben phai + trang sao
    p.rect(0.695, 0.115, 0.945, 0.585, pal["win_fr"])
    p.rect(0.703, 0.139, 0.937, 0.561, pal["win_in"])
    p.circle(0.862, 0.265, 0.052, pal["moon"])
    p.circle(0.880, 0.248, 0.046, pal["win_in"])
    for sx, sy in [(0.735, 0.20), (0.745, 0.44), (0.905, 0.47)]:
        if 0.6 + 0.4 * math.sin(tm * 2.3 + sx * 20) > 0.55:
            cx, cy = int(sx * p.w), int(sy * p.h)
            p.rect_px(cx - 2, cy, cx + 2, cy, pal["star"])
            p.rect_px(cx, cy - 2, cx, cy + 2, pal["star"])
    # bong bong suy nghi: pop-in theo t, qua cau ben trong pulse
    bs = ease_out_back(window(t, 0.05, 0.30))
    if bs > 0.05:
        bcx, bcy = 0.535, 0.232  # tam bong bong
        def bub_rect(x0, y0, x1, y1, c):
            p.rect(bcx + (x0 - bcx) * bs, bcy + (y0 - bcy) * bs,
                   bcx + (x1 - bcx) * bs, bcy + (y1 - bcy) * bs, c)
        p.circle(0.312, 0.378, 0.013 * bs, pal["bubble"])
        p.circle(0.352, 0.332, 0.019 * bs, pal["bubble"])
        bub_rect(0.405, 0.120, 0.665, 0.345, pal["bubble"])
        bub_rect(0.405, 0.329, 0.665, 0.345, pal["bubble_d"])
        if bs > 0.55:
            pu = (1 + 0.05 * math.sin(tm * 2.0)) * (bs - 0.55) / 0.45
            draw_orb(p, 0.556, 0.232, 0.066 * pu, 0.090 * pu)
    # ghe + nhan vat (chi la phan tu trong canh) - dau gat nhe theo nhip
    bob = 0.0025 * math.sin(tm * 1.8)
    p.rect(0.098, 0.560, 0.138, 0.865, pal["chair"])
    p.rect(0.145, 0.745, 0.237, 0.885, pal["pants"])
    p.rect(0.122, 0.512, 0.248, 0.752, pal["shirt"])
    p.rect(0.122, 0.690, 0.248, 0.752, pal["shirt_d"])
    p.rect(0.228, 0.512, 0.248, 0.752, pal["shirt_d"])
    hcy = 0.402 + bob
    p.circle(0.185, hcy, 0.058, pal["skin"])
    p.arc(0.127, 0.315 + bob, 0.243, 0.49 + bob, 20, 160, pal["skin_d"], wpx=2)
    hx0, hy0 = 0.185 - 0.058, hcy - 0.058 * p.w / p.h
    hx1, hy1 = 0.185 + 0.058, hcy + 0.058 * p.w / p.h
    p.d.pieslice([hx0 * p.w, hy0 * p.h, hx1 * p.w, hy1 * p.h],
                 180, 360, fill=pal["hair"])
    for ex in (0.166, 0.204):
        gx, gy = int(ex * p.w), int((0.408 + bob) * p.h)
        p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, pal["black"])
    p.arc(0.168, 0.415 + bob, 0.202, 0.455 + bob, 15, 165, pal["black"], wpx=2)
    # tay go may: dau tay nhap nho theo nhip go ~7Hz
    tap = 0.007 * math.sin(tm * 13.0)
    tap2 = 0.007 * math.sin(tm * 13.0 + math.pi)
    p.poly([(0.198, 0.578), (0.415, 0.650 + tap), (0.418, 0.686 + tap),
            (0.205, 0.616)], pal["skin"])
    p.line(0.205, 0.616, 0.418, 0.686 + tap, pal["skin_d"], wpx=1)
    # ban + laptop + den ban
    p.rect(0.128, 0.735, 0.648, 0.768, pal["desk"])
    p.rect(0.128, 0.752, 0.648, 0.768, pal["desk_d"])
    p.rect(0.152, 0.768, 0.178, 0.895, pal["desk_d"])
    p.rect(0.598, 0.768, 0.624, 0.895, pal["desk_d"])
    p.rect(0.435, 0.545, 0.577, 0.738, pal["lap_fr"])
    p.rect(0.447, 0.557, 0.565, 0.726, pal["lap_in"])
    # dong code tren laptop hien dan + con tro nhap nhay
    if t > 0.15:
        p.line(0.462, 0.665, 0.462 + 0.083 * window(t, 0.15, 0.35), 0.600,
               pal["lap_ln1"], wpx=2)
    if t > 0.45:
        p.line(0.462, 0.695, 0.462 + 0.058 * window(t, 0.45, 0.35), 0.648,
               pal["lap_ln2"], wpx=2)
    if math.sin(tm * 3.2) > 0:
        gx, gy = int(0.552 * p.w), int(0.700 * p.h)
        p.rect_px(gx, gy, gx + 2, gy + 2, pal["lap_ln1"])
    p.rect(0.420, 0.738, 0.592, 0.756, pal["lap_fr"])
    # den ban: quay sang phat sang dao dong nhe
    p.line(0.636, 0.738, 0.617, 0.520, pal["lamp_pole"], wpx=2)
    p.poly([(0.584, 0.438), (0.652, 0.438), (0.636, 0.548), (0.600, 0.548)],
           pal["lamp"])
    glow_r = 0.016 * (1 + 0.18 * math.sin(tm * 2.7))
    p.circle(0.618, 0.500, glow_r, pal["lamp_hi"])
    for gx, gy in [(0.600, 0.475), (0.636, 0.475), (0.618, 0.545),
                   (0.594, 0.520), (0.642, 0.520)]:
        p.px(gx, gy, pal["lamp_hi"])


# ================================================================= CANH 09
def scene09(p, t, tm, params=None):
    """Sao bang quet canh (MOI V2.6): sao chao lon quet cheo qua bau
    troi sao kem duoi sang dai, 3 sao bang nho chay ngau nhien theo
    chu ky; mat trang pulse nhe o goc. Hop cau 'bung no / vuot troi /
    khoanh khac dang nho'."""
    pal = p.pal
    draw_background(p, stars_for(777), tm)
    # mat trang pulse goc tren trai
    pu = 1 + 0.05 * math.sin(tm * 1.8)
    p.circle(0.085, 0.14, 0.045 * pu, pal["moon"])
    p.circle(0.072, 0.125, 0.012, pal["window_d"])
    p.circle(0.098, 0.155, 0.009, pal["window_d"])

    def meteor(q, x0, y0, dx, dy, tail, head_c, mid_c):
        """1 sao bang: q = tien trinh 0..1 doc duong cheo."""
        hx, hy = x0 + dx * q, y0 + dy * q
        segs = 7
        for i in range(segs):
            f0 = i / float(segs)
            f1 = (i + 1) / float(segs)
            c = head_c if i == 0 else (mid_c if i < 3 else pal["star_dim"])
            p.line(hx - dx * tail * f0, hy - dy * tail * f0,
                   hx - dx * tail * f1, hy - dy * tail * f1,
                   c, wpx=2 if i < 2 else 1)
        # dau sao: cum pixel sang + halo
        gx, gy = int(hx * p.w), int(hy * p.h)
        p.rect_px(gx - 2, gy - 2, gx + 2, gy + 2, pal["halo_teal"])
        p.rect_px(gx - 1, gy - 1, gx + 1, gy + 1, head_c)

    # sao chao CHINH: quet cheo phai-tren -> trai-duoi, chu ky 2.4s,
    # nghi 0.5s giua 2 lan quet
    cyc = (tm % 2.9) / 2.4
    if cyc <= 1.0:
        meteor(cyc, 1.08, 0.02, -1.30, 0.78, 0.30,
               pal["window"], pal["orange"])
        # vong pulse khi sao di qua giua khung
        if 0.42 < cyc < 0.75:
            k = (cyc - 0.42) / 0.33
            r = 0.03 + 0.16 * k
            p.arc(0.44 - r, 0.36 - r * p.w / p.h, 0.44 + r,
                  0.36 + r * p.w / p.h, 0, 360, pal["cyan_d"], wpx=1)
    # 3 sao bang nho: chu ky lech pha nhau
    for i, (per, ph) in enumerate([(1.7, 0.4), (2.3, 1.3), (3.1, 2.2)]):
        q = ((tm + ph) % per) / per
        if q > 0.85:
            continue
        meteor(q, 0.95 - 0.18 * i, 0.06 + 0.10 * i, -0.85, 0.52, 0.16,
               pal["star"], pal["cyan"])


SCENES = {
    1: ("Quả cầu nuốt cảnh", "tăng trưởng · nguy cơ phình to", scene01),
    2: ("Cân so sánh A vs B", "so sánh · bên nào nặng hơn", scene02),
    3: ("Mạng lưới node", "hệ thống · kết nối · lan truyền", scene03),
    4: ("Dòng thời gian", "lịch sử · tiến trình · các mốc", scene04),
    5: ("Rơi & xếp chồng", "tích lũy · số lượng tăng dần", scene05),
    6: ("Bản đồ hành trình", "quá trình · từng bước một", scene06),
    7: ("Cỗ máy vận hành", "cơ chế · bên trong nó chạy thế nào", scene07),
    8: ("Người trong cảnh", "con người · bị công nghệ tác động", scene08),
    9: ("Sao băng quét cảnh", "bùng nổ · khoảnh khắc vụt sáng", scene09),
}


def draw_scene(scene_id, t, tm, params=None):
    """Ve 1 frame cua canh len luoi 320x180, tra ve PIL Image (RGB).

    Tuy chon MOI (V2.6): params {"fx": "pixelate"} = chuyen canh VO
    PIXEL - dau shot vo manh roi ro dan, cuoi shot vo lai. Mac dinh
    (khong co fx) giu nguyen 100% hanh vi cu."""
    p = Painter()
    SCENES[int(scene_id)][2](p, clamp(t), max(0.0, tm), params=params)
    img = p.img
    fx = str(_params(params).get("fx", "") or "").strip().lower()
    if fx in ("pixelate", "vo-pixel", "vo_pixel"):
        block = 0
        if t < 0.10:
            block = int(9 * (1 - t / 0.10)) + 1
        elif t > 0.92:
            block = int(9 * ((t - 0.92) / 0.08)) + 1
        if block > 1:
            small = img.resize((max(1, p.w // block),
                                max(1, p.h // block)), Image.NEAREST)
            img = small.resize((p.w, p.h), Image.NEAREST)
    return img
