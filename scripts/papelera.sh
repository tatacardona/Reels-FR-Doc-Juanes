#!/usr/bin/env bash
# Manda archivos a la Papelera (Mac) o a la Papelera de reciclaje (Windows): se pueden recuperar.
# Nunca borrar archivos de la persona con rm.
# Uso: ./scripts/papelera.sh archivo1 [archivo2 ...]
for f in "$@"; do
  [ -e "$f" ] || { echo "no existe: $f"; continue; }
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      W=$(cygpath -w "$(cd "$(dirname "$f")" && pwd)/$(basename "$f")")
      if [ -d "$f" ]; then M=DeleteDirectory; else M=DeleteFile; fi
      powershell.exe -NoProfile -Command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::$M('$W','OnlyErrorDialogs','SendToRecycleBin')" ;;
    *)
      # Nombre libre en la Papelera: "x 2.mp4", "node_modules 2"… (nunca mover DENTRO de una carpeta que ya esté ahí)
      b=$(basename "$f"); t="$HOME/.Trash/$b"; n=2
      while [ -e "$t" ]; do
        case "$b" in ?*.*) t="$HOME/.Trash/${b%.*} $n.${b##*.}" ;; *) t="$HOME/.Trash/$b $n" ;; esac; n=$((n+1))
      done
      mv "$f" "$t" ;;
  esac && echo "a la papelera: $f"
done
