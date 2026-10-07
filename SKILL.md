---
name: editar-reel-fr
description: Edita videos crudos de Futuros Residentes / Doc Juanes (una persona hablando a cámara, guiones grabados) y los convierte en Reels verticales 9:16 dinámicos con Remotion. Corta claquetas, tomas falsas, repeticiones y silencios, limpia el audio, pone subtítulos palabra por palabra con énfasis de color que nunca tapan la cara, cambia de plano en cada corte y, si se pide, agrega fotos superpuestas (incluso rasgándose), emojis/stickers con efectos de sonido, destellos de luz en las transiciones y música libre de derechos. Úsalo siempre que la usuaria pase o mencione un video crudo, un "guion N", una grabación de Doc Juanes o Futuros Residentes, o pida editar, cortar, subtitular o dejar listo un video para Instagram/TikTok/Reels/Shorts, aunque no diga "Remotion" ni "skill".
---

# Editar Reel de Futuros Residentes / Doc Juanes

Antes de decidir nada editorial, lee `references/estilo.md`: ahí están sus preferencias y el porqué
de cada una. Si algo falla, revisa `references/problemas.md`: casi todo lo que puede salir mal ya
pasó una vez. Para música, `references/musica.md`.

## Cómo trabajar con ella
- Escríbele en español, claro y sin jerga técnica. Ella no programa: explícale qué ves y qué harás.
- **Antes de ejecutar, cuéntale el plan completo y espera su aprobación.** Puedes preparar y
  transcribir el crudo antes, para que el plan sea concreto.
- Tú no puedes escuchar audio. Verifica con mediciones y re-transcripciones, y pídele que escuche
  lo subjetivo: efectos de sonido, volumen de la música y cortes muy apretados.
- Muéstrale fotogramas y el MP4 en cada versión. Cuando pida un cambio, ubícalo en el segundo del
  video EDITADO que ella menciona (mapea con `src/Reel/edit.json`) y confirma qué frase es.
- **Nombres:** en el plan propón (o pídele) un **NOMBRE_CORTO** en mayúsculas con guiones bajos
  (p. ej. `JUANCHO_PASASTE`); es también el nombre de la carpeta del proyecto.
  - Mientras se revisa: cada versión con número para que no vea una vieja ("no percibe cambios"):
    `NOMBRE_CORTO_REEL_v2.mp4`, `NOMBRE_CORTO_PORTADA_1.jpg`… En Descargas, solo la última versión.
  - **Cuando ella apruebe la versión definitiva**, renómbralos quitando todo lo demás, incluido el
    número: **`NOMBRE_CORTO_REEL.mp4`** y **`NOMBRE_CORTO_PORTADA.jpg`**, y borra de Descargas las
    versiones y portadas descartadas.
  - **Portada: en cuanto ella elige una, renómbrala de inmediato a `NOMBRE_CORTO_PORTADA.jpg`** (sin
    número), en Descargas y en `out/portadas/`, aunque el video siga en revisión, y quita las demás
    opciones. Si después pide ajustes a la elegida, sobrescribe ese mismo archivo sin número.
  - **Imágenes de prueba** que le envías (fuentes, colores, luz, efectos, fotogramas de revisión):
    `NOMBRE_CORTO_PRUEBA_<TEMA>_N.jpg` (p. ej. `NOMBRE_CORTO_PRUEBA_FUENTES_1.jpg`). Al aprobar la versión
    definitiva, bórralas igual que las versiones descartadas: solo quedan el REEL y la PORTADA.
- **Música:** no todos los videos llevan; solo si la pide. **Nunca repitas una canción** ya usada
  (lista en `references/musica.md`), salvo que ella diga que se puede reciclar.
- **Antes de cambiar este skill, pregúntale siempre** y espera su sí: dile en una línea qué cambiarías
  y por qué sirve para todos los videos. Lo puntual de un video (canción, tiempos, posiciones,
  volúmenes) va solo en su proyecto, nunca en el skill. Si ella misma pide el cambio, ya está aprobado.
- Los programas interactivos (como `npx create-video`) corren en una pestaña del panel Terminal:
  dile que haga clic en la pestaña y responda ahí, explicándole cada pregunta.

## Paso 0: Herramientas (una vez por máquina)
```bash
source ~/.claude/skills/editar-reel-fr/scripts/setup-tools.sh   # exporta $PY y $FF
```
Instala ffmpeg completo, faster-whisper, DeepFilterNet (quita eco) y OpenCV en un entorno propio.
La primera transcripción descarga el modelo large-v3-turbo (~1,6 GB): pide permiso antes.

