import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";

// Fuente de los subtítulos (decisión de estilo de la marca)
export const { fontFamily: CAPTION_FONT } = loadMontserrat("normal", {
  weights: ["800", "900"],
  subsets: ["latin"],
});

// Punto de la cara en el cuadro vertical: los zooms se hacen hacia aquí.
// Ajústalo por video mirando un fotograma (x% y%). Los subtítulos van debajo de CAPTION_TOP
// para que nunca tapen la cara, ni siquiera en el primer plano de 1.8x.
// Palabras clave (énfasis). Por defecto Montserrat amarilla; se puede cambiar por video
// (p. ej. Anton a 140 px, weight 400). Carga la fuente aquí si cambias de familia. El color debe
// contrastar con la pared del video.
export const EMPH_FONT = CAPTION_FONT;
export const EMPH_WEIGHT = 900;
export const EMPH_COLOR = "#FFD60A";
export const EMPH_SIZE = 120;
export const EMPH_STROKE = 14;
export const EMPH_STYLE: "normal" | "italic" = "normal";
export const EMPH_STROKE_COLOR = "#000";
// Segunda fuente de resaltado (opcional): palabras marcadas "alt" en emphasis. Por defecto = la primera.
// Se propone por video según el mood: una o dos fuentes, mismo color o distinto.
export const EMPH2_FONT = EMPH_FONT;
export const EMPH2_WEIGHT = EMPH_WEIGHT;
export const EMPH2_STYLE: "normal" | "italic" = "normal";
export const EMPH2_COLOR = EMPH_COLOR;
export const EMPH2_SIZE = EMPH_SIZE;

// Video base: la copia vertical de prep.sh, o la procesada (p. ej. fondo difuminado: "video-fondo.mp4")
export const VIDEO_SRC = "video-vertical.mp4";

export const FACE_ORIGIN = "50% 23%";
export const CAPTION_TOP = "63%";

// Música de fondo: SOLO si la piden. Archivo en /public, con licencia libre (CC0 / dominio público).
// Anota aquí título, artista, licencia y fuente.
export const MUSICA: string | null = null;
export const MUSICA_INICIO_SEG = 0; // desde qué segundo de la canción empieza (donde ya tiene energía)
export const VOLUMEN_MUSICA = 0.1; // ~20 dB por debajo de la voz

// Tono de luz según el mood: WARM > 0 = cálido (0.6 = "cálido suave"); COOL > 0 = frío (azulado suave).
export const WARM = 0;
export const COOL = 0;

// Destellos de luz en transiciones (fx "leak"): 0.25 = discreto (el aprobado)
export const LEAK_STRENGTH = 0.25;
// Sonido en el destello: null por defecto (se descartaron las campanitas "sfx-shimmer.wav")
export const LEAK_SOUND: string | null = null;
