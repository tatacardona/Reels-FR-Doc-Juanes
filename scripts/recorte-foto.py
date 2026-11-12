"""Recorta a la persona de una foto (MediaPipe) y la encaja en un lienzo 1440x2560 con la cara del mismo
tamaño y en el mismo punto que en la referencia (otro recorte ya usado en la portada), para usarla en CoverDJ.
Uso: $PY scripts/recorte-foto.py <foto> <salida.png> <recorte_de_referencia.png>"""
import sys, numpy as np, cv2, mediapipe as mp
src, out, REF = sys.argv[1], sys.argv[2], sys.argv[3]
def face(img):
    with mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.4) as fd:
        r = fd.process(cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2RGB))
    b = max(r.detections, key=lambda d: d.location_data.relative_bounding_box.width).location_data.relative_bounding_box
    h, w = img.shape[:2]; return ((b.xmin + b.width / 2) * w, (b.ymin + b.height / 2) * h, b.width * w)
ref = cv2.imread(REF, cv2.IMREAD_UNCHANGED); rx, ry, rw = face(ref)
img = cv2.imread(src); h, w = img.shape[:2]
if max(h, w) > 3000: img = cv2.resize(img, None, fx=3000 / max(h, w), fy=3000 / max(h, w), interpolation=cv2.INTER_AREA); h, w = img.shape[:2]
with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0) as seg:
    m = seg.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).segmentation_mask
a = (cv2.GaussianBlur((m > 0.5).astype(np.uint8) * 255, (0, 0), 2)).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats((a > 128).astype(np.uint8))
if n > 1:
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); a = np.where(lab == big, a, 0).astype(np.uint8)
fx, fy, fw = face(img); s = rw / fw
M = np.float32([[s, 0, rx - fx * s], [0, s, ry - fy * s]])
rgba = cv2.warpAffine(np.dstack([img, a]), M, (1440, 2560), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
cv2.imwrite(out, rgba); print(out, round(s, 2))
