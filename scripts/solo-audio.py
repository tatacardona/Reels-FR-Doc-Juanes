#!/usr/bin/env python3
"""Cambia SOLO el audio de un Reel ya exportado, sin volver a exportar la imagen (Janeth, 25 oct 2026: «cuando es solo volumen de
la canción, no debe renderizar»; el método viene del skill de 10FR, donde se usa desde el 19 oct).

Sirve únicamente cuando la imagen no cambia: mismo edit.json en tramos, cortes y duraciones; solo cambian la música (volumen,
rampas, otra parte de la canción) o los efectos de sonido. Si cambió una palabra, un corte, un subtítulo o un sticker, exporta completo.

Uso (desde la carpeta del proyecto, con $FF exportado):
  "$PY" scripts/solo-audio.py out/NOMBRE_REEL_v3.mp4 out/NOMBRE_REEL_v4.mp4 [--comp Reel] [--factor 1.06] [--concurrency 2]
  --factor: el mismo de speed.sh si el video se aceleró (el audio nuevo se acelera igual, sin cambiar el tono).

1. Exporta solo el audio de la composición (wav).
2. Mide el desfase contra el audio del video anterior (las voces son las mismas: se correlacionan en tres puntos; el wav suele salir
   ≈ 43 ms adelantado por el retardo del codificador AAC).
3. Une la imagen del video anterior (sin recodificar) con el audio corrido ese desfase y vuelve a medir: debe quedar en menos de 2 ms.
   Si no, avisa y no deja el video nuevo.
"""
import os, shutil, subprocess, sys
import numpy as np

FF = os.environ["FF"]
viejo, nuevo = sys.argv[1], sys.argv[2]
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
comp, factor, conc = opt("--comp", "Reel"), opt("--factor"), opt("--concurrency")
os.makedirs("work", exist_ok=True)
wav, wav2 = "work/solo_audio.wav", "work/solo_audio_vel.wav"
npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"  # en Windows es npx.cmd


def dur(f):
    out = subprocess.run([FF, "-hide_banner", "-i", f], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def audio(f, t0, d, sr=8000):
    r = subprocess.run([FF, "-v", "error", "-ss", str(t0), "-t", str(d), "-i", f, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True).stdout
    return np.frombuffer(r, np.float32)


def desfase(ref, otro):
    """ms que hay que retrasar 'otro' para que coincida con 'ref' (mediana de tres puntos con voz)."""
    D = dur(ref); res = []
    for t0 in (0.15 * D, 0.5 * D, 0.85 * D):
        x = audio(ref, t0, 4); y = audio(otro, t0, 4); n = min(len(x), len(y)); x, y = x[:n], y[:n]
        c = np.correlate(y[400:-400], x, "valid"); res.append(-(np.argmax(c) - 400) / 8)
    return float(np.median(res)), res


print("1/3 audio de la composición…")
subprocess.run([npx, "remotion", "render", comp, wav, "--codec=wav", "--log=error"] + (["--concurrency=" + conc] if conc else []), check=True)
if factor:
    subprocess.run([FF, "-v", "error", "-y", "-i", wav, "-af", f"atempo={factor}", wav2], check=True); os.replace(wav2, wav)
ms, pts = desfase(viejo, wav)
print(f"2/3 desfase del wav: {ms:.1f} ms (puntos: {', '.join(f'{p:.1f}' for p in pts)})")
D = dur(viejo)
af = (f"adelay={max(0, round(ms))}:all=1," if ms >= 0 else f"atrim=start={-ms / 1000:.4f},asetpts=PTS-STARTPTS,") + f"atrim=0:{D:.3f}"
tmp = nuevo + ".tmp.mp4"
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", viejo, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", af, "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", tmp], check=True)
ms2, pts2 = desfase(viejo, tmp)
print(f"3/3 desfase final: {ms2:.1f} ms (puntos: {', '.join(f'{p:.1f}' for p in pts2)})")
if abs(ms2) > 2:
    print("⚠ el audio quedó corrido: no se deja el video nuevo; exporta completo"); os.remove(tmp); sys.exit(1)
os.replace(tmp, nuevo); os.remove(wav)
print(f"listo: {nuevo} (imagen de {viejo} + audio nuevo). Mide el volumen con verify.sh antes de entregar.")
