import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  random,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Línea de rasgado irregular (siempre la misma en cada render)
const STEPS = 26;
const tearLine = Array.from({ length: STEPS + 1 }, (_, i) => {
  const y = (i / STEPS) * 100;
  const x = 50 + (random(`tear-${i}`) - 0.5) * 9 + Math.sin(i * 0.9) * 2.5;
  return { x, y };
});
const leftPath = `polygon(0% 0%, ${tearLine.map((p) => `${p.x}% ${p.y}%`).join(", ")}, 0% 100%)`;
const rightPath = `polygon(100% 0%, ${tearLine.map((p) => `${p.x}% ${p.y}%`).join(", ")}, 100% 100%)`;

// Foto impresa: borde blanco, sombra y la imagen mejorada
const PrintedPhoto: React.FC<{ src: string }> = ({ src }) => (
  <div
    style={{
      background: "#FAFAF7",
      padding: 22,
      paddingBottom: 70,
      borderRadius: 6,
      boxShadow: "0 30px 70px rgba(0,0,0,0.55), 0 6px 18px rgba(0,0,0,0.35)",
    }}
  >
    <Img src={staticFile(src)} style={{ display: "block", maxWidth: 860, maxHeight: 900, objectFit: "contain" }} />
  </div>
);

const Half: React.FC<{ src: string; side: "left" | "right"; t: number }> = ({ src, side, t }) => {
  const dir = side === "left" ? -1 : 1;
  // primero se abre la grieta, luego las mitades caen hacia los lados
  const open = interpolate(t, [0, 4], [0, 1], clamp);
  const fall = interpolate(t, [3, 24], [0, 1], { ...clamp, easing: (x) => x * x });
  const x = dir * (open * 14 + fall * 320);
  const y = fall * 700;
  const rot = dir * (open * 3 + fall * 22);
  return (
    <div
      style={{
        position: "absolute",
        clipPath: side === "left" ? leftPath : rightPath,
        transform: `translate(${x}px, ${y}px) rotate(${rot}deg)`,
        transformOrigin: side === "left" ? "0% 100%" : "100% 100%",
        opacity: interpolate(t, [16, 26], [1, 0], clamp),
        // borde de fibra blanca en el corte
        filter: "drop-shadow(0 0 1.5px rgba(255,255,255,0.95))",
      }}
    >
      <PrintedPhoto src={src} />
    </div>
  );
};

// Foto que entra sobre el video y se rasga en `tearAt` (frames relativos al inicio de la secuencia)
const PhotoInner: React.FC<{ src: string; tearAt: number; exitAt: number }> = ({ src, tearAt, exitAt }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: f, fps, config: { damping: 14, stiffness: 140 } });
  const t = f - tearAt;
  const torn = t >= 0;

  // Entrada: cae girando levemente y se asienta; luego flota muy despacio
  const scale = interpolate(enter, [0, 1], [1.3, 1]) * (1 + f * 0.0008);
  const rot = interpolate(enter, [0, 1], [-9, -2.5]);
  const drop = interpolate(enter, [0, 1], [-120, 0]);
  // Temblor justo antes y durante el rasgado
  const shake = torn ? interpolate(t, [0, 6], [10, 0], clamp) : interpolate(t, [-4, 0], [0, 4], clamp);
  const sx = (random(`sx${f}`) - 0.5) * shake;
  const sy = (random(`sy${f}`) - 0.5) * shake;
  const dim = torn
    ? interpolate(t, [8, 22], [0.35, 0], clamp)
    : Math.min(interpolate(f, [0, 8], [0, 0.35], clamp), interpolate(f, [exitAt - 6, exitAt], [0.35, 0], clamp));
  // Sin rasgado: la foto sale con un fundido corto
  const exit = interpolate(f, [exitAt - 6, exitAt], [1, 0], clamp);

  return (
    <AbsoluteFill>
      {/* Oscurece un poco el video para que resalte la foto */}
      <AbsoluteFill style={{ background: `rgba(0,0,0,${dim})` }} />
      {/* Zona de la foto: arriba del área de subtítulos (63%) para no taparlos */}
      <AbsoluteFill style={{ height: "60%", top: "2%", alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            position: "relative",
            transform: `translate(${sx}px, ${drop + sy}px) rotate(${rot}deg) scale(${scale})`,
            opacity: Math.min(interpolate(f, [0, 4], [0, 1], clamp), exit),
          }}
        >
          {torn ? (
            <div style={{ position: "relative" }}>
              <div style={{ visibility: "hidden" }}>
                <PrintedPhoto src={src} />
              </div>
              <AbsoluteFill>
                <Half src={src} side="left" t={t} />
                <Half src={src} side="right" t={t} />
              </AbsoluteFill>
            </div>
          ) : (
            <PrintedPhoto src={src} />
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Foto superpuesta. Con tearAt se rasga en ese frame; sin tearAt sale con fundido en end.
export const TornPhoto: React.FC<{ src: string; from: number; tearAt?: number; end?: number }> = ({
  src,
  from,
  tearAt,
  end,
}) => {
  const tears = tearAt !== undefined;
  const tearRel = tears ? tearAt - from : 100000;
  const dur = tears ? tearRel + 28 : Math.max(10, (end ?? from + 75) - from);
  return (
    <Sequence from={from} durationInFrames={dur} name="Foto">
      <PhotoInner src={src} tearAt={tearRel} exitAt={tears ? 100000 : dur} />
      <Audio src={staticFile("sfx-whoosh.wav")} volume={0.25} />
      {tears ? (
        <Sequence from={tearRel - 2} name="Rasgado">
          <Audio src={staticFile("sfx-tear.wav")} volume={0.75} />
          <Audio src={staticFile("sfx-boom.wav")} volume={0.3} />
        </Sequence>
      ) : null}
    </Sequence>
  );
};
