# Página de revisión de un Reel: el video arriba y el texto abajo (los subtítulos de src/Reel/edit.json), palabra por palabra y
# sincronizado con el video. Janeth marca en el texto (selecciona una palabra o frase) o en el video (lo pausa en el punto) qué
# hay que cortar, qué se oye mal o una nota, y copia la lista para pegarla en el chat: cada marca trae el segundo del video final
# y la frase, y se corrige como «Corta el segundo X» (mapea el segundo en edit.json → tramo y frase).
# Uso (desde la carpeta del proyecto, después del render): "$PY" scripts/revision.py out/NOMBRE_CORTO_REEL_vN.mp4 [velocidad]
#   → out/NOMBRE_CORTO_REEL_vN_REVISION.html junto al video (se abre con doble clic; es local, no se publica).
#   velocidad: el factor de speed.sh si el video se aceleró (p. ej. 1.06), para que el texto siga al video.
import html, json, os, sys

VIDEO = sys.argv[1]
VEL = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
SALIDA = VIDEO[:-4] + "_REVISION.html"
ed = json.load(open("src/Reel/edit.json", encoding="utf-8"))
fps = ed.get("fps", 25)
cortes = sorted(c["start"] for c in ed.get("clips", []))  # un párrafo por tramo del video
bloques, n = [], 0
for k, cap in enumerate(ed["captions"]):
    a, b = cap["start"] / fps / VEL, cap["end"] / fps / VEL
    nuevo = not bloques or any(bloques[-1]["f0"] < c <= cap["start"] for c in cortes)
    if nuevo:
        bloques.append({"tipo": "voz", "pid": "", "quien": "", "t": round(a, 2), "palabras": [], "f0": cap["start"]})
    ws = cap["words"]; d = (b - a) / max(1, len(ws))
    for j, w in enumerate(ws):  # el subtítulo no trae el tiempo de cada palabra: se reparte el tramo del subtítulo
        bloques[-1]["palabras"].append([n, w["t"], round(a + j * d, 2), round(a + (j + 1) * d, 2)]); n += 1
    bloques[-1]["f0"] = cap["start"]
for x in bloques: x.pop("f0")
DATOS = json.dumps({"video": os.path.basename(VIDEO), "reel": True, "bloques": bloques}, ensure_ascii=False)
NOMBRE = html.escape(os.path.basename(VIDEO)[:-4])

