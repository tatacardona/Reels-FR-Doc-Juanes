import {
  AbsoluteFill,
  Audio,
  interpolate,
  random,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FACE_ORIGIN } from "./constants";
import edit from "./edit.json";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const INK = "#1A1A1A";

// Generado por scripts/build-edit.py a partir de "stickers" en edit-config.json
export type Sticker = {
  kind: string; // "broken-heart" | una clave de ART
  start: number; // frame de aparición (video editado)
  dur: number;
  x?: number; // posición en % del cuadro
  y?: number;
  size?: number; // ancho en px
  breakAt?: number; // corazón: se parte (frames desde start)
  track?: number[][]; // cabeza [x%, y%] por cuadro, sin zoom (scripts/head-track.py), si un efecto la sigue
  sfx?: { src: string; at: number; volume: number }[];
};

type Clip = { start: number; dur: number; zoom: number };

// Zoom del tramo que está en pantalla en el frame absoluto `f`
export const zoomAt = (f: number) => {
  const c = (edit.clips as Clip[]).find((k) => f >= k.start && f < k.start + k.dur);
  return c ? c.zoom : 1;
};
// Un punto del cuadro sin zoom (en %) llevado a pantalla con el zoom de la toma (hacia FACE_ORIGIN)
const [OX, OY] = FACE_ORIGIN.split(" ").map((v) => parseFloat(v));
export const toScreen = (x: number, y: number, z: number) => [OX + (x - OX) * z, OY + (y - OY) * z];

// ---------------- Dibujos (vectores propios, sin derechos de terceros) ----------------
const HEART =
  "M100 178 C 30 128, 0 92, 0 56 C 0 22, 26 0, 56 0 C 76 0, 92 12, 100 28 C 108 12, 124 0, 144 0 C 174 0, 200 22, 200 56 C 200 92, 170 128, 100 178 Z";
const CRACK = [[100, 28], [86, 62], [110, 86], [84, 114], [106, 140], [100, 178]];
const pct = ([x, y]: number[]) => `${(x / 200) * 100}% ${(y / 180) * 100}%`;
const HeartSvg: React.FC<{ half?: "left" | "right" }> = ({ half }) => {
  const clip =
    half === "left"
      ? `polygon(0% 0%, ${CRACK.map(pct).join(", ")}, 0% 100%)`
      : half === "right"
        ? `polygon(100% 0%, ${CRACK.map(pct).join(", ")}, 100% 100%)`
        : undefined;
  return (
    <div style={{ width: "100%", height: "100%", clipPath: clip }}>
      <svg viewBox="-6 -6 212 192" width="100%" height="100%">
        <defs>
          <linearGradient id="red" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#FF5A6E" />
            <stop offset="1" stopColor="#C8102E" />
          </linearGradient>
        </defs>
        <path d={HEART} fill="url(#red)" stroke={INK} strokeWidth="8" strokeLinejoin="round" />
        <path d="M40 40 Q 52 22 72 24" stroke="#FFC2CB" strokeWidth="10" fill="none" strokeLinecap="round" />
        {half ? <polyline points={CRACK.map((p) => p.join(",")).join(" ")} fill="none" stroke={INK} strokeWidth="7" strokeLinejoin="round" /> : null}
      </svg>
    </div>
  );
};

