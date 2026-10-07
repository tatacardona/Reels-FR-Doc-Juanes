// Pegar en src/Root.tsx (además de lo que ya tenga):
import { Reel, REEL_DURATION } from "./Reel";
import { Cover } from "./Cover";

// ...dentro del <>...</> de RemotionRoot:
<Composition id="Reel" component={Reel} durationInFrames={REEL_DURATION} fps={25} width={1080} height={1920} />
<Composition id="Cover" component={Cover} durationInFrames={1} fps={25} width={1080} height={1920}
  defaultProps={{ frame: 0, zoom: 1.1, kicker: "", big: "", sub: "", bigFirst: true, alt: false }} />
