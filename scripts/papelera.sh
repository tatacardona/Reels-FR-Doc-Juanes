#!/usr/bin/env bash
# Manda archivos a la Papelera (Mac) o a la Papelera de reciclaje (Windows): se pueden recuperar.
# Nunca borrar archivos de la persona con rm.
# Uso: ./scripts/papelera.sh archivo1 [archivo2 ...]
for f in "$@"; do
  [ -e "$f" ] || { echo "no existe: $f"; continue; }
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      W=$(cygpath -w "$(cd "$(dirname "$f")" && pwd)/$(basename "$f")")
      powershell.exe -NoProfile -Command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('$W','OnlyErrorDialogs','SendToRecycleBin')" ;;
    *)
      b=$(basename "$f"); [ -e "$HOME/.Trash/$b" ] && b="${b%.*}_$(date +%s).${b##*.}"
      mv "$f" "$HOME/.Trash/$b" ;;
  esac && echo "a la papelera: $f"
done
