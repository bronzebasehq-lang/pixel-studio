#!/usr/bin/env python3
"""
PIXEL VIDEO - phu de chay theo cau o day khung (font pixel VT323).
Khung day an toan: khoi phu de ket thuc o 85% chieu cao (cach day 15%).
"""
import os

from PIL import Image, ImageDraw, ImageFont

FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "fonts")
FVT = os.path.join(FONTS, "VT323.ttf")

_font_cache = {}


def _font(size):
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FVT, size)
    return _font_cache[size]


def _wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines[:3]


def draw_subtitle(img, text):
    """Ve phu de len frame full-res (PIL Image RGB) — sua truc tiep + tra img."""
    if not text or not text.strip():
        return img
    W, H = img.size
    size = max(30, int(H * 0.052))          # ~56px o 1080p
    font = _font(size)
    probe = ImageDraw.Draw(img)
    lines = _wrap(probe, text.strip(), font, int(W * 0.84))
    line_h = int(size * 0.92)
    block_h = line_h * len(lines) + int(H * 0.018)
    bottom = int(H * 0.85)                   # an toan 15% day
    top = bottom - block_h
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, top - int(H * 0.006), W, bottom + int(H * 0.006)],
                 fill=(4, 4, 10, 168))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    y = top + int(H * 0.009)
    for ln in lines:
        w = d.textlength(ln, font=font)
        d.text(((W - w) / 2 + 2, y + 2), ln, font=font, fill=(0, 0, 0))
        d.text(((W - w) / 2, y), ln, font=font, fill=(245, 246, 252))
        y += line_h
    return img
