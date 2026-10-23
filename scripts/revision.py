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
:root { --fondo:#f8f2e2; --tinta:#1f3550; --azul:#2f6aa3; --agua:#6fb3b8; --suave:#e9e0c8; --marca:#ffd9a8; --mal:#ffc2c2; --nota:#cfe6ff; --sonido:#e2d4f5; --ahora:#bfe3e5; }
* { box-sizing:border-box; }
body { margin:0; background:var(--fondo); color:var(--tinta); font:16px/1.6 -apple-system, "Segoe UI", Poppins, sans-serif; }
header { position:sticky; top:0; z-index:5; background:var(--fondo); border-bottom:2px solid var(--suave); padding:10px 16px; }
.fila { display:flex; gap:16px; align-items:flex-start; max-width:1400px; margin:0 auto; }
video { height:min(86vh, 960px); width:auto; max-width:48vw; object-fit:contain; border-radius:10px; background:#000; }  /* reel vertical: entra completo en la pantalla */
.panel { flex:1; min-width:260px; }
h1 { font-size:18px; margin:0 0 6px; }
.ayuda { font-size:13px; opacity:.8; margin:0 0 8px; }
button { font:inherit; font-size:14px; border:0; border-radius:8px; padding:7px 12px; margin:0 6px 6px 0; cursor:pointer; color:var(--tinta); }
.b-cortar { background:var(--marca); } .b-mal { background:var(--mal); } .b-nota { background:var(--nota); } .b-sonido { background:var(--sonido); } 
.b-copiar { background:var(--azul); color:#fff; } .b-ini { background:var(--suave); }
select { font:inherit; font-size:14px; border-radius:8px; padding:6px; margin:0 6px 6px 0; border:1px solid var(--suave); background:#fffaf0; color:var(--tinta); }
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
.w.ahora { background:var(--ahora); } .w.elegida { outline:2px solid var(--azul); }
.w.cortar { background:var(--marca); text-decoration:line-through; } .w.mal { background:var(--mal); } .w.nota { background:var(--nota); } .w.sonido { background:var(--sonido); }
.g { display:inline-block; min-width:1.1em; height:1.25em; vertical-align:-.25em; border-radius:4px; cursor:pointer; text-align:center; font-size:12px; line-height:1.25em; color:#d6caa8; }
.g:hover { background:var(--suave); color:var(--tinta); }
.g.fin { min-width:1.6em; color:#b8a777; font-weight:700; }  /* espacio al final del renglón: más oscuro que los demás (Janeth, 18 oct, ALEX_LOPEZ_10FR: con el color --suave no se veía y no lo podía marcar) */
.g.sel { background:var(--azul); color:#fff; } .g.cortar { background:var(--marca); color:var(--tinta); } .g.mal { background:var(--mal); color:var(--tinta); } .g.nota { background:var(--nota); color:var(--tinta); } .g.sonido { background:var(--sonido); color:var(--tinta); }
@media (max-width:800px) { body { display:block; height:auto; overflow:visible; } header { position:sticky; height:auto; border-right:0; } main { height:auto; overflow:visible; } .fila { flex-direction:column; } video { width:100%; height:auto; max-width:none; max-height:70vh; } }
/* Reel vertical (Janeth, UNO_DE_CUATRO): video a la izquierda a toda la altura, botones al lado y el texto en su propia columna
   con scroll, grande y cómodo; antes el encabezado fijo con el video se comía la pantalla y el texto quedaba en una franja mínima */
@media (min-width:801px) {
  body { display:flex; height:100vh; overflow:hidden; }
  header { position:static; height:100vh; flex:0 0 auto; border-bottom:0; border-right:2px solid var(--suave); padding:10px 12px; }
  header .fila { height:100%; }
  video { height:calc(100vh - 20px); max-width:none; }
  .panel { width:270px; flex:0 0 270px; height:100%; overflow:auto; }
  #marcas { max-height:none; }
  main { flex:1; height:100vh; overflow:auto; max-width:none; padding:16px 28px 120px; font-size:20px; line-height:1.9; }
}
</style></head>
<body>
<header><div class="fila">
  <video id="v" src="__VIDEO__" controls preload="metadata"></video>
  <div class="panel">
    <h1>Revisión · __NOMBRE__</h1>
    <p id="objetivo" class="ayuda"></p>
    <br>
    <button class="b-cortar" onclick="marcar('cortar')">✂ Cortar</button>
    <button class="b-mal" onclick="marcar('mal')">🔇 Se oye mal</button>
    <button class="b-sonido" onclick="marcar('sonido')" title="Un ruido, golpe, respiración o sílaba suelta que hay que quitar: pausa el video justo ahí">🔊 Sonido</button>
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
const ir = s => { v.pause(); v.currentTime = Math.max(0, s); };  // salta y queda en pausa: sigue solo con play
const huecos = []; let gapSel = null;  // espacios entre palabras (y entre renglones), marcables
function hueco(prev, sig) {  // sig = null: después de la última palabra de una pieza (antes de la tarjeta o del final)
  const g = document.createElement('span'); g.className = 'g'; g.textContent = '·'; g.dataset.k = huecos.length;
  if (!prev) {  // prev = null: antes de la primera palabra del renglón, después de la tarjeta (Janeth, 20 oct, JANETH_CARDONA_10FR v3)
    g.title = 'Espacio antes de «' + sig.textContent + '» (comienzo del renglón)';
    g.dataset.t = Math.max(0, +sig.dataset.t0 - 0.12).toFixed(2);
    prev = { textContent: '(comienzo del renglón)', dataset: {} };
    g.onclick = e => { e.stopPropagation(); window.getSelection().removeAllRanges(); soltarPalabra(); elegirHueco(g); };
    g._prev = prev; g._sig = sig; huecos.push(g); return g;
  }
  const misma = sig && sig.dataset.pid === prev.dataset.pid;
  g.title = misma ? 'Espacio entre «' + prev.textContent + '» y «' + sig.textContent + '»' : 'Espacio después de «' + prev.textContent + '» (final del renglón)';
  g.dataset.t = (misma ? (+prev.dataset.t1 + +sig.dataset.t0) / 2 : +prev.dataset.t1 + 0.12).toFixed(2);
  if (!misma) sig = { textContent: '(final del renglón)', dataset: {} };
  g.onclick = e => { e.stopPropagation(); window.getSelection().removeAllRanges(); soltarPalabra(); elegirHueco(g); };
  g._prev = prev; g._sig = sig; huecos.push(g); return g;
}
function elegirHueco(g) {
  if (gapSel) gapSel.classList.remove('sel');
  gapSel = g; g.classList.add('sel'); ir(+g.dataset.t); objetivo();
}
function soltarHueco() { if (gapSel) gapSel.classList.remove('sel'); gapSel = null; }
let palSel = null;  // palabra elegida con un clic: es la que se marca (no la que el video crea que suena)
function elegirPalabra(s) {
  soltarHueco(); soltarPalabra(); palSel = s; s.classList.add('elegida');
  ir(+s.dataset.t0 + 0.02); resaltar(s); objetivo();
}
function soltarPalabra() { if (palSel) palSel.classList.remove('elegida'); palSel = null; }
const todas = [];
for (const b of D.bloques) {
  if (b.tipo === 'card') {
    const d = document.createElement('div'); d.className = 'card';
    d.innerHTML = (b.kicker ? '<small>' + b.kicker + '</small>' : '') + '<b>' + b.texto + '</b> <span class="min">' + mmss(b.t) + '</span>';
    d.onclick = () => ir(b.t + 0.3); G.appendChild(d);
  } else {
    const p = document.createElement('p'); p.className = 'voz';
    const q = document.createElement('span'); q.className = 'quien'; q.textContent = b.quien; q.onclick = () => ir(b.t + 0.3); p.appendChild(q);
    const m = document.createElement('span'); m.className = 'min'; m.textContent = mmss(b.t); p.appendChild(m);
    for (const [i, txt, t0, t1] of b.palabras) {
      const s = document.createElement('span'); s.className = 'w'; s.textContent = txt;
      s.dataset.pid = b.pid; s.dataset.i = i; s.dataset.t0 = t0; s.dataset.t1 = t1;
      s.onclick = () => { if (!String(window.getSelection()).trim()) elegirPalabra(s); };
      if (todas.length && todas[todas.length - 1].parentNode === p) {  // espacio entre dos palabras del mismo renglón
        p.appendChild(document.createTextNode(' ')); p.appendChild(hueco(todas[todas.length - 1], s)); p.appendChild(document.createTextNode(' '));
      } else {  // espacio al comienzo del renglón, antes de su primera palabra
        const g0 = hueco(null, s); g0.classList.add('fin'); p.appendChild(g0); p.appendChild(document.createTextNode(' '));
      }
      p.appendChild(s); todas.push(s);
    }
    if (p.querySelector('.w')) {  // espacio al final del renglón (después de su última palabra): siempre, también en el último
      const g = hueco(todas[todas.length - 1], null); g.classList.add('fin'); p.appendChild(document.createTextNode(' ')); p.appendChild(g);
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
  return palSel ? [palSel] : null;
}
function enVideo() {  // la palabra que suena donde está el video (o la más cercana a menos de 0,6 s); puede no haber ninguna (tarjeta)
  const t = v.currentTime;
  let mejor = null, d = 0.6;
  for (const s of todas) {
    const x = t < +s.dataset.t0 ? +s.dataset.t0 - t : (t > +s.dataset.t1 ? t - +s.dataset.t1 : 0);
    if (x < d || (x === 0 && t >= +s.dataset.t0 && t < +s.dataset.t1)) { d = x; mejor = s; }
  }
  return mejor ? [mejor] : [];
}
let ini = null, fin = null;  // inicio y fin del fragmento (segundos del video), si los hay
v.addEventListener('play', () => { soltarHueco(); soltarPalabra(); });
// Seleccionar texto con el mouse también detiene el video en la primera palabra elegida (sigue solo con play)
G.addEventListener('mouseup', () => {
  const sel = window.getSelection(); if (!sel || sel.isCollapsed) return;
  const r = sel.getRangeAt(0), ws = todas.filter(s => r.intersectsNode(s)); if (!ws.length) return;
  soltarHueco(); soltarPalabra(); ir(+ws[0].dataset.t0 + 0.02); resaltar(ws[0]); objetivo();
});
function inicio() { soltarHueco(); soltarPalabra(); ini = +v.currentTime.toFixed(2); fin = null; v.pause(); window.getSelection().removeAllRanges(); objetivo(); }
function final() {
  if (ini === null) { alert('Primero pausa donde empieza el fragmento y presiona «Inicio del fragmento».'); return; }
  fin = +v.currentTime.toFixed(2); v.pause(); window.getSelection().removeAllRanges(); objetivo();
}
function rango() { const b = fin !== null ? fin : +v.currentTime.toFixed(2); return [Math.min(ini, b), Math.max(ini, b)]; }
function enRango(a, b) { return todas.filter(s => +s.dataset.t1 > a && +s.dataset.t0 < b); }
function objetivo() {
  const ws = seleccionadas(), o = document.getElementById('objetivo');
  if (ws) soltarHueco();
  if (!ws && gapSel) o.innerHTML = 'Vas a marcar <b>el espacio</b> entre «' + gapSel._prev.textContent + '» y «' + gapSel._sig.textContent + '» (' + mmss(+gapSel.dataset.t) + '): «Cortar» si el silencio es muy largo, «Se oye mal» o «Sonido» si hay un ruido ahí';
  else if (ws) o.innerHTML = 'Vas a marcar <b>en el texto</b>: «' + ws.map(s => s.textContent).join(' ').slice(0, 80) + '»';
  else if (ini !== null) { const [a, b] = rango();
    o.innerHTML = 'Vas a marcar <b>el fragmento del video</b> de ' + mmss(a) + ' a ' + mmss(b) +
    (fin === null ? ' (pausa donde termina y presiona «Fin del fragmento»)' : ' · ya está listo: elige qué pasa') +
    ' <button class="x" onclick="ini=null;fin=null;objetivo()">✕ quitar fragmento</button>'; }
  else { const w = enVideo(); o.innerHTML = 'Vas a marcar <b>en el video</b>, en ' + mmss(v.currentTime) + (w.length ? ' (suena «' + w[0].textContent + '»)' : ''); }
}
document.addEventListener('selectionchange', objetivo);
function marcar(tipo) {
  let ws = seleccionadas(), desde = 'texto', t, hasta = null;
  if (!ws && gapSel) {
    const g = gapSel, donde = 'el espacio entre «' + g._prev.textContent + '» y «' + g._sig.textContent + '»';
    const nota = tipo === 'sonido' ? prompt('¿Qué sonido hay en ' + donde + '? (opcional: «golpe», «respiración», «sílaba suelta»…)', '') : tipo === 'nota' ? prompt('¿Qué hay que hacer en ' + donde + '?') : (prompt('Comentario (opcional) sobre ' + donde + ':') || '');
    if (nota === null || (tipo === 'nota' && !nota)) return;
    const piezas = {};
    for (const s of [g._prev, g._sig]) if (s.dataset.pid) (piezas[s.dataset.pid] = piezas[s.dataset.pid] || []).push(+s.dataset.i);
    marcas.push({ tipo, t: +g.dataset.t, fin: null, desde: 'espacio', que: '', texto: g._prev.textContent + ' | ' + g._sig.textContent, piezas, hueco: +g.dataset.k, nota });
    soltarHueco(); guardar(); objetivo(); return;
  }
  if (ws && tipo === 'sonido') { const u = ws[ws.length - 1]; if (Math.abs(v.currentTime - +u.dataset.t1) > 3) v.currentTime = +u.dataset.t1; ws = null; }  // un sonido va en el video: junto a la frase elegida
  if (ws) t = +ws[0].dataset.t0;
  else if (ini !== null) { desde = 'video'; v.pause(); [t, hasta] = rango(); ws = enRango(t, hasta); }
  else { ws = enVideo(); desde = 'video'; t = +v.currentTime.toFixed(2); v.pause(); }
  const donde = desde === 'texto' ? '«' + ws.map(s => s.textContent).join(' ') + '»' : (hasta !== null ? 'el fragmento ' + mmss(t) + '–' + mmss(hasta) : 'el video en ' + mmss(t));
  const nota = tipo === 'sonido' ? prompt('¿Qué sonido hay en ' + donde + '? (opcional: «golpe», «respiración», «sílaba suelta»…)', '') : tipo === 'nota' ? prompt('¿Qué hay que hacer en ' + donde + '?') : (prompt('Comentario (opcional) sobre ' + donde + ':') || '');
  if (nota === null || (tipo === 'nota' && !nota)) return;
  const piezas = {};
  for (const s of ws) (piezas[s.dataset.pid] = piezas[s.dataset.pid] || []).push(+s.dataset.i);
  marcas.push({ tipo, t, fin: hasta, desde, que: '', texto: ws.map(s => s.textContent).join(' '), piezas, nota });
  ini = null; fin = null; soltarPalabra(); guardar(); window.getSelection().removeAllRanges(); objetivo();
}
function guardar() {
  marcas.sort((a, b) => a.t - b.t);
  try { localStorage.setItem(CLAVE, JSON.stringify(marcas)); } catch (e) {}
  pintar();
}
const NOMBRES = { cortar: 'CORTAR', mal: 'SE OYE MAL', nota: 'NOTA', sonido: 'SONIDO' };
function linea(m, n) {
  const pz = D.reel ? '' : Object.entries(m.piezas).map(([p, is]) => p + ' ' + Math.min(...is) + (is.length > 1 ? '–' + Math.max(...is) : '')).join(', ');
  if (m.desde === 'espacio') return n + '. ' + ({ cortar: 'CORTAR ESPACIO', mal: 'SE OYE MAL EN EL ESPACIO', sonido: 'SONIDO EN EL ESPACIO', nota: 'NOTA EN EL ESPACIO' })[m.tipo] + ' · ' + mmss(m.t) + ' · entre «' + m.texto.split(' | ').join('» y «') + '»' + (pz ? ' · [' + pz + ']' : '') + (m.nota ? ' · ' + m.nota : '');
  return n + '. ' + NOMBRES[m.tipo] + (m.que ? ' ' + (m.que === 'sonido' ? 'SOLO EL SONIDO' : 'SOLO LA IMAGEN') : '') + ' · ' + mmss(m.t) + (m.fin != null ? '–' + mmss(m.fin) : '') + (m.desde === 'video' ? ' (en el video' + (m.texto ? ', suena' : '') : '') + (m.texto ? (m.desde === 'video' ? ' «' + m.texto + '»)' : ' · «' + m.texto + '»') : (m.desde === 'video' ? ')' : '')) + (pz ? ' · [' + pz + ']' : '') + (m.nota ? ' · ' + m.nota : '') +
''; 
}
function pintar() {
  L.innerHTML = '';
  todas.forEach(s => s.classList.remove('cortar', 'mal', 'nota', 'sonido'));
  huecos.forEach(g => g.classList.remove('cortar', 'mal', 'nota', 'sonido'));
  marcas.forEach((m, k) => {
    const li = document.createElement('li'); li.textContent = linea(m, k + 1).replace(/^\\d+\\. /, '');
    li.style.cursor = 'pointer'; li.onclick = () => ir(m.t);
    const x = document.createElement('button'); x.className = 'x'; x.textContent = '✕'; x.title = 'Quitar';
    x.onclick = e => { e.stopPropagation(); marcas.splice(k, 1); guardar(); };
    li.appendChild(x); L.appendChild(li);
    if (m.hueco != null && huecos[m.hueco]) { huecos[m.hueco].classList.add(m.tipo); return; }  // un espacio: se pinta el hueco, no las palabras
    for (const [p, is] of Object.entries(m.piezas))
      todas.filter(s => s.dataset.pid === p && is.includes(+s.dataset.i)).forEach(s => s.classList.add(m.tipo));
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
function resaltar(s) {
  if (s === actual) return;
  if (actual) actual.classList.remove('ahora');
  if (s) { s.classList.add('ahora'); const r = s.getBoundingClientRect(); if (r.top < (D.reel && innerWidth > 800 ? 40 : 260) || r.bottom > innerHeight - 40) s.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
  actual = s;
}
v.addEventListener('timeupdate', () => {
  if (!seleccionadas() && !gapSel) objetivo();
  if (v.paused) return;  // en pausa se queda resaltada la palabra elegida
  const t = v.currentTime;
  resaltar(todas.find(s => t >= +s.dataset.t0 && t < +s.dataset.t1) || todas.find(s => t >= +s.dataset.t0 && t <= +s.dataset.t1 + 0.05));
});
pintar(); objetivo();
</script>
</body></html>
"""
open(SALIDA, "w", encoding="utf-8").write(PAGINA.replace("__DATOS__", DATOS).replace("__VIDEO__", html.escape(os.path.basename(VIDEO))).replace("__NOMBRE__", NOMBRE))
print(f"{SALIDA}: {len(bloques)} tramos, {n} palabras")
