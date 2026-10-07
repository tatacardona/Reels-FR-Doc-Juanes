"""Re-transcribe SOLO la voz editada (sin efectos de sonido), uniendo los tramos de src/Reel/edit.json.
Sirve para saber si una palabra rara en verify.sh es un corte real o un efecto que suena encima.
Uso: $PY scripts/voz-sola.py"""
import json, numpy as np, wave
from faster_whisper import WhisperModel
e = json.load(open("src/Reel/edit.json")); fps = e["fps"]
w = wave.open("work/voz16k.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
parts = []
for c in e["clips"]:
    s = int(c["trim"] / fps * 16000); x = a[s:s + int(c["dur"] / fps * 16000)].copy()
    f = 160; x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f); parts.append(x)
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
seg, _ = m.transcribe(np.concatenate(parts), language="es", beam_size=5)
for s in seg: print("%5.1f %s" % (s.start, s.text))
