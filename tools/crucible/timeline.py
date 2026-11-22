"""Write timeline.json for compose.py from frames.json: live piece counter + hook.
usage: python3 timeline.py frames.json full/timeline.json "Smashing a jelly cube" "into 1,000 pieces"
(compose.py swaps "1,000" for the final count). Counts pieces that moved > 4 cm since just before impact."""
import json, sys
import numpy as np
F = json.load(open(sys.argv[1])); keys = sorted(F, key=int)
ball = next(k for k in F[keys[0]] if k.startswith('ball'))
y = np.array([F[k][ball][13] for k in keys]); vy = np.diff(y)
hit = int(np.argmax(np.diff(vy))) + 1
frags = [n for n in F[keys[0]] if 'frag' in n]
ref = {n: np.array(F[keys[max(0, hit - 1)]][n][12:15]) for n in frags}
counts, c = [], 1
for i, k in enumerate(keys):
    if i >= hit:
        c = max(c, sum(np.linalg.norm(np.array(F[k][n][12:15]) - ref[n]) > 0.04 for n in frags))
    counts.append(int(c))
hook = sys.argv[3:5] if len(sys.argv) > 4 else ["Smashing one block", "into 1,000 pieces"]
json.dump({"fps": 30, "counts": counts, "trim": 0.0, "theme": {"hook": hook, "hook_b": ["Wait for the", "steel ball"]}}, open(sys.argv[2], 'w'))
print('impact frame', hit, 'final count', counts[-1])
