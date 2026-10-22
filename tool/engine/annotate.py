#!/usr/bin/env python3
"""
PIXEL STUDIO V2 - mui ten chu thich (annotation) pop-in.

Mau da kiem chung: pixel-hybrid-test/build_hybrid_v3.py
(ham annotation_shapes + hi_text_layer):
  - Lop hinh (hop + mui ten) ve o luoi thap 320x180, scale quanh tam hop.
  - Lop chu ve o do phan giai that 1920x1080 (VT323 52px) cho net,
    scale quanh tam hop voi cung he so.

API:
  pop_scale(tm) -> float | None
  annotation_layers(label, target, scale) -> (low_img, hi_img)
    target: 0..8 (luoi 3x3) - diem dich = tam o do.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
FVT = os.path.join(TOOL_DIR, "fonts", "VT323.ttf")

GW, GH = 320, 180           # luoi thap
HW, HH = 1920, 1080         # full-res (x6)
LABEL_SIZE = 52             # co chu nhan o full-res
BOX_H = 88                  # chieu cao hop nhan o full-res
BOX_PAD_X = 28              # le chu trong hop (moi ben) o full-res

DARK = (8, 10, 20, 255)
BOX_FILL = (10, 14, 30, 242)
YELLOW = (255, 205, 40)
YELLOW_A = (255, 205, 40, 255)
TEXT_COLOR = (255, 240, 170, 255)

_font_cache = {}


def _font(size):
    size = int(size)
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FVT, size)
    return _font_cache[size]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def pop_scale(tm):
    """He so pop-in theo thoi gian that trong canh (giay).

    None neu tm < 0.10 (chua xuat hien). Cua so pop 0.10 -> 0.43s:
    scale 0.5 -> 1.0 bang ease-out cubic, nhan them nay nhe
    (1 + 0.10*sin(p*pi)) nhu ban mau. Sau cua so: 1.0.
    """
    if tm is None or tm < 0.10:
        return None
    p = _clamp((tm - 0.10) / 0.33, 0.0, 1.0)
    if p >= 1.0:
        return 1.0
    s = 0.5 + 0.5 * (1 - (1 - p) ** 3)
    s *= 1.0 + 0.10 * math.sin(p * math.pi)
    return s


def _scale_layer(layer, anchor_px, scale):
    """Scale toan bo lop quanh diem neo (px), giong cach ban mau lam."""
    if scale is None or scale == 1.0:
        return layer
    w, h = layer.size
    nw, nh = max(2, int(w * scale)), max(2, int(h * scale))
    resized = layer.resize((nw, nh), Image.NEAREST)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(resized, (int(anchor_px[0] - anchor_px[0] * scale),
                                  int(anchor_px[1] - anchor_px[1] * scale)))
    return out


def annotation_layers(label, target, scale):
    """Tra (low_img 320x180 RGBA, hi_img 1920x1080 RGBA).

    low_img: hop nhan (co theo chu) + mui ten chi toi diem dich.
    hi_img: chi chua chu nhan VT323 52px, dat trong hop.
    Ca 2 lop deu scale quanh tam hop theo `scale`.
    """
    label = "" if label is None else str(label)
    try:
        target = int(target)
    except (TypeError, ValueError):
        target = 4
    target = int(_clamp(target, 0, 8))
    if scale is None:
        scale = 1.0
    scale = float(scale)

    # ---- diem dich = tam o luoi 3x3 (toa do chuan hoa)
    tx = (target % 3) / 3.0 + 1.0 / 6.0
    ty = (target // 3) / 3.0 + 1.0 / 6.0

    # ---- hop nhan tu co theo chu (do o full-res)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8), (0, 0, 0, 0)))
    font = _font(LABEL_SIZE)
    text_w = probe.textlength(label, font=font) if label else 0.0
    box_w = text_w + BOX_PAD_X * 2
    box_h = float(BOX_H)

    cx = 0.74 if tx < 0.5 else 0.26
    cy = 0.20 if ty > 0.45 else 0.70
    # kep tam hop de hop khong tran khung (theo be rong hop that)
    cx_px = cx * HW
    half = box_w / 2.0
    if box_w >= HW:
        cx_px = HW / 2.0
    else:
        cx_px = _clamp(cx_px, half, HW - half)
    cy_px = cy * HH
    box_x0 = cx_px - half
    box_y0 = cy_px - box_h / 2.0
    box_x1 = box_x0 + box_w
    box_y1 = box_y0 + box_h
    box_cx_px, box_cy_px = cx_px, cy_px

    # ================= lop luoi thap: hop + mui ten =================
    low = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
    d = ImageDraw.Draw(low)
    lx0, ly0 = box_x0 / 6.0, box_y0 / 6.0
    lx1, ly1 = box_x1 / 6.0, box_y1 / 6.0
    hx, hy = tx * GW, ty * GH
    # duoi mui ten = diem tren bien hop gan dich nhat
    tail_x = _clamp(hx, lx0, lx1)
    tail_y = _clamp(hy, ly0, ly1)
    # mui ten: line toi rong -> line vang hep, dau tam giac (nhu ban mau)
    d.line([tail_x, tail_y, hx, hy], fill=DARK, width=7)
    d.line([tail_x, tail_y, hx, hy], fill=YELLOW_A, width=4)
    dx, dy = hx - tail_x, hy - tail_y
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    vx, vy = -uy, ux

    def _head(reach, back, half_w, color):
        tip = (hx + ux * reach, hy + uy * reach)
        bcx_, bcy_ = hx - ux * back, hy - uy * back
        d.polygon([tip, (bcx_ + vx * half_w, bcy_ + vy * half_w),
                   (bcx_ - vx * half_w, bcy_ - vy * half_w)], fill=color)

    _head(5, 10, 8, DARK)
    _head(3, 8, 5.5, YELLOW_A)
    # hop ve sau cung de che chan mui ten nam duoi hop
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=3, fill=BOX_FILL,
                        outline=YELLOW, width=2)
    low = _scale_layer(low, (box_cx_px / 6.0, box_cy_px / 6.0), scale)

    # ================= lop full-res: chi chu nhan =================
    hi = Image.new("RGBA", (HW, HH), (0, 0, 0, 0))
    if label:
        hd = ImageDraw.Draw(hi)
        bb = hd.textbbox((0, 0), label, font=font)
        glyph_h = bb[3] - bb[1]
        text_x = box_x0 + BOX_PAD_X
        text_y = box_y0 + (box_h - glyph_h) / 2.0 - bb[1]
        hd.text((text_x, text_y), label, font=font, fill=TEXT_COLOR)
    hi = _scale_layer(hi, (box_cx_px, box_cy_px), scale)

    return low, hi