const ExamSvg: React.FC = () => (
  <svg viewBox="0 0 200 200" width="100%" height="100%">
    <rect x="34" y="14" width="132" height="172" rx="8" fill="#FFFFFF" stroke={INK} strokeWidth="7" />
    <rect x="50" y="30" width="100" height="18" rx="4" fill="#2E8BFF" />
    <text x="100" y="44" textAnchor="middle" fontFamily="Arial Black, Arial" fontWeight="900" fontSize="14" fill="#fff">EXAMEN</text>
    {[70, 100, 130, 160].map((y, i) => (
      <g key={y}>
        <rect x="50" y={y - 9} width="14" height="14" rx="3" fill="none" stroke={INK} strokeWidth="4" />
        <line x1="74" y1={y - 2} x2={140 - (i % 2) * 22} y2={y - 2} stroke="#9AA3AD" strokeWidth="6" strokeLinecap="round" />
      </g>
    ))}
    <path d="M52 63 l5 6 l9 -12" stroke="#2EE86B" strokeWidth="5" fill="none" strokeLinecap="round" />
    <g transform="rotate(35 160 140)">
      <rect x="150" y="70" width="20" height="96" rx="3" fill="#FFC21A" stroke={INK} strokeWidth="5" />
      <path d="M150 166 L160 188 L170 166 Z" fill="#F5D9B0" stroke={INK} strokeWidth="5" strokeLinejoin="round" />
      <rect x="150" y="62" width="20" height="14" rx="3" fill="#FF7A8A" stroke={INK} strokeWidth="5" />
    </g>
  </svg>
);

const StethoscopeSvg: React.FC = () => (
  <svg viewBox="0 0 200 200" width="100%" height="100%">
    <path d="M56 22 C 40 70, 54 110, 92 116 C 130 110, 144 70, 128 22" fill="none" stroke={INK} strokeWidth="16" strokeLinecap="round" />
    <path d="M56 22 C 40 70, 54 110, 92 116 C 130 110, 144 70, 128 22" fill="none" stroke="#2E8BFF" strokeWidth="9" strokeLinecap="round" />
    <path d="M92 116 C 92 150, 112 172, 140 160" fill="none" stroke={INK} strokeWidth="16" strokeLinecap="round" />
    <path d="M92 116 C 92 150, 112 172, 140 160" fill="none" stroke="#2E8BFF" strokeWidth="9" strokeLinecap="round" />
    <circle cx="56" cy="20" r="10" fill="#C9D2DB" stroke={INK} strokeWidth="5" />
    <circle cx="128" cy="20" r="10" fill="#C9D2DB" stroke={INK} strokeWidth="5" />
    <circle cx="154" cy="152" r="26" fill="#DDE4EA" stroke={INK} strokeWidth="7" />
    <circle cx="154" cy="152" r="14" fill="#9AA6B2" stroke={INK} strokeWidth="4" />
    <circle cx="147" cy="145" r="4" fill="#fff" />
  </svg>
);

const BrainSvg: React.FC = () => (
  <svg viewBox="0 0 200 180" width="100%" height="100%">
    <path
      d="M100 30 C 86 10, 54 12, 48 34 C 24 32, 12 56, 22 74 C 6 88, 12 116, 32 122 C 32 146, 58 160, 78 148 C 88 162, 100 160, 100 150
         C 100 160, 112 162, 122 148 C 142 160, 168 146, 168 122 C 188 116, 194 88, 178 74 C 188 56, 176 32, 152 34 C 146 12, 114 10, 100 30 Z"
      fill="#FF9EC0"
      stroke={INK}
      strokeWidth="7"
      strokeLinejoin="round"
    />
    <path d="M100 30 C 94 60, 106 90, 100 150" fill="none" stroke={INK} strokeWidth="6" strokeLinecap="round" />
    {[
      "M48 34 C 58 46, 74 46, 80 60",
      "M22 74 C 40 80, 54 74, 62 86",
      "M32 122 C 46 112, 60 118, 70 106",
      "M152 34 C 142 46, 126 46, 120 60",
      "M178 74 C 160 80, 146 74, 138 86",
      "M168 122 C 154 112, 140 118, 130 106",
    ].map((d, i) => (
      <path key={i} d={d} fill="none" stroke="#C2457A" strokeWidth="6" strokeLinecap="round" />
    ))}
    <path d="M58 26 C 66 20, 78 20, 84 26" fill="none" stroke="#FFD6E4" strokeWidth="6" strokeLinecap="round" />
  </svg>
);

