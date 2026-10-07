#!/usr/bin/env bash
# Sube archivos finales a una carpeta de Drive usando Google Drive para escritorio (Mac o Windows)
# y, cuando Drive les asigna su identificador, imprime el enlace de cada uno para el aviso de Chat.
# La carpeta debe verse en el computador: si fue compartida por otra persona, primero hay que
# agregarle un acceso directo en Mi unidad (Drive web: clic derecho → Organizar → Agregar acceso directo).
# Uso: ./scripts/subir-drive.sh "<nombre o ruta de la carpeta>" archivo1 [archivo2 ...]
DEST="$1"; shift
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)   # Drive para escritorio monta una unidad (normalmente G:)
    for L in g h i j k l m n o p q r s t u v w x y z d e f; do
      [ -d "/$L/Mi unidad" ] || [ -d "/$L/My Drive" ] && { ROOT="/$L"; break; }; done ;;
  *) ROOT=$(ls -d "$HOME"/Library/CloudStorage/GoogleDrive-* 2>/dev/null | head -1) ;;
esac
[ -n "$ROOT" ] || { echo "No encuentro Google Drive para escritorio: ¿está instalado y con la sesión iniciada?"; exit 1; }

if [ -d "$DEST" ]; then DIR="$DEST"
else
  # Busca la carpeta por nombre en Mi unidad y en las unidades compartidas (poca profundidad: Drive es lento)
  for B in "$ROOT/Mi unidad" "$ROOT/My Drive" "$ROOT/Unidades compartidas" "$ROOT/Shared drives"; do
    [ -d "$B" ] || continue
    DIR=$(find "$B" -maxdepth 3 -type d -name "$DEST" 2>/dev/null | head -1); [ -n "$DIR" ] && break
  done
fi
[ -n "$DIR" ] || { echo "No veo la carpeta \"$DEST\" en Drive para escritorio. Si es compartida, agrégale un acceso directo en Mi unidad."; exit 1; }
echo "carpeta: $DIR"

for f in "$@"; do
  cp "$f" "$DIR/" || { echo "no se pudo copiar: $f"; continue; }
  dst="$DIR/$(basename "$f")"; id=""
  if command -v xattr >/dev/null; then   # Mac: Drive guarda el identificador del archivo en un atributo
    for _ in $(seq 1 60); do
      id=$(xattr -p 'com.google.drivefs.item-id#S' "$dst" 2>/dev/null) && [ -n "$id" ] && break; sleep 5
    done
  fi
  if [ -n "$id" ]; then echo "$(basename "$f"): https://drive.google.com/file/d/$id/view"
  else echo "$(basename "$f"): copiado; el enlace se copia desde Drive (clic derecho → Compartir → Copiar enlace)"; fi
done
echo "Drive termina de subirlos en segundo plano (mira el ícono de Drive en la barra de menú o de tareas)."
