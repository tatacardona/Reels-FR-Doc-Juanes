import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Destello de luz de sol con colores ("light leak") para las transiciones: manchas de luz cálida
// (dorado, naranja, rosa) con un toque frío (turquesa) que cruzan el cuadro en diagonal y se
// suman a la imagen (mezcla "screen"), más un haz suave tipo reflejo de lente. Sutil: pico ~0.55.
// `seed` cambia la dirección y los colores en cada corte para que no se repita igual.
export const LightLeak: React.FC<{ dur: number; seed: number; strength?: number }> = ({ dur, seed, strength = 0.6 }) => {
  const f = useCurrentFrame();
  const t = f / dur; // 0 → 1
  const env = interpolate(t, [0, 0.4, 1], [0, 1, 0], { ...clamp, easing: (x) => Math.sin((x * Math.PI) / 2) });
  const dir = random(`d${seed}`) > 0.5 ? 1 : -1;
  // entra por un borde (arriba a un lado) y cruza: la luz viene "de afuera", sin quedarse sobre la cara
  const x = 50 + dir * interpolate(t, [0, 1], [-55, 30]);
  const y = 4 + random(`y${seed}`) * 12;
  const hue = random(`h${seed}`) * 40 - 20; // variación de tono por corte
  const blobs = [
    { dx: 0, dy: 0, r: 42, c: `hsla(${38 + hue}, 100%, 62%, 1)` }, // dorado
    { dx: -14 * dir, dy: 10, r: 32, c: `hsla(${18 + hue}, 100%, 58%, 0.9)` }, // naranja
    { dx: 16 * dir, dy: -4, r: 26, c: `hsla(${330 + hue}, 95%, 66%, 0.8)` }, // rosa
    { dx: 26 * dir, dy: 16, r: 20, c: `hsla(${185 + hue}, 90%, 62%, 0.5)` }, // turquesa suave
  ];
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", opacity: env * strength, pointerEvents: "none" }}>
      {blobs.map((b, i) => (
        <AbsoluteFill
          key={i}
          style={{
            background: `radial-gradient(circle at ${x + b.dx}% ${y + b.dy}%, ${b.c} 0%, transparent ${b.r}%)`,
            filter: "blur(30px)",
          }}
        />
      ))}
      {/* haz diagonal, como un reflejo de sol en el lente */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(${dir > 0 ? 115 : 65}deg, transparent ${x - 9}%, rgba(255,236,200,0.45) ${x - 1}%, rgba(255,250,240,0.6) ${x}%, rgba(255,200,230,0.3) ${x + 3}%, transparent ${x + 9}%)`,
          filter: "blur(12px)",
        }}
      />
      {/* pequeños destellos (bokeh) */}
      {Array.from({ length: 5 }).map((_, i) => {
        const bx = x + (random(`bx${seed}-${i}`) - 0.5) * 60;
        const by = y + (random(`by${seed}-${i}`) - 0.2) * 50;
        const s = 40 + random(`bs${seed}-${i}`) * 70;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${bx}%`,
              top: `${by}%`,
              width: s,
              height: s,
              borderRadius: "50%",
              transform: "translate(-50%, -50%)",
              background: `radial-gradient(circle, hsla(${(40 + i * 70 + hue) % 360}, 100%, 80%, 0.55) 0%, transparent 70%)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