## Paso 1: Proyecto Remotion
- Proyectos en **Películas → Reels Doc Juanes → NOMBRE_CORTO** (uno por video).
- Lo más rápido: copia `package.json`, `package-lock.json`, `tsconfig.json`, `remotion.config.ts`,
  `src/index.ts`, `src/index.css` y `src/Root.tsx` de un proyecto anterior, y `node_modules` con
  `cp -c -R` (clon instantáneo). Sin proyecto previo: `npx create-video@latest` (Blank, Tailwind Yes),
  `npm i` y `npm i @remotion/google-fonts@<versión de remotion>`.
- Plantilla y scripts: `cp -R ~/.claude/skills/editar-reel-fr/assets/template/src/Reel src/Reel` y
  `mkdir -p scripts && cp ~/.claude/skills/editar-reel-fr/scripts/* scripts/`.
- Registra la composición (ver `assets/template/Root.snippet.tsx`) y `"resolveJsonModule": true`.

## Paso 2: Preparar el crudo
1. Extrae un fotograma (`$FF -ss 20 -i crudo -frames:v 1 x.jpg`) y míralo: orientación (si la
   persona sale de lado usa `ccw`/`cw`), **color de la pared** (decide el color de las palabras clave)
   y posición de la cara (`FACE_ORIGIN`).
2. `FF=$FF ./scripts/prep.sh "<crudo>" <none|ccw|cw>` → `public/video-vertical.mp4` (con la curva de
   iluminación que aclara sombras; `LIGHT=0` la quita) + audios en `work/`.

3. **Si pide mejorar el fondo o la luz** (fondo cargado, cara oscura por luz de arriba): `scripts/fondo-luz.py`
   separa a la persona con IA y crea `public/video-fondo.mp4` con fondo difuminado, luz de relleno que
   sigue la cara y, si se quiere, luces de colores tipo vitral en la pared. Ajustes en `edit-config.json`
   → `"fondo"` (ver el encabezado del script); se corre después de `build-edit.py` (solo procesa los
   tramos usados; **vuelve a correrlo si cambian los tramos**, o esos cuadros saldrán sin procesar) y se
   activa con `VIDEO_SRC = "video-fondo.mp4"`. Muéstrale antes un fotograma de prueba.
   Ella lo prefiere **sutil**: desenfoque leve (5), borde muy suave (14) y vitral/bokeh muy tenues.

## Paso 3: Transcribir y mapear
```bash
$PY scripts/transcribe.py          # frases con tiempos → work/transcript.json
$PY scripts/energy.py words        # volumen de cada palabra vs. su frase (+dB = énfasis)
```
Arma el mapa editorial y cuéntaselo en una lista corta:
- **Fuera:** claqueta ("Listo, guion N…"), tomas falsas ("otra vez", groserías, risas), frases
  repetidas (quédate con la toma más limpia; suele ser la última), arranques en falso, cierre ("listo").
- **Gancho:** la primera frase fuerte; va primero.
- Palabras estiradas (p. ej. "no" de 3 s), palabras raras o voz sin transcribir = tomas repetidas o
  arranques en falso: **re-transcribe esos tramos aislados** (WhisperModel sobre el pedazo de audio) y
  afina con `energy.py zoom <inicio> <fin>`.

## Paso 4: Audio
```bash
FF=$FF PY=$PY ./scripts/audio.sh   # voz con menos eco y natural (DeepFilterNet + expansor suave, −14 LUFS)
$PY scripts/energy.py              # mide sobre la voz limpia → cortes más apretados
$PY scripts/sfx-stickers.py        # solo si habrá stickers con sonido
$PY scripts/sfx-tear.py            # solo si habrá foto rasgándose
```

## Paso 5: `edit-config.json`: las decisiones editoriales
Base: `assets/edit-config.example.json`. Todos los tiempos en segundos del video CRUDO:
- `clips`: un tramo por frase o idea, en orden, con margen amplio. El script recorta los silencios
  dentro y fuera, **sin cortar nunca una palabra**. `fx`: `punch` (continuación), `whoosh` (cambio de
  tema), `leak` (destello de luz de sol con colores; para videos inspiradores, ver `estilo.md`),
  `flash` (destello blanco). `zoom` fija el plano de un tramo; `steps: [[seg, zoom], …]` es una
  escalera de planos sin cortar el audio. `hold_zoom: true` = un solo plano. `tail: 0.1` = margen
  extra al final del tramo si el corte se come una consonante final suave.
