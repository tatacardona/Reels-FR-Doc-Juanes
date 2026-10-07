"""Eco suave para frases de trascendencia: genera public/eco-N.wav con SOLO las repeticiones (3 rebotes
que se apagan, más opacos que la voz). El Reel las suma encima de la voz desde el inicio de la frase.
Las frases van en edit-config.json → "echo": [[inicio, fin], ...] (segundos del video CRUDO).
Uso: $PY scripts/eco.py"""
import json, wave
import numpy as np

c = json.load(open("edit-config.json"))
w = wave.open("public/voz-mejorada.wav"); sr = w.getframerate(); ch = w.getnchannels()
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
if ch > 1: a = a.reshape(-1, ch).mean(1)
for i, (t0, t1) in enumerate(c.get("echo", [])):
    x = a[int(t0 * sr):int(t1 * sr)]
    out = np.zeros(len(x) + int(1.6 * sr))
    for d, g in ((0.30, 0.38), (0.60, 0.22), (0.90, 0.12)):  # retardo (s), volumen
        s = int(d * sr); out[s:s + len(x)] += x * g
    k = np.exp(-2 * np.pi * 3500 / sr); y = np.zeros_like(out); p = 0.0  # paso bajo: eco lejano
    for j, v in enumerate(out): p = (1 - k) * v + k * p; y[j] = p
    y[-int(0.3 * sr):] *= np.linspace(1, 0, int(0.3 * sr))
    f = wave.open(f"public/eco-{i}.wav", "wb"); f.setnchannels(2); f.setsampwidth(2); f.setframerate(sr)
    f.writeframes((np.clip(np.stack([y, y], 1), -1, 1) * 32767).astype(np.int16).tobytes()); f.close()
    print(f"listo: public/eco-{i}.wav ({t0}-{t1} s)")
