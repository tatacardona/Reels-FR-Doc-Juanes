import { AbsoluteFill } from "remotion";
import { Footage, Tone, Vignette } from "./Reel/Footage";
import {
  CAPTION_FONT, EMPH_COLOR, EMPH_FONT, EMPH_STROKE_COLOR, EMPH_STYLE, EMPH_WEIGHT,
  EMPH2_COLOR, EMPH2_FONT, EMPH2_STYLE, EMPH2_WEIGHT,
} from "./Reel/constants";

const stroke = (px: number, color = "#000") => ({ WebkitTextStroke: `${px}px ${color}`, paintOrder: "stroke fill" as const });

// Portada 9:16 para Instagram con el MISMO estilo del video: un cuadro del crudo (con su luz/tono) y el
// texto en las fuentes y colores de los resaltados. El texto queda dentro del recorte 4:5 que muestra la
// cuadrícula del perfil (y entre 285 y 1635 px). Uso: npx remotion still Cover out/portadas/portada-N.jpg --props='{…}'
//   frame: cuadro del video CRUDO (seg × 25) con buena expresión; zoom: encuadre (1.0-1.4)
//   kicker: etiqueta corta arriba (opcional); big: frase gancho grande; sub: frase de apoyo; alt: big con la 2.ª fuente
export const Cover: React.FC<{ frame: number; zoom: number; kicker: string; big: string; sub: string; bigFirst: boolean; alt: boolean }> = ({
  frame, zoom, kicker, big, sub, bigFirst, alt,
}) => {
  const Big = (
    <div
      style={{
        fontFamily: alt ? EMPH2_FONT : EMPH_FONT,
        fontStyle: alt ? EMPH2_STYLE : EMPH_STYLE,
        fontWeight: alt ? EMPH2_WEIGHT : EMPH_WEIGHT,
        fontSize: 124, lineHeight: 1.04, color: alt ? EMPH2_COLOR : EMPH_COLOR, textWrap: "balance",
        ...stroke(20, EMPH_STROKE_COLOR), textShadow: "0 10px 30px rgba(0,0,0,0.5)",
      }}
    >
      {big}
    </div>
  );
  const Sub = (
    <div style={{ fontFamily: CAPTION_FONT, fontWeight: 900, fontSize: 60, lineHeight: 1.1, color: "#fff", textWrap: "balance", maxWidth: 900, ...stroke(12), textShadow: "0 8px 24px rgba(0,0,0,0.5)" }}>
      {sub}
    </div>
  );
  return (
    <AbsoluteFill className="bg-black">
      <Footage trim={frame} dur={1} zoom={zoom} />
      <Vignette />
      <Tone />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, transparent 45%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0.5) 100%)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 330, padding: "0 60px", display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: 18 }}>
        {kicker ? (
          <div style={{ fontFamily: CAPTION_FONT, fontWeight: 800, fontSize: 38, color: "#111", background: EMPH_COLOR, padding: "10px 28px", borderRadius: 40, letterSpacing: "0.02em" }}>
            {kicker}
          </div>
        ) : null}
        {bigFirst ? Big : Sub}
        {bigFirst ? Sub : Big}
      </div>
    </AbsoluteFill>
  );
};
