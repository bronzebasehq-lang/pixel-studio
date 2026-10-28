#!/usr/bin/env python3
"""SHOW SFX - tieng hieu ung goi SHOW (gameshow TV), tong hop ffmpeg.

  tick.wav    - vong quay tach tach / den bat (click cao ngan)
  bell.wav    - chuong "dung" (sine 1320 + hoa am, tan dan dai)
  buzz.wav    - coi "sai" (song vuong 140Hz)
  fanfare.wav - keo thang giai: 4 not sine thang dan 660/880/990/1320
  sparkle.wav - lap lanh bien marquee (arp sine cao rat nhanh)

File ra: <tool>/sfx-show/. Goi ensure_sfx() de sinh khi thieu.
Cung pattern voi crt_sfx.py.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-show")
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
    out["tick"] = _gen(
        "tick.wav", "0.55*sin(2*PI*2100*t)*exp(-170*t)", 0.04)
    out["bell"] = _gen(
        "bell.wav",
        "0.5*sin(2*PI*1320*t)*exp(-6*t)+0.25*sin(2*PI*1980*t)*exp(-8*t)"
        "+0.15*sin(2*PI*2640*t)*exp(-10*t)", 0.5)
    out["buzz"] = _gen(
        "buzz.wav",
        "0.42*sgn(sin(2*PI*140*t))*(0.7+0.3*sin(2*PI*30*t))*lt(t,0.32)",
        0.36)
    out["fanfare"] = _gen(
        "fanfare.wav",
        "0.4*sin(2*PI*660*t)*exp(-9*t)"
        "+0.4*sin(2*PI*880*(t-0.11))*exp(-9*(t-0.11))*gte(t,0.11)"
        "+0.4*sin(2*PI*990*(t-0.22))*exp(-9*(t-0.22))*gte(t,0.22)"
        "+0.5*sin(2*PI*1320*(t-0.33))*exp(-5*(t-0.33))*gte(t,0.33)", 0.75)
    out["sparkle"] = _gen(
        "sparkle.wav",
        "0.35*sin(2*PI*2640*t)*exp(-16*t)"
        "+0.35*sin(2*PI*3520*(t-0.05))*exp(-16*(t-0.05))*gte(t,0.05)", 0.2)
    return out


if __name__ == "__main__":
    for k, v in sorted(ensure_sfx().items()):
        print(k, "->", v)
