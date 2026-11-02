"""Generate, clean, measure and score TB-500 voice takes against RUBRIC.md.

python tune.py <round.json>
round.json: {"round": "r1", "seeds": [42], "lines": {"hook": "say override"},
             "settings": [{"name": "e45_c30", "exaggeration": 0.45, "cfg_weight": 0.3,
                           "temperature": 0.8, "atempo": 1.0, "ref": null}]}
Writes work/<round>/<setting>/<line>_s<seed>.wav and work/<round>/results.json.
"""
import difflib, json, os, re, subprocess, sys, time
import numpy as np, soundfile as sf, torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vox import analyze, load as vload

LINES = json.load(open(os.path.join(HERE, "lines.json")))
WC = {l["id"]: len(l["text"].split()) for l in LINES}
KEYS = {
    "hook": [r"tb500|tbfivehundred", "banned", "prosport", "lab"],
    "heart": ["mice", "heartattack", "musclecells", "survived", "workedbetter"],
    "cells": [r"actin(?!g)", "bricks", "crawl"],
    "mol": ["thymosin", r"beta4|betafour", r"43|fortythree", "aminoacids", r"tb500|tbfivehundred", r"just7|justseven"],
    "verdict": ["mice", "rats", "cells", "thinhumandata", "casestaysopen"],
    "end": ["savethis", r"info30|infothirty", "void", "linkinbio"],
}
NUM = {"500": "fivehundred", "43": "fortythree", "30": "thirty", "7": "seven", "4": "four"}


def norm(s):
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    for k, v in sorted(NUM.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    return s


def frames_db(x, sr):
    fl = int(0.02 * sr); n = len(x) // fl
    fr = x[:n * fl].reshape(n, fl)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9), fl


