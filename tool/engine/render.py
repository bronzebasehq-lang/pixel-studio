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
import os
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

from PIL import Image  # noqa: E402

import annotate as annot_mod  # noqa: E402
import painter as painter_mod  # noqa: E402
import scenes as scenes_mod  # noqa: E402
import subtitles as sub_mod  # noqa: E402
import voice as voice_mod  # noqa: E402

FPS = 30
OUT_W, OUT_H = 1920, 1080
LEAD = 0.15    # giay im lang truoc khi giong bat dau trong moi canh
TAIL = 0.25    # giay duoi sau khi giong ket thuc


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
                    params=None, annotation=None, bg_img=None):
    """Ve frame cua 1 canh, pipe thang vao ffmpeg kem tieng. Tra ve file mp4.
    V2: params = du kien tham so hoa canh; annotation = mui ten chu thich
    {label, target}; bg_img = anh nen lai (PIL 320x180) thay canh code."""
    seg_path = os.path.join(work_dir, "seg-%02d.mp4" % seg_idx)
    n_frames = max(1, int(round(seg_dur * FPS)))
    black = Image.new("RGB", (OUT_W, OUT_H), (0, 0, 0))
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "%dx%d" % (OUT_W, OUT_H), "-r", str(FPS), "-i", "pipe:",
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
            if bg_img is not None:
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
                    base.alpha_composite(low_layer)
                    frame = base.convert("RGB")
            frame = frame.resize((OUT_W, OUT_H), Image.NEAREST)
            if hi_layer is not None:
                base = frame.convert("RGBA")
                base.alpha_composite(hi_layer)
                frame = base.convert("RGB")
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
               log=print):
    """sentences: [{'text':..., 'scene': 1..8}] -> tra ve duong dan video."""
    tempfile.tempdir = os.path.join(TOOL_DIR, "work")
    os.makedirs(tempfile.tempdir, exist_ok=True)
    work_dir = tempfile.mkdtemp(prefix="job-", dir=tempfile.tempdir)
    log("[render] Thu muc tam: %s" % work_dir)

    # 1) giong doc tung cau -> thoi luong canh = thoi luong giong that
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
        segs.append({"text": s["text"], "scene": int(s["scene"]),
                     "wav": wav, "dur": seg_dur,
                     "params": s.get("params") or None,
                     "annotation": annotation, "bg_img": bg_img})
        total_dur += seg_dur
        log("[render] Cau %d/%d: giong %.2fs -> canh %.2fs (mau %d)"
            % (i + 1, len(sentences), dur, seg_dur, int(s["scene"])))
    total_frames = max(1, int(round(total_dur * FPS)))

    # 2) render tung doan
    seg_files = []
    done = 0
    for i, sg in enumerate(segs):
        seg_files.append(_render_segment(
            i, sg["text"], sg["scene"], sg["wav"], sg["dur"], work_dir,
            progress, total_frames, done, params=sg["params"],
            annotation=sg["annotation"], bg_img=sg["bg_img"]))
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
    out = render_job(job, music_path=a.music, out_path=a.out,
                     progress=lambda k: print("[render] %.0f%%" % (k * 100)))
    print(json.dumps({"video": out}))


if __name__ == "__main__":
    main()
