#!/usr/bin/env python3
"""
PIXEL STUDIO - pipeline render video:
  kich ban -> cat cau -> giong am_adam tung cau -> ve frame pixel theo
  thoi luong giong that -> ffmpeg tung doan -> ghep (hard cut) ->
  tron nhac nen (neu co) -> loudnorm -15 LUFS -> Videos/video-<ngay-gio>.mp4

Chay doc lap:
  python3 render.py --script "Cau mot. Cau hai." --scenes 1,8
  python3 render.py --script-file kichban.txt --scenes 3,3,5 --music nhac.mp3
"""
import argparse
import datetime
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
sys.path.insert(0, ENGINE_DIR)

# ffmpeg.exe dat ngay trong thu muc tool thi tu them vao PATH
if os.path.isfile(os.path.join(TOOL_DIR, "ffmpeg.exe")):
    os.environ["PATH"] = TOOL_DIR + os.pathsep + os.environ.get("PATH", "")

from PIL import Image, ImageDraw  # noqa: E402

import annotate as annot_mod  # noqa: E402
import packs as packs_mod  # noqa: E402
import painter as painter_mod  # noqa: E402
import scenes as scenes_mod  # noqa: E402
import style2_scenes as s2s_mod  # noqa: E402
import test01_scenes as t1s_mod  # noqa: E402
import subtitles as sub_mod  # noqa: E402
import voice as voice_mod  # noqa: E402

FPS = 30
OUT_W, OUT_H = 1920, 1080
VERT_W, VERT_H = 1080, 1920   # dinh dang doc 9:16 (Shorts) - V2.3
LEAD = 0.15    # giay im lang truoc khi giong bat dau trong moi canh
TAIL = 0.25    # giay duoi sau khi giong ket thuc

# Sao cho nen doc: sinh 1 lan, co dinh (seed) de cac frame lien nhau on dinh
_rng_v = random.Random(99)
_VSTARS = [(_rng_v.uniform(0.01, 0.99), _rng_v.uniform(0.01, 0.82),
            _rng_v.random(), _rng_v.uniform(0, 6.28)) for _ in range(150)]


def _out_size(fmt):
    return (VERT_W, VERT_H) if fmt == "9:16" else (OUT_W, OUT_H)


def _vertical_bg(tm):
    """Nen doc 1080x1920: troi sao + dat ve phu KIN khung (khong den tran).

    Ve o luoi thap 180x320 (dung bang mau khoa cua painter) roi phong
    NEAREST - cung chat pixel 16-bit nhu nen ngang."""
    pal = painter_mod.PAL
    lw, lh = 180, 320
    low = Image.new("RGB", (lw, lh), pal["sky"])
    dr = ImageDraw.Draw(low)
    bands = [(0.0, 0.30, pal["sky_top"]), (0.30, 0.58, pal["sky"]),
             (0.58, 0.85, pal["sky_low"]), (0.85, 1.0, pal["ground"])]
    for y0f, y1f, c in bands:
        dr.rectangle([0, int(y0f * lh), lw, int(y1f * lh)], fill=c)
    gy = int(0.85 * lh)
    dr.rectangle([0, gy, lw, gy + 2], fill=pal["ground_hi"])
    for (fx, fy, b, ph) in _VSTARS:
        v = b * (0.68 + 0.32 * math.sin(tm * 2.1 + ph))
        c = pal["star"] if v > 0.42 else pal["star_dim"]
        s = 2 if v > 0.80 else 1
        gx, gy2 = int(fx * lw), int(fy * lh)
        dr.rectangle([gx, gy2, gx + s - 1, gy2 + s - 1], fill=c)
    return low.resize((VERT_W, VERT_H), Image.NEAREST)


