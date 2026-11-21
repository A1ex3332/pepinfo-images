"""Code-made smash sound driven by the physics in frames.json (from frames.py).
usage: python3 sound.py frames.json out.wav [seconds]
Big crunch + thump where the ball stops falling; a click per fragment that suddenly slows (lands/knocks)."""
import json, sys, wave
import numpy as np
F = json.load(open(sys.argv[1])); out_path = sys.argv[2]
fps = 30; T = float(sys.argv[3]) if len(sys.argv) > 3 else len(F) / fps
sr = 48000; n = int(sr * T); out = np.zeros(n); rng = np.random.default_rng(7)
keys = sorted(F, key=int)
pos = {name: np.array([F[k][name][12:15] if F[k].get(name) else [np.nan]*3 for k in keys]) for name in F[keys[0]]}
def burst(t, amp, dur, lp):
    i = int(t * sr); m = int(dur * sr)
    if i >= n: return
    x = rng.standard_normal(m); a = np.exp(-2 * np.pi * lp / sr)
    y = np.zeros(m); acc = 0.0
    for k in range(m): acc = (1 - a) * x[k] + a * acc; y[k] = acc
    seg = y * np.exp(-np.linspace(0, 1, m) * 8) * amp; e = min(n, i + m); out[i:e] += seg[:e - i]
ball = next(k for k in pos if k.startswith('ball'))
vy = np.diff(pos[ball][:, 1]) * fps
hit = int(np.argmax(np.diff(vy))) + 1  # biggest upward change of velocity = impact
th = hit / fps; print('impact at', round(th, 3), 's')
burst(th, 6, 0.5, 1800); burst(th, 3, 0.25, 5000)
t = np.arange(int(0.4 * sr)) / sr; i = int(th * sr)
thump = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 9) * 0.9; out[i:i + len(thump)] += thump[:max(0, n - i)]
for name, p in pos.items():
    if 'frag' not in name: continue
    v = np.linalg.norm(np.diff(p, axis=0), axis=1) * fps
    for f in range(1, len(v)):
        dv = v[f - 1] - v[f]
        if dv > 1.2 and f / fps > th:  # sudden slow-down = a knock
            burst(f / fps + rng.uniform(0, 0.02), min(1.6, dv / 3), rng.uniform(0.03, 0.08), rng.uniform(2500, 7000))
out /= np.abs(out).max() * 1.12
w = wave.open(out_path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
