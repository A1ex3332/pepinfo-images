"""Pick the best passing take per line (tightest pitch spread), polish, re-score, join.

python final.py r2 r3 ...   -> final/<line>.wav, final/voice-final.wav, final/final.json
"""
import json, os, re, subprocess, sys, difflib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tune import LINES, WC, KEYS, norm, score_line, consistency
from vox import analyze, load as vload

SKIP = {"def_e45_c30"}  # duplicate of ref_e45_c30 (reused the reference conditionals)
POLISH = ("highpass=f=80,deesser=i=0.5:m=0.5:f=0.55:s=o,"
          "acompressor=ratio=3:threshold=-20dB:attack=5:release=80:makeup=2,"
          "loudnorm=I=-16:TP=-1.5:LRA=7")


def candidates(rounds):
    c = {l["id"]: [] for l in LINES}
    for r in rounds:
        res = json.load(open(os.path.join(HERE, "work", r, "results.json")))
        for s in res["settings"]:
            if s["name"] in SKIP: continue
            for lid, takes in s["lines"].items():
                for t in takes:
                    if not t["fails"] and t["m"]["f0_med"]:
                        c[lid].append({**t, "round": r, "setting": s["name"],
                                       "path": os.path.join(HERE, "work", r, s["name"], f"{lid}_s{t['seed']}.wav")})
    return c


def pick(c):
    best = None
    for L in sorted({t["m"]["f0_med"] for v in c.values() for t in v}):
        H = L * 2 ** (1.8 / 12)
        sel = {}
        for lid, v in c.items():
            ok = [t for t in v if L <= t["m"]["f0_med"] <= H]
            if not ok: break
            sel[lid] = min(ok, key=lambda t: t["dist"])
        else:
            cost = sum(t["dist"] for t in sel.values()) + consistency([t["m"]["f0_med"] for t in sel.values()]) * 0.1
            if best is None or cost < best[0]: best = (cost, sel)
    return best[1] if best else None


def main():
    c = candidates(sys.argv[1:])
    print({k: len(v) for k, v in c.items()})
    sel = pick(c)
    if not sel:
        sel = {lid: min(v, key=lambda t: t["dist"]) for lid, v in c.items() if v}
        print("no set within 2 st; fell back to best per line")
    fdir = os.path.join(HERE, "final"); os.makedirs(fdir, exist_ok=True)
    from faster_whisper import WhisperModel
    asr = WhisperModel("small.en", device="cuda", compute_type="float16")
    out = {}
    for L in LINES:
        lid = L["id"]
        if lid not in sel: print("MISSING", lid); continue
        t = sel[lid]; dst = os.path.join(fdir, f"{lid}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", t["path"], "-af", POLISH,
                        "-ar", "48000", "-ac", "1", dst], check=True)
        m = analyze(vload(dst), WC[lid])
        segs = list(asr.transcribe(dst, language="en", beam_size=5)[0])
        txt = " ".join(s.text.strip() for s in segs); n = norm(txt)
        w = {"text": txt, "no_speech": round(max(s.no_speech_prob for s in segs), 3),
             "logprob": round(min(s.avg_logprob for s in segs), 3),
             "sim": round(difflib.SequenceMatcher(None, n, norm(t["say"])).ratio(), 3),
             "missing": [k for k in KEYS[lid] if not re.search(k, n)]}
        w["words_ok"] = not w["missing"] and w["sim"] >= 0.9
        fails, dist = score_line(lid, m, w)
        out[lid] = {"from": f"{t['round']}/{t['setting']}/s{t['seed']}", "say": t["say"],
                    "m": m, "w": w, "fails": fails}
        print(lid, out[lid]["from"], fails, m["wps"], m["f0_sd_semitones"], m["f0_med"], "|", txt)
    cons = consistency([v["m"]["f0_med"] for v in out.values()])
    print("consistency_st", cons)
    # join with 0.18 s gaps
    files = [os.path.join(fdir, f"{l['id']}.wav") for l in LINES if l["id"] in out]
    inputs = sum((["-i", f] for f in files), [])
    n = len(files)
    fc = "".join(f"[{i}:a]apad=pad_dur=0.18[p{i}];" for i in range(n - 1))
    fc += "".join(f"[p{i}]" for i in range(n - 1)) + f"[{n-1}:a]concat=n={n}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[o]",
                    "-ar", "48000", "-ac", "1", os.path.join(fdir, "voice-final.wav")], check=True)
    json.dump({"lines": out, "consistency_st": cons}, open(os.path.join(fdir, "final.json"), "w"), indent=1,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))


if __name__ == "__main__":
    main()
