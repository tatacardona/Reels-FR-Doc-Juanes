#!/usr/bin/env bash
# Pone la portada como PRIMEROS cuadros del video (0,12 s por defecto) para que Instagram/TikTok la usen
# como miniatura por defecto al publicar. El resto del video queda igual.
# Uso: FF=... ./scripts/portada.sh portada.jpg video.mp4 salida.mp4 [cuadros=3]
set -e
IMG="$1"; IN="$2"; OUT="$3"; N=${4:-3}
Q=(-hide_banner -loglevel error -y)
TMP=$(mktemp -d)
"$FF" "${Q[@]}" -loop 1 -i "$IMG" -f lavfi -i "anullsrc=r=48000:cl=stereo" -frames:v $N -r 25 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p" \
  -t $(awk "BEGIN{print $N/25}") -c:v libx264 -preset slow -crf 16 -c:a aac -b:a 320k -ar 48000 "$TMP/p.mp4"
"$FF" "${Q[@]}" -i "$IN" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 25 -c:a aac -b:a 320k -ar 48000 -ac 2 "$TMP/v.mp4"
"$FF" "${Q[@]}" -i "$TMP/p.mp4" -i "$TMP/v.mp4" -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart "$OUT"
rm -rf "$TMP"; echo "listo: $OUT (portada en los primeros $N cuadros)"
