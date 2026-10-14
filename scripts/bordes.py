# Revisa los primeros cuadros de CADA corte del Reel renderizado (Janeth, 13 oct): ahí aparecen cosas de 1 o 2 cuadros que
# la hoja de fotogramas no ve (un salto de zoom raro, una toma que no era, algo que se cuela al empezar el plano).
# Uso (desde la carpeta del proyecto, con el edit.json de esa versión):
#   "$PY" scripts/bordes.py out/NOMBRE_CORTO_REEL_vN.mp4 [factor de speed.sh]
#   → out/NOMBRE_CORTO_REEL_vN_BORDES_N.jpg: una fila por corte (segundo del video y sus 3 primeros cuadros).
# Si en un corte se ve algo raro: corre el comienzo del tramo en edit-config.json (o el corte) y vuelve a exportar.
import json, os, subprocess, sys
from PIL import Image, ImageDraw

FF = os.environ["FF"]
VIDEO = sys.argv[1]
VEL = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
N, W, POR_HOJA = 3, 140, 40  # cuadros por corte, ancho de cada cuadro (vertical), cortes por hoja
ed = json.load(open("src/Reel/edit.json", encoding="utf-8"))
fps = ed.get("fps", 25)
cortes = [(round(c["start"] / fps / VEL, 3), f"tramo {k + 1}") for k, c in enumerate(sorted(ed.get("clips", []), key=lambda c: c["start"]))]


def cuadros(t0):
    """Los N primeros cuadros a partir de t0 (segundos del video), como imágenes de W de ancho."""
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", VIDEO, "-frames:v", str(N), "-vf", f"scale={W}:-2",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    h = len(raw) // (W * 3 * N) if raw else 0
    return [Image.frombytes("RGB", (W, h), raw[i * W * h * 3:(i + 1) * W * h * 3]) for i in range(N)] if h else []


base = VIDEO[:-4]
hojas = [cortes[i:i + POR_HOJA] for i in range(0, len(cortes), POR_HOJA)]
for k, grupo in enumerate(hojas, 1):
    filas = []
    for t0, pid in grupo:
        fs = cuadros(t0)
        if not fs: continue
        h = fs[0].height
        fila = Image.new("RGB", (110 + N * (W + 4), h + 4), "white")
        d = ImageDraw.Draw(fila)
        d.text((4, 4), f"{int(t0 // 60)}:{t0 % 60:05.2f}", fill="black"); d.text((4, 20), pid[:22], fill="black")
        for i, f in enumerate(fs): fila.paste(f, (110 + i * (W + 4), 2))
        filas.append(fila)
    hoja = Image.new("RGB", (max(f.width for f in filas), sum(f.height for f in filas)), "white")
    y = 0
    for f in filas: hoja.paste(f, (0, y)); y += f.height
    hoja.save(f"{base}_BORDES_{k}.jpg", quality=80)
print(f"{len(cortes)} cortes → {len(hojas)} hojas: {base}_BORDES_*.jpg")
