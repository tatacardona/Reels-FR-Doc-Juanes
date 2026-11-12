import { AbsoluteFill, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { CAPTION_TOP } from "./constants";
import { DJ, DJ_BASE, DJ_HAND, Icon, Rays, Underline } from "../DJ";

// Subtítulos con la línea gráfica de los posts de Doc Juanes (nov 2026). Variante aprobada: A
//  impacto = barra lima con letra oliva; emotivo = letra a mano sobre papel crema rasgado.
// Cada tipo de letra lleva sus propios dibujos, que se van turnando (Janeth, 11 nov: "varía el dibujo"),
// pegados a la palabra resaltada.
export type Variant = "A" | "B" | "C";
export const CAPTION_VARIANT: Variant = "A";

export type Caption = { start: number; end: number; words: { t: string; emph: boolean; alt?: boolean }[] };

const TORN =
  "polygon(0% 8%, 6% 0%, 14% 6%, 23% 1%, 31% 7%, 40% 2%, 49% 8%, 58% 1%, 66% 6%, 75% 0%, 84% 7%, 92% 2%, 100% 9%, 98% 50%, 100% 92%, 93% 100%, 85% 94%, 76% 100%, 67% 95%, 58% 100%, 49% 93%, 40% 99%, 31% 94%, 22% 100%, 13% 95%, 5% 100%, 0% 92%, 2% 50%)";

const DOODLES_IMPACTO = ["rayitas", "estrella", "puntos"] as const;
const DOODLES_EMOTIVO = ["corazon", "subrayado", "flecha"] as const;
type Doodle = (typeof DOODLES_IMPACTO)[number] | (typeof DOODLES_EMOTIVO)[number];

const Dibujo: React.FC<{ d: Doodle }> = ({ d }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: f - 3, fps, config: { damping: 10, stiffness: 200 }, durationInFrames: 10 });
  const pos: React.CSSProperties = { position: "absolute", transform: `scale(${s})`, pointerEvents: "none" };
  switch (d) {
    case "rayitas":
      return <Rays style={{ ...pos, right: -70, top: -62 }} size={110} delay={3} outline />;
    case "estrella":
      return <Icon kind="estrella" size={86} style={{ ...pos, right: -48, top: -52, transform: `scale(${s}) rotate(12deg)` }} />;
    case "puntos":
      return (
        <svg width={96} height={64} viewBox="0 0 60 40" style={{ ...pos, right: -64, top: -46 }}>
          {[[10, 30], [28, 14], [48, 6]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={6} fill={DJ.lima} stroke={DJ.oliva} strokeWidth={3} />)}
        </svg>
      );
    case "corazon":
      return <Icon kind="corazon" size={88} style={{ ...pos, right: -52, top: -48, transform: `scale(${s}) rotate(14deg)` }} />;
    case "subrayado":
      return <Underline w={300} style={{ ...pos, left: "50%", marginLeft: -150, bottom: -22 }} />;
    case "flecha":
      // flechita a mano que señala la palabra desde abajo a la izquierda
      return (
        <svg width={120} height={80} viewBox="0 0 120 80" style={{ ...pos, left: -96, bottom: -40, overflow: "visible" }}>
          {[DJ.oliva, DJ.lima].map((col, i) => (
            <g key={i} stroke={col} strokeWidth={i ? 8 : 15} fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10 70 C 30 70, 40 40, 90 28" />
              <path d="M70 16 L 92 27 L 76 46" />
            </g>
          ))}
        </svg>
      );
  }
};

