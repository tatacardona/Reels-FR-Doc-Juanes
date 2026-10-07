#!/bin/zsh
# Prepara el video crudo: copia vertical enderezada para Remotion + audios para análisis.
# Uso: FF=... ./scripts/prep.sh "/ruta/al/crudo.MP4" [none|ccw|cw]
#   ccw = girar 90° antihorario (cámara grabó en vertical pero el archivo quedó acostado con la cabeza a la derecha)
#   cw  = girar 90° horario (cabeza a la izquierda);  none = ya está vertical
# Iluminación: por defecto aclara sombras y medios tonos (curva suave) sin quemar la pared blanca;
#   ella pidió "quitar un poco la oscuridad". LIGHT=0 la desactiva.
# Salidas: public/video-vertical.mp4 (1440x2560, 25 fps), work/audio16k.wav, work/audio48k.wav
set -e
SRC="$1"; ROT=${2:-none}
mkdir -p public work
case $ROT in
  ccw) VF="transpose=2,";; cw) VF="transpose=1,";; *) VF="";;
esac
Q=(-hide_banner -loglevel error -y)
LUZ=""
[ "${LIGHT:-1}" = "1" ] && LUZ=",curves=all='0/0 0.12/0.17 0.4/0.5 0.75/0.83 1/1',eq=saturation=1.06"
$FF $Q -i "$SRC" -vf "${VF}scale=1440:2560:force_original_aspect_ratio=increase:flags=lanczos,crop=1440:2560,fps=25${LUZ}" \
  -c:v libx264 -preset fast -crf 16 -pix_fmt yuv420p -g 25 -an public/video-vertical.tmp.mp4
mv public/video-vertical.tmp.mp4 public/video-vertical.mp4
$FF $Q -i "$SRC" -vn -ac 1 -ar 16000 work/audio16k.wav
$FF $Q -i "$SRC" -vn -ac 1 -ar 48000 work/audio48k.wav
echo "listo: public/video-vertical.mp4, work/audio16k.wav, work/audio48k.wav"
