"""Transcribe work/audio16k.wav con tiempos por palabra -> work/transcript.json
Uso: $PY scripts/transcribe.py [modelo]   (por defecto large-v3-turbo, ~1,6 GB la primera vez)
Imprime cada frase con su tiempo para detectar claquetas, tomas falsas y repeticiones."""
import json, sys
from faster_whisper import WhisperModel
model = WhisperModel(sys.argv[1] if len(sys.argv) > 1 else "large-v3-turbo", device="cpu", compute_type="int8")
segments, _ = model.transcribe("work/audio16k.wav", language="es", word_timestamps=True,
                               vad_filter=False, condition_on_previous_text=False, beam_size=5)
out = []
for s in segments:
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": w.start, "e": w.end, "p": w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}", flush=True)
json.dump(out, open("work/transcript.json", "w"), ensure_ascii=False, indent=1)
