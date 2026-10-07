"""Sigue la cabeza cuadro a cuadro en public/video-vertical.mp4 (para efectos que deben quedarse
sobre la cabeza aunque la persona se mueva).
Uso: $PY scripts/head-track.py <inicio_seg> <fin_seg>      (segundos del video CRUDO)
Salida: work/head.json  {"fps":25, "t0": inicio, "pts": [[x%, y%, ancho_cara%], ...]}
  x%,y% = centro-arriba de la cabeza (borde superior del pelo) en el cuadro vertical SIN zoom.
build-edit.py lo usa para los stickers con "follow_head": true.
Requiere opencv-python-headless<5 (la 5 ya no trae CascadeClassifier): $PY -m pip install "opencv-python-headless<5"."""
import json, subprocess, sys
import numpy as np, cv2

t0, t1 = float(sys.argv[1]), float(sys.argv[2])
W, H, FPS = 360, 640, 25
FF = __import__("imageio_ffmpeg").get_ffmpeg_exe()
raw = subprocess.run([FF, "-loglevel", "error", "-ss", str(t0), "-i", "public/video-vertical.mp4", "-t", str(t1 - t0),
                      "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
pts, last = [], None
for g in frames:
    faces = det.detectMultiScale(g, 1.1, 5, minSize=(40, 40))
    if len(faces):
        # la cara más parecida a la anterior (o la más grande)
        x, y, w, h = min(faces, key=lambda f: abs(f[0] - last[0]) + abs(f[1] - last[1])) if last is not None \
            else max(faces, key=lambda f: f[2] * f[3])
        last = (x, y, w, h)
    if last is None:
        pts.append(None); continue
    x, y, w, h = last
    # el detector encierra frente-mentón: el pelo empieza ~0,28 caras más arriba
    pts.append([(x + w / 2) / W * 100, (y - 0.28 * h) / H * 100, w / W * 100])
# rellenar huecos y suavizar (media móvil de 5 cuadros) para que no tiemble
first = next(p for p in pts if p)
pts = [p or first for p in pts]
for i in range(1, len(pts)):
    pts[i] = pts[i] if pts[i] else pts[i - 1]
a = np.array(pts)
k = 5
sm = np.array([a[max(0, i - k // 2): i + k // 2 + 1].mean(0) for i in range(len(a))])
json.dump({"fps": FPS, "t0": t0, "pts": sm.round(2).tolist()}, open("work/head.json", "w"))
print(f"{len(sm)} cuadros; cabeza x {sm[:,0].min():.0f}-{sm[:,0].max():.0f}%, y {sm[:,1].min():.0f}-{sm[:,1].max():.0f}%, "
      f"ancho cara ~{sm[:,2].mean():.0f}%")
