#!/usr/bin/env python3
"""TEST01 SFX - thu vien tieng hieu ung tong hop bang ffmpeg (khong co san).

Project chua co thu vien SFX nen cac tieng duoc TONG HOP tu song sine/
nhieu trang bang bieu thuc aevalsrc cua ffmpeg (48kHz, mono, 16-bit):
  pop.wav       - chu bat vao (sine quet len + tat nhanh)
  stamp.wav     - dong dau (tram 110Hz + click nhieu)
  type.wav      - go phim (click ngan cao)
  tick.wav      - dem mac dinh
  tick_rise_N.wav (N=0..10) - chuoi tick len tong dan cho bo dem
  glitch.wav    - nut tach mau (nhieu dut doan)
  click.wav     - bam nut (2 not xac nhan)
  whoosh.wav    - chuyen canh (nhieu hong quet dai)

File ra: <tool>/sfx-test01/. Goi ensure_sfx() de sinh khi thieu.
"""
import os
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(TOOL_DIR, "sfx-test01")
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
    """Sinh du bo tieng (neu chua co). Tra dict ten -> duong dan."""
    os.makedirs(SFX_DIR, exist_ok=True)
    out = {}
    out["pop"] = _gen(
        "pop.wav",
        "0.85*sin(2*PI*(520*t+2600*t*t))*exp(-26*t)", 0.10)
    out["stamp"] = _gen(
        "stamp.wav",
        "0.95*sin(2*PI*110*t)*exp(-15*t)+0.35*random(0)*exp(-70*t)", 0.24)
    out["type"] = _gen(
        "type.wav", "0.45*sin(2*PI*2300*t)*exp(-150*t)", 0.035)
    out["tick"] = _gen(
        "tick.wav", "0.6*sin(2*PI*1150*t)*exp(-95*t)", 0.05)
    out["glitch"] = _gen(
        "glitch.wav",
        "0.55*random(0)*exp(-7*t)*(0.6+0.4*sin(2*PI*95*t))", 0.18)
    out["click"] = _gen(
        "click.wav",
        "0.75*sin(2*PI*1560*t)*exp(-42*t)"
        "+0.55*sin(2*PI*2093*(t-0.055))*exp(-42*(t-0.055))*gte(t,0.055)",
        0.16)
    # whoosh: nhieu hong + phong bao sin theo thoi gian
    whoosh = os.path.join(SFX_DIR, "whoosh.wav")
    if not os.path.isfile(whoosh):
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
               "anoisesrc=d=0.28:c=pink:s=%d" % SR,
               "-af", "highpass=f=500,lowpass=f=3200,"
                      "volume='0.8*sin(PI*t/0.28)':eval=frame",
               "-ac", "1", "-ar", str(SR), whoosh]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("Sinh whoosh loi:\n%s" % r.stderr[-800:])
    out["whoosh"] = whoosh
    freqs = [660, 740, 830, 930, 1040, 1170, 1310, 1470, 1650, 1850, 2080]
    for i, f in enumerate(freqs):
        out["tick_rise_%d" % i] = _gen(
            "tick_rise_%d.wav" % i,
            "0.6*sin(2*PI*%d*t)*exp(-95*t)" % f, 0.05)
    return out


if __name__ == "__main__":
    paths = ensure_sfx()
    for k, v in sorted(paths.items()):
        print(k, "->", v)
