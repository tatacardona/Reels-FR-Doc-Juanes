#!/bin/zsh
# Voz mejorada + efectos de sonido sintetizados (sin derechos de autor).
# Uso: FF=... PY=... ./scripts/audio.sh   (después vuelve a correr $PY scripts/energy.py)
set -e
Q=(-hide_banner -loglevel error -y)
# Voz con MENOS ECO pero natural (versión que ella eligió al oír 3 pruebas):
# 1) DeepFilterNet3 (IA) quita ruido y parte de la reverberación del cuarto.
# 2) Expansor SUAVE (range 0.4, release 220 ms): baja colas de eco sin comerse finales de palabra.
#    NO usar uno rápido/profundo (range 0.12, release 60 ms): quitaba más eco (-61 dB) pero ella oía
#    las palabras "cortadas" ("pueblo", "año", "actitud", "elegibles"). Esta queda en -43 dB a 100 ms.
# Si DeepFilterNet no está, cae a una cadena solo con ffmpeg.
DF=$(dirname "$PY")/deepFilter
SRC=work/audio48k.wav
if [ -x "$DF" ]; then
  "$DF" work/audio48k.wav -o work/df >/dev/null 2>&1 && SRC=work/df/audio48k_DeepFilterNet3.wav
else
  echo "AVISO: sin DeepFilterNet (pip install deepfilternet torch==2.0.1 torchaudio==2.0.2); el eco se reduce menos"
  PRE="afftdn=nf=-50:nr=12:tn=1,"
fi
$FF $Q -i $SRC -af "highpass=f=90,lowpass=f=14000,${PRE}equalizer=f=300:t=q:w=1.0:g=-3,\
equalizer=f=3200:t=q:w=1.5:g=2.5,deesser=i=0.3,\
agate=threshold=0.01:ratio=1.5:range=0.4:attack=5:release=220:knee=8,\
acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,\
loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000" public/voz-mejorada.wav
# Copia a 16 kHz para energy.py: los cortes se miden sobre la voz limpia (sin colas de eco = menos tiempos muertos)
$FF $Q -i public/voz-mejorada.wav -ac 1 -ar 16000 work/voz16k.wav
# Whoosh para transiciones
$FF $Q -f lavfi -i "anoisesrc=color=pink:d=0.5:a=0.6" -af "highpass=f=700,lowpass=f=6500,\
afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.18,aresample=48000" public/sfx-whoosh.wav
# Golpe grave ("boom") para impactos (p. ej. foto rasgándose)
$FF $Q -f lavfi -i "sine=f=42:d=2.2" -f lavfi -i "anoisesrc=color=brown:d=2.2:a=0.9" \
  -filter_complex "[0]volume=1.2[a];[1]lowpass=f=220[b];[a][b]amix=2,\
afade=t=out:st=0.05:d=2.1:curve=exp,volume=2.2,aresample=48000" public/sfx-boom.wav
echo "audio listo: public/voz-mejorada.wav + sfx-whoosh/boom"
