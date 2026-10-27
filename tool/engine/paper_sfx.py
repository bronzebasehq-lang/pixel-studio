#!/usr/bin/env python3
"""PAPER SFX - tieng hieu ung goi PAPER (giay & muc), tong hop bang ffmpeg.

  pop.wav    - note dan/bat vao (tieng "bop" giay ngan)
  draw.wav   - but chi keo tren giay (nhieu loc thong dai ngan)
  stamp.wav  - dong tem muc (thud mem + tieng giay)
  flip.wav   - lat trang (nhieu quet thap, mem)
  tick.wav   - tich vao o (click nhe)
  tape.wav   - xe bang dinh (nhieu dut quang)

File ra: <tool>/sfx-paper/. Goi ensure_sfx() de sinh khi thieu.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-paper")
SR = 48000


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("Sinh SFX loi:\n%s" % r.stderr[-800:])


def _gen_expr(name, expr, dur):
    out = os.path.join(SFX_DIR, name)
    if os.path.isfile(out):
        return out
    _run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
          "aevalsrc='%s':d=%.3f:s=%d" % (expr, dur, SR),
          "-ac", "1", "-ar", str(SR), out])
    return out


def _gen_noise(name, dur, af):
    out = os.path.join(SFX_DIR, name)
    if os.path.isfile(out):
        return out
    _run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
          "anoisesrc=d=%.3f:c=white:s=%d" % (dur, SR),
          "-af", af, "-ac", "1", "-ar", str(SR), out])
    return out


def ensure_sfx():
    os.makedirs(SFX_DIR, exist_ok=True)
    out = {}
    out["pop"] = _gen_expr(
        "pop.wav",
        "0.7*sin(2*PI*(380*t+1800*t*t))*exp(-30*t)"
        "+0.25*random(0)*exp(-60*t)", 0.09)
    out["draw"] = _gen_noise(
        "draw.wav", 0.22,
        "bandpass=f=2800:width_type=h:w=900,volume='0.5*sin(PI*t/0.22)':eval=frame")
    out["stamp"] = _gen_expr(
        "stamp.wav",
        "0.9*sin(2*PI*95*t)*exp(-16*t)+0.3*random(0)*exp(-45*t)", 0.22)
    out["flip"] = _gen_noise(
        "flip.wav", 0.32,
        "lowpass=f=1400,volume='0.7*sin(PI*t/0.32)':eval=frame")
    out["tick"] = _gen_expr(
        "tick.wav", "0.5*sin(2*PI*1900*t)*exp(-110*t)", 0.04)
    out["tape"] = _gen_expr(
        "tape.wav",
        "0.4*random(0)*(0.5+0.5*sin(2*PI*37*t))*exp(-9*t)", 0.26)
    return out


if __name__ == "__main__":
    for k, v in sorted(ensure_sfx().items()):
        print(k, "->", v)
