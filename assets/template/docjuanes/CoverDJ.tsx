import { AbsoluteFill, Img, staticFile } from "remotion";
import { Footage, Tone } from "./Reel/Footage";
import { Arrow, Bars, DJ, DJ_BASE, DJ_HAND, Grid, Icon, Logo, OliveTexture, Rays, TORN_EDGE, Underline } from "./DJ";

// Portadas con la línea gráfica de los posts de @docjuanes. Todo el texto queda en la zona 4:5 de la
// cuadrícula del perfil (y 285-1635). Juanes recortado con IA (scripts/recorte.py → public/recorte-<seg>.png).
// Uso: npx remotion still CoverDJ out/portadas/NO_RENUNCIES_PORTADA_N.jpg --props='{"n":1}'

const Persona: React.FC<{ src: string; w: number; left: number; top: number; shadow?: boolean }> = ({ src, w, left, top, shadow = true }) => (
  <Img
    src={staticFile(src)}
    style={{ position: "absolute", width: w, maxWidth: "none", height: "auto", left, top, filter: shadow ? "drop-shadow(0 30px 40px rgba(0,0,0,0.45))" : undefined }}
  />
);

const Paper: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; rot?: number }> = ({ children, style, rot = -4 }) => (
  <div style={{ position: "absolute", transform: `rotate(${rot}deg)`, filter: "drop-shadow(0 14px 18px rgba(0,0,0,0.35))", ...style }}>
    <div style={{ background: DJ.crema, clipPath: TORN_EDGE, padding: "44px 46px 30px", fontFamily: DJ_HAND, fontWeight: 700, color: DJ.oliva, lineHeight: 1.05 }}>
      {children}
    </div>
  </div>
);

// 1 · Oscuro (como "Nadie sabía la fecha…"): el dato fuerte "15 años" en lima
const Uno: React.FC = () => (
  <AbsoluteFill>
    <OliveTexture />
    <Grid w={330} h={150} style={{ position: "absolute", right: 0, bottom: 0, opacity: 0.9 }} />
    <Persona src="recorte-8.2.png" w={2350} left={-330} top={330} />
    <div style={{ position: "absolute", left: 70, top: 300, width: 620, fontFamily: DJ_BASE, color: "#fff" }}>
      <div style={{ fontSize: 58, fontWeight: 600, lineHeight: 1.15 }}>Un médico llevaba</div>
      <div style={{ fontSize: 210, fontWeight: 900, color: DJ.lima, lineHeight: 0.95, marginTop: 10 }}>15 años</div>
      <div style={{ fontSize: 50, fontWeight: 800, lineHeight: 1.15, marginTop: 8 }}>presentándose a la especialización.</div>
      <Underline w={420} style={{ marginTop: 6 }} />
    </div>
    <Rays style={{ position: "absolute", left: 610, top: 360 }} size={120} />
    <Paper style={{ left: 30, top: 1420 }} rot={-5}>
      <div style={{ fontSize: 66 }}>¿Cuántos intentos</div>
      <div style={{ fontSize: 66 }}>llevas <span style={{ background: DJ.lima, padding: "0 12px" }}>tú?</span></div>
    </Paper>
    <Arrow style={{ position: "absolute", left: 90, top: 1300 }} w={220} color={DJ.lima} />
    <Logo style={{ left: 60, bottom: 60 }} />
  </AbsoluteFill>
);

// 2 · Crema (como "En Futuros Residentes tenemos prohibido…"): la frase emotiva "no renuncian a ese sueño"
const Dos: React.FC<{ foto: string; pw: number; pl: number; pt: number }> = ({ foto, pw, pl, pt }) => (
  <AbsoluteFill>
    <OliveTexture light />
    <div style={{ position: "absolute", left: -60, right: -60, top: 980, height: 980, background: DJ.olivaMedio, clipPath: TORN_EDGE, transform: "rotate(-3deg)" }} />
    <Persona src={foto} w={pw} left={pl} top={pt} />
    <div style={{ position: "absolute", left: 70, right: 70, top: 300, fontFamily: DJ_BASE, color: DJ.oliva, textAlign: "left" }}>
      <Bars style={{ marginBottom: 22 }} color={DJ.olivaMedio} />
      <div style={{ fontSize: 64, fontWeight: 800, lineHeight: 1.1 }}>
        Un médico llevaba{" "}
        <span style={{ background: DJ.lima, padding: "0 16px", fontWeight: 900, fontSize: 92, display: "inline-block", transform: "rotate(-2deg)", boxShadow: `8px 8px 0 ${DJ.oliva}` }}>15 años</span>
        <br />presentándose a la <span style={{ color: DJ.olivaMedio }}>especialización.</span>
      </div>
    </div>
    <Icon kind="reloj" size={130} style={{ position: "absolute", right: 90, top: 640, transform: "rotate(12deg)" }} />
    <Rays style={{ position: "absolute", right: 60, top: 330 }} size={110} color={DJ.olivaMedio} flip />
    <div
      style={{
        position: "absolute", left: 60, top: 1500, fontFamily: DJ_HAND, fontWeight: 700, fontSize: 70, color: "#fff",
        background: DJ.oliva, padding: "10px 26px", transform: "rotate(-3deg)",
      }}
    >
      ¿Cuántos intentos <span style={{ color: DJ.lima }}>llevas tú?</span>
    </div>
    <Logo style={{ left: 60, bottom: 60 }} />
  </AbsoluteFill>
);

// 3 · Sobre el video (como los reels con texto encima): la invitación final
const Tres: React.FC = () => (
  <AbsoluteFill className="bg-black">
    <Footage trim={Math.round(89.8 * 25)} dur={1} zoom={1.0} />
    <Tone />
    <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 40%, ${DJ.oliva}CC 60%, ${DJ.oliva} 90%)` }} />
    <div style={{ position: "absolute", left: 70, right: 70, top: 940, fontFamily: DJ_BASE, color: "#fff", textAlign: "center" }}>
      <div style={{ fontSize: 60, fontWeight: 800, lineHeight: 1.1 }}>Un médico llevaba</div>
      <div style={{ fontSize: 170, fontWeight: 900, lineHeight: 1, color: DJ.lima }}>15 años</div>
      <div style={{ fontSize: 56, fontWeight: 800, lineHeight: 1.15 }}>presentándose a la especialización.</div>
      <Underline w={520} style={{ marginTop: 4 }} />
    </div>
    <Paper style={{ left: 70, top: 1400 }} rot={-3}>
      <div style={{ fontSize: 64, display: "flex", alignItems: "center", gap: 14, whiteSpace: "nowrap" }}>
        <Icon kind="reloj" size={80} /> ¿Cuántos intentos llevas tú?
      </div>
    </Paper>
    <Rays style={{ position: "absolute", left: 60, top: 980 }} size={110} flip />
    <Icon kind="estrella" size={90} style={{ position: "absolute", right: 70, top: 1040, transform: "rotate(10deg)" }} />
    <Logo style={{ left: 60, bottom: 60 }} />
  </AbsoluteFill>
);

export const CoverDJ: React.FC<{ n: number; foto?: string; pw?: number; pl?: number; pt?: number }> = ({ n, foto = "recorte-13.7.png", pw = 2250, pl = -560, pt = 260 }) =>
  n === 1 ? <Uno /> : n === 2 ? <Dos foto={foto} pw={pw} pl={pl} pt={pt} /> : <Tres />;
