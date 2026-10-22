#!/usr/bin/env python3
"""
PIXEL STUDIO - giong doc Kokoro 'am_adam' (sid 5) qua sherpa-onnx, chay local.

- Neu sherpa_onnx import duoc trong python hien tai -> sinh truc tiep.
- Neu khong -> goi tts_worker.py bang 1 python khac co sherpa_onnx
  (bien moi truong PIXEL_TTS_PYTHON, hoac venv trong thu muc tool).
- Model nam o <tool>/models/kokoro-en-v0_19. Thieu -> tu tai tu nguon
  chinh thuc k2-fsa (GitHub releases cua sherpa-onnx) va giai nen.
"""
import io
import json
import os
import subprocess
import sys
import tarfile
import urllib.request
import wave

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(ENGINE_DIR)
MODEL_DIR = os.path.join(TOOL_DIR, "models", "kokoro-en-v0_19")
MODEL_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
             "tts-models/kokoro-en-v0_19.tar.bz2")
SID_AM_ADAM = 5
SPEED = 1.0

_tts = None


def model_ready():
    return os.path.isfile(os.path.join(MODEL_DIR, "model.onnx"))


def ensure_model(log=print):
    """Tai model Kokoro tu nguon chinh thuc k2-fsa neu chua co."""
    if model_ready():
        return MODEL_DIR
    os.makedirs(os.path.dirname(MODEL_DIR), exist_ok=True)
    archive = os.path.join(TOOL_DIR, "models", "kokoro-en-v0_19.tar.bz2")
    log("[voice] Chua co model giong doc — dang tai Kokoro tu k2-fsa "
        "(~350MB, chi tai 1 lan)...")
    urllib.request.urlretrieve(MODEL_URL, archive)
    with tarfile.open(archive, "r:bz2") as tf:
        tf.extractall(os.path.join(TOOL_DIR, "models"))
    os.remove(archive)
    if not model_ready():
        raise RuntimeError("Tai model xong nhung khong thay model.onnx")
    log("[voice] Tai model xong.")
    return MODEL_DIR


def _load_tts():
    global _tts
    if _tts is not None:
        return _tts
    import sherpa_onnx
    ensure_model()
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=os.path.join(MODEL_DIR, "model.onnx"),
                voices=os.path.join(MODEL_DIR, "voices.bin"),
                tokens=os.path.join(MODEL_DIR, "tokens.txt"),
                data_dir=os.path.join(MODEL_DIR, "espeak-ng-data"),
            ),
            num_threads=2,
            debug=False,
            provider="cpu",
        ),
        max_num_sentences=1,
    )
    _tts = sherpa_onnx.OfflineTts(cfg)
    return _tts


def _synth_inprocess(text, out_wav):
    import soundfile as sf
    import sherpa_onnx
    tts = _load_tts()
    gc = sherpa_onnx.GenerationConfig()
    gc.sid = SID_AM_ADAM
    gc.speed = SPEED
    audio = tts.generate(text, gc)
    sf.write(out_wav, audio.samples, samplerate=audio.sample_rate)
    return len(audio.samples) / float(audio.sample_rate)


def _find_tts_python():
    """Tim python co sherpa_onnx de chay worker (khi python hien tai thieu)."""
    env = os.environ.get("PIXEL_TTS_PYTHON")
    cands = []
    if env:
        cands.append(env)
    cands += [
        os.path.join(TOOL_DIR, "venv", "Scripts", "python.exe"),
        os.path.join(TOOL_DIR, "venv", "bin", "python"),
        os.path.expanduser("~/workspace/voicestudio/venv/bin/python"),
        sys.executable,
        "python3",
        "python",
    ]
    for c in cands:
        if not c or (os.path.sep in c and not os.path.isfile(c)):
            continue
        try:
            r = subprocess.run([c, "-c", "import sherpa_onnx, soundfile"],
                               capture_output=True, timeout=60)
            if r.returncode == 0:
                return c
        except Exception:
            pass
    return None


def _synth_worker(text, out_wav):
    py = _find_tts_python()
    if not py:
        raise RuntimeError(
            "Khong tim thay Python co sherpa_onnx. Hay cai: "
            "pip install sherpa-onnx soundfile (xem HUONG-DAN.md)")
    worker = os.path.join(ENGINE_DIR, "tts_worker.py")
    r = subprocess.run([py, worker, text, out_wav, MODEL_DIR],
                       capture_output=True, text=True, timeout=1200)
    if r.returncode != 0:
        raise RuntimeError("TTS worker loi: " + (r.stderr or r.stdout)[-800:])
    info = json.loads(r.stdout.strip().splitlines()[-1])
    return float(info["duration"])


def synthesize(text, out_wav):
    """Sinh giong doc cho 1 cau -> file wav. Tra ve thoi luong (giay)."""
    ensure_model()
    try:
        import sherpa_onnx  # noqa: F401
        return _synth_inprocess(text, out_wav)
    except ImportError:
        return _synth_worker(text, out_wav)


def wav_duration(path):
    with contextlib.closing(wave.open(path, "rb")) as w:
        return w.getnframes() / float(w.getframerate())


import contextlib  # noqa: E402  (dat cuoi de cac ham tren doc de hon)


if __name__ == "__main__":
    txt = sys.argv[1] if len(sys.argv) > 1 else "Hello from Pixel Studio."
    out = sys.argv[2] if len(sys.argv) > 2 else "voice-test.wav"
    print("duration:", synthesize(txt, out), "->", out)
