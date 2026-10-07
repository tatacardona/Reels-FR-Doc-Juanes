"""Avisa en Google Chat que un reel quedó listo (webhook entrante). Cada marca tiene su propio espacio:
  dj  Doc Juanes          → ~/.reels-fr-webhook-dj  (o variable GCHAT_WEBHOOK_DJ)
  fr  Futuros Residentes  → ~/.reels-fr-webhook-fr  (o variable GCHAT_WEBHOOK_FR)
Las URL son secretas: NUNCA van en este repositorio (una línea por archivo; Janeth las comparte en privado).
Uso: "$PY" scripts/avisar-chat.py <dj|fr> NOMBRE_CORTO [--video ENLACE] [--portada ENLACE] [--nota "texto"]
     "$PY" scripts/avisar-chat.py <dj|fr> --prueba      (mensaje de prueba)
"""
import argparse, json, os, sys, urllib.request
from pathlib import Path

MARCAS = {"dj": "Doc Juanes", "fr": "Futuros Residentes"}
ap = argparse.ArgumentParser()
ap.add_argument("marca", choices=MARCAS)
ap.add_argument("nombre", nargs="?", default="")
ap.add_argument("--video", default="")
ap.add_argument("--portada", default="")
ap.add_argument("--nota", default="")
ap.add_argument("--prueba", action="store_true")
a = ap.parse_args()

url = os.environ.get(f"GCHAT_WEBHOOK_{a.marca.upper()}", "").strip()
f = Path.home() / f".reels-fr-webhook-{a.marca}"
if not url and f.exists():
    url = f.read_text(encoding="utf-8").strip()
if not url.startswith("https://chat.googleapis.com/"):
    sys.exit(f"Falta la URL del webhook de {MARCAS[a.marca]}: pídesela a Janeth y guárdala en ~/{f.name}")

if a.prueba:
    text = f"✅ Prueba: los avisos de reels nuevos de {MARCAS[a.marca]} llegarán a este espacio."
else:
    if not a.nombre:
        sys.exit("Falta el NOMBRE_CORTO del video")
    lineas = [f"🎬 *Nuevo reel listo:* {a.nombre.replace('_', ' ')}"]
    if a.video:
        lineas.append(f"👉 Video: {a.video}")
    if a.portada:
        lineas.append(f"🖼️ Portada: {a.portada}")
    if a.nota:
        lineas.append(a.nota)
    text = "\n".join(lineas)

req = urllib.request.Request(url, data=json.dumps({"text": text}).encode("utf-8"),
                             headers={"Content-Type": "application/json; charset=UTF-8"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"aviso enviado al chat de {MARCAS[a.marca]}" if r.status == 200 else f"respuesta {r.status}")
except Exception as e:
    sys.exit(f"no se pudo enviar el aviso: {e}")
