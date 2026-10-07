#!/usr/bin/env bash
# Prepara las herramientas en Mac o en Windows (Git Bash, la terminal que usa Claude Code en Windows).
# Crea un entorno Python con ffmpeg COMPLETO (el de Remotion no trae filtros de audio), faster-whisper,
# DeepFilterNet (quita eco) y OpenCV/mediapipe. Deja exportados:
#   $PY  python del entorno      $FF  ffmpeg completo
#   $DESCARGAS  carpeta Descargas $PROYECTOS  carpeta "Reels Doc Juanes" (Mac: Películas; Windows: Videos)
# Uso: source scripts/setup-tools.sh [carpeta_venv]
# Windows necesita antes (una sola vez): Python 3.11 (winget install Python.Python.3.11) y Node.js LTS
# (winget install OpenJS.NodeJS.LTS). torch 2.0.1 no existe para Python 3.12 o más nuevo.
VENV=${1:-$HOME/.cache/reel-fr-venv}
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) REELFR_WIN=1 ;; *) REELFR_WIN=0 ;; esac
if [ "$REELFR_WIN" = 1 ]; then VBIN="$VENV/Scripts"; else VBIN="$VENV/bin"; fi
reelfr_base_python() { if [ "$REELFR_WIN" = 1 ]; then py -3.11 "$@"; else python3 "$@"; fi; }
if [ ! -x "$VBIN/python" ] && [ ! -x "$VBIN/python.exe" ]; then
  reelfr_base_python -m venv "$VENV" && "$VBIN/python" -m pip -q install imageio-ffmpeg faster-whisper deepfilternet "torch==2.0.1" "torchaudio==2.0.2" "mediapipe==0.10.14" 2>&1 | grep -v -i -E "warn|upgrade"
  # mediapipe arrastra numpy 2 y opencv-contrib 5: rompen torch y CascadeClassifier. Se fijan después.
  "$VBIN/python" -m pip -q uninstall -y opencv-contrib-python >/dev/null 2>&1
  "$VBIN/python" -m pip -q install "numpy<2" "opencv-python-headless<5" --force-reinstall --no-deps 2>&1 | grep -v -i -E "warn|upgrade"
fi
export PYTHONUTF8=1   # Windows: tildes y flechas en archivos y mensajes sin errores de codificación
if [ "$REELFR_WIN" = 1 ]; then
  export PY=$(cygpath -m "$VBIN/python.exe")
  export FF=$(cygpath -m "$("$PY" -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")")
  export PROYECTOS="$HOME/Videos/Reels Doc Juanes"
else
  export PY="$VBIN/python"
  export FF=$("$PY" -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
  export PROYECTOS="$HOME/Movies/Reels Doc Juanes"
fi
export DESCARGAS="$HOME/Downloads"
mkdir -p "$PROYECTOS"
echo "PY=$PY"; echo "FF=$FF"; echo "PROYECTOS=$PROYECTOS"; echo "DESCARGAS=$DESCARGAS"
