#!/usr/bin/env python3
"""
Worker sinh giong Kokoro am_adam — chay bang python CO sherpa_onnx.
Dung: python tts_worker.py "<cau thoai>" <file_wav_ra> <thu_muc_model>
In ra dong cuoi: {"duration": <giay>, "sample_rate": <hz>}
"""
import json
import os
import sys

import soundfile as sf
import sherpa_onnx

SID_AM_ADAM = 5


def main():
    text, out_wav, model_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=os.path.join(model_dir, "model.onnx"),
                voices=os.path.join(model_dir, "voices.bin"),
                tokens=os.path.join(model_dir, "tokens.txt"),
                data_dir=os.path.join(model_dir, "espeak-ng-data"),
            ),
            num_threads=2,
            debug=False,
            provider="cpu",
        ),
        max_num_sentences=1,
    )
    tts = sherpa_onnx.OfflineTts(cfg)
    gc = sherpa_onnx.GenerationConfig()
    gc.sid = SID_AM_ADAM
    gc.speed = 1.0
    audio = tts.generate(text, gc)
    sf.write(out_wav, audio.samples, samplerate=audio.sample_rate)
    dur = len(audio.samples) / float(audio.sample_rate)
    print(json.dumps({"duration": dur, "sample_rate": audio.sample_rate}))


if __name__ == "__main__":
    main()
