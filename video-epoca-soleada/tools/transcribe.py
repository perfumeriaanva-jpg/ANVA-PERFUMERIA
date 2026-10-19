"""Transcribe un WAV mono 16 kHz con Parakeet TDT v3 (sherpa-onnx) y guarda palabras con tiempos.

Uso: python3 transcribe.py <dir_modelo> <audio.wav> <salida.json>
"""
import json
import sys
from pathlib import Path

import sherpa_onnx
import soundfile as sf


def main(model_dir, wav, out):
    m = Path(model_dir)
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(m / "encoder.int8.onnx"),
        decoder=str(m / "decoder.int8.onnx"),
        joiner=str(m / "joiner.int8.onnx"),
        tokens=str(m / "tokens.txt"),
        model_type="nemo_transducer",
        num_threads=4,
    )
    audio, sr = sf.read(wav, dtype="float32")
    s = rec.create_stream()
    s.accept_waveform(sr, audio)
    rec.decode_stream(s)
    r = s.result

    # Une tokens SentencePiece ("▁" o espacio inicial = palabra nueva) en palabras con inicio/fin.
    words = []
    for tok, t in zip(r.tokens, r.timestamps):
        if tok.startswith((" ", "▁")) or not words:
            words.append({"w": tok.strip(" ▁"), "start": t, "end": t})
        else:
            words[-1]["w"] += tok
        words[-1]["end"] = t
    for a, b in zip(words, words[1:]):
        a["end"] = max(a["end"] + 0.08, min(b["start"], a["end"] + 0.4))
    words[-1]["end"] += 0.3

    Path(out).write_text(json.dumps({"text": r.text, "words": words}, ensure_ascii=False, indent=1))
    print(r.text)


if __name__ == "__main__":
    main(*sys.argv[1:4])