def clean(x, sr, max_pause):
    """Trim lead/tail to 0.04 s and squeeze internal silences longer than max_pause."""
    db, fl = frames_db(x, sr)
    speech = db > db.max() - 35
    idx = np.where(speech)[0]
    a, b = idx[0], idx[-1]
    keep = int(0.04 * sr)
    out, i, cur = [], a, a * fl
    target = int((max_pause - 0.06) * sr)
    while i <= b:
        if speech[i]:
            i += 1; continue
        j = i
        while j <= b and not speech[j]:
            j += 1
        if (j - i) * 0.02 > max_pause - 0.06:
            s, e = i * fl, j * fl
            mid = (s + e) // 2
            out.append(x[cur:s + target // 2])
            cur = e - target // 2
        i = j
    out.append(x[cur:(b + 1) * fl])
    pieces = []
    for k, p in enumerate(out):  # 5 ms fades at joins
        p = p.copy(); f = min(int(0.005 * sr), len(p) // 2)
        if k > 0 and f: p[:f] *= np.linspace(0, 1, f)
        if k < len(out) - 1 and f: p[-f:] *= np.linspace(1, 0, f)
        pieces.append(p)
    y = np.concatenate(pieces)
    lead = x[max(0, a * fl - keep):a * fl]
    tail = x[(b + 1) * fl:(b + 1) * fl + keep]
    return np.concatenate([lead, y, tail]).astype(np.float32)


def atempo(path, factor):
    if abs(factor - 1) < 1e-3: return
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-af", f"atempo={factor}", tmp], check=True)
    os.replace(tmp, path)


def score_line(lid, m, w):
    fails, dist = [], 0.0
    if not w["words_ok"]: fails.append("words"); dist += 10
    lo, hi = (3.3, 3.6) if lid == "hook" else (3.0, 3.4)
    wps = m.get("wps", 0)
    if not lo <= wps <= hi: fails.append(f"pace {wps}"); dist += abs(wps - (lo if wps < lo else hi)) * 4
    lim = 0.20 if lid == "hook" else 0.30
    if any(p > lim for p in m["pauses"]): fails.append(f"pause {max(m['pauses'])}"); dist += 1
    if m["lead_sil"] > 0.06 or m["tail_sil"] > 0.06: fails.append("edge sil"); dist += 1
    sd = m["f0_sd_semitones"]
    if not 3.5 <= sd <= 6: fails.append(f"f0sd {sd}"); dist += abs(sd - (3.5 if sd < 3.5 else 6))
    if m["clip_pct"] > 0: fails.append("clip"); dist += 1
    if w["no_speech"] >= 0.1 or w["logprob"] <= -0.5: fails.append("asr conf"); dist += 1
    return fails, round(dist, 3)


def consistency(f0s):
    f0s = [f for f in f0s if f]
    return round(12 * np.log2(max(f0s) / min(f0s)), 2) if f0s else 99


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8-sig"))
    rnd = cfg["round"]; seeds = cfg.get("seeds", [42])
    root = os.path.join(HERE, "work", rnd)
    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    tts = ChatterboxTTS.from_pretrained(device="cuda")
    asr = WhisperModel("small.en", device="cuda", compute_type="float16")
    results = {"round": rnd, "settings": []}
    only = cfg.get("only")
    for st in cfg["settings"]:
        sdir = os.path.join(root, st["name"]); os.makedirs(sdir, exist_ok=True)
        srec = {**st, "lines": {}}
        for L in LINES:
            lid = L["id"]
            if only and lid not in only: continue
            say = cfg.get("lines", {}).get(lid, L["say"])
            say = st.get("lines", {}).get(lid, say)
            takes = []
            for seed in seeds:
                torch.manual_seed(seed); np.random.seed(seed)
                kw = dict(exaggeration=st["exaggeration"], cfg_weight=st["cfg_weight"],
                          temperature=st.get("temperature", 0.8))
                if st.get("ref"): kw["audio_prompt_path"] = os.path.join(HERE, st["ref"])
                t0 = time.time()
                raw = os.path.join(sdir, f"{lid}_s{seed}.raw.wav")
                if os.path.exists(raw) and cfg.get("reuse", True):
                    wav, _ = sf.read(raw, dtype="float32")
                else:
                    wav = tts.generate(say, **kw).squeeze(0).cpu().numpy()
                    sf.write(raw, wav, tts.sr)
                out = os.path.join(sdir, f"{lid}_s{seed}.wav")
                sf.write(out, wav, tts.sr)
                atempo(out, st.get("atempo", 1.0))
                x, sr = sf.read(out, dtype="float32")
                hold = st.get("hold", {}).get(lid, st.get("hold_default", 0.24 if lid != "hook" else 0.14))
                y = clean(x, sr, hold + 0.06)
                sf.write(out, y * (0.89 / max(1e-6, np.abs(y).max())), sr)
                m = analyze(vload(out), WC[lid])
                tempo = 1.0
                if st.get("autotempo") and m.get("wps"):
                    mid = 3.45 if lid == "hook" else 3.2
                    tempo = round(float(np.clip(mid / m["wps"], *st.get("tempo_range", [0.88, 1.15]))), 3)
                    atempo(out, tempo)
                    m = analyze(vload(out), WC[lid])
                m["tempo"] = tempo
                segs, info = asr.transcribe(out, language="en", beam_size=5)
                segs = list(segs)
                txt = " ".join(s.text.strip() for s in segs)
                n = norm(txt)
                w = {"text": txt,
                     "no_speech": round(max(s.no_speech_prob for s in segs), 3) if segs else 1.0,
                     "logprob": round(min(s.avg_logprob for s in segs), 3) if segs else -9,
                     "sim": round(difflib.SequenceMatcher(None, n, norm(say)).ratio(), 3),
                     "missing": [k for k in KEYS[lid] if not re.search(k, n)]}
                w["words_ok"] = not w["missing"] and w["sim"] >= 0.9
                fails, dist = score_line(lid, m, w)
                takes.append({"seed": seed, "say": say, "m": m, "w": w, "fails": fails, "dist": dist})
                print(f"{rnd}/{st['name']}/{lid} s{seed} {time.time()-t0:.1f}s wps={m.get('wps')} "
                      f"sd={m['f0_sd_semitones']} f0={m['f0_med']} fails={fails} | {txt}", flush=True)
            srec["lines"][lid] = sorted(takes, key=lambda t: (len(t["fails"]), t["dist"]))
        best = [v[0] for v in srec["lines"].values()]
        srec["consistency_st"] = consistency([t["m"]["f0_med"] for t in best])
        srec["total_fails"] = sum(len(t["fails"]) for t in best) + (srec["consistency_st"] > 2)
        srec["total_dist"] = round(sum(t["dist"] for t in best), 3)
        results["settings"].append(srec)
        print(f"== {st['name']}: fails={srec['total_fails']} dist={srec['total_dist']} cons={srec['consistency_st']}", flush=True)
    json.dump(results, open(os.path.join(root, "results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))


if __name__ == "__main__":
    main()
