import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { COOL, FACE_ORIGIN, VIDEO_SRC, WARM } from "./constants";

type Props = {
  trim: number;
  dur: number;
  zoom: number;
  fx?: string;
  push?: { at: number; to: number };
  rate?: number;
  bw?: boolean;
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Un clip del video crudo: enderezado, con corrección de color, zoom y entrada dinámica.
export const Footage: React.FC<Props> = ({ trim, dur, zoom, fx = "none", push, rate = 1, bw }) => {
  const f = useCurrentFrame();

  let scale = zoom;
  if (push && push.at < dur - 1) {
    scale = interpolate(f, [push.at, dur], [zoom, push.to], {
      ...clamp,
      easing: Easing.inOut(Easing.cubic),
    });
  }
  // Cada toma queda fija en su encuadre: el cambio de plano ocurre solo en el corte.
  // En los cambios de tema, un desenfoque de movimiento muy corto marca la transición.
  const blur = fx === "whoosh" ? interpolate(f, [0, 4], [10, 0], clamp) : 0;

  // Iluminación: un poco más de luz, contraste y color natural (la persona se ve igual)
  // (la curva que aclara sombras ya viene en video-vertical.mp4, ver prep.sh)
  const grade = bw
    ? "grayscale(1) contrast(1.45) brightness(0.8)"
    : `brightness(1.04) contrast(1.05) saturate(${1.06 + WARM * 0.08}) sepia(${WARM * 0.18})`;

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${scale})`,
        transformOrigin: FACE_ORIGIN,
        filter: `${grade}${blur > 0.1 ? ` blur(${blur}px)` : ""}`,
      }}
    >
      {/* Copia vertical ya enderezada del video crudo (scripts/prep.sh) */}
      <OffthreadVideo
        src={staticFile(VIDEO_SRC)}
        trimBefore={trim}
        playbackRate={rate}
        muted
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};

// Viñeta suave para centrar la mirada en la persona
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.18 }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse 75% 60% at ${FACE_ORIGIN}, transparent 45%, rgba(0,0,0,${strength}) 100%)`,
    }}
  />
);

// Tono de luz según el mood: cálido (dorado desde arriba) o frío (azulado suave), en "soft-light"
// para no cambiar el color de piel. WARM y COOL en constants.ts (0 = neutro).
export const Tone: React.FC = () => (
  <>
    {WARM > 0 ? (
      <AbsoluteFill
        style={{
          mixBlendMode: "soft-light",
          background: `radial-gradient(ellipse 90% 70% at 35% 20%, rgba(255,170,90,${0.55 * WARM}) 0%, rgba(255,140,60,${0.25 * WARM}) 55%, rgba(120,60,20,${0.2 * WARM}) 100%)`,
        }}
      />
    ) : null}
    {COOL > 0 ? (
      <AbsoluteFill
        style={{
          mixBlendMode: "soft-light",
          background: `radial-gradient(ellipse 90% 70% at 60% 20%, rgba(120,170,255,${0.5 * COOL}) 0%, rgba(80,120,200,${0.25 * COOL}) 60%, rgba(20,40,90,${0.2 * COOL}) 100%)`,
        }}
      />
    ) : null}
  </>
);
