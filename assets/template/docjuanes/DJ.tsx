import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont as loadPoppins } from "@remotion/google-fonts/Poppins";
import { loadFont as loadKalam } from "@remotion/google-fonts/Kalam";

// Línea gráfica de los posts de @docjuanes (revisada el 11 nov 2026):
// verde oliva oscuro con textura, verde lima de acento, papel crema rasgado, sans gruesa blanca,
// letra a mano para lo emotivo, rayitas lima, flechas dibujadas, cuadrícula lima y el logo abajo a la izquierda.
export const DJ = {
  lima: "#C8E03A",
  oliva: "#26310F",
  olivaMedio: "#46561D",
  crema: "#EFE7D4",
  cremaOscuro: "#D9CDB0",
  negro: "#12170A",
};

export const { fontFamily: DJ_BASE } = loadPoppins("normal", { weights: ["600", "800", "900"], subsets: ["latin"] });
export const { fontFamily: DJ_HAND } = loadKalam("normal", { weights: ["700"], subsets: ["latin"] });

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Tres rayitas lima que "brotan" (como en los posts)
export const Rays: React.FC<{ style?: React.CSSProperties; size?: number; delay?: number; color?: string; flip?: boolean; outline?: boolean }> = ({
  style, size = 90, delay = 0, color = DJ.lima, flip, outline,
}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [delay, delay + 6], [0, 1], clamp);
  const lines = [
    [18, 70, 42, 52],
    [30, 40, 58, 30],
    [54, 82, 84, 76],
  ];
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ ...style, transform: flip ? "scaleX(-1)" : undefined, overflow: "visible" }}>
      {outline
        ? lines.map(([x1, y1, x2, y2], i) => (
            <line key={`o${i}`} x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} stroke={DJ.oliva} strokeWidth={17} strokeLinecap="round" />
          ))
        : null}
      {lines.map(([x1, y1, x2, y2], i) => (
        <line key={i} x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} stroke={color} strokeWidth={10} strokeLinecap="round" />
      ))}
    </svg>
  );
};

// Flecha dibujada a mano (curva con punta)
export const Arrow: React.FC<{ style?: React.CSSProperties; w?: number; color?: string; flip?: boolean }> = ({ style, w = 260, color = "#fff", flip }) => (
  <svg width={w} height={w * 0.5} viewBox="0 0 200 100" style={{ ...style, transform: flip ? "scaleX(-1)" : undefined, overflow: "visible" }}>
    <path d="M8 70 C 40 20, 70 95, 105 55 S 160 30, 182 48" fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" />
    <path d="M160 30 L 184 48 L 158 64" fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

// Subrayado a mano
export const Underline: React.FC<{ w?: number; color?: string; style?: React.CSSProperties }> = ({ w = 400, color = DJ.lima, style }) => (
  <svg width={w} height={30} viewBox="0 0 400 30" preserveAspectRatio="none" style={style}>
    <path d="M6 18 C 90 6, 200 26, 394 10" fill="none" stroke={color} strokeWidth={9} strokeLinecap="round" />
  </svg>
);

// Barras lima (como "▬▬ ▬" de los posts)
export const Bars: React.FC<{ style?: React.CSSProperties; color?: string }> = ({ style, color = DJ.lima }) => (
  <div style={{ display: "flex", gap: 10, ...style }}>
    {[70, 40, 22].map((w, i) => (
      <div key={i} style={{ width: w, height: 14, background: color }} />
    ))}
  </div>
);

// Retazo de cuadrícula lima (esquina de los posts)
export const Grid: React.FC<{ w: number; h: number; style?: React.CSSProperties }> = ({ w, h, style }) => (
  <div
    style={{
      width: w, height: h, ...style,
      backgroundColor: DJ.lima,
      backgroundImage: `linear-gradient(${DJ.oliva}33 2px, transparent 2px), linear-gradient(90deg, ${DJ.oliva}33 2px, transparent 2px)`,
      backgroundSize: "34px 34px",
    }}
  />
);

// Íconos dibujados (propios, sin emojis con derechos)
export const Icon: React.FC<{ kind: "reloj" | "check" | "corazon" | "estrella" | "birrete"; size?: number; style?: React.CSSProperties; color?: string; ink?: string }> = ({
  kind, size = 140, style, color = DJ.lima, ink = DJ.oliva,
}) => {
  const s = { stroke: ink, strokeWidth: 6, strokeLinejoin: "round" as const, strokeLinecap: "round" as const };
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ ...style, overflow: "visible" }}>
      {kind === "reloj" && (
        <g {...s}>
          <rect x="22" y="8" width="56" height="10" rx="3" fill={ink} />
          <rect x="22" y="82" width="56" height="10" rx="3" fill={ink} />
          <path d="M28 18 C 28 40, 50 42, 50 50 C 50 58, 28 60, 28 82 L 72 82 C 72 60, 50 58, 50 50 C 50 42, 72 40, 72 18 Z" fill={DJ.crema} />
          <path d="M36 76 C 40 64, 60 64, 64 76 Z" fill={color} />
          <path d="M40 30 L 60 30 C 56 38, 44 38, 40 30 Z" fill={color} />
        </g>
      )}
      {kind === "check" && (
        <g {...s}>
          <circle cx="50" cy="50" r="42" fill={color} />
          <path d="M30 52 L 45 66 L 72 36" fill="none" strokeWidth={10} />
        </g>
      )}
      {kind === "corazon" && (
        <path {...s} d="M50 86 C 18 64, 8 46, 14 30 C 20 14, 42 12, 50 30 C 58 12, 80 14, 86 30 C 92 46, 82 64, 50 86 Z" fill={color} />
      )}
      {kind === "estrella" && (
        <path {...s} d="M50 6 L 58 40 L 94 50 L 58 60 L 50 94 L 42 60 L 6 50 L 42 40 Z" fill={color} />
      )}
      {kind === "birrete" && (
        <g {...s}>
          <path d="M6 40 L 50 20 L 94 40 L 50 60 Z" fill={color} />
          <path d="M26 50 L 26 70 C 40 82, 60 82, 74 70 L 74 50" fill={DJ.crema} />
          <path d="M86 44 L 86 72" fill="none" />
          <circle cx="86" cy="76" r="5" fill={ink} />
        </g>
      )}
    </svg>
  );
};

