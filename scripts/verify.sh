#!/usr/bin/env bash
# Verifica el video exportado: duración, formato, volumen (-14 LUFS), silencios que sobren,
# y re-transcribe para confirmar que ningún corte se comió palabras.
# Uso: FF=... PY=... ./scripts/verify.sh out/reel.mp4
V=${1:-out/reel.mp4}
"$FF" -hide_banner -i "$V" 2>&1 | grep -E "Duration|Stream"
"$FF" -hide_banner -nostats -i "$V" -vn -af "silencedetect=n=-40dB:d=0.25,ebur128" -f null - 2>&1 | grep -E "silence_duration|^\s+I:"
"$FF" -hide_banner -loglevel error -y -i "$V" -vn -ac 1 -ar 16000 work/verify.wav
"$PY" - <<PYEOF 2>&1 | grep -v -i warn
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
for s in m.transcribe("work/verify.wav", language="es")[0]: print(f"[{s.start:5.1f}] {s.text.strip()}")
PYEOF
