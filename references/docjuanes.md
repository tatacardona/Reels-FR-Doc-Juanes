# Línea gráfica de Doc Juanes (desde nov 2026, aprobada en NO_RENUNCIES)

Janeth pidió que los videos y las portadas de Doc Juanes se vean como los posts actuales de @docjuanes.
Úsala en todo video de Doc Juanes salvo que pida otra cosa. Los componentes listos están en
`assets/template/docjuanes/` (ver "Instalar" abajo).

## Paleta y letras
| Elemento | Valor |
|---|---|
| Verde lima (acento) | `#C8E03A` |
| Verde oliva oscuro (fondos, bordes, texto sobre lima) | `#26310F` · medio `#46561D` |
| Papel crema | `#EFE7D4` |
| Letra base | **Poppins** 800 blanca con borde oliva (`@remotion/google-fonts/Poppins`) |
| Letra emotiva | **Kalam** 700 (a mano) (`@remotion/google-fonts/Kalam`) |

## Subtítulos (variante A, la elegida)
- Palabras normales: Poppins 800 blanca, borde oliva de 10 px y sombra suave.
- **Impacto** (`emphasis` sin "alt"): Poppins 900 oliva sobre **barra lima**, girada −2°, con sombra sólida oliva.
- **Emotivo** (`emphasis` con "alt"): Kalam oliva sobre **papel crema rasgado**, girado −3°.
- **Un dibujo por frase, pegado a la palabra resaltada, que se turna por tipo de letra** (Janeth: "no siempre las 3 rayitas"):
  impacto → rayitas · estrella · puntos; emotivo → corazón · subrayado · flechita. Lima con borde oliva para que se vean
  sobre pared blanca. Si quedan lejos de la palabra o muy pequeños, se nota: revisa en fotogramas.
- Opcional al final: flecha a mano que rebota hacia abajo bajo "Cuéntame…/Comenta…" (`ArrowDown` de DJ.tsx).

## Portadas (`CoverDJ`, 3 diseños; Janeth eligió el 2 "crema")
- 1 oscuro (textura oliva, dato grande en lima) · 2 crema con franja oliva rasgada · 3 sobre el video.
- Juan **recortado con IA** como en los posts: `scripts/recorte-fino.py <seg> work/rec.png` (MediaPipe + GrabCut,
  sin halo blanco y borde apenas suavizado; el recorte básico dejaba restos de pared) y luego
  `scripts/luz-recorte.py work/rec.png public/recorte-<seg>.png` (aclara sombras, luz en la cara, toque cálido).
- Que se le vean **brazos y manos completos**: en `CoverDJ` el diseño 2 recibe `pw/pl/pt` (ancho, izquierda, arriba).
  En NO_RENUNCIES quedó `{"pw":1800,"pl":-340,"pt":160}`.
- Ofrece **varias fotos de Juan** (expresiones del video y fotos de la sesión profesional de abril 2025 en Drive:
  EST_DOCJUANES/DOC_MARCAPERSONAL/EST_Fotos_JuanPelaez_Abril2025; las de estudio con fondo blanco recortan muy
  bien, las de charlas con fondo oscuro no). `scripts/recorte-foto.py <foto> <salida> <recorte_ref>` encaja la cara
  al mismo tamaño y lugar que la referencia.
- Texto de la portada: pregúntalo; en NO_RENUNCIES lo dio Janeth ("Un médico llevaba 15 años… ¿Cuántos intentos
  llevas tú?"). Íconos dibujados propios (reloj de arena, corazón, estrella, check, birrete), nunca emojis de Apple.

## Logo
- **Oficial, completo** (monograma + "Doc Juanes"): Drive → Mi unidad → BOTS_REELS_ICONOS →
  `Logo_Doc_Juanes_V1.png` (verde + negro, fondo claro), `V2` (blanco), `V3` (verde + blanco, fondo oscuro), `V4` (negro).
  Recórtalos y guárdalos en `public/` (el componente `Logo` de DJ.tsx usa V3 y, con `claro`, V1).
- La carpeta EST_DOCJUANES/DOC_MARCAPERSONAL/PNG solo tiene el monograma: no sirve como logo completo.
- Nunca dibujes ni "extraigas" un logo propio si existen los oficiales.

## Instalar en un proyecto
```bash
cp ~/.claude/skills/editar-reel-fr/assets/template/docjuanes/DJ.tsx src/
cp ~/.claude/skills/editar-reel-fr/assets/template/docjuanes/CoverDJ.tsx src/
cp ~/.claude/skills/editar-reel-fr/assets/template/docjuanes/Captions.tsx src/Reel/Captions.tsx
```
En `src/Root.tsx` registra `<Composition id="CoverDJ" component={CoverDJ} durationInFrames={1} fps={25} width={1080}
height={1920} defaultProps={{ n: 2, foto: "recorte-<seg>.png" }} />`. Cambia en `CoverDJ.tsx` los textos (son los de
NO_RENUNCIES). Muestras: `npx remotion still CoverDJ out/portadas/NOMBRE_PORTADA_N.jpg --props='{"n":2,"foto":"…"}'`.