const ShhSvg: React.FC = () => (
  <svg viewBox="0 0 200 200" width="100%" height="100%" style={{ overflow: "visible" }}>
    <circle cx="96" cy="96" r="80" fill="#FFD23F" stroke={INK} strokeWidth="7" />
    {/* ojos mirando de lado, cómplices */}
    <ellipse cx="66" cy="76" rx="9" ry="13" fill={INK} />
    <ellipse cx="122" cy="76" rx="9" ry="13" fill={INK} />
    <path d="M52 56 Q 64 50 78 56" fill="none" stroke={INK} strokeWidth="6" strokeLinecap="round" />
    <path d="M110 56 Q 122 50 136 56" fill="none" stroke={INK} strokeWidth="6" strokeLinecap="round" />
    {/* labios fruncidos, visibles a ambos lados del dedo */}
    <ellipse cx="96" cy="134" rx="28" ry="11" fill="#C0392B" stroke={INK} strokeWidth="5" />
    {/* dedo índice vertical sobre los labios (sin puño, para que nunca se lea como otro gesto) */}
    <rect x="88" y="104" width="16" height="58" rx="8" fill="#F2B98A" stroke={INK} strokeWidth="5" />
    <ellipse cx="96" cy="111" rx="4.5" ry="4" fill="#FFE1CC" />
    <text x="170" y="22" textAnchor="middle" fontFamily="Arial Black, Arial" fontWeight="900" fontSize="44" fill="#FFFFFF" stroke={INK} strokeWidth="9" paintOrder="stroke" transform="rotate(14 170 22)">shhh</text>
  </svg>
);

// Calendario con hojas que pasan rápido (años de experiencia)
const CalendarArt: React.FC = () => {
  const f = useCurrentFrame();
  const page = Math.floor(f / 2);
  const months = ["ENE", "MAR", "MAY", "JUL", "SEP", "NOV"];
  const flip = (f % 2) / 2;
  return (
    <svg viewBox="0 0 200 200" width="100%" height="100%">
      <rect x="22" y="34" width="156" height="148" rx="14" fill="#FFFFFF" stroke={INK} strokeWidth="7" />
      <rect x="22" y="34" width="156" height="44" rx="12" fill="#E8263B" stroke={INK} strokeWidth="7" />
      <text x="100" y="66" textAnchor="middle" fontFamily="Arial Black, Arial" fontWeight="900" fontSize="24" fill="#fff">{months[page % months.length]}</text>
      <text x="100" y="156" textAnchor="middle" fontFamily="Arial Black, Arial" fontWeight="900" fontSize="62" fill={INK}>{2015 + Math.min(10, Math.floor(page / 2))}</text>
      <path d={`M24 78 L176 78 L176 ${78 + 100 * (1 - flip)} L24 ${78 + 100 * (1 - flip)} Z`} fill="#F1F1F1" opacity={0.5 * (1 - flip)} />
      {[62, 138].map((x) => (
        <rect key={x} x={x - 7} y="18" width="14" height="32" rx="7" fill="#C9D2DB" stroke={INK} strokeWidth="5" />
      ))}
    </svg>
  );
};

const XStampSvg: React.FC = () => (
  <svg viewBox="0 0 200 200" width="100%" height="100%">
    <g stroke={INK} strokeWidth="50" strokeLinecap="round">
      <line x1="40" y1="40" x2="160" y2="160" />
      <line x1="160" y1="40" x2="40" y2="160" />
    </g>
    <g stroke="#E8263B" strokeWidth="34" strokeLinecap="round">
      <line x1="40" y1="40" x2="160" y2="160" />
      <line x1="160" y1="40" x2="40" y2="160" />
    </g>
  </svg>
);

// Dibujos para stickers libres (kind en edit-config.json)
export const ART: Record<string, React.FC> = {
  exam: ExamSvg,
  stethoscope: StethoscopeSvg,
  brain: BrainSvg,
  shh: ShhSvg,
  calendar: CalendarArt,
  "x-stamp": XStampSvg,
};

