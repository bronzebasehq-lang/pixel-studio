#!/usr/bin/env python3
"""FLAT SFX - tieng hieu ung goi FLAT, tong hop bang ffmpeg.

Am thanh sach, toi gian, "kho" kieu UI hien dai:
  click.wav - click giao dien (sine cao rat ngan)
  pop.wav   - khoi phang pop-in (sine truot xuong ngan)
  swipe.wav - hang truot vao (nhieu hong quet ngan)
  ding.wav  - xac nhan (sine 1560Hz tan dan)

File ra: <tool>/sfx-flat/. Goi ensure_sfx() de sinh khi thieu.
Cung pattern voi crt_sfx.py.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-flat")
SR = 48000


def _gen(name, expr, dur):
    out = os.path.join(SFX_DIR, name)
    if os.path.isfile(out):
        return out
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "lavfi", "-i",
           "aevalsrc='%s':d=%.3f:s=%d" % (expr, dur, SR),
           "-ac", "1", "-ar", str(SR), out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("Sinh SFX %s loi:\n%s" % (name, r.stderr[-800:]))
    return out


def ensure_sfx():
    os.makedirs(SFX_DIR, exist_ok=True)
    out = {}
    out["click"] = _gen(
        "click.wav", "0.5*sin(2*PI*1900*t)*exp(-180*t)", 0.035)
    out["pop"] = _gen(
        "pop.wav", "0.6*sin(2*PI*(520*t-2600*t*t))*exp(-30*t)", 0.09)
    out["swipe"] = _gen(
        "swipe.wav", "0.30*random(0)*sin(PI*t/0.13)*exp(-9*t)", 0.13)
    out["ding"] = _gen(
        "ding.wav",
        "0.5*sin(2*PI*1560*t)*exp(-11*t)+0.22*sin(2*PI*2340*t)*exp(-14*t)",
        0.28)
    return out


if __name__ == "__main__":
    for k, v in sorted(ensure_sfx().items()):
        print(k, "->", v)
