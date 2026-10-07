"""Sintetiza el sonido de una foto/papel rasgándose (sin derechos de autor) -> public/sfx-tear.wav"""
import numpy as np, wave
sr = 48000; rng = np.random.default_rng(7)
dur = 0.75; n = int(sr * dur); t = np.arange(n) / sr
noise = rng.standard_normal(n); crackle = np.zeros(n); pos = 0.0
while pos < dur - 0.02:  # crujidos cada vez más rápidos: las fibras cediendo
    i = int(pos * sr); L = int(sr * rng.uniform(0.002, 0.009))
    crackle[i:i + L] += rng.uniform(0.4, 1.0) * np.hanning(L)
    pos += rng.uniform(0.004, 0.02) * (1.2 - pos / dur)
sig = noise * (0.25 + crackle)
F = np.fft.rfft(sig); f = np.fft.rfftfreq(n, 1 / sr)
F *= np.clip((f - 600) / 600, 0, 1) * np.clip((9000 - f) / 3000, 0, 1) * (1 + 0.6 * np.exp(-((f - 3200) / 1200) ** 2))
sig = np.fft.irfft(F, n)
sig *= np.minimum(t / 0.015, 1) * np.exp(-np.maximum(t - 0.45, 0) / 0.08) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t) ** 2)
sig = sig / np.abs(sig).max() * 0.85
w = wave.open("public/sfx-tear.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((sig * 32767).astype(np.int16).tobytes()); w.close(); print("public/sfx-tear.wav listo")
