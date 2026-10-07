#!/usr/bin/env bash
# Acelera el video YA EXPORTADO sin cambiar el tono de la voz (atempo) y manteniendo todo sincronizado
# (subtítulos, stickers, destellos y música se aceleran juntos).
# Uso: FF=... ./scripts/speed.sh entrada.mp4 salida.mp4 1.06
set -e
IN="$1"; OUT="$2"; K=${3:-1.06}
"$FF" -hide_banner -loglevel error -y -i "$IN" -filter_complex "[0:v]setpts=PTS/${K}[v];[0:a]atempo=${K}[a]" \
  -map "[v]" -map "[a]" -r 25 -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart "$OUT"
echo "listo: $OUT (x${K})"
