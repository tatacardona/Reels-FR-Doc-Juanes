"""Energía del audio cada 50 ms -> work/energy.json, e imprime las regiones con voz.
Sirve para ubicar cortes exactos (Whisper suele adelantar el inicio de la primera palabra)
y para medir énfasis (palabras más fuertes que el resto de su frase).
Uso: $PY scripts/energy.py            -> regiones de voz
     $PY scripts/energy.py words      -> cada palabra con su volumen relativo a la frase (+dB = énfasis)
     $PY scripts/energy.py zoom 84 87 -> dB cada 50 ms en ese rango (para afinar un corte)"""
import numpy as np, wave, json, sys, statistics as st
import os
# Si existe la voz ya limpia (sin eco, de audio.sh), se mide sobre ella: así los cortes no incluyen
# las colas de eco y las pausas entre frases quedan más cortas.
SRC = "work/voz16k.wav" if os.path.exists("work/voz16k.wav") else "work/audio16k.wav"
w = wave.open(SRC); sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
hop = sr // 20
db = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(a) - hop, hop)])
json.dump({"db": db.round(1).tolist(), "hop": 0.05, "clean": SRC.endswith("voz16k.wav")}, open("work/energy.json", "w"))
mode = sys.argv[1] if len(sys.argv) > 1 else "regions"
if mode == "words":
    for s in json.load(open("work/transcript.json")):
        vals = [(x["w"], max(db[int(x["s"] * 20):max(int(x["e"] * 20), int(x["s"] * 20) + 1)])) for x in s["words"]]
        med = st.median(v for _, v in vals)
        print(f"[{s['start']:6.1f}] " + " ".join(f"{t}({v - med:+.0f})" for t, v in vals))
elif mode == "zoom":
    t0, t1 = float(sys.argv[2]), float(sys.argv[3])
    print(" ".join(f"{t0 + i * 0.05:.2f}:{db[int(t0 * 20) + i]:.0f}" for i in range(int((t1 - t0) * 20))))
else:
    floor = np.percentile(db, 10); thr = floor + 12
    print(f"piso de ruido {floor:.1f} dB, umbral de voz {thr:.1f} dB")
    regs, start = [], None
    for i, v in enumerate(db > thr):
        if v and start is None: start = i * 0.05
        if not v and start is not None: regs.append([start, i * 0.05]); start = None
    m = []
    for r in regs:
        if m and r[0] - m[-1][1] < 0.25: m[-1][1] = r[1]
        else: m.append(r)
    print("  ".join(f"{r[0]:.2f}-{r[1]:.2f}" for r in m if r[1] - r[0] > 0.12))
