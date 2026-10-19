"""Base musical original y discreta: piano eléctrico FM, bajo suave y un pulso de hi-hat muy bajo.

Uso: python3 make_music.py <salida.wav> <duracion_s>
"""
import sys

import numpy as np
import soundfile as sf

SR = 48000
BPM = 96
BEAT = 60 / BPM
rng = np.random.default_rng(7)

# Fmaj9 – Em7 – Dm9 – Cmaj9: luminoso y tranquilo, sin dramatismo.
CHORDS = [
    ([53, 57, 60, 64, 67], 41),
    ([52, 55, 59, 62, 67], 40),
    ([50, 53, 57, 60, 64], 38),
    ([48, 52, 55, 59, 62], 36),
]


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def epiano(f, dur):
    t = np.arange(int(dur * SR)) / SR
    index = 1.4 * np.exp(-t * 3.0)
    mod = np.sin(2 * np.pi * f * t) * index
    env = (1 - np.exp(-t * 400)) * np.exp(-t * 1.1)
    return np.sin(2 * np.pi * f * t + mod) * env


def bass(f, dur):
    t = np.arange(int(dur * SR)) / SR
    env = (1 - np.exp(-t * 60)) * np.exp(-t * 1.6)
    return (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t)) * env


def hat(dur=0.05):
    n = int(dur * SR)
    x = np.diff(rng.standard_normal(n + 1))  # ruido con énfasis en agudos
    return x * np.exp(-np.arange(n) / SR * 90)


def reverb(x, secs=1.8, mix=0.28):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir = np.convolve(ir, np.ones(24) / 24, mode="same")  # suaviza la cola
    wet = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[: len(x)]
    wet *= np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)
    return (1 - mix) * x + mix * wet


def main(out, duration):
    duration = float(duration)
    n = int((duration + 2) * SR)
    keys, low, hats = np.zeros(n), np.zeros(n), np.zeros(n)

    def add(buf, sig, t):
        i = int(t * SR)
        sig = sig[: max(0, n - i)]
        buf[i : i + len(sig)] += sig

    bar = 4 * BEAT
    t, k = 0.0, 0
    while t < duration + 1:
        notes, root = CHORDS[k % len(CHORDS)]
        for hit in (0, 2.5 * BEAT):  # acorde + anticipación sincopada suave
            for j, m in enumerate(notes):
                add(keys, epiano(hz(m), bar) * (0.22 if hit == 0 else 0.12), t + hit + j * 0.012)
        add(low, bass(hz(root), 1.6 * BEAT), t)
        add(low, bass(hz(root), 1.2 * BEAT) * 0.7, t + 2.5 * BEAT)
        for b in range(8):
            add(hats, hat() * (0.05 if b % 2 else 0.025), t + b * BEAT / 2)
        t += bar
        k += 1

    mix = reverb(keys) + 0.55 * low + hats
    mix = np.tanh(mix * 1.2) / 1.2
    mix = mix[: int(duration * SR)]
    fade_in, fade_out = int(1.0 * SR), int(1.6 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out) ** 2
    mix /= np.max(np.abs(mix)) / 0.7
    stereo = np.stack([mix, np.roll(mix, int(0.011 * SR))], axis=1)  # leve amplitud estéreo
    sf.write(out, stereo, SR)


if __name__ == "__main__":
    main(*sys.argv[1:3])
