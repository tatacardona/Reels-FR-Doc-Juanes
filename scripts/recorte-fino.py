"""Recorte fino de la persona para portadas: MediaPipe da la silueta inicial, GrabCut la ajusta por color
(separa la pared blanca de la camisa), se quita el halo (erosión 2 px) y se suaviza el borde apenas.
Uso: $PY scripts/recorte-fino.py <segundo> <salida.png> [video]   (por defecto public/video-limpio.mp4 o public/video-vertical.mp4)"""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
import os
t, out = float(sys.argv[1]), sys.argv[2]
VID = sys.argv[3] if len(sys.argv) > 3 else next(v for v in ["public/video-limpio.mp4", "public/video-vertical.mp4"] if os.path.exists(v))
FF = __import__("imageio_ffmpeg").get_ffmpeg_exe()
raw = subprocess.run([FF, "-loglevel", "error", "-ss", str(t), "-i", VID, "-frames:v", "1",
                      "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR); h, w = img.shape[:2]
with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0) as seg:
    m = cv2.resize(seg.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).segmentation_mask, (w, h))
k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))
fg0 = (m > 0.5).astype(np.uint8)
gc = np.full((h, w), cv2.GC_BGD, np.uint8)
gc[cv2.dilate(fg0, k(61)) > 0] = cv2.GC_PR_BGD
gc[fg0 > 0] = cv2.GC_PR_FGD
gc[cv2.erode(fg0, k(41)) > 0] = cv2.GC_FGD
s = 0.5; small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
gs = cv2.resize(gc, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(small, gs, None, bgm, fgm, 6, cv2.GC_INIT_WITH_MASK)
a = np.where((gs == cv2.GC_FGD) | (gs == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
a = cv2.resize(a, (w, h), interpolation=cv2.INTER_LINEAR); a = (a > 127).astype(np.uint8) * 255
n, lab, st, _ = cv2.connectedComponentsWithStats(a)
if n > 1:
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); a = np.where(lab == big, 255, 0).astype(np.uint8)
a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, k(7))
a = cv2.erode(a, k(5))                     # quita el halo blanco (~2 px)
a = cv2.GaussianBlur(a, (0, 0), 1.6)       # suavizado mínimo del borde
cv2.imwrite(out, np.dstack([img, a])); print(out)
