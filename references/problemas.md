# Problemas conocidos y soluciones

| Síntoma | Causa | Solución |
|---|---|---|
| El video se ve acostado (persona de lado) | La cámara grabó en vertical pero el archivo quedó 3840x2160 sin metadato de rotación | `prep.sh <crudo> ccw` (cabeza a la derecha) o `cw` (cabeza a la izquierda). Mira un fotograma antes. |
| En el render final el video sale corrido/pequeño con franjas negras, aunque en el Studio se ve bien | Rotar con CSS (`rotate(-90deg)`) en `OffthreadVideo` falla al renderizar | Nunca rotar por CSS: usar la copia vertical que genera `prep.sh`. |
| Studio lento o se congela | Decodificar 4K en un M1 de 8 GB | La copia 1440x2560 de `prep.sh` lo resuelve. Borrar la copia 4K de `public/` después. |
| `installWhisperCpp` falla: `cmake` no existe, o "ld: tapi error… unknown architecture arm64e" | Command Line Tools desajustadas con el SDK de macOS | No compilar: usar `faster-whisper` (wheels ya compilados) vía `setup-tools.sh`. |
| ffmpeg: "No such filter: afftdn/highpass/…" | El ffmpeg que trae Remotion es mínimo | Usar el ffmpeg completo de `imageio-ffmpeg` (`$FF` de `setup-tools.sh`). |
| En zsh: "Unrecognized option 'hide_banner -loglevel error -y'" | zsh no divide variables de texto | Usar arrays (`Q=(-hide_banner …)`) o `${=Q}`. |
| Falta la primera palabra de una frase en los subtítulos ("Nos", "Los", "¿Qué") | Whisper adelanta el inicio de la primera palabra y cae antes del corte | `build-edit.py` ya incluye palabras que se solapan con el tramo; si aún falta, `word_fixes` con el tiempo real (mírala con `energy.py zoom`). |
| Una palabra aparece dos veces | Una palabra "estirada" por Whisper cruza dos tramos | `word_fixes` con los tiempos reales (re-transcribe el tramo aislado para verlos). |
| Una palabra suave ("y") no se oye | Compuerta de ruido dura, o el whoosh le cae encima | Compuerta suave (ya en `audio.sh`); whoosh termina en el corte (ya en la plantilla). |
| La primera palabra de una idea sale en minúscula | Whisper la escribió así (p. ej. "y eso es…") | Agregar su tiempo a `idea_start`. |
| Error "inputRange must be strictly monotonically increasing" | Un `push` que empieza después de que termina el tramo | La plantilla ya lo evita (`push.at < dur - 1`). |
| `renderStill` da 404 en `public/…` | Archivos de `public/` como enlaces simbólicos | Copiar (o `cp -c`) en lugar de enlazar. |
| Chosic devuelve 429 | Demasiadas peticiones seguidas | Usar las páginas por categoría (`/free-music/<tag>/?attribution=no`), no consultar canción por canción. |
| La usuaria no ve cambios en el Studio | El Studio se detuvo | Reabrir con `npm run dev` en una pestaña de terminal y navegar a `localhost:3000/Reel`. |
| Se oye mucho eco / cuarto vacío | Reverberación de la sala | `audio.sh` con DeepFilterNet3 + expansor (ver `estilo.md`). Mide la cola tras cada frase. |
| `deepFilter`: "No module named torch" o error de torchaudio | Falta PyTorch o versión nueva incompatible | `$PY -m pip install deepfilternet "torch==2.0.1" "torchaudio==2.0.2"` |
| `cv2` sin `CascadeClassifier` | OpenCV 5 lo quitó | `$PY -m pip install "opencv-python-headless<5"` |
| La re-transcripción cambia una palabra del final de frase | Un whoosh, la música o un efecto encima, o el corte se comió una consonante final suave | `voz-sola.py` separa las causas: si la voz sola está bien, es el sonido encima; si no, `tail` en el tramo. |
| Un efecto de sonido se corta | Estaba dentro de la secuencia del sticker y terminó con él | La plantilla ya los monta fuera; si agregas otro, igual. |
| Video más corto de lo esperado tras pruebas | `energy.json` se regeneró desde otro audio | Corre `$PY scripts/energy.py` de nuevo antes de `build-edit.py`. |
| Palabras de final de frase "cortadas" o "con un corte en medio" | El recorte terminaba antes de la última palabra o cortaba la micro-pausa de una oclusiva; o un expansor rápido en la voz | Ya resuelto en `build-edit.py` (protege palabras + `end_pad`) y en `audio.sh` (expansor suave). Si vuelve a pasar, sube `end_pad`. |
| En zsh `$var:ratio` da error raro en ffmpeg | zsh interpreta `:r` como modificador | Escribe `${var}:ratio`. |
| Quedan pausas entre comas aunque `max_pause` es bajo | Whisper estira la palabra sobre el silencio y la protección de palabras lo conservaba | Resuelto: solo se protegen micro-pausas < `inner_max` (0,15 s). Si una palabra sale "partida", corrige su inicio con `word_fixes`. |
| Los listados de Chosic cuelgan el navegador integrado | Página pesada | Cierra la pestaña, abre otra y entra directo a `/download-audio/<id>/`. |
| "Sonidito extraño" en algunos cortes | Trozos de voz < 0,1 s que se borraban, inicios suaves ("y", "J") comidos, fragmentos sueltos, o un `src` que entra en la cola de otra toma o en un chasquido | Resuelto en `build-edit.py` (bordes extendidos, `min_piece`, AVISO corte sobre voz). Revisa cada AVISO con `energy.py zoom`. |
