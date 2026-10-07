# Música de fondo (solo si quien pide el video la quiere)

## Reglas
- **No todos los videos llevan música.** Pregunta o espera a que la pida.
- **Nunca repitas una canción ya usada** (lista abajo), salvo que Janeth autorice reciclarla.
- Siempre libre de derechos: CC0 / dominio público, o licencia comercial clara sin atribución.
  Verifica la licencia en la página de cada canción ("License:"), no en el listado.
- Si pide una canción comercial ("como Demons de Imagine Dragons"), explícale que tiene derechos y
  ofrece las alternativas libres más cercanas en espíritu.
- Pregúntale el mood del video; no asumas el género. El rock denso, aunque vaya bajo, puede sonar a
  "ruido de fondo"; ritmos con más espacio (funk, cinematográfico suave) acompañan mejor la voz.
- Evitar: clásica, navidad, infantil, ukulele, palmas, "corporate", videojuego/8-bit, circo, metal,
  agresivas, tristes u oscuras (salvo que el video lo pida).

## Cómo buscar (Chosic, filtro "sin atribución")
1. En el navegador integrado: `https://www.chosic.com/free-music/<tag>/?sort=&attribution=no`.
   Etiquetas que existen: `funky`, `energetic`, `upbeat`, `dance`, `hype`, `rock`, `lofi`, `uplifting`,
   `cinematic`, `motivational`, `epic`. (`funk`, `inspirational`, `inspiring` no existen o cuelgan.)
2. Leer la lista con JavaScript, esperando ~4 s a que cargue (título, artista, duración, enlace
   `/download-audio/<id>/`). Si un listado cuelga el navegador, abre otra pestaña y entra directo a las
   páginas `/download-audio/<id>/`. Pocas peticiones y espaciadas (Chosic bloquea con 429).
3. En la página de cada candidata leer "Track Tags … Track Info" y "License:".
4. Proponer 3-4 opciones con enlace para que la persona las escuche, describirlas en una línea y recomendar una.
5. Descargar solo la elegida (es su aprobación): la URL está en `data-url` de la página; curl con
   `-A "Mozilla/5.0"` y `-e <página>`. FreePD cerró; Canva no sirve (no permite extraer la música).
- Si aparece un aviso del llavero "Chrome Safe Storage" (importar cookies): no hace falta, que lo cancele.
  Nunca pedirle esa contraseña en el chat.

## Segunda fuente: Pixabay Music (sobre todo piano y estilos que Chosic casi no tiene en CC0)
- Licencia de Pixabay: uso gratuito, comercial y monetizado, sin atribución. Janeth lo aprobó **solo** con
  canciones gratuitas que no generen reclamos de derechos.
- **Descartar toda canción con "Content ID Registered"** en su página: Instagram/YouTube marcarían el video.
  La mayoría lo tiene; revisa cada candidata.
- Buscar: `https://pixabay.com/music/search/<términos>/`. Con JavaScript en la página se pueden revisar
  varias candidatas con `fetch('/music/<slug>/')` buscando "Content ID Registered", el título y el
  `"name":"Mood","value":"…"`. El MP3 está en la página como `https://cdn.pixabay.com/audio/…mp3`
  (descargar con curl `-A "Mozilla/5.0"` y `-e <página>`).

## Ajustar
- Original en `work/`; en `public/musica.mp3` una versión con hueco de ecualización para la voz:
  `equalizer=f=2500:t=q:w=1.2:g=-7,equalizer=f=1200:t=q:w=1:g=-4,equalizer=f=300:t=q:w=1:g=-2`.
- Medir la energía cada 3 s para elegir `MUSICA_INICIO_SEG` (donde ya suena la banda completa, o la
  parte más fuerte si la piden).
- `VOLUMEN_MUSICA` según la fuerza de esa parte: mide "música X dB bajo la voz" y apunta a ~18-23 dB.
- Anotar título, artista, licencia y URL en `constants.ts` del proyecto.

## Canciones ya usadas (no repetir)
| Video | Canción | Artista | Chosic |
|---|---|---|---|
| Guion 6 | Be A Good Punk | Monplaisir | `/download-audio/25202/` |
| Guion 7 (EL_MEDICO_DEL_PUEBLO) | Friend To Friend | Loyalty Freak Music | `/download-audio/24540/` |
| Guion 9 (YA_SABIA_QUE_IBA_A_PASAR) | Hope And Love | Loyalty Freak Music | `/download-audio/24475/` |
| Guion 10 (JUANCHO_PASASTE) | Ambiant Hope | Komiku | `/download-audio/25470/` |
| Guion 14 | Emotional Piano | prettyjohn1 (Pixabay) | `pixabay.com/music/solo-piano-emotional-piano-487334/` |
| Guion 5 (FORMULA_EXITO) | Positive Acoustic Guitar with Soft Beat | JorisVermeer (Pixabay) | `pixabay.com/music/beats-positive-acoustic-guitar-with-soft-beat-526509/` |
| Guion 3 (SACRIFICIO) | Inspirational Emotional | prettyjohn1 (Pixabay) | `pixabay.com/music/orchestral-inspirational-emotional-580034/` |

Probadas y rechazadas por Janeth (no volver a proponer): Ghost Surf Rock (Loyalty Freak Music),
Powerful Stasis (Soft and Furious).
