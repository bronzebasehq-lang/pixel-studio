#!/usr/bin/env python3
"""
PIXEL VIDEO - sinh GIF preview DONG (~2 giay, loop) cho tung mau canh.
File ra: <tool>/previews/scene-0X.gif (480x270, 15fps x 30 frame).
Server tu goi khi file chua co.
"""
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
sys.path.insert(0, ENGINE_DIR)

from PIL import Image  # noqa: E402

import scenes as scenes_mod  # noqa: E402

PREVIEW_DIR = os.path.join(TOOL_DIR, "previews")
PW, PH = 480, 270
N_FRAMES, GIF_FPS = 30, 15


def preview_path(scene_id):
    return os.path.join(PREVIEW_DIR, "scene-%02d.gif" % int(scene_id))


def make_preview(scene_id):
    frames = []
    for i in range(N_FRAMES):
        tm = i / float(GIF_FPS)
        t = i / float(N_FRAMES - 1)
        img = scenes_mod.draw_scene(scene_id, t, tm)
        frames.append(img.resize((PW, PH), Image.NEAREST))
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    out = preview_path(scene_id)
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=int(1000 / GIF_FPS), loop=0, optimize=True)
    return out


def ensure_previews(log=print):
    for sid in scenes_mod.SCENES:
        if not os.path.isfile(preview_path(sid)):
            log("[preview] Sinh GIF mau %d..." % sid)
            make_preview(sid)
    return PREVIEW_DIR


if __name__ == "__main__":
    ensure_previews()
    print("previews ->", PREVIEW_DIR)