const Word: React.FC<{ w: Caption["words"][number]; v: Variant; doodle?: Doodle }> = ({ w, v, doodle }) => {
  const wrap: React.CSSProperties = { position: "relative", display: "inline-block", margin: "6px 10px" };
  const base: React.CSSProperties = { display: "inline-block", paintOrder: "stroke fill", lineHeight: 1.08 };
  let inner: React.ReactNode;
  if (!w.emph) {
    inner = (
      <span
        style={{
          ...base, fontFamily: DJ_BASE, fontWeight: 800, fontSize: 80, color: "#FFFFFF",
          WebkitTextStroke: v === "C" ? "0px" : `10px ${DJ.oliva}`,
          textShadow: v === "C" ? "none" : "0 6px 18px rgba(20,28,8,0.55)",
        }}
      >
        {w.t}
      </span>
    );
  } else if (w.alt) {
    const paper = v === "A";
    inner = (
      <span
        style={{
          ...base, fontFamily: DJ_HAND, fontWeight: 700, fontSize: 116,
          color: paper ? DJ.oliva : DJ.crema,
          WebkitTextStroke: paper || v === "C" ? "0px" : `9px ${DJ.oliva}`,
          background: paper ? DJ.crema : "none",
          clipPath: paper ? TORN : undefined,
          padding: paper ? "4px 30px 0" : 0,
          transform: "rotate(-3deg)",
          textShadow: paper || v === "C" ? "none" : "0 6px 18px rgba(20,28,8,0.5)",
        }}
      >
        {w.t}
      </span>
    );
  } else {
    const bar = v === "A";
    inner = (
      <span
        style={{
          ...base, fontFamily: DJ_BASE, fontWeight: 900, fontSize: 112,
          color: bar ? DJ.oliva : DJ.lima,
          background: bar ? DJ.lima : "none",
          padding: bar ? "0 20px" : 0,
          WebkitTextStroke: bar || v === "C" ? "0px" : `13px ${DJ.oliva}`,
          transform: bar ? "rotate(-2deg)" : undefined,
          boxShadow: bar ? `8px 8px 0 ${DJ.oliva}` : undefined,
          textShadow: bar || v === "C" ? "none" : "0 8px 22px rgba(20,28,8,0.55)",
        }}
      >
        {w.t}
      </span>
    );
  }
  return (
    <span style={wrap}>
      {inner}
      {doodle ? <Dibujo d={doodle} /> : null}
    </span>
  );
};

export const Chunk: React.FC<{ c: Caption; v?: Variant; idx?: number }> = ({ c, v = CAPTION_VARIANT, idx = 0 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hasEmph = c.words.some((w) => w.emph);
  const pop = spring({ frame: f, fps, config: { damping: 12, stiffness: 220 }, durationInFrames: 8 });
  const scale = interpolate(pop, [0, 1], [hasEmph ? 0.6 : 0.82, 1]);
  const lift = interpolate(pop, [0, 1], [18, 0]);
  // un solo dibujo por frase: en la última palabra resaltada, según su tipo, turnándose
  const last = c.words.map((w, i) => (w.emph ? i : -1)).filter((i) => i >= 0).pop();
  const lw = last !== undefined ? c.words[last] : undefined;
  const doodle: Doodle | undefined = lw ? (lw.alt ? DOODLES_EMOTIVO : DOODLES_IMPACTO)[idx % 3] : undefined;
  return (
    <AbsoluteFill style={{ top: CAPTION_TOP, alignItems: "center" }}>
      <div
        style={{
          position: "relative", textAlign: "center", maxWidth: 960,
          transform: `translateY(${lift}px) scale(${scale})`,
          opacity: interpolate(f, [0, 2], [0, 1], { extrapolateRight: "clamp" }),
          background: v === "C" ? "rgba(36,46,15,0.88)" : "none",
          padding: v === "C" ? "18px 34px 24px" : 0,
          borderRadius: v === "C" ? 18 : 0,
        }}
      >
        {c.words.map((w, i) => (
          <Word key={i} w={w} v={v} doodle={i === last ? doodle : undefined} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const Captions: React.FC<{ captions: Caption[] }> = ({ captions }) => {
  // un turno por tipo de letra: cada uno recorre sus propios dibujos
  const n = { imp: 0, emo: 0 };
  return (
    <>
      {captions.map((c, i) => {
        const lw = [...c.words].reverse().find((w) => w.emph);
        const idx = !lw ? 0 : lw.alt ? n.emo++ : n.imp++;
        return (
          <Sequence key={i} from={c.start} durationInFrames={Math.max(1, c.end - c.start)} layout="none">
            <Chunk c={c} idx={idx} />
          </Sequence>
        );
      })}
    </>
  );
};
