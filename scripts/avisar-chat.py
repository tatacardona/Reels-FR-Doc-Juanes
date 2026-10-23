"""Avisa en Google Chat que un reel quedó listo. Cada marca tiene su propio espacio y su bot de aprobación:
  dj  Doc Juanes          → bot «Aprobaciones Doc Juanes» (~/.reels-bot-dj.json) o webhook ~/.reels-fr-webhook-dj
  fr  Futuros Residentes  → bot «Aprobaciones FR»         (~/.reels-bot-fr.json) o webhook ~/.reels-fr-webhook-fr
Con el bot, el aviso es una tarjeta con ✅ Aprobado y ✏️ Corregir; las respuestas quedan en la hoja del bot y se leen
con --respuestas. Sin el archivo del bot (o con --webhook, o si el bot falla) se manda el texto por el webhook de siempre.
Las URL, secretos y webhooks NUNCA van en este repositorio (Janeth los comparte en privado; variables GCHAT_WEBHOOK_DJ/FR).
Uso: "$PY" scripts/avisar-chat.py <dj|fr> NOMBRE_CORTO [--video ENLACE] [--portada ENLACE] [--nota "texto"] [--webhook]
     "$PY" scripts/avisar-chat.py <dj|fr> --respuestas [--pieza NOMBRE_CORTO]   (qué respondieron en la tarjeta)
     "$PY" scripts/avisar-chat.py <dj|fr> --prueba      (mensaje de prueba por el webhook)
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
ap.add_argument("--webhook", action="store_true", help="manda el texto por el webhook aunque haya bot")
ap.add_argument("--respuestas", action="store_true")
ap.add_argument("--pieza", default="")
a = ap.parse_args()

BOT = Path.home() / f".reels-bot-{a.marca}.json"


def bot(datos):
    """Habla con la app web del bot (Apps Script). Responde con un 302 que urllib sigue con GET, como pide Google."""
    cfg = json.loads(BOT.read_text(encoding="utf-8"))
    datos = dict(datos, secreto=cfg["secreto"], url=cfg["url"])
    r = urllib.request.Request(cfg["url"], data=json.dumps(datos).encode("utf-8"),
                               headers={"Content-Type": "text/plain; charset=UTF-8"})
    res = json.loads(urllib.request.urlopen(r, timeout=60).read().decode("utf-8"))
    if not res.get("ok"):
        raise RuntimeError(res.get("error"))
    return res


if a.respuestas:
    if not BOT.exists():
        sys.exit(f"Falta ~/{BOT.name} (bot de {MARCAS[a.marca]}): pídeselo a Janeth")
    res = bot({"accion": "respuestas", "pieza": a.pieza})
    print("Hoja:", res["hoja"])
    for r in res["respuestas"]:
        print(f"\n{r['Fecha']} · {r['Pieza']} · {r['Decisión']} · {r['Respondió']}")
        if r["Observaciones"]:
            print("  " + r["Observaciones"].replace("\n", "\n  "))
    if not res["respuestas"]:
        print("(sin respuestas todavía)")
    sys.exit()

if not a.prueba and not a.nombre:
    sys.exit("Falta el NOMBRE_CORTO del video")

if BOT.exists() and not a.prueba and not a.webhook:
    contexto = "\n".join(x for x in [a.nota, f'Portada: <a href="{a.portada}">ver portada</a>' if a.portada else ""] if x)
    try:
        bot({"accion": "enviar", "pieza": a.nombre, "enlace": a.video or a.portada, "contexto": contexto, "para": "equipo"})
        print(f"tarjeta enviada al chat de {MARCAS[a.marca]} (bot de aprobación)")
        sys.exit()
    except Exception as e:  # el webhook queda de respaldo
        print(f"el bot no respondió ({e}); mando el aviso por el webhook")

url = os.environ.get(f"GCHAT_WEBHOOK_{a.marca.upper()}", "").strip()
f = Path.home() / f".reels-fr-webhook-{a.marca}"
if not url and f.exists():
    url = f.read_text(encoding="utf-8").strip()
if not url.startswith("https://chat.googleapis.com/"):
    sys.exit(f"Falta la URL del webhook de {MARCAS[a.marca]}: pídesela a Janeth y guárdala en ~/{f.name}")

if a.prueba:
    text = f"✅ Prueba: los avisos de reels nuevos de {MARCAS[a.marca]} llegarán a este espacio."
else:
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
