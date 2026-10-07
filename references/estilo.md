# Guía de estilo: Reels de Futuros Residentes / Doc Juanes

Cada regla viene de una corrección o aprobación explícita de la usuaria. El porqué importa: si un
video nuevo no encaja en una regla, decide con el espíritu de la regla.

## Ritmo y cortes
- **Silencios al mínimo, dentro y entre frases.** Lo ha pedido en casi todos los videos ("menos tiempos
  muertos", "corta más los cambios de frase"). Por defecto: márgenes de 0,03 s al inicio/final del tramo,
  0,02 s en las pausas internas, pausas > 0,08 s fuera, umbral 40 dB sobre la voz limpia.
- **Nunca se corta una palabra**, ni por dentro (las t/k/p/g dejan micro-silencios < 0,15 s que parecen
  pausas) ni al final de frase, que se dice más bajito. Ella lo nota de inmediato. Whisper "estira"
  palabras sobre el silencio vecino: la protección solo cubre micro-pausas, las pausas reales sí se cortan.
- **Fuera todo lo que no es el guion final:** claqueta, tomas falsas, arranques en falso (pueden durar
  menos de medio segundo), groserías de error, frases repetidas (la toma más limpia, normalmente la
  última) y el cierre ("listo", "ahí quedó").

## Encuadres y movimiento
- **Plano fijo en cada toma; el plano cambia solo en el corte.** Rechaza el acercamiento progresivo
  durante la toma, los golpes de zoom al entrar y los pulsos en énfasis ("palpitaciones").
- **Cada corte con un zoom distinto** (diferencia ≥ 0,15): abierto (1.0), medio (1.1-1.3), cerrado (1.4-1.55).
- **Sin saltos de zoom en pedazos cortos** (< 0,6 s): se sienten "bruscos e innecesarios". En una
  escalera el plano solo cambia en los `steps`.
- **Escaleras de zoom** en ideas que escalan, hasta ~1.8x en la palabra culminante.
- Preguntas clave o frases de impacto: primer plano (1.5-1.6). Zooms siempre hacia la cara (`FACE_ORIGIN`).
- **Final nítido, sin fundido a negro:** acercamiento suave a la cara (`end_push`) y ahí termina.

## Subtítulos
- Normales: Montserrat 900, 82 px, blancas. **Sin mayúsculas sostenidas:** minúsculas con mayúscula al
  inicio de cada idea. Marcas ("Futuros Residentes", "Doc Juanes", universidades) bien escritas y juntas.
- 1-3 palabras por subtítulo; corte en cada idea, en comas/puntos y cuando cambia el énfasis. Palabras
  cortas no quedan solas. Conserva signos que dan sentido cuando ella los pida (p. ej. ":").
- **Palabras clave:** las dichas con fuerza o con carga clave, solas o en pareja, grandes (110-140 px),
  borde oscuro grueso, entrada con rebote; ~1 cada 1,5-2 s. **Fuente y color se proponen por video según
  el mood**: una o dos fuentes, mismo color o distinto. Le han gustado: Anton (enérgico), Montserrat
  cursiva (inspirador), Baskerville cursiva + Lilita One en verde limón (nostálgico/emotivo).
  **El color contrasta con la pared** (nunca el mismo tono del fondo).
- **Nunca tapan la cara:** desde el 63 % de la altura hacia abajo.

## Imagen
- **Tono de luz según el mood**, siempre como propuesta con muestra: cálido para lo nostálgico/emotivo
  (le gustó "cálido suave"), neutro por defecto, frío si el tema lo pide.
- **Nada de "segunda cámara" simulada** (girar/recortar el mismo plano): no le gustó. Solo si graban
  con una segunda cámara real.
- **Más luz, sin oscuridad:** curva en `prep.sh` que aclara sombras y medios tonos sin quemar la pared,
  corrección suave y viñeta muy suave (0.18). La persona debe verse real: nada de suavizado de piel.
- Fotos superpuestas: como foto impresa, en la mitad superior; los subtítulos siempre por encima.

## Audio
- **Menos eco pero voz natural:** DeepFilterNet + expansor SUAVE + EQ anti-cajón, −14 LUFS. Quitar todo
  el eco con un expansor rápido suena a palabras cortadas: ella prefirió la versión natural.
- Micro-fundidos solo en cortes reales; tramos contiguos sin fundido.
- El whoosh es corto (7 cuadros), suave (0.3) y termina justo en el corte: si es largo tapa el final de
  la palabra anterior o la primera sílaba de la siguiente. Donde ya hay otro sonido, no se pone whoosh.

## Eco
- Eco suave (3 rebotes que se apagan, sin tapar lo siguiente) para una frase de trascendencia. Se propone
  si se detecta una frase así, o se aplica si ella lo pide.

## Efectos y stickers (solo si los pide)
- Cada efecto tiene que ver con lo que se dice; ~1 cada 3-5 s, no más. Salen del lado hacia donde la
  persona mueve las manos.
- Dibujos propios estilo emoji (contorno oscuro, colores planos), nada que pueda leerse como gesto grosero.
- Nada que al aparecer pase por encima de la cara (animaciones sin rebote cerca de ella).
- Sonidos cómicos suaves (~0.35): suenan **completos** aunque el dibujo ya se haya ido y empiezan al
  INICIO de la palabra clave.
- En videos inspiradores, sin stickers salvo que los pida.

## Transiciones con destello de luz (`fx: "leak"`)
- Para videos inspiradores: luz de sol con colores (dorado, naranja, rosa, toque turquesa) que entra por
  una esquina superior y cruza, solo en los **cambios de tema**, no en cada corte.
- **Discreto** (`LEAK_STRENGTH` 0.25): uno fuerte lava la cara como neblina. **Sin sonido** (`LEAK_SOUND`
  null): un brillo de campanitas no le gustó.

## Música (solo si la pide)
- Ver `musica.md`. Siempre libre de derechos, nunca repetida salvo que ella diga que se puede reciclar.
- Va suave debajo de la voz, con hueco de ecualización para la voz, fundido de 1 s al entrar y salir.
  Ni tan baja que "no se perciba" ni tan alta que compita: ~18-23 dB bajo la voz.
