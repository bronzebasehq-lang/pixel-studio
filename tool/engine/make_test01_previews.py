#!/usr/bin/env python3
"""Sinh GIF preview dong cho 11 mau test01 -> previews/test01-<key>.gif.

Cung chuan voi previews.py cua canh code: 480x270, ~2s loop.
Chay tay: python3 engine/make_test01_previews.py
"""
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
sys.path.insert(0, ENGINE_DIR)

from PIL import Image  # noqa: E402

import test01_scenes as t1s  # noqa: E402

PREVIEW_DIR = os.path.join(TOOL_DIR, "previews")
PW, PH = 480, 270
N_FRAMES, GIF_FPS, DUR = 24, 12, 4.2


def make_preview(key):
    frames = []
    for i in range(N_FRAMES):
        tm = i / float(GIF_FPS)
        img = t1s.draw_template(key, None, tm, DUR, "")
        frames.append(img.convert("RGB").resize((PW, PH), Image.NEAREST))
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    out = os.path.join(PREVIEW_DIR, "test01-%s.gif" % key)
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=int(1000 / GIF_FPS), loop=0, optimize=True)
    return out


def main():
    for key in t1s.TEMPLATES:
        print("preview:", make_preview(key))


if __name__ == "__main__":
    main()