- `emphasis`: `[palabra, segundo]` de las palabras dichas con fuerza o clave (~1 cada 1,5-2 s).
- `word_fixes`: tiempos reales de una palabra. Después confirma que quedó DENTRO del tramo (si cae
  en el silencio previo, desaparece del subtítulo).
- `idea_start`: mayúscula de inicio de idea (afecta a toda palabra a < 0,1 s: si la siguiente está
  muy cerca, como "Y no", usa un tiempo justo antes de la primera).
- `text_fixes`: `[{"at": seg, "text": "pregunta:"}]` texto exacto de una palabra (p. ej. conservar ":").
- `brand_words` (protege "Futuros Residentes", "Doc Juanes"; agrega otras como "UdeA"),
  `small_extra` (palabras cortas que nunca van solas: "fue", "esa", "mi", "tan"…).
- `photos`: `{src, show_at, tear_at}` (se rasga) o `{src, show_at, hide_at}`.
- `stickers` (solo si los pide; ejemplo en `assets/edit-config.stickers.example.json`):
  `{kind, show_at, hide_at, x, y, size, sfx: [[archivo, seg, volumen]]}`. Tipos: `broken-heart`
  (`break_at`) y dibujos de `ART` en `src/Reel/Stickers.tsx`. Para uno nuevo, dibújalo como SVG propio
  (nunca emojis de Apple ni imágenes con derechos). Ponlos donde la persona mueve las manos (mira
  fotogramas), nunca sobre la cara ni los subtítulos. Si un efecto debe seguir la cabeza,
  `$PY scripts/head-track.py <inicio> <fin>` + `follow_head: true` dan su posición cuadro a cuadro (`track`).
- `sounds`: `[[archivo, seg, volumen, desfase_seg]]`; `shakes`: segundos con sacudida (impactos).
- `end_push: {at, to}`: **cierre por defecto**, acercamiento suave a la cara (~1,6) sin fundido a negro.
  `end_hold`: segundos extra al final.
- `speed`: si pide acelerar (ver Paso 7).
- **Fuente base** (palabras normales): Montserrat Black 900, blanca con borde negro. No cambia.
- **Palabras resaltadas: propónselas en el plan según el mood del video**, con 2-3 opciones sobre un
  fotograma real: **una sola fuente** o **dos fuentes** (p. ej. una elegante/serif para lo emotivo y una
  gordita para lo de impacto), con el **mismo color o colores distintos**. Fuentes y colores acordes al
  mood (inspirador, nostálgico, enérgico, cómico…). `EMPH_*` (primera) y `EMPH2_*` (segunda, palabras
  marcadas `"alt"` en `emphasis`) en `constants.ts`. **El color debe contrastar con la pared.**
- `echo`: `[[inicio, fin]]` eco suave en una frase de trascendencia (después: `$PY scripts/eco.py`).
  **Proponlo** si detectas una frase así, o aplícalo si ella lo pide.
- **Tono de luz según el mood** (`WARM` cálido / `COOL` frío en `constants.ts`, 0 = neutro): proponlo en el
  plan con una muestra (p. ej. sin / suave / intenso) y que ella elija.

```bash
python3 scripts/build-edit.py      # imprime duración, nº de cortes, avisos y TODOS los subtítulos
```
Si imprime **AVISO palabra con el final cortado / partida**, revisa (suele ser un inicio que Whisper
estiró: corrígelo con `word_fixes`). **AVISO corte sobre voz** = el límite del tramo (`src`) corta una
palabra o deja entrar un ruido de la toma vecina ("otra vez", chasquido de labios): mira `energy.py zoom`
y mueve ese límite. Pon los `src` con margen amplio hacia el silencio: el script encuentra el borde real
de la voz (extiende inicios y colas suaves) y nunca deja trozos sueltos < 0,25 s, que suenan a "sonidito". Revisa los subtítulos: que no falten palabras al inicio de las
frases, ni haya duplicadas, ni palabras cortas solas, y que las marcas estén bien escritas.

**Aprobación del texto (obligatoria, antes de exportar):** cuando tengas los fragmentos finales, envíale
el **texto completo** del video, frase por frase, con las **palabras a resaltar marcadas** (y, si hay dos
fuentes, cuál lleva cada una). Espera su aprobación o sus correcciones antes de exportar la primera versión.

