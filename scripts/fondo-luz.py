"""Fondo difuminado sutil + luz de relleno en la cara + luces de colores tipo vitral en la pared.
Procesa public/video-vertical.mp4 cuadro a cuadro (solo los tramos que usa src/Reel/edit.json; el resto
se copia igual) y escribe public/video-fondo.mp4, que es el que usa el Reel (VIDEO_SRC en constants.ts).

La IA (MediaPipe) separa a la persona del fondo. Ajustes por video en edit-config.json → "fondo":
  blur      desenfoque del fondo (5 = sutil, la persona casi no "recortada")
  feather   suavidad del borde de la silueta (14 = no se nota el borde)
  fill      luz de relleno en la cara (0 = nada; 0.9 = ojos y barba claros sin quemar)
  vitral    intensidad de las luces de colores en la pared (0 = nada; 0.22 = muy tenue)
  bokeh     intensidad de los destellos redondos (0.18 = casi imperceptibles)
Uso: $PY scripts/fondo-luz.py
Requiere mediapipe==0.10.14 con numpy<2 y opencv-python-headless<5 (setup-tools.sh)."""
import json, subprocess, sys, time
import numpy as np, cv2, mediapipe as mp

cfg = json.load(open("edit-config.json")).get("fondo", {})
BLUR, FEATHER = cfg.get("blur", 5), cfg.get("feather", 14)
FILL, VITRAL, BOKEH = cfg.get("fill", 0.9), cfg.get("vitral", 0.22), cfg.get("bokeh", 0.18)
FF = __import__("imageio_ffmpeg").get_ffmpeg_exe()
W, H, FPS = 1440, 2560, 25

edit = json.load(open("src/Reel/edit.json"))
need = set()
for c in edit["clips"]:
    need.update(range(max(0, c["trim"] - 5), c["trim"] + c["dur"] + 5))

dec = subprocess.Popen([FF, "-loglevel", "error", "-i", "public/video-vertical.mp4", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen([FF, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "25",
                        "public/video-fondo.tmp.mp4"], stdin=subprocess.PIPE)

seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0)
fd = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.4)

# Mapas de luz a 1/4 de resolución (se escalan): manchas de color que se mueven muy despacio + bokeh tenue
w4, h4 = W // 4, H // 4
yy, xx = np.mgrid[0:h4, 0:w4].astype(np.float32)
COLS = [(0.75, 0.45, 1.0), (0.35, 0.85, 1.0), (1.0, 0.8, 0.35), (0.95, 0.55, 0.9)]  # BGR: rosa, dorado, turquesa, lila
rng = np.random.default_rng(3)
BLOBS = [(0.15 + 0.7 * ((i * 0.37) % 1), 0.15 + 0.6 * rng.random(), rng.uniform(0, 6.28)) for i in range(4)]
BOK = [(rng.random() * w4, rng.random() * h4 * 0.8, rng.uniform(5, 14), rng.uniform(0, 6.28)) for _ in range(14)]


def light_maps(t):
    L = np.zeros((h4, w4, 3), np.float32); A = np.zeros((h4, w4, 1), np.float32)
    for i, (px, py, ph) in enumerate(BLOBS):
        cx = (px + 0.06 * np.sin(t * 0.15 + ph)) * w4; cy = (py + 0.05 * np.cos(t * 0.12 + ph)) * h4; r = 0.28 * w4
        g = np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / (r * 1.3)) ** 2))[..., None]
        L += g * np.array(COLS[i], np.float32); A += g
    for i, (bx, by, br, ph) in enumerate(BOK):
        d = np.sqrt((xx - bx - 6 * np.sin(t * 0.2 + ph)) ** 2 + (yy - by - 4 * np.cos(t * 0.17 + ph)) ** 2)
        disc = (np.clip(1 - (d - br) / 5.5, 0, 1) * BOKEH * (0.6 + 0.4 * np.sin(t * 0.8 + ph) ** 2))[..., None]
        L += disc * np.array(COLS[i % 4], np.float32); A += disc
    A = np.clip(A, 0, 1); col = np.clip(L / np.maximum(A, 1e-3), 0, 1)
    return cv2.resize(A, (W, H))[..., None], cv2.resize(col, (W, H))


prev_m, face, n, done, t0 = None, None, 0, 0, time.time()
fy, fx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    if n not in need:
        enc.stdin.write(buf); n += 1; continue
    img8 = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    rgb4 = cv2.cvtColor(cv2.resize(img8, (W // 4, H // 4)), cv2.COLOR_BGR2RGB)
    m = seg.process(rgb4).segmentation_mask
    m = m if prev_m is None or n - 1 not in need else 0.55 * m + 0.45 * prev_m  # suaviza en el tiempo (sin parpadeo)
    prev_m = m
    if n % 3 == 0 or face is None:
        det = fd.process(cv2.resize(cv2.cvtColor(img8, cv2.COLOR_BGR2RGB), (W // 2, H // 2))).detections
        if det:
            r = det[0].location_data.relative_bounding_box
            new = np.array([(r.xmin + r.width / 2) * W, (r.ymin + r.height / 2) * H, r.width * W, r.height * H])
            face = new if face is None else 0.6 * face + 0.4 * new
    img = img8.astype(np.float32) / 255
    mm = np.clip((m - 0.3) / 0.4, 0, 1); mm = cv2.GaussianBlur(mm, (0, 0), FEATHER / 4)
    if FILL > 0 and face is not None:
        cx, cy, fw, fh = face / 4
        ell = np.exp(-(((fx - cx) / (fw * 1.1)) ** 2 + ((fy - cy) / (fh * 1.2)) ** 2)) * mm
        ell = cv2.resize(ell, (W, H))[..., None]
        img = img * (1 - ell) + (1 - (1 - img) ** (1 + FILL)) * ell
        img = np.clip(img * (1 + 0.06 * ell), 0, 1)
    M = cv2.resize(mm, (W, H))[..., None]
    bg = cv2.GaussianBlur(img, (0, 0), BLUR)
    if VITRAL > 0:
        A, col = light_maps(n / FPS)
        bg = bg * (1 - VITRAL * A) + (bg * col) * (VITRAL * A)
        bg = 1 - (1 - bg) * (1 - 0.2 * VITRAL * A * col)
    out = img * M + bg * (1 - M)
    enc.stdin.write((np.clip(out, 0, 1) * 255).astype(np.uint8).tobytes())
    n += 1; done += 1
    if done % 250 == 0:
        print(f"{done}/{len(need)} cuadros procesados ({(time.time() - t0) / done:.2f} s/cuadro)", flush=True)
enc.stdin.close(); enc.wait(); dec.wait()
import os; os.replace("public/video-fondo.tmp.mp4", "public/video-fondo.mp4")
print(f"listo: public/video-fondo.mp4 ({n} cuadros, {done} procesados)")
