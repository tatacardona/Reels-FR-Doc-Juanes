"""Mide el consumo REAL de tokens de la conversación actual de Claude Code y su costo aproximado.
Sirve para comparar con la proyección del plan y para afinar las cifras de referencia del skill.
Uso: python3 scripts/consumo.py [--desde "texto de un mensaje de la persona"]
  --desde: cuenta solo desde el primer mensaje que contenga ese texto (p. ej. "guion 5").
Costo = tarifa pública de la API (USD por millón de tokens). Con plan Team/Enterprise la factura puede
ser distinta, pero sirve para comparar planes de acción entre sí.
"""
import glob, json, os, sys

# USD por millón: entrada, escritura de caché (1 h), lectura de caché, salida
PRECIOS = {"opus-5-5": (4, 8, 0.20, 20), "sonnet-5-5": (2, 4, 0.20, 10), "fable-5": (10, 20, 0.25, 50),
           "haiku-4-5": (1, 2, 0.10, 5)}

def precio(model):
    for k, v in PRECIOS.items():
        if k in (model or ""): return v
    return PRECIOS["opus-5-5"]

files = [f for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))]
if not files: sys.exit("No encontré conversaciones de Claude Code.")
f = max(files, key=os.path.getmtime)  # la conversación más reciente = la actual
desde = sys.argv[sys.argv.index("--desde") + 1].lower() if "--desde" in sys.argv else None
activo = desde is None
seen, n, tok, usd = set(), 0, [0, 0, 0, 0], 0.0
for line in open(f, encoding="utf-8"):
    try: d = json.loads(line)
    except ValueError: continue
    m = d.get("message") or {}
    if not activo and d.get("type") == "user" and isinstance(m.get("content"), str) and desde in m["content"].lower():
        activo = True
    if not activo or d.get("type") != "assistant" or "usage" not in m or m.get("id") in seen: continue
    seen.add(m.get("id")); n += 1; u = m["usage"]
    t = [u.get("input_tokens", 0), u.get("cache_creation_input_tokens", 0), u.get("cache_read_input_tokens", 0),
         u.get("output_tokens", 0)]
    tok = [a + b for a, b in zip(tok, t)]
    usd += sum(x * p for x, p in zip(t, precio(m.get("model")))) / 1e6
if not n: sys.exit("No hay consumo registrado" + (f" desde «{desde}»." if desde else "."))
print(f"Pasos del modelo: {n}")
print(f"Tokens nuevos (entrada + caché escrita): {(tok[0] + tok[1]) / 1e6:.2f} M")
print(f"Tokens releídos (caché): {tok[2] / 1e6:.1f} M   ← releer la conversación; crece con su largo")
print(f"Tokens escritos por Claude: {tok[3] / 1e3:.0f} mil")
print(f"Costo aproximado (tarifa API): US$ {usd:.2f}")
