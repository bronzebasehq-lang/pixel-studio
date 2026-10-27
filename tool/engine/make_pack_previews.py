#!/usr/bin/env python3
"""Sinh GIF preview dong cho 3 goi moi -> previews/<tien-to>-<key>.gif.

Cung chuan voi make_test01_previews.py: 480x270, ~2s loop, 24 khung.
Chay tay: python3 engine/make_pack_previews.py [crt|paper|zine ...]
"""
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
sys.path.insert(0, ENGINE_DIR)

from PIL import Image  # noqa: E402

import crt_scenes  # noqa: E402
import paper_scenes  # noqa: E402
import zine_scenes  # noqa: E402

PREVIEW_DIR = os.path.join(TOOL_DIR, "previews")
PW, PH = 480, 270
N_FRAMES, GIF_FPS, DUR = 24, 12, 4.2

MODS = {"crt": (crt_scenes, "crt"), "paper": (paper_scenes, "paper"),
        "zine": (zine_scenes, "zine")}


def make_preview(mod, prefix, key):
    frames = []
    for i in range(N_FRAMES):
        tm = i / float(GIF_FPS)
        img = mod.draw_template(key, None, tm, DUR, "")
        frames.append(img.convert("RGB").resize((PW, PH), Image.NEAREST))
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    out = os.path.join(PREVIEW_DIR, "%s-%s.gif" % (prefix, key))
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=int(1000 / GIF_FPS), loop=0, optimize=True)
    return out


def main():
    wanted = sys.argv[1:] or list(MODS)
    for name in wanted:
        mod, prefix = MODS[name]
        if name == "zine":
            mod.set_shot_context(777)  # seed co dinh cho preview on dinh
        for key in mod.TEMPLATES:
            print("preview:", make_preview(mod, prefix, key))


if __name__ == "__main__":
    main()
