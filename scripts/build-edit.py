"""Genera src/Reel/edit.json (cortes, zooms, transiciones, subtítulos, fotos) a partir de:
  - work/transcript.json  (scripts/transcribe.py)
  - work/energy.json      (scripts/energy.py)
  - edit-config.json      (decisiones editoriales de ESTE video; ver assets/edit-config.example.json)

Uso (desde la raíz del proyecto Remotion):  python3 scripts/build-edit.py
Imprime la duración final y todos los subtítulos para revisarlos.
"""
import json, re, sys

cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "edit-config.json"))
FPS = cfg.get("fps", 25)
words = [w for s in json.load(open("work/transcript.json")) for w in s["words"]]

# Correcciones de tiempos donde Whisper se equivocó (arranques en falso, palabras muy suaves)
for fx in cfg.get("word_fixes", []):
    for w in words:
        if abs(w["s"] - fx["at"]) < 0.03 and w["w"].strip().lower().startswith(fx["word"].lower()):
            w["s"], w["e"] = fx["s"], fx["e"]

energy = json.load(open("work/energy.json")); DB, HOP = energy["db"], energy["hop"]
FLOOR = sorted(DB)[len(DB) // 10]; THR = FLOOR + cfg.get("voice_threshold_db", 40 if energy.get("clean") else 12)  # 40 dB sobre la voz limpia

# Ritmo apretado (ella lo pide en casi todos los videos): márgenes chicos y pausas internas > 0,08 s fuera
PAD_IN = cfg.get("pad_in", 0.02); PAD_OUT = cfg.get("pad_out", 0.02); MAX_PAUSE = cfg.get("max_pause", 0.08)
FRAMINGS = cfg.get("framings", [1.0, 1.35, 1.12, 1.5, 1.0, 1.25, 1.42, 1.08, 1.55, 1.2])
MIN_ZOOM_JUMP = cfg.get("min_zoom_jump", 0.15)
END_PAD = cfg.get("end_pad", 0.02)  # margen tras la última palabra de cada tramo
INNER_MAX = cfg.get("inner_max", 0.15)  # pausas más cortas que esto dentro de una palabra no se cortan
INNER_PAD = cfg.get("inner_pad", 0.02)  # margen en las pausas internas de una frase
ONSET = FLOOR + cfg.get("onset_db", 33)  # nivel hasta donde se extienden los bordes (sonidos suaves)
EDGE_MAX = cfg.get("edge_max", 0.08)  # máximo que se extiende cada borde
MIN_PIECE = cfg.get("min_piece", 0.25)  # trozo de voz mínimo entre dos cortes
# Un pedazo de menos de MIN_SHOT s (p. ej. "¿Por…" antes de una pausa) no cambia de plano: el salto
# de zoom en un fragmento tan corto se siente brusco.
MIN_SHOT = cfg.get("min_shot", 0.6)
CLIPS = cfg["clips"]
ENFASIS = [tuple(e) for e in cfg.get("emphasis", [])]  # [palabra, seg] o [palabra, seg, "alt"] (segunda fuente)
IDEA_START = cfg.get("idea_start", [])
BRAND = {k.lower(): v for k, v in cfg.get("brand_words", {"futuros": "Futuros", "residentes": "Residentes",
                                                            "doc": "Doc", "juanes": "Juanes"}).items()}
KEEP_TOGETHER = [p.lower() for p in cfg.get("keep_together_after", ["futuros", "doc"])]
SMALL = {"a", "y", "la", "el", "en", "lo", "de", "que", "las", "los", "tu", "te", "mis", "con", "es", "un", "una", "al", "del"} | set(cfg.get("small_extra", []))  # palabras que nunca van solas


def speech_ranges(a, b):
    """Recorta el tramo a donde hay voz y quita pausas internas > MAX_PAUSE, sin comerse sonidos suaves."""
    i0, i1 = int(a / HOP), min(int(b / HOP), len(DB))
    on = [k for k in range(i0, i1) if DB[k] > THR]
    if not on:
        return [(a, b)]
    regs = [[on[0], on[0]]]
    for k in on[1:]:
        if (k - regs[-1][1]) * HOP > MAX_PAUSE: regs.append([k, k])
        else: regs[-1][1] = k
    # Bordes: se extienden mientras siga sonando la voz suave (inicios como "y", "J"; colas de "s")
    # por encima de ONSET (más bajo que el umbral), hasta EDGE_MAX s. Antes se comían esos sonidos.
    lim = int(EDGE_MAX / HOP)
    for r in regs:
        k = 0
        while k < lim and r[0] - 1 >= i0 and DB[r[0] - 1] > ONSET: r[0] -= 1; k += 1
        k = 0
        while k < lim and r[1] + 1 < i1 and DB[r[1] + 1] > ONSET: r[1] += 1; k += 1
    merged = [regs[0]]
    for r in regs[1:]:
        if r[0] - merged[-1][1] <= int(MAX_PAUSE / HOP) + 1: merged[-1][1] = max(merged[-1][1], r[1])
        else: merged.append(r)
    regs = merged
    # Nunca pedacitos sueltos: un trozo de voz más corto que MIN_PIECE se une a su vecino (con su pausa)
    # en vez de borrarse o quedar aislado (sonaba a "sonidito" entre cortes).
    mp_ = int(MIN_PIECE / HOP); k = 0
    while len(regs) > 1 and k < len(regs):
        if regs[k][1] - regs[k][0] + 1 < mp_:
            if k > 0: regs[k - 1][1] = regs[k][1]; regs.pop(k)
            else: regs[1][0] = regs[0][0]; regs.pop(0)
        else: k += 1
    # márgenes completos al inicio y final del tramo; dentro de la frase, INNER_PAD (más apretado)
    n = len(regs)
    return [(max(a, r[0] * HOP - (PAD_IN if i == 0 else INNER_PAD)),
             min(b, (r[1] + 1) * HOP + (PAD_OUT if i == n - 1 else INNER_PAD))) for i, r in enumerate(regs)]


def bare(w): return re.sub(r"[^\wáéíóúñü]", "", w.lower())
TEXT_FIXES = cfg.get("text_fixes", [])  # [{"at": seg, "text": "pregunta:"}] texto exacto (p. ej. conservar ":")


def show(w):
    for tf in TEXT_FIXES:
        if abs(w["s"] - tf["at"]) < 0.1: return tf["text"]
    t = re.sub(r"[.,;:!¡]", "", w["w"]).strip()
    if any(abs(w["s"] - x) < 0.1 for x in IDEA_START): t = t[:1].upper() + t[1:]
    return BRAND.get(bare(t), t)
def emph_kind(w):
    for e in ENFASIS:
        if bare(w["w"]) == bare(e[0]) and abs(w["s"] - e[1]) < 0.35: return 2 if len(e) > 2 and e[2] == "alt" else 1
    return 0
def is_emph(w): return emph_kind(w) > 0


out = {"fps": FPS, "clips": [], "captions": [], "photos": []}
f = 0


# ---- Cuerpo: tramos, silencios recortados y un encuadre distinto por corte ----
subs = []  # (src_a, src_b, out_start, idea)
k = 0; prev_z = None
for ci, c in enumerate(CLIPS):
    rngs = speech_ranges(*c["src"])
    # PROTEGER PALABRAS (se notaban cortadas al final de frase y por dentro en las oclusivas):
    # 1) nunca cortar dentro de una palabra (las oclusivas t/k/p/g dejan micro-silencios que parecen pausas)
    inner = [(w["s"] + 0.03, w["e"] - 0.03) for w in words if c["src"][0] <= w["s"] < c["src"][1]]
    merged = [list(rngs[0])]
    for a2, b2 in rngs[1:]:
        # solo micro-pausas (< INNER_MAX, cierres de t/k/p/g) dentro de una palabra; una pausa más larga es
        # silencio real aunque Whisper "estire" la palabra encima
        if (a2 - merged[-1][1]) + 2 * INNER_PAD < INNER_MAX and any(ws < a2 and we > merged[-1][1] for ws, we in inner): merged[-1][1] = b2
        else: merged.append([a2, b2])
    rngs = [tuple(r) for r in merged]
    # 1b) inicios suaves (j, s, f: casi solo aire) quedan por debajo del umbral: si una palabra empieza
    #     hasta 0,15 s antes del trozo, el trozo retrocede hasta su inicio (máx. 0,12 s)
    starts = [w["s"] for w in words if c["src"][0] <= w["s"] < c["src"][1]]
    for i, (ra, rb) in enumerate(rngs):
        near = [st for st in starts if ra - 0.15 <= st < ra + 0.02]
        if near:
            na = max(min(near) - 0.01, ra - 0.12, c["src"][0], rngs[i - 1][1] if i else -1)
            rngs[i] = (min(ra, na), rb)
    # 2) el final de la frase llega hasta el final de su última palabra + END_PAD (se dice más suave)
    ends = [w["e"] for w in words if c["src"][0] <= w["s"] < c["src"][1]]
    if ends: rngs[-1] = (rngs[-1][0], min(c["src"][1], max(rngs[-1][1], max(ends) + END_PAD)))
    if "tail" in c:  # margen extra al final del tramo (p. ej. una "s" final suave que el corte se comía)
        rngs[-1] = (rngs[-1][0], min(c["src"][1], rngs[-1][1] + c["tail"]))
    cuts = {t: z for t, z in c.get("steps", [])}  # cambios de plano forzados sin cortar audio
    split = []
    for a, b in rngs:
        pts = [t for t in sorted(cuts) if a < t < b]
        edges = [a] + pts + [b]
        split += [(edges[i], edges[i + 1], cuts.get(edges[i])) for i in range(len(edges) - 1)]
    for j, (a, b, forced) in enumerate(split):
        dur = round(b * FPS) - round(a * FPS)
        if dur <= 0: continue
        prev_short = j > 0 and out["clips"] and out["clips"][-1]["dur"] < MIN_SHOT * FPS
        this_short = dur < MIN_SHOT * FPS and j > 0
        if forced is not None: z = forced
        elif j == 0 and "zoom" in c: z = c["zoom"]
        elif (prev_short or this_short or c.get("hold_zoom")) and prev_z is not None: z = prev_z
        elif "steps" in c and prev_z is not None: z = prev_z  # dentro de una escalera: solo cambia en los steps (saltos de 0,07 se ven como error)
        else:
            z = FRAMINGS[k % len(FRAMINGS)]
            nxt = CLIPS[ci + 1].get("zoom") if j == len(split) - 1 and ci + 1 < len(CLIPS) else None
            tries = 0
            while tries < len(FRAMINGS) and ((prev_z is not None and abs(z - prev_z) < MIN_ZOOM_JUMP)
                                             or (nxt is not None and abs(z - nxt) < MIN_ZOOM_JUMP)):
                k += 1; tries += 1; z = FRAMINGS[k % len(FRAMINGS)]
        k += 1; prev_z = z
        fx = c.get("fx", "punch") if j == 0 else "cut"
        out["clips"].append(dict(start=f, dur=dur, trim=round(a * FPS), zoom=z, fx=fx))
        subs.append((a, b, f, ci)); f += dur
# Remate opcional: la última toma sigue unos cuadros más (para que se vea un sticker final antes del fundido)
hold = round(cfg.get("end_hold", 0) * FPS)
if hold:
    out["clips"][-1]["dur"] += hold; f += hold
    a_, b_, o_, ci_ = subs[-1]; subs[-1] = (a_, b_ + hold / FPS, o_, ci_)
out["total"] = f
# Cierre: acercamiento suave a la cara desde end_push.at (seg. crudo) hasta end_push.to (sin fundido a negro)
ep = cfg.get("end_push")
if ep:
    last = out["clips"][-1]
    at = max(0, round(ep["at"] * FPS) - last["trim"])
    last["push"] = dict(at=min(at, last["dur"] - 2), to=ep["to"])


def src2out(t):
    for a, b, o, _ in subs:
        if t < b: return o + round((max(t, a) - a) * FPS)
    return f


def idea(w):
    for a, b, _, ci in subs:
        if w["e"] > a + 0.03 and w["s"] < b - 0.03: return ci
    return None


# ---- Subtítulos: 1-3 palabras, énfasis solos y en amarillo, cortes en cada idea ----
ws = [w for w in words if idea(w) is not None]
chunks, cur = [], []
for w in ws:
    emph = is_emph(w)
    if cur:
        last = cur[-1][0]["w"]
        jump = idea(w) != idea(cur[-1][0]) or w["w"].strip()[:1].isupper() or w["w"].strip().startswith("¿")
        chars = sum(len(x[0]["w"]) for x in cur) + len(w["w"])
        brk = (jump or re.search(r"[,.?!]$", last.strip())
               or (emph and not all(x[1] or bare(x[0]["w"]) in SMALL for x in cur))
               or (cur[-1][1] and not emph) or sum(x[1] for x in cur) >= 2 or len(cur) >= 3
               or (chars > 16 and bare(last) not in SMALL))
        same_idea = idea(w) == idea(cur[-1][0])
        if bare(last) in KEEP_TOGETHER and same_idea: brk = False  # nombres van juntos aunque el 2º lleve mayúscula
        if brk: chunks.append(cur); cur = []
    cur.append((w, emph))
if cur: chunks.append(cur)
for j, ch in enumerate(chunks):
    s = src2out(ch[0][0]["s"]); e = src2out(ch[-1][0]["e"]) + 5
    if j + 1 < len(chunks): e = min(e, src2out(chunks[j + 1][0][0]["s"]))
    out["captions"].append(dict(words=[dict(t=show(x[0]), emph=x[1], alt=emph_kind(x[0]) == 2) for x in ch], start=s, end=max(e, s + 4)))

# ---- Fotos superpuestas (opcional): aparecen/se rasgan en segundos del video crudo ----
for p in cfg.get("photos", []):
    ph = dict(src=p["src"], start=src2out(p["show_at"]))
    if p.get("tear_at") is not None: ph["tearAt"] = src2out(p["tear_at"])
    else: ph["end"] = src2out(p["hide_at"])
    out["photos"].append(ph)

# ---- Stickers y sonidos sueltos (opcional): tiempos en segundos del video crudo ----
def out2src(fr):
    for c in out["clips"]:
        if c["start"] <= fr < c["start"] + c["dur"]: return (c["trim"] + fr - c["start"]) / FPS
    return None


head = None
out["stickers"] = []
for st in cfg.get("stickers", []):
    s0 = src2out(st["show_at"]); s1 = src2out(st["hide_at"])
    k = dict(kind=st["kind"], start=s0, dur=max(6, s1 - s0))
    for key in ("x", "y", "size"):
        if key in st: k[key] = st[key]
    for key, name in (("fall_at", "fallAt"), ("break_at", "breakAt")):
        if key in st: k[name] = src2out(st[key]) - s0
    k["sfx"] = [dict(src=a, at=src2out(t) - s0, volume=v) for a, t, v in st.get("sfx", [])]
    if st.get("follow_head"):  # posición de la cabeza cuadro a cuadro (scripts/head-track.py)
        head = head or json.load(open("work/head.json"))
        trk = []
        for fr in range(s0, s0 + k["dur"]):
            t = out2src(fr)
            i = min(max(0, round(((t if t is not None else st["show_at"]) - head["t0"]) * FPS)), len(head["pts"]) - 1)
            trk.append(head["pts"][i][:2])
        k["track"] = trk
    out["stickers"].append(k)
out["sounds"] = [dict(src=a, start=max(0, src2out(t) + round(off * FPS)), volume=v)
                 for a, t, v, off in ((x + [0])[:4] for x in cfg.get("sounds", []))]
out["shakes"] = [src2out(t) for t in cfg.get("shakes", [])]  # sacudidas de imagen (impactos)
# eco suave sobre una frase: [inicio, fin] en seg. crudos (el audio lo genera scripts/eco.py)
out["echo"] = [dict(start=src2out(e[0]), end=src2out(e[1])) for e in cfg.get("echo", [])]

# ---- Control: ningún corte cae sobre voz (sonido fuerte justo al lado del corte) ----
for i, c in enumerate(out["clips"]):
    a3, b3 = c["trim"] / FPS, (c["trim"] + c["dur"]) / FPS
    prev_end = out["clips"][i - 1]["trim"] + out["clips"][i - 1]["dur"] if i else None
    nxt = out["clips"][i + 1]["trim"] if i + 1 < len(out["clips"]) else None
    if prev_end != c["trim"]:
        k = int(a3 / HOP) - 1
        if 0 <= k < len(DB) and DB[k] > ONSET: print("AVISO corte sobre voz al entrar en %.2f (%.0f dB)" % (a3, DB[k] - FLOOR))
    if nxt is not None and nxt != c["trim"] + c["dur"]:
        k = int(b3 / HOP)
        if k < len(DB) and DB[k] > ONSET: print("AVISO corte sobre voz al salir en %.2f (%.0f dB)" % (b3, DB[k] - FLOOR))

# ---- Control: ninguna palabra conservada puede quedar recortada por un corte ----
kept = [(a3, b3) for a3, b3, _, _ in subs]
# (el inicio no se revisa: Whisper adelanta el inicio de la primera palabra de cada frase)
for w in ws:
    end_ok = any(a3 <= w["e"] - 0.03 <= b3 for a3, b3 in kept)
    pieces = [(a3, b3) for a3, b3 in kept if b3 > w["s"] + 0.08 and a3 < w["e"] - 0.05]
    split = len(pieces) > 1 and any(pieces[i][1] < pieces[i + 1][0] - 0.01 for i in range(len(pieces) - 1))
    if not end_ok or split:
        print("AVISO palabra %s: %s %.2f-%.2f" % ("partida" if split else "con el final cortado", w["w"], w["s"], w["e"]))
json.dump(out, open(cfg.get("output", "src/Reel/edit.json"), "w"), ensure_ascii=False, indent=1)
print("duración final: %.1f s, %d cortes" % (f / FPS, len(out["clips"])))
print(" | ".join(" ".join(("*" + w["t"] + "*") if w["emph"] else w["t"] for w in c["words"]) for c in out["captions"]))
