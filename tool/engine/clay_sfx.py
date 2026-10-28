#!/usr/bin/env python3
"""CLAY SFX - tieng hieu ung goi DAT SET, tong hop bang ffmpeg.

  pop.wav    - cuc dat set roi/xuat hien (sine truot xuong + click)
  boing.wav  - nay squash (FM rung tan so, giong lo xo dat set)
  splat.wav  - con dau dap / nut bi ep (nhieu dap + thum thap)
  plip.wav   - blip ngan khi so nhay / dong phu xuat hien
  chime.wav  - 2 not chuong nhe o man cuoi

File ra: <tool>/sfx-clay/. Goi ensure_sfx() de sinh khi thieu.
Cung pattern voi crt_sfx.py.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-clay")
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
    out["pop"] = _gen(
        "pop.wav",
        "0.7*sin(2*PI*(330*t-1400*t*t))*exp(-26*t)"
        "+0.25*random(0)*exp(-160*t)", 0.11)
    out["boing"] = _gen(
        "boing.wav",
        "0.6*sin(2*PI*190*t+3.4*sin(2*PI*8.5*t)*exp(-4*t))*exp(-6.5*t)",
        0.34)
    out["splat"] = _gen(
        "splat.wav",
        "0.85*random(0)*exp(-38*t)+0.7*sin(2*PI*95*t)*exp(-20*t)", 0.16)
    out["plip"] = _gen(
        "plip.wav", "0.5*sin(2*PI*760*t)*exp(-46*t)", 0.06)
    out["chime"] = _gen(
        "chime.wav",
        "0.42*sin(2*PI*880*t)*exp(-7*t)"
        "+0.42*sin(2*PI*1318*(t-0.09))*exp(-7*(t-0.09))*gte(t,0.09)", 0.42)
    return out


if __name__ == "__main__":
    for k, v in sorted(ensure_sfx().items()):
        print(k, "->", v)
