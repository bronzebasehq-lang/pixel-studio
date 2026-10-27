#!/usr/bin/env python3
"""Kiểm chứng v2: (1) tự gán 3 câu mẫu SPEC; (2) render video test full tính năng."""
import json, sys
sys.path.insert(0, "engine")
import autosuggest

SENTS = [
    "It grew 300% in just 3 years.",
    "ChatGPT vs Claude: which one wins?",
    "First, connect the tools. Then the system runs itself.",
]
print("=== TU GAN CANH ===")
results = []
for s in SENTS:
    r = autosuggest.analyze(s)
    results.append(r)
    print(json.dumps(r, ensure_ascii=False))

print("=== RENDER TEST ===")
import render as render_mod
job = []
for s, r in zip(SENTS, results):
    job.append({"text": s, "scene": r["scene"], "params": r.get("params")})
job[0]["annotation"] = {"label": "300% GROWTH", "target": 8}  # đích: lưới 3x3, ô giữa-dưới
out = render_mod.render_job(job, music_path="music/01-empire-rising.mp3",
                            out_path="Videos/verify-v2-test.mp4")
print("VIDEO:", out)
