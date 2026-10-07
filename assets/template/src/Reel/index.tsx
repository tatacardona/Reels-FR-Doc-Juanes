import { AbsoluteFill, Audio, interpolate, random, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Captions, type Caption } from "./Captions";
import { MUSICA, MUSICA_INICIO_SEG, VOLUMEN_MUSICA } from "./constants";
import edit from "./edit.json";
import { Footage, Tone, Vignette } from "./Footage";
import { LEAK_SOUND, LEAK_STRENGTH } from "./constants";
import { LightLeak } from "./LightLeak";
import { Stickers, type Sticker } from "./Stickers";
import { TornPhoto } from "./TornPhoto";

// Duración total, calculada por scripts/build-edit.py
export const REEL_DURATION = Math.max(1, edit.total);

type Clip = { start: number; dur: number; trim: number; zoom: number; fx: string; push?: { at: number; to: number } };
type Photo = { src: string; start: number; tearAt?: number; end?: number };

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Voz mejorada del tramo, con micro-fundidos solo en los cortes reales
// (si el siguiente tramo continúa el mismo audio, no hay fundido para que no se note)
const Voice: React.FC<{ trim: number; dur: number; fadeIn: boolean; fadeOut: boolean }> = ({
  trim,
  dur,
  fadeIn,
  fadeOut,
}) => (
  <Audio
    src={staticFile("voz-mejorada.wav")}
    trimBefore={trim}
    volume={(f) =>
      Math.min(fadeIn ? interpolate(f, [0, 1], [0, 1], clamp) : 1, fadeOut ? interpolate(f, [dur - 2, dur], [1, 0], clamp) : 1)
    }
  />
);

const Flash: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ background: "white", opacity: interpolate(f, [0, 9], [1, 0], clamp) }} />;
};

// Sacudida corta de la imagen en los impactos (quiebre, corazón roto, sello)
const Shake: React.FC<{ at: number[]; children: React.ReactNode }> = ({ at, children }) => {
  const f = useCurrentFrame();
  const t = Math.min(...at.map((a) => (f >= a ? f - a : 1e9)));
  const amp = t < 8 ? interpolate(t, [0, 8], [22, 0], clamp) : 0;
  return (
    <AbsoluteFill style={{ transform: `translate(${(random(`sx${f}`) - 0.5) * amp}px, ${(random(`sy${f}`) - 0.5) * amp}px)` }}>
      {children}
    </AbsoluteFill>
  );
};

export const Reel: React.FC = () => {
  const clips = edit.clips as Clip[];
  const bodyDur = edit.total;

  return (
    <AbsoluteFill className="bg-black">
      {/* Cada tramo con su encuadre fijo: el plano cambia solo en el corte */}
      <Shake at={edit.shakes ?? []}>
        {clips.map((c, i) => (
          <Sequence key={i} from={c.start} durationInFrames={c.dur} name={`Clip ${i + 1}`}>
            <Footage trim={c.trim} dur={c.dur} zoom={c.zoom} fx={c.fx} push={c.push} />
            <Vignette />
          </Sequence>
        ))}
        <Tone />
      </Shake>
      {clips.map((c, i) => (
        <Sequence key={i} from={c.start} durationInFrames={c.dur} name={`Voz ${i + 1}`} layout="none">
          <Voice
            trim={c.trim}
            dur={c.dur}
            fadeIn={i === 0 || clips[i - 1].trim + clips[i - 1].dur !== c.trim}
            fadeOut={i === clips.length - 1 || c.trim + c.dur !== clips[i + 1].trim}
          />
          {c.fx === "flash" ? <Flash /> : null}
        </Sequence>
      ))}

      {/* Whoosh en los cambios de tema: termina justo en el corte para no tapar la primera sílaba de la siguiente frase */}
      {clips
        .filter((c) => c.fx === "whoosh" || c.fx === "flash")
        .map((c, i) => (
          <Sequence key={i} from={Math.max(0, c.start - 7)} durationInFrames={7} name="Whoosh">
            {/* solo la cola del whoosh (7 cuadros) y más suave: con cortes apretados ya no hay silencio
                antes del corte y un whoosh largo tapa el final de la palabra anterior ("elegibles") */}
            <Audio src={staticFile("sfx-whoosh.wav")} trimBefore={6} volume={0.3} />
          </Sequence>
        ))}

      {MUSICA ? (
        <Sequence durationInFrames={bodyDur} name="Música">
          <Audio
            src={staticFile(MUSICA)}
            trimBefore={MUSICA_INICIO_SEG * edit.fps}
            volume={(f) =>
              interpolate(f, [0, 25, bodyDur - 25, bodyDur], [0, VOLUMEN_MUSICA, VOLUMEN_MUSICA, 0], clamp)
            }
          />
        </Sequence>
      ) : null}

      {/* Fotos superpuestas: debajo de los subtítulos para que siempre se lean */}
      {(edit.photos as Photo[]).map((p, i) => (
        <TornPhoto key={i} src={p.src} from={p.start} tearAt={p.tearAt} end={p.end} />
      ))}

      {/* Destello de luz de sol con colores en los cambios de tema (fx "leak"): empieza un poco antes
          del corte y lo cubre; discreto y, por defecto, sin sonido (LEAK_SOUND) */}
      {clips
        .filter((c) => c.fx === "leak")
        .map((c, i) => (
          <Sequence key={`leak${i}`} from={Math.max(0, c.start - 8)} durationInFrames={22} name="Destello de luz">
            <LightLeak dur={22} seed={i + 1} strength={LEAK_STRENGTH} />
            {LEAK_SOUND ? <Audio src={staticFile(LEAK_SOUND)} volume={0.22} /> : null}
          </Sequence>
        ))}

      {/* Stickers (dibujos propios) con sus efectos de sonido */}
      <Stickers stickers={(edit.stickers ?? []) as Sticker[]} />
      {((edit.sounds ?? []) as { src: string; start: number; volume: number }[]).map((s, i) => (
        <Sequence key={i} from={s.start} name="Sonido" layout="none">
          <Audio src={staticFile(s.src)} volume={s.volume} />
        </Sequence>
      ))}

      {/* Eco suave sobre frases de trascendencia (solo las repeticiones: public/eco-N.wav, scripts/eco.py) */}
      {((edit as { echo?: { start: number }[] }).echo ?? []).map((e, i) => (
        <Sequence key={`eco${i}`} from={e.start} name="Eco" layout="none">
          <Audio src={staticFile(`eco-${i}.wav`)} volume={0.9} />
        </Sequence>
      ))}

      <Captions captions={edit.captions as Caption[]} />

      {/* Sin fundido a negro: el final queda nítido, con un acercamiento suave (end_push) */}
    </AbsoluteFill>
  );
};