// ---------------- Corazón roto: entra, late, se parte en dos y cae ----------------
const BrokenHeart: React.FC<{ s: Sticker }> = ({ s }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: f, fps, config: { damping: 10, stiffness: 200 } });
  const t = f - (s.breakAt ?? 10);
  const beat = t < 0 ? 1 + 0.07 * Math.max(0, Math.sin((f / fps) * Math.PI * 5)) : 1;
  const size = s.size ?? 300;
  const half = (side: "left" | "right") => {
    const dir = side === "left" ? -1 : 1;
    const open = interpolate(t, [0, 3], [0, 1], clamp);
    const fall = interpolate(t, [6, 28], [0, 1], { ...clamp, easing: (v) => v * v });
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${dir * (open * 20 + fall * 70)}px, ${fall * 520}px) rotate(${dir * (open * 12 + fall * 28)}deg)`,
          transformOrigin: "50% 100%",
        }}
      >
        <HeartSvg half={side} />
      </div>
    );
  };
  const shake = t >= 0 ? interpolate(t, [0, 6], [14, 0], clamp) : 0;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: `${s.x ?? 50}%`,
          top: `${s.y ?? 45}%`,
          width: size,
          height: size * 0.9,
          transform: `translate(-50%, -50%) translate(${(random(`hx${f}`) - 0.5) * shake}px, ${(random(`hy${f}`) - 0.5) * shake}px) scale(${interpolate(enter, [0, 1], [0.2, 1]) * beat})`,
          opacity: interpolate(f, [s.dur - 4, s.dur], [1, 0], clamp),
          filter: "drop-shadow(0 12px 20px rgba(0,0,0,0.5))",
        }}
      >
        {t < 0 ? (
          <HeartSvg />
        ) : (
          <>
            {half("left")}
            {half("right")}
          </>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------------- Sticker libre: entra con rebote (o como sello), se mece y sale ----------------
const Generic: React.FC<{ s: Sticker }> = ({ s }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const Art = ART[s.kind];
  const size = s.size ?? 220;
  const stamp = s.kind === "x-stamp";
  const enter = spring({ frame: f, fps, config: stamp ? { damping: 14, stiffness: 400 } : { damping: 9, stiffness: 220 } });
  const scale = stamp ? interpolate(enter, [0, 1], [2.6, 1]) : interpolate(enter, [0, 1], [0, 1]);
  const rot = stamp ? -8 : interpolate(enter, [0, 1], [-30, 0]) + Math.sin(f / 6) * 4;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: `${s.x ?? 78}%`,
          top: `${s.y ?? 40}%`,
          width: size,
          height: size,
          transform: `translate(-50%, -50%) scale(${scale}) rotate(${rot}deg)`,
          opacity: Math.min(stamp ? interpolate(f, [0, 2], [0, 1], clamp) : 1, interpolate(f, [s.dur - 4, s.dur], [1, 0], clamp)),
          filter: "drop-shadow(0 10px 16px rgba(0,0,0,0.5))",
        }}
      >
        {Art ? <Art /> : null}
      </div>
    </AbsoluteFill>
  );
};

// Los sonidos van fuera de la secuencia del sticker para que suenen completos aunque el dibujo ya se haya ido
export const Stickers: React.FC<{ stickers: Sticker[] }> = ({ stickers }) => (
  <>
    {stickers.map((s, i) => (
      <Sequence key={i} from={s.start} durationInFrames={s.dur} name={`Sticker ${s.kind}`}>
        {s.kind === "broken-heart" ? <BrokenHeart s={s} /> : <Generic s={s} />}
      </Sequence>
    ))}
    {stickers.flatMap((s, i) =>
      (s.sfx ?? []).map((x, j) => (
        <Sequence key={`${i}-${j}`} from={Math.max(0, s.start + x.at)} name={`Sonido ${s.kind}`} layout="none">
          <Audio src={staticFile(x.src)} volume={x.volume} />
        </Sequence>
      )),
    )}
  </>
);