// Logo oficial (Drive · carpeta de logos 1-IRcl5jGlg2AHknMEX-V6oLamhrkRLOb): V3 verde+blanco (fondo oscuro), V1 verde+negro (fondo claro)
// claro = texto oliva para fondos crema/blancos
export const Logo: React.FC<{ style?: React.CSSProperties; w?: number; claro?: boolean }> = ({ style, w = 250, claro }) => (
  <Img src={staticFile(claro ? "Logo_Doc_Juanes_V1.png" : "Logo_Doc_Juanes_V3.png")} style={{ position: "absolute", width: w, maxWidth: "none", height: "auto", filter: "drop-shadow(0 3px 8px rgba(0,0,0,0.55))", ...style }} />
);

// Fondo oliva con textura de grano (como los posts oscuros)
export const OliveTexture: React.FC<{ light?: boolean }> = ({ light }) => (
  <div style={{ position: "absolute", inset: 0, background: light ? DJ.crema : `radial-gradient(120% 90% at 30% 20%, ${DJ.olivaMedio} 0%, ${DJ.oliva} 60%, ${DJ.negro} 100%)` }}>
    <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: light ? 0.18 : 0.35, mixBlendMode: light ? "multiply" : "overlay" }}>
      <filter id="grano">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grano)" />
    </svg>
  </div>
);

export const TORN_EDGE =
  "polygon(0% 6%, 5% 0%, 12% 5%, 20% 1%, 28% 6%, 37% 0%, 45% 5%, 54% 1%, 62% 6%, 71% 0%, 79% 5%, 88% 1%, 95% 6%, 100% 2%, 100% 96%, 94% 100%, 86% 95%, 77% 100%, 69% 95%, 60% 100%, 51% 94%, 42% 100%, 34% 95%, 25% 100%, 17% 94%, 8% 100%, 0% 95%)";

// Flecha dibujada a mano que apunta hacia abajo y rebota (invita a comentar). Lima con borde oliva.
export const ArrowDown: React.FC<{ style?: React.CSSProperties; size?: number }> = ({ style, size = 150 }) => {
  const f = useCurrentFrame();
  const entra = interpolate(f, [0, 8], [0, 1], clamp);
  const bote = Math.sin((f / 25) * Math.PI * 2 * 1.4) * 16; // ~1,4 rebotes por segundo
  return (
    <svg width={size} height={size * 1.3} viewBox="0 0 100 130"
      style={{ ...style, overflow: "visible", opacity: entra, transform: `translateY(${bote + (1 - entra) * -30}px)` }}>
      {[DJ.oliva, DJ.lima].map((col, i) => (
        <g key={i} stroke={col} strokeWidth={i ? 10 : 19} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <path d="M50 8 C 40 40, 62 70, 50 108" />
          <path d="M26 86 L 50 112 L 74 84" />
        </g>
      ))}
    </svg>
  );
};