## Paso 6: Revisar antes de exportar
- `npx tsc --noEmit`.
- Fotogramas clave: `SCALE=0.35 node scripts/stills.mjs work <frames…>` y únelos con `hstack`.
  Revisa que los subtítulos nunca tapen la cara, que cada corte cambie de plano y que los efectos se vean bien.

## Paso 7: Exportar y verificar
```bash
npx remotion render Reel out/<NOMBRE_CORTO>_REEL_v<N>.mp4 --codec=h264 --crf=18 --concurrency=4
FF=$FF PY=$PY ./scripts/verify.sh out/<NOMBRE_CORTO>_REEL_v<N>.mp4    # 1080x1920, −14 LUFS, re-transcripción
$PY scripts/voz-sola.py                                     # re-transcripción de la voz editada sin efectos
```
Si `verify.sh` oye una palabra distinta pero `voz-sola.py` la oye bien, es un efecto o la música encima,
no un corte. **Acelerar** (si lo pide): exporta a `work/base_vN.mp4` con crf 16 y luego
`FF=$FF ./scripts/speed.sh work/base_vN.mp4 out/<NOMBRE_CORTO>_REEL_vN.mp4 <factor>` (todo sincronizado, la voz
no cambia de tono). Los renders largos van en segundo plano. Envíale el MP4, resume los cambios en
viñetas cortas y deja la copia en Descargas.

## Paso 8: Portadas (siempre, sin que ella lo pida)
Con la primera versión del video (o cuando la apruebe), **propónle 3 portadas** distintas:
- Fotogramas con buena expresión (ojos abiertos, sonrisa o gesto que invite), revisados antes en una tira
  de miniaturas. Cada opción con un fotograma y un ángulo de texto distinto (el gancho, la frase emotiva,
  la invitación final), siempre fiel a lo que él dice.
- Plantilla `src/Cover.tsx` (registrada como composición `Cover`, ver `Root.snippet.tsx`): usa el MISMO
  estilo del video (cuadro con su luz y tono, fuentes y colores de los resaltados).
  `npx remotion still Cover out/portadas/portada-N.jpg --props='{"frame":…,"zoom":1.1,"kicker":"…","big":"…","sub":"…","bigFirst":true,"alt":false}'`
  (`frame` = segundo del crudo × 25; `alt` usa la 2.ª fuente). El texto queda dentro de la zona 4:5 de la
  cuadrícula de Instagram; equilibra los renglones para que no quede una palabra sola.
- Entrega las 3 como imagen (`NOMBRE_CORTO_PORTADA_1.jpg`, `_2`, `_3`); apenas elija una,
  renómbrala ya a **`NOMBRE_CORTO_PORTADA.jpg`** (sin número, sin esperar a que apruebe el video) y el video **sin**
  portada (ella la sube a mano en Instagram: "Editar portada → Agregar desde la galería"). Solo si lo pide,
  `FF=$FF ./scripts/portada.sh portada.jpg video.mp4 salida.mp4` la pone como primer cuadro (0,12 s).

## Pedidos frecuentes
- **"Corta el segundo X":** mapea X en `edit.json` → tramo y frase; re-transcribe ese pedazo; corrige
  `clips`/`word_fixes` y vuelve a exportar.
- **"Más corto / menos silencios":** los valores por defecto ya son apretados. Mide los silencios que
  quedan en la voz editada antes de tocar nada; si casi no hay, lo que queda es el ritmo natural del
  habla: ofrécele acelerar 5-8 % o quitar una frase.
- **"Se cortan las palabras":** primero el audio (un expansor/compuerta rápida suena a palabras
  cortadas), luego los cortes (`AVISO` de `build-edit.py`, final de frase, `tail`).
- **"Tiene eco":** ya lo corrige `audio.sh`. **No** lo endurezcas con un expansor rápido. Si pide más o
  menos limpieza, hazle 3 pruebas cortas (A/B/C, 15 s, solo voz, en Descargas) y que elija con el oído.
- **"Está oscuro":** sube el punto 0.4/0.5 de la curva de `prep.sh`.
- **"Más dinámico":** más `steps` y más contraste entre planos; nada de movimiento dentro de la toma.
- **Música:** `references/musica.md`.
- **Foto de alguien:** búscala en Descargas (`image*.png` recientes), mejórala con
  `FF=$FF ./scripts/enhance-photo.sh <foto> public/<nombre>-mejorada.jpg` y muéstrale antes/después.
- **Trabajar desde el iPad:** no puede editar ahí (iPadOS no ejecuta estas herramientas). Con Remote
  Control da las instrucciones desde el iPad y el Mac (encendido, app abierta) edita.
