#!/usr/bin/env python3
"""CRT SFX - tieng hieu ung goi CRT (terminal co), tong hop bang ffmpeg.

  type.wav   - go phim (click ngan, cao, kho nhu phim co)
  beep.wav   - beep he thong (song sine 990Hz ngan)
  beep_hi.wav- beep xac nhan cao hon (1320Hz)
  tick.wav   - dem/nhay o (sine 1500Hz rat ngan)
  alarm.wav  - canh bao (2 xung vuong 620Hz)
  enter.wav  - phim Enter (thud + beep xac nhan)
  hum.wav    - tieng quat/um dien thap 1.2s (lap lam nen rat nhe)
  scan.wav   - quet giai ma (sine quet len 300->1800Hz)

File ra: <tool>/sfx-crt/. Goi ensure_sfx() de sinh khi thieu.
Cung pattern voi test01_sfx.py.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-crt")
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
    out["type"] = _gen(
        "type.wav",
        "0.5*random(0)*exp(-120*t)+0.3*sin(2*PI*2600*t)*exp(-160*t)", 0.045)
    out["beep"] = _gen(
        "beep.wav", "0.55*sin(2*PI*990*t)*lt(t,0.07)", 0.09)
    out["beep_hi"] = _gen(
        "beep_hi.wav", "0.55*sin(2*PI*1320*t)*lt(t,0.06)", 0.08)
    out["tick"] = _gen(
        "tick.wav", "0.5*sin(2*PI*1500*t)*exp(-120*t)", 0.04)
    out["alarm"] = _gen(
        "alarm.wav",
        "0.5*(sin(2*PI*620*t)+0.3*sin(2*PI*1240*t))"
        "*(lt(mod(t,0.16),0.08))", 0.34)
    out["enter"] = _gen(
        "enter.wav",
        "0.8*sin(2*PI*140*t)*exp(-22*t)"
        "+0.45*sin(2*PI*1560*(t-0.05))*exp(-50*(t-0.05))*gte(t,0.05)", 0.14)
    out["hum"] = _gen(
        "hum.wav",
        "0.16*sin(2*PI*55*t)+0.08*sin(2*PI*110*t)+0.05*sin(2*PI*165*t)",
        1.2)
    out["scan"] = _gen(
        "scan.wav",
        "0.4*sin(2*PI*(300*t+2600*t*t))*exp(-2.5*t)", 0.5)
    return out


if __name__ == "__main__":
    for k, v in sorted(ensure_sfx().items()):
        print(k, "->", v)
