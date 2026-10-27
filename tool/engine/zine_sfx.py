#!/usr/bin/env python3
"""ZINE SFX - tieng hieu ung goi ZINE (cat dan), tong hop bang ffmpeg.

  paste.wav - o giay dan xuong (vo tay giay: nhieu thap + thud)
  tear.wav  - xe giay (nhieu rang cua dut quang)
  pin.wav   - ghim dinh (click kim loai rat ngan, cao)
  pop.wav   - muc nho bat vao
  stamp.wav - tem nhan gia dong xuong (thud + vang giay)

File ra: <tool>/sfx-zine/. Goi ensure_sfx() de sinh khi thieu.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-zine")
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
    out["paste"] = _gen_expr(
        "paste.wav",
        "0.5*random(0)*exp(-40*t)+0.8*sin(2*PI*120*t)*exp(-20*t)", 0.13)
    out["tear"] = _gen_expr(
        "tear.wav",
        "0.45*random(0)*(0.4+0.6*abs(sin(2*PI*23*t)))*exp(-4*t)", 0.38)
    out["pin"] = _gen_expr(
        "pin.wav",
        "0.6*sin(2*PI*3400*t)*exp(-180*t)+0.3*random(0)*exp(-90*t)", 0.04)
    out["pop"] = _gen_expr(
        "pop.wav", "0.7*sin(2*PI*(420*t+2000*t*t))*exp(-28*t)", 0.09)
    out["stamp"] = _gen_expr(
        "stamp.wav",
        "0.9*sin(2*PI*105*t)*exp(-15*t)+0.35*random(0)*exp(-55*t)", 0.2)
    return out


if __name__ == "__main__":
    for k, v in sorted(ensure_sfx().items()):
        print(k, "->", v)