PAGINA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revisión __NOMBRE__</title>
<style>
:root { --fondo:#f8f2e2; --tinta:#1f3550; --azul:#2f6aa3; --agua:#6fb3b8; --suave:#e9e0c8; --marca:#ffd9a8; --mal:#ffc2c2; --nota:#cfe6ff; --ahora:#bfe3e5; }
* { box-sizing:border-box; }
body { margin:0; background:var(--fondo); color:var(--tinta); font:16px/1.6 -apple-system, "Segoe UI", Poppins, sans-serif; }
header { position:sticky; top:0; z-index:5; background:var(--fondo); border-bottom:2px solid var(--suave); padding:10px 16px; }
.fila { display:flex; gap:16px; align-items:flex-start; max-width:1400px; margin:0 auto; }
video { width:min(640px, 55vw); max-height:62vh; object-fit:contain; border-radius:10px; background:#000; }
.panel { flex:1; min-width:260px; }
h1 { font-size:18px; margin:0 0 6px; }
.ayuda { font-size:13px; opacity:.8; margin:0 0 8px; }
button { font:inherit; font-size:14px; border:0; border-radius:8px; padding:7px 12px; margin:0 6px 6px 0; cursor:pointer; color:var(--tinta); }
.b-cortar { background:var(--marca); } .b-mal { background:var(--mal); } .b-nota { background:var(--nota); } 
.b-copiar { background:var(--azul); color:#fff; }
#marcas { max-height:28vh; overflow:auto; font-size:13px; margin:0; padding-left:20px; }
#marcas li { margin-bottom:4px; } #marcas .x { background:none; padding:0 4px; margin:0; opacity:.6; }
main { max-width:900px; margin:0 auto; padding:12px 16px 120px; }
.card { margin:26px 0 8px; padding:10px 14px; border-left:4px solid var(--agua); background:#fffaf0; border-radius:6px; cursor:pointer; }
.card small { display:block; letter-spacing:.12em; text-transform:uppercase; font-size:11px; color:var(--agua); }
.card b { color:var(--azul); }
.voz { margin:8px 0 14px; }
.quien { font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:.05em; margin-right:6px; cursor:pointer; }
.min { font-size:12px; opacity:.6; margin-right:6px; }
.w { cursor:pointer; border-radius:4px; padding:0 1px; }
.w:hover { background:var(--suave); }
.w.ahora { background:var(--ahora); }
.w.cortar { background:var(--marca); text-decoration:line-through; } .w.mal { background:var(--mal); } .w.nota { background:var(--nota); }
@media (max-width:800px) { .fila { flex-direction:column; } video { width:100%; } }
</style></head>
<body>
<header><div class="fila">
  <video id="v" src="__VIDEO__" controls preload="metadata"></video>
  <div class="panel">
    <h1>Revisión · __NOMBRE__</h1>
    <p class="ayuda">Clic en una palabra = el video salta ahí. Para marcar hay dos formas: <b>en el texto</b>, selecciona la palabra o la frase con el mouse;
    <b>en el video</b>, páusalo en el punto (sirve para algo raro que se ve o se oye sin palabra: un zoom extraño, alguien que aparece, un golpe, una respiración). Luego elige qué pasa.
    Al terminar: «Copiar correcciones» y pégalas en el chat.</p>
    <p id="objetivo" class="ayuda"></p>
    <button class="b-cortar" onclick="marcar('cortar')">✂ Cortar</button>
    <button class="b-mal" onclick="marcar('mal')">🔇 Se oye mal</button>
    <button class="b-nota" onclick="marcar('nota')">✎ Nota</button>
    <button class="b-copiar" onclick="copiar()">Copiar correcciones</button>
    <ol id="marcas"></ol>
  </div>
</div></header>
<main id="guion"></main>
<script>
const D = __DATOS__;
const v = document.getElementById('v'), G = document.getElementById('guion'), L = document.getElementById('marcas');
const CLAVE = 'revision_' + D.video;
let marcas = [];
try { marcas = JSON.parse(localStorage.getItem(CLAVE) || '[]'); } catch (e) {}
const mmss = s => { const m = Math.floor(s / 60), x = (s - m * 60).toFixed(1); return m + ':' + (x < 10 ? '0' : '') + x; };
const ir = s => { v.currentTime = Math.max(0, s - 0.3); v.play(); };
const todas = [];
for (const b of D.bloques) {
  if (b.tipo === 'card') {
    const d = document.createElement('div'); d.className = 'card';
    d.innerHTML = (b.kicker ? '<small>' + b.kicker + '</small>' : '') + '<b>' + b.texto + '</b> <span class="min">' + mmss(b.t) + '</span>';
    d.onclick = () => ir(b.t + 0.3); G.appendChild(d);
  } else {
    const p = document.createElement('p'); p.className = 'voz';
    const q = document.createElement('span'); q.className = 'quien'; q.textContent = b.quien || '▶'; q.onclick = () => ir(b.t + 0.3); p.appendChild(q);
    const m = document.createElement('span'); m.className = 'min'; m.textContent = mmss(b.t); p.appendChild(m);
    for (const [i, txt, t0, t1] of b.palabras) {
      const s = document.createElement('span'); s.className = 'w'; s.textContent = txt;
      s.dataset.pid = b.pid; s.dataset.i = i; s.dataset.t0 = t0; s.dataset.t1 = t1;
      s.onclick = () => { if (!String(window.getSelection()).trim()) ir(t0); };
      p.appendChild(s); p.appendChild(document.createTextNode(' ')); todas.push(s);
    }
    G.appendChild(p);
  }
}
function seleccionadas() {
  const sel = window.getSelection();
  if (sel && !sel.isCollapsed) {
    const r = sel.getRangeAt(0), ws = todas.filter(s => r.intersectsNode(s));
    if (ws.length) return ws;
  }
  return null;
}
function enVideo() {  // la palabra que suena donde está el video (o la más cercana a menos de 0,6 s); puede no haber ninguna (tarjeta)
  const t = v.currentTime;
  let mejor = null, d = 0.6;
  for (const s of todas) {
    const x = t < +s.dataset.t0 ? +s.dataset.t0 - t : (t > +s.dataset.t1 ? t - +s.dataset.t1 : 0);
    if (x < d) { d = x; mejor = s; }
  }
  return mejor ? [mejor] : [];
}
function objetivo() {
  const ws = seleccionadas(), o = document.getElementById('objetivo');
  if (ws) o.innerHTML = 'Vas a marcar <b>en el texto</b>: «' + ws.map(s => s.textContent).join(' ').slice(0, 80) + '»';
  else { const w = enVideo(); o.innerHTML = 'Vas a marcar <b>en el video</b>, en ' + mmss(v.currentTime) + (w.length ? ' (suena «' + w[0].textContent + '»)' : ''); }
}
document.addEventListener('selectionchange', objetivo);
function marcar(tipo) {
  let ws = seleccionadas(), desde = 'texto', t;
  if (ws) t = +ws[0].dataset.t0;
  else { ws = enVideo(); desde = 'video'; t = +v.currentTime.toFixed(2); v.pause(); }
  const donde = desde === 'texto' ? '«' + ws.map(s => s.textContent).join(' ') + '»' : 'el video en ' + mmss(t);
  const nota = tipo === 'nota' ? prompt('¿Qué hay que hacer en ' + donde + '?') : (prompt('Comentario (opcional) sobre ' + donde + ':') || '');
  if (nota === null || (tipo === 'nota' && !nota)) return;
  const piezas = {};
  for (const s of ws) (piezas[s.dataset.pid] = piezas[s.dataset.pid] || []).push(+s.dataset.i);
  marcas.push({ tipo, t, desde, texto: ws.map(s => s.textContent).join(' '), piezas, nota });
  guardar(); window.getSelection().removeAllRanges();
}
function guardar() {
  marcas.sort((a, b) => a.t - b.t);
  try { localStorage.setItem(CLAVE, JSON.stringify(marcas)); } catch (e) {}
  pintar();
}
const NOMBRES = { cortar: 'CORTAR', mal: 'SE OYE MAL', nota: 'NOTA', sonido: 'SONIDO' };
function linea(m, n) {
  const pz = Object.entries(m.piezas).map(([p, is]) => p + ' ' + Math.min(...is) + (is.length > 1 ? '–' + Math.max(...is) : '')).join(', ');
  return n + '. ' + NOMBRES[m.tipo] + ' · ' + mmss(m.t) + (m.desde === 'video' ? ' (en el video' + (m.texto ? ', suena' : '') : '') + (m.texto ? (m.desde === 'video' ? ' «' + m.texto + '»)' : ' · «' + m.texto + '»') : (m.desde === 'video' ? ')' : '')) + (pz && !D.reel ? ' · [' + pz + ']' : '') + (m.nota ? ' · ' + m.nota : '') +
''; 
}
function pintar() {
  L.innerHTML = '';
  todas.forEach(s => s.classList.remove('cortar', 'mal', 'nota'));
  marcas.forEach((m, k) => {
    const li = document.createElement('li'); li.textContent = linea(m, k + 1).replace(/^\\d+\\. /, '');
    li.style.cursor = 'pointer'; li.onclick = () => ir(m.t);
    const x = document.createElement('button'); x.className = 'x'; x.textContent = '✕'; x.title = 'Quitar';
    x.onclick = e => { e.stopPropagation(); marcas.splice(k, 1); guardar(); };
    li.appendChild(x); L.appendChild(li);
    for (const [p, is] of Object.entries(m.piezas))
      todas.filter(s => s.dataset.pid === p && is.includes(+s.dataset.i)).forEach(s => s.classList.add(m.tipo === 'sonido' ? 'nota' : m.tipo));
  });
}
function copiar() {
  if (!marcas.length) { alert('Todavía no hay correcciones.'); return; }
  const txt = 'Correcciones de ' + D.video + ':\\n' + marcas.map((m, k) => linea(m, k + 1)).join('\\n');
  const listo = () => alert('Copiado. Pégalo en el chat con Claude.');
  if (navigator.clipboard) navigator.clipboard.writeText(txt).then(listo, () => prompt('Copia este texto:', txt));
  else prompt('Copia este texto:', txt);
}
let actual = null;
v.addEventListener('timeupdate', () => {
  if (!seleccionadas()) objetivo();
  const t = v.currentTime, s = todas.find(s => t >= +s.dataset.t0 && t <= +s.dataset.t1 + 0.05);
  if (s !== actual) {
    if (actual) actual.classList.remove('ahora');
    if (s) { s.classList.add('ahora'); const r = s.getBoundingClientRect(); if (r.top < 260 || r.bottom > innerHeight - 40) s.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
    actual = s;
  }
});
pintar(); objetivo();
</script>
</body></html>
"""
open(SALIDA, "w", encoding="utf-8").write(PAGINA.replace("__DATOS__", DATOS).replace("__VIDEO__", html.escape(os.path.basename(VIDEO))).replace("__NOMBRE__", NOMBRE))
print(f"{SALIDA}: {len(bloques)} tramos, {n} palabras")
