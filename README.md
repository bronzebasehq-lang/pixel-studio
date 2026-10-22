# Pixel Studio

A code-drawn explainer video tool with a **locked PIXEL 16-BIT style**.
Paste a script → pick a code-drawn animated scene per sentence → render.
No video-editing timeline, no stock footage — every frame is drawn by code.

Built for a faceless YouTube channel (new channel project, separate from the
[Fireship-style video tool](https://github.com/bronzebasehq-lang/video-tools)).

## Locked style spec

- Canvas: drawn on a **320×180 pixel grid**, upscaled with NEAREST
  (crisp square pixels, never blurred) to 1920×1080 @ 30fps.
- Palette: fixed dark indigo starfield, 2–3 tone shading + SNES-style dithering.
- Every scene template **must animate** (hard rule): nodes light up in
  sequence, the sphere grows, gears turn, blocks fall and stack, the route
  draws itself… plus shared effects (fade-in, pop, pulse, twinkling stars).
- Scene changes are hard cuts. No zoom-pan on still images.
- Voice: Kokoro `am_adam` via sherpa-onnx (local, Apache-2.0) — one fixed
  channel voice. Subtitles burned per sentence in the VT323 pixel font.

## Repo layout

| Folder | What it is |
|---|---|
| `tool/` | The working tool (v1): Python/PIL scene engine + local web UI (3 columns: script → per-sentence scene picker with animated GIF previews → render). Start with `tool/START-PIXEL.bat`; full beginner guide in `tool/HUONG-DAN.md` (Vietnamese). The Kokoro voice model (~350MB) auto-downloads from k2-fsa on first render into `tool/models/`. |
| `mockup/` | The approved UI mockup + the 8 scene-template keyframes the tool was built from (`SPEC.md` inside). |
| `samples/` | Style exploration: the 8-bit vs 16-bit comparison board (16-bit won) and `test-pixel-studio.mp4` — the first real render from the tool (3 sentences, 3 animated scenes, real `am_adam` voice, −16.6 LUFS). |

## The 8 scene templates (v1)

1. **Sphere swallows the scene** — growth, looming risk
2. **Balance scale A vs B** — comparisons, trade-offs
3. **Node network** — systems, connections, spread
4. **Timeline** — history, milestones
5. **Falling & stacking blocks** — accumulation over time
6. **Journey map** — step-by-step processes
7. **Working machine** (gears + conveyor) — how something works inside
8. **Person in scene** — a person affected by the tech (a scene element,
   never a fixed mascot)

## Status

v1 built and verified with a real test render (2026-10-22). In user testing.
Part of the [Bronze Base](https://cleantake.bronzebasehq.workers.dev) build-in-public journey toward $1M from products built solo with AI.
