"""Efectos de sonido sintetizados (sin derechos de autor) para stickers y momentos cómicos.
Uso (desde la raíz del proyecto):  $PY scripts/sfx-stickers.py
Salidas en public/:
  sfx-ding.wav      brillo de triunfo (logro, acierto)
  sfx-crash.wav     algo que se quiebra y se cae (vidrio + golpe + rebotes)
  sfx-fail.wav      trombón triste "wah wah wah waaah" (fracaso divertido)
  sfx-pop.wav       pop corto cuando aparece un sticker
  sfx-shimmer.wav   brillo suave de campanitas (transiciones con destello de luz, videos inspiradores)
"""
import wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def save(name, x, gain=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    st = np.stack([x, x], 1)
    with wave.open(f"public/{name}", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def t(d): return np.arange(int(SR * d)) / SR


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); p = 0.0
    for i, v in enumerate(x): p = (1 - a) * v + a * p; y[i] = p
    return y


def bell(f, d, decay):
    tt = t(d)
    return sum(np.sin(2 * np.pi * f * m * tt) * g for m, g in [(1, 1), (2.76, 0.35), (5.4, 0.15)]) * np.exp(-tt * decay)


# ---- Ding de triunfo: arpegio brillante ascendente ----
out = np.zeros(int(SR * 1.3))
for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
    s = int(k * 0.07 * SR); b = bell(f, 1.3 - k * 0.07, 4.5)
    out[s:s + len(b)] += b * (0.8 if k < 3 else 1.0)
shimmer = rng.standard_normal(len(out)) * np.exp(-t(1.3) * 6) * 0.05
save("sfx-ding.wav", out + np.diff(np.concatenate([[0], shimmer])), 0.8)

# ---- Quiebre: vidrio que se rompe + golpe + pedacitos que rebotan ----
d = 1.6; out = np.zeros(int(SR * d))
noise = rng.standard_normal(int(SR * 0.5))
crack = np.diff(np.concatenate([[0], noise])) * np.exp(-t(0.5) * 9)
out[:len(crack)] += crack * 0.9
for _ in range(14):  # tintineos agudos del vidrio
    f = rng.uniform(2500, 6500); s = int(rng.uniform(0, 0.45) * SR)
    b = np.sin(2 * np.pi * f * t(0.35)) * np.exp(-t(0.35) * rng.uniform(15, 30)) * rng.uniform(0.15, 0.4)
    out[s:s + len(b)] += b[: len(out) - s]
thud = np.sin(2 * np.pi * 70 * t(0.4) * np.exp(-t(0.4) * 2)) * np.exp(-t(0.4) * 9)
out[:len(thud)] += thud * 1.1
for k, at in enumerate([0.55, 0.8, 0.98, 1.1]):  # pedazos que caen y rebotan
    s = int(at * SR); n = rng.standard_normal(int(0.12 * SR))
    b = np.diff(np.concatenate([[0], n])) * np.exp(-t(0.12) * 40) * (0.45 / (k + 1))
    b += np.sin(2 * np.pi * rng.uniform(3000, 5000) * t(0.12)) * np.exp(-t(0.12) * 35) * 0.2 / (k + 1)
    out[s:s + len(b)] += b
save("sfx-crash.wav", out, 0.85)

# ---- Trombón triste: wah wah wah waaaah ----
notes = [(293.66, 0.42), (277.18, 0.42), (261.63, 0.42), (246.94, 1.35)]
parts = []
for k, (f, d) in enumerate(notes):
    tt = t(d); last = k == len(notes) - 1
    vib = 1 + (0.012 * np.sin(2 * np.pi * 5.5 * tt) * np.clip((tt - 0.25) * 3, 0, 1) if last else 0)
    bend = 1 - 0.01 * tt / d  # cae un poquito al final de cada nota
    ph = 2 * np.cumsum(np.pi * f * vib * bend / SR)
    # "wah": los armónicos se abren y se cierran (como la sordina)
    wah = np.clip(np.sin(np.pi * np.clip(tt / min(d, 0.42), 0, 1)) ** 0.6, 0, 1)
    if last: wah = np.clip(np.minimum(tt / 0.15, 1) * np.exp(-np.maximum(tt - 0.6, 0) * 1.4), 0, 1)
    tone = sum(np.sin(m * ph) * (wah ** (0.5 + m * 0.35)) / m ** 0.9 for m in range(1, 12))
    env = np.minimum(tt / 0.03, 1) * np.minimum((d - tt) / 0.06, 1)
    parts.append(tone * env); parts.append(np.zeros(int(0.03 * SR)))
save("sfx-fail.wav", lowpass(np.concatenate(parts), 2600), 0.8)

# ---- Pop de aparición ----
tt = t(0.14)
pop = np.sin(2 * np.pi * (900 - 2500 * tt) * tt) * np.exp(-tt * 38)
save("sfx-pop.wav", pop, 0.7)
# ---- Brillo suave (shimmer): campanitas agudas que suben, con cola larga y muy suave ----
d = 1.6; out = np.zeros(int(SR * d))
for k, f in enumerate([1568.0, 1760.0, 2093.0, 2349.3, 2637.0, 3136.0, 3520.0]):
    s0 = int((0.05 + k * 0.06 + rng.uniform(0, 0.02)) * SR)
    b = bell(f, d - s0 / SR, rng.uniform(3.0, 4.5)) * (0.5 + 0.08 * k)
    out[s0:s0 + len(b)] += b[: len(out) - s0]
air = rng.standard_normal(len(out)); air = np.diff(np.concatenate([[0], air])) * 0.03
env = np.minimum(t(d) / 0.35, 1) * np.exp(-np.maximum(t(d) - 0.35, 0) * 2.2)
save("sfx-shimmer.wav", lowpass(out + air * env, 9000) * np.minimum(t(d) / 0.04, 1), 0.6)

print("listo: public/sfx-ding.wav, sfx-crash.wav, sfx-fail.wav, sfx-pop.wav, sfx-shimmer.wav")
