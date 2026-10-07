// Exporta fotogramas sueltos para revisar encuadres, subtítulos y cara sin renderizar todo.
// Uso: node scripts/stills.mjs <carpeta_salida> <frame> [frame...]
import {bundle} from "@remotion/bundler";
import {renderStill, selectComposition} from "@remotion/renderer";
const serveUrl = await bundle({entryPoint: "src/index.ts"});
const comp = await selectComposition({serveUrl, id: "Reel"});
for (const f of process.argv.slice(3).map(Number)) {
  await renderStill({serveUrl, composition: comp, frame: f, output: `${process.argv[2]}/f${f}.jpg`, imageFormat: "jpeg", scale: Number(process.env.SCALE ?? 0.25)});
}
console.log("ok", comp.durationInFrames, "frames");
