#!/bin/zsh
# Crea un entorno Python con ffmpeg COMPLETO (el de Remotion no trae filtros de audio)
# y faster-whisper (whisper.cpp suele fallar al compilar en Macs con Command Line Tools desajustadas).
# Uso: source scripts/setup-tools.sh [carpeta_venv]   -> deja $FF y $PY exportados
VENV=${1:-$HOME/.cache/reel-fr-venv}
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV" && "$VENV/bin/pip" -q install imageio-ffmpeg faster-whisper deepfilternet "torch==2.0.1" "torchaudio==2.0.2" "mediapipe==0.10.14" 2>&1 | grep -v -i -E "warn|upgrade"
  # mediapipe arrastra numpy 2 y opencv-contrib 5: rompen torch y CascadeClassifier. Se fijan después.
  "$VENV/bin/pip" -q uninstall -y opencv-contrib-python >/dev/null 2>&1
  "$VENV/bin/pip" -q install "numpy<2" "opencv-python-headless<5" --force-reinstall --no-deps 2>&1 | grep -v -i -E "warn|upgrade"
fi
export PY="$VENV/bin/python"
export FF=$("$PY" -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
echo "PY=$PY"; echo "FF=$FF"
