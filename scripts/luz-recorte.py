"""Mejora la luz de un recorte PNG (portadas): aclara sombras (CLAHE suave), luz de relleno en la cara,
un toque cálido y más contraste local. Uso: $PY scripts/luz-recorte.py entrada.png salida.png"""
import sys, numpy as np, cv2, mediapipe as mp
im = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED); bgr, a = im[..., :3], im[..., 3]
lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB); L, A, B = cv2.split(lab)
L2 = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8)).apply(L)
L = cv2.addWeighted(L, 0.45, L2, 0.55, 0)
# luz de relleno centrada en la cara
h, w = L.shape
with mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.4) as fd:
    r = fd.process(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
if r.detections:
    bb = r.detections[0].location_data.relative_bounding_box
    cx, cy, s = (bb.xmin + bb.width / 2) * w, (bb.ymin + bb.height / 2) * h, bb.width * w * 1.3
    yy, xx = np.mgrid[0:h, 0:w]
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s)))
    Lf = L.astype(np.float32); Lf += g * 26 * (1 - Lf / 255) ** 0.7 * 1.6; L = np.clip(Lf, 0, 255).astype(np.uint8)
B = cv2.add(B, 4); A = cv2.add(A, 2)  # toque cálido
out = cv2.cvtColor(cv2.merge([L, A, B]), cv2.COLOR_LAB2BGR)
# nitidez suave
bl = cv2.GaussianBlur(out, (0, 0), 3); out = cv2.addWeighted(out, 1.25, bl, -0.25, 0)
cv2.imwrite(sys.argv[2], np.dstack([out, a])); print(sys.argv[2], bool(r.detections))
