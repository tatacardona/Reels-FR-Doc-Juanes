import { AbsoluteFill, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";
import {
  CAPTION_FONT, CAPTION_TOP, EMPH_COLOR, EMPH_FONT, EMPH_SIZE, EMPH_STROKE, EMPH_STROKE_COLOR, EMPH_STYLE, EMPH_WEIGHT,
  EMPH2_COLOR, EMPH2_FONT, EMPH2_SIZE, EMPH2_STYLE, EMPH2_WEIGHT,
} from "./constants";

export type Caption = { start: number; end: number; words: { t: string; emph: boolean; alt?: boolean }[] };

const Chunk: React.FC<{ c: Caption }> = ({ c }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hasEmph = c.words.some((w) => w.emph);
  const pop = spring({ frame: f, fps, config: { damping: 12, stiffness: 220 }, durationInFrames: 8 });
  const scale = interpolate(pop, [0, 1], [hasEmph ? 0.55 : 0.8, 1]);
  const lift = interpolate(pop, [0, 1], [18, 0]);

  return (
    <AbsoluteFill style={{ top: CAPTION_TOP, alignItems: "center" }}>
      <div
        style={{
          fontFamily: CAPTION_FONT,
          fontWeight: 900,
          textAlign: "center",
          lineHeight: 1.05,
          maxWidth: 940,
          transform: `translateY(${lift}px) scale(${scale})`,
          opacity: interpolate(f, [0, 2], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        {c.words.map((w, i) => (
          <span
            key={i}
            style={{
              display: "inline-block",
              margin: "0 12px",
              fontFamily: w.emph ? (w.alt ? EMPH2_FONT : EMPH_FONT) : CAPTION_FONT,
              fontWeight: w.emph ? (w.alt ? EMPH2_WEIGHT : EMPH_WEIGHT) : 900,
              fontStyle: w.emph ? (w.alt ? EMPH2_STYLE : EMPH_STYLE) : "normal",
              fontSize: w.emph ? (w.alt ? EMPH2_SIZE : EMPH_SIZE) : 82,
              color: w.emph ? (w.alt ? EMPH2_COLOR : EMPH_COLOR) : "#FFFFFF",
              WebkitTextStroke: w.emph ? `${EMPH_STROKE}px ${EMPH_STROKE_COLOR}` : "11px #000",
              paintOrder: "stroke fill",
              textShadow: "0 8px 24px rgba(0,0,0,0.55)",
              letterSpacing: "0.005em",
            }}
          >
            {w.t}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const Captions: React.FC<{ captions: Caption[] }> = ({ captions }) => (
  <>
    {captions.map((c, i) => (
      <Sequence key={i} from={c.start} durationInFrames={Math.max(1, c.end - c.start)} layout="none">
        <Chunk c={c} />
      </Sequence>
    ))}
  </>
);