def split_script(text):
    """Cat kich ban thanh tung cau (giu nguyen 'R.A.G.' vi khong co khoang trang)."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p and p.strip()]


def _run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError("Loi chay %s:\n%s" % (cmd[0], (r.stderr or "")[-1500:]))
    return r


def _load_bg(bg_path):
    """Tai anh nen lai cua 1 shot -> pixel hoa ve luoi 320x180."""
    raw = Image.open(bg_path).convert("RGB")
    return raw.resize((painter_mod.GW, painter_mod.GH), Image.LANCZOS)


def _render_segment(seg_idx, text, scene_id, wav_path, seg_dur, work_dir,
                    progress=None, total_frames=1, frames_done=0,
                    params=None, annotation=None, bg_img=None,
                    fmt="16:9", template=None):
    """Ve frame cua 1 canh, pipe thang vao ffmpeg kem tieng. Tra ve file mp4.
    V2: params = du kien tham so hoa canh; annotation = mui ten chu thich
    {label, target}; bg_img = anh nen lai (PIL 320x180) thay canh code.
    V2.3: fmt = "16:9" | "9:16" (doc: nen sao phu kin khung 1080x1920,
    noi dung ngang dat giua khung, KHONG keo gian); template = dict
    {name, tparams, typed, popup} -> shot ve bang template style2."""
    seg_path = os.path.join(work_dir, "seg-%02d.mp4" % seg_idx)
    n_frames = max(1, int(round(seg_dur * FPS)))
    out_w, out_h = _out_size(fmt)
    vertical = (fmt == "9:16")
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "%dx%d" % (out_w, out_h), "-r", str(FPS), "-i", "pipe:",
        "-i", wav_path,
        "-filter_complex",
        "[1:a]adelay=%d|%d,apad,atrim=0:%.3f[a]" % (int(LEAD * 1000),
                                                    int(LEAD * 1000), seg_dur),
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
        "-t", "%.3f" % seg_dur, seg_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for i in range(n_frames):
            tm = i / FPS
            t = i / (n_frames - 1) if n_frames > 1 else 1.0
            if template is not None:
                mod = (packs_mod.module_for(template.get("pack"))
                       or s2s_mod)
                frame = mod.draw_template(
                    template["name"], template.get("tparams"),
                    tm, seg_dur, text, template.get("typed"),
                    template.get("popup")).convert("RGB")
            elif bg_img is not None:
                frame = bg_img.copy()
            else:
                frame = scenes_mod.draw_scene(scene_id, t, tm, params)
            # mui ten chu thich: hinh ve o luoi thap (pop-in), chu o full-res
            hi_layer = None
            if annotation:
                a_scale = annot_mod.pop_scale(tm)
                if a_scale is not None:
                    low_layer, hi_layer = annot_mod.annotation_layers(
                        annotation["label"],
                        int(annotation.get("target", 4)), a_scale)
                    base = frame.convert("RGBA")
                    if frame.size == low_layer.size:
                        base.alpha_composite(low_layer)
                    else:
                        base.alpha_composite(low_layer.resize(
                            (OUT_W, OUT_H), Image.NEAREST))
                    frame = base.convert("RGB")
            if frame.size != (OUT_W, OUT_H):
                frame = frame.resize((OUT_W, OUT_H), Image.NEAREST)
            if hi_layer is not None:
                base = frame.convert("RGBA")
                base.alpha_composite(hi_layer)
                frame = base.convert("RGB")
            if vertical:
                # nen sao phu kin khung doc; noi dung ngang phong theo
                # chieu ngang 1080 (cao 607) dat giua khung - khong meo
                canvas = _vertical_bg(tm)
                band_h = int(VERT_W * 9 / 16)
                canvas.paste(frame.resize((VERT_W, band_h), Image.NEAREST),
                             (0, (VERT_H - band_h) // 2))
                frame = canvas
            # Shot template co CHU CHAY bat thi chu chay dong vai phu de
            # (dung ban Nokia goc) - khong ve them phu de tinh trung lap.
            if not (template is not None
                    and s2s_mod.typed_enabled(template.get("typed"))):
                frame = sub_mod.draw_subtitle(frame, text)
            # HARD CUT 100% giua cac canh (chuan khoa cua kenh) - KHONG fade.
            # Ban cu co fade-in 0.35s + fade-out 0.25s moi doan -> video dai
            # nhap nhay lien tuc; Minh phat hien 22/10, da go bo.
            proc.stdin.write(frame.tobytes())
            if progress and (i % 15 == 0):
                progress((frames_done + i) / float(total_frames))
    finally:
        proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace")
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg doan %d loi:\n%s" % (seg_idx, err[-1500:]))
    return seg_path


def render_job(sentences, music_path=None, out_path=None, progress=None,
               log=print, fmt="16:9"):
    """sentences: [{'text':..., 'scene': 1..8}] hoac cau template style2
    {'text':..., 'template': <key>, 'tparams': {...}, 'typed': {...},
    'popup': {...}} -> tra ve duong dan video.
    fmt: "16:9" (1920x1080) hoac "9:16" (1080x1920, cho Shorts)."""
    if fmt not in ("16:9", "9:16"):
        fmt = "16:9"
    tempfile.tempdir = os.path.join(TOOL_DIR, "work")
    os.makedirs(tempfile.tempdir, exist_ok=True)
    work_dir = tempfile.mkdtemp(prefix="job-", dir=tempfile.tempdir)
    log("[render] Thu muc tam: %s" % work_dir)

    # 1) giong doc tung cau -> thoi luong canh = thoi luong giong that
    job_seed = packs_mod.job_seed_of(
        [str(s.get("text", "")) for s in sentences])
    segs = []
    total_dur = 0.0
    for i, s in enumerate(sentences):
        wav = os.path.join(work_dir, "voice-%02d.wav" % i)
        dur = voice_mod.synthesize(s["text"], wav)
        seg_dur = dur + LEAD + TAIL
        annotation = s.get("annotation") or None
        if annotation is not None and not str(
                annotation.get("label", "")).strip():
            annotation = None
        bg_img = _load_bg(s["bg"]) if s.get("bg") else None
        tpl = s.get("template") or None
        tpl_info = None
        if tpl:
            pack = packs_mod.normalize_pack(s.get("tpack"))
            mod = packs_mod.module_for(pack)
            if mod is None or str(tpl) not in mod.TEMPLATES:
                # payload cu/thieu tpack: suy ra goi tu template id
                pack, mod = None, None
                for cand in ("stage", "style2", "crt", "paper", "zine"):
                    m2 = packs_mod.module_for(cand)
                    if m2 is not None and str(tpl) in m2.TEMPLATES:
                        pack, mod = cand, m2
                        break
            if mod is not None and str(tpl) in mod.TEMPLATES:
                params = dict(s.get("tparams") or {})
                layout = None
                if pack in packs_mod.VARIANT_PACKS:
                    layout, layout_src = packs_mod.resolve_layout(
                        pack, str(tpl), params, i, job_seed)
                    params["layout"] = str(layout + 1)
                tpl_info = {"name": str(tpl), "pack": pack,
                            "tparams": params,
                            "typed": s.get("typed"), "popup": s.get("popup"),
                            "layout": layout,
                            "layout_src": (layout_src
                                           if layout is not None else None)}
                log("[tpl] Cau %d -> %s:%s%s" % (
                    i + 1, pack, tpl,
                    (" (bien the %d, %s)" % (layout + 1, layout_src))
                    if layout is not None else ""))
            else:
                log("[tpl] Bo qua template khong biet: %s" % tpl)
        segs.append({"text": s["text"],
                     "scene": int(s.get("scene") or 0),
                     "wav": wav, "dur": seg_dur,
                     "params": s.get("params") or None,
                     "annotation": annotation, "bg_img": bg_img,
                     "template": tpl_info})
        total_dur += seg_dur
        log("[render] Cau %d/%d: giong %.2fs -> canh %.2fs (mau %s)"
            % (i + 1, len(sentences), dur, seg_dur,
               ("%s:%s" % (tpl_info["pack"], tpl)) if tpl_info
               else int(s.get("scene") or 0)))
    total_frames = max(1, int(round(total_dur * FPS)))

    # 1b) BO QUET NHIP + QUET TRUNG KHUON: chay cho MOI goi.
    # - Quet nhip: doan >5s khong co bien co hinh anh thi canh bao.
    #   Canh template dung events_for cua goi; canh khong template
    #   (pixel/style2) dong gop nhip 2.5s/lan (ve lai theo chu ky canh)
    #   de khong bao dong gia.
    # - Quet trung: chi ap cho 4 goi co lop bien the (stage/crt/
    #   paper/zine): mau dung >2 lan hoac 1 bien the lap >3 lan.
    _shots = []
    _dup_shots = []
    for sg in segs:
        tp = sg["template"]
        if tp and tp.get("pack") in packs_mod.VARIANT_PACKS:
            mod = packs_mod.module_for(tp["pack"])
            _shots.append({
                "name": "%s:%s" % (tp["pack"], tp["name"]),
                "dur": sg["dur"],
                "events": mod.events_for(tp["name"], tp.get("tparams"),
                                          sg["dur"])})
            _dup_shots.append({"pack": tp["pack"], "name": tp["name"],
                               "layout": tp.get("layout")})
        else:
            _ev = [(0.0, "start")]
            _tt = 2.5
            while _tt < sg["dur"]:
                _ev.append((_tt, "beat"))
                _tt += 2.5
            _shots.append({
                "name": (("%s:%s" % (tp["pack"], tp["name"]))
                         if tp else "scene %s" % sg["scene"]),
                "dur": sg["dur"], "events": _ev})
    _pw = packs_mod.scan_pacing(_shots)
    for w in _pw:
        log("[nhip] CANH BAO: %s" % w)
    if not _pw:
        log("[nhip] Quet nhip: DAT - khong doan nao >5s thieu bien co.")
    _dw = packs_mod.scan_duplicates(_dup_shots)
    for w in _dw:
        log("[trung] CANH BAO TRUNG KHUON: %s" % w)
    if _dup_shots and not _dw:
        log("[trung] Quet trung khuon: DAT - khong mau/bien the nao "
            "lap qua nguong.")

    # 2) render tung doan
    seg_files = []
    done = 0
    for i, sg in enumerate(segs):
        if sg["template"] and sg["template"].get("pack") == "zine":
            # goi ZINE xao o theo seed cua shot (tai lap theo job)
            packs_mod.module_for("zine").set_shot_context(
                job_seed + i * 1000003)
        seg_files.append(_render_segment(
            i, sg["text"], sg["scene"], sg["wav"], sg["dur"], work_dir,
            progress, total_frames, done, params=sg["params"],
            annotation=sg["annotation"], bg_img=sg["bg_img"],
            fmt=fmt, template=sg["template"]))
        done += int(round(sg["dur"] * FPS))

    # 3) ghep cac doan (hard cut, cung tham so nen copy thang)
    list_file = os.path.join(work_dir, "concat.txt")
    with open(list_file, "w") as f:
        for sf_ in seg_files:
            f.write("file '%s'\n" % sf_)
    merged = os.path.join(work_dir, "merged.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
          "-c", "copy", merged])

    # 4) nhac nen (neu co) + loudnorm ve -15 LUFS
    if not out_path:
        stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
        out_path = os.path.join(TOOL_DIR, "Videos", "video-%s.mp4" % stamp)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if music_path:
        af = ("[1:a]aloop=loop=-1:size=2147483647,volume=0.34[m];"
              "[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,"
              "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[a]")
        _run(["ffmpeg", "-y", "-i", merged, "-i", music_path,
              "-filter_complex", af, "-map", "0:v", "-map", "[a]",
              "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
              "-ar", "48000", out_path])
    else:
        _run(["ffmpeg", "-y", "-i", merged,
              "-af", "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000",
              "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
              "-ar", "48000", out_path])
    if progress:
        progress(1.0)
    log("[render] XONG: %s" % out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Pixel Studio render")
    ap.add_argument("--script", default=None)
    ap.add_argument("--script-file", default=None)
    ap.add_argument("--scenes", default=None,
                    help="Danh sach mau canh, cach nhau dau phay, vd: 1,8,3")
    ap.add_argument("--music", default=None)
    ap.add_argument("--format", default="16:9", choices=["16:9", "9:16"],
                    help="16:9 ngang (mac dinh) hoac 9:16 doc cho Shorts")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    text = a.script
    if a.script_file:
        with open(a.script_file, encoding="utf-8") as f:
            text = f.read()
    if not text:
        ap.error("Can --script hoac --script-file")
    sents = split_script(text)
    scene_ids = ([int(x) for x in a.scenes.split(",")]
                 if a.scenes else [1] * len(sents))
    if len(scene_ids) < len(sents):
        scene_ids += [scene_ids[-1]] * (len(sents) - len(scene_ids))
    job = [{"text": s, "scene": scene_ids[i]} for i, s in enumerate(sents)]
    out = render_job(job, music_path=a.music, out_path=a.out, fmt=a.format,
                     progress=lambda k: print("[render] %.0f%%" % (k * 100)))
    print(json.dumps({"video": out}))


if __name__ == "__main__":
    main()
