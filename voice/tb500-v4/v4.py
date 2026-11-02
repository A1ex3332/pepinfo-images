"""TB-500 Reel v4 voice lines: generate, score against ../tune/RUBRIC.md, pick, polish.

python v4.py gen <round.json>   -> work/<round>/<setting>/<line>_s<seed>.wav + results.json
python v4.py final r1 [r2 ...]  -> l1.wav ... l6.wav (48 kHz mono) + final.json
Reuses clean/atempo/consistency from ../tune/tune.py and vox.py, the round-1 reference voice
(../tune/ref/ref_r1.wav) and the earlier final takes' pitch (../tune/final/final.json).
"""
import difflib, json, os, re, subprocess, sys, time
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TUNE = os.path.join(HERE, "..", "tune")
sys.path.insert(0, TUNE)
from tune import clean, atempo, consistency
from vox import analyze, load as vload

REF = os.path.join(TUNE, "ref", "ref_r1.wav")
LINES = json.load(open(os.path.join(HERE, "lines.json"), encoding="utf-8"))
WC = {l["id"]: len(l["text"].split()) for l in LINES}
HOOK = "l1"
KEYS = {
    "l1": ["banned", "sport", r"since(2018|twentyeighteen)", "mostpeople", "neverseen", "labdata"],
    "l2": [r"2004|twothousandfour", "mice", "heartattack", "heartcells", "survived"],
    "l3": ["insidecells", r"actin(?!g)", "bricks", r"use(d)?tomove"],
    "l4": [r"tb500|tbfivehundred", r"just7|justseven", r"43|fortythree", "aminoacids"],
    "l5": ["mice", "rats", "cells", "humandata", "thin"],
    "l6": ["whichpeptide", "zoom", "next"],
}
NUM = {"2018": "twentyeighteen", "2004": "twothousandfour", "500": "fivehundred",
       "43": "fortythree", "7": "seven"}
OLD = [v["m"]["f0_med"] for v in json.load(open(os.path.join(TUNE, "final", "final.json")))["lines"].values()]
POLISH = ("highpass=f=80,deesser=i=0.5:m=0.5:f=0.55:s=o,"
          "acompressor=ratio=3:threshold=-20dB:attack=5:release=80:makeup=2,"
          "loudnorm=I=-16:TP=-1.5:LRA=7")


def norm(s):
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    for k, v in sorted(NUM.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    return s


WORDNUM = {"seven": "7", "fortythree": "43", "twothousandfour": "2004", "twentyeighteen": "2018"}
# Whisper spellings let through but listed in SCORES.md (same "used" call the earlier final made)
TOL = {("use", "used"), ("sport", "sports")}


def words(s):
    s = re.sub(r"\btb[ -]?500\b", "tb500", s.lower())
    s = re.sub(r"two thousand (and )?four", "2004", s)
    s = re.sub(r"twenty eighteen", "2018", s)
    ws = re.findall(r"[a-z0-9]+", s.replace("-", ""))
    return [WORDNUM.get(x, x) for x in ws]


def hear(asr, path, say, lid):
    segs = list(asr.transcribe(path, language="en", beam_size=5)[0])
    txt = " ".join(s.text.strip() for s in segs); n = norm(txt)
    text = next(l["text"] for l in LINES if l["id"] == lid)
    a, b = words(text), words(txt)
    diff, tol = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal": continue
        pair = (" ".join(a[i1:i2]), " ".join(b[j1:j2]))
        (tol if pair in TOL else diff).append(f"{pair[0] or '+'}->{pair[1] or '-'}")
    w = {"text": txt,
         "no_speech": round(max(s.no_speech_prob for s in segs), 3) if segs else 1.0,
         "logprob": round(min(s.avg_logprob for s in segs), 3) if segs else -9,
         "sim": round(difflib.SequenceMatcher(None, n, norm(say)).ratio(), 3),
         "missing": [k for k in KEYS[lid] if not re.search(k, n)], "diff": diff, "tolerated": tol}
    w["words_ok"] = not w["missing"] and not diff
    return w


def score_line(lid, m, w):
    fails, dist = [], 0.0
    if not w["words_ok"]: fails.append("words"); dist += 10
    lo, hi = (3.3, 3.6) if lid == HOOK else (3.0, 3.4)
    wps = m.get("wps", 0)
    if not lo <= wps <= hi: fails.append(f"pace {wps}"); dist += abs(wps - (lo if wps < lo else hi)) * 4
    lim = 0.20 if lid == HOOK else 0.30
    if any(p > lim for p in m["pauses"]): fails.append(f"pause {max(m['pauses'])}"); dist += 1
    if m["lead_sil"] > 0.06 or m["tail_sil"] > 0.06: fails.append("edge sil"); dist += 1
    sd = m["f0_sd_semitones"]
    if not 3.5 <= sd <= 6: fails.append(f"f0sd {sd}"); dist += abs(sd - (3.5 if sd < 3.5 else 6))
    if m["clip_pct"] > 0: fails.append("clip"); dist += 1
    if w["no_speech"] >= 0.1 or w["logprob"] <= -0.5: fails.append("asr conf"); dist += 1
    return fails, round(dist, 3)


def dump(obj, path):
    json.dump(obj, open(path, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))


def gen(cfg_path):
    import torch
    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    cfg = json.load(open(cfg_path, encoding="utf-8-sig"))
    rnd = cfg["round"]; seeds = cfg.get("seeds", [42])
    root = os.path.join(HERE, "work", rnd)
    tts = ChatterboxTTS.from_pretrained(device="cuda")
    asr = WhisperModel("small.en", device="cuda", compute_type="float16")
    results = {"round": rnd, "settings": []}
    for st in cfg["settings"]:
        sdir = os.path.join(root, st["name"]); os.makedirs(sdir, exist_ok=True)
        srec = {**st, "lines": {}}
        for L in LINES:
            lid = L["id"]
            if st.get("only") and lid not in st["only"]: continue
            say = st.get("lines", {}).get(lid, L["say"])
            takes = []
            for seed in st.get("seeds", seeds):
                torch.manual_seed(seed); np.random.seed(seed)
                t0 = time.time()
                raw = os.path.join(sdir, f"{lid}_s{seed}.raw.wav")
                if os.path.exists(raw):
                    wav, _ = sf.read(raw, dtype="float32")
                else:
                    wav = tts.generate(say, exaggeration=st["exaggeration"], cfg_weight=st["cfg_weight"],
                                       temperature=st.get("temperature", 0.8),
                                       audio_prompt_path=REF).squeeze(0).cpu().numpy()
                    sf.write(raw, wav, tts.sr)
                out = os.path.join(sdir, f"{lid}_s{seed}.wav")
                x = wav
                hold = st.get("hold", {}).get(lid, 0.14 if lid == HOOK else 0.24)
                y = clean(x, tts.sr, hold + 0.06)
                sf.write(out, y * (0.89 / max(1e-6, np.abs(y).max())), tts.sr)
                m = analyze(vload(out), WC[lid])
                mid = 3.45 if lid == HOOK else 3.2
                tempo = round(float(np.clip(mid / m["wps"], *st.get("tempo_range", [0.88, 1.12]))), 3)
                atempo(out, tempo)
                m = analyze(vload(out), WC[lid]); m["tempo"] = tempo
                w = hear(asr, out, say, lid)
                fails, dist = score_line(lid, m, w)
                takes.append({"seed": seed, "say": say, "m": m, "w": w, "fails": fails, "dist": dist})
                print(f"{rnd}/{st['name']}/{lid} s{seed} {time.time()-t0:.1f}s wps={m.get('wps')} tempo={tempo} "
                      f"sd={m['f0_sd_semitones']} f0={m['f0_med']} fails={fails} | {w['text']}", flush=True)
            srec["lines"][lid] = sorted(takes, key=lambda t: (len(t["fails"]), t["dist"]))
        results["settings"].append(srec)
    dump(results, os.path.join(root, "results.json"))


def candidates(rounds):
    c = {l["id"]: [] for l in LINES}
    for r in rounds:
        res = json.load(open(os.path.join(HERE, "work", r, "results.json")))
        for s in res["settings"]:
            for lid, takes in s["lines"].items():
                for t in takes:
                    if not t["fails"] and t["m"]["f0_med"]:
                        # prefer takes Whisper hears word for word over tolerated spellings
                        c[lid].append({**t, "dist": t["dist"] + 0.5 * len(t["w"].get("tolerated", [])),
                                       "round": r, "setting": s["name"],
                                       "path": os.path.join(HERE, "work", r, s["name"], f"{lid}_s{t['seed']}.wav")})
    return c


def pick(c):
    """Lowest-distance set whose pitch, together with the earlier final takes, fits one 1.8 st window."""
    best = None
    for lo in sorted({t["m"]["f0_med"] for v in c.values() for t in v} | set(OLD)):
        hi = lo * 2 ** (1.8 / 12)
        if not all(lo <= f <= hi for f in OLD): continue
        sel = {}
        for lid, v in c.items():
            ok = [t for t in v if lo <= t["m"]["f0_med"] <= hi]
            if not ok: break
            sel[lid] = min(ok, key=lambda t: t["dist"])
        else:
            cost = sum(t["dist"] for t in sel.values())
            if best is None or cost < best[0]: best = (cost, sel)
    return best[1] if best else None


def final(rounds):
    from faster_whisper import WhisperModel
    import shutil
    asr = WhisperModel("small.en", device="cuda", compute_type="float16")
    c = candidates(rounds)
    print({k: len(v) for k, v in c.items()})
    # polish every passing take, then re-measure and re-hear it: polish moves f0 and can change what Whisper hears
    pdir = os.path.join(HERE, "work", "polished"); os.makedirs(pdir, exist_ok=True)
    pc = {}
    for lid, v in c.items():
        pc[lid] = []
        for t in v:
            dst = os.path.join(pdir, f"{lid}_{t['round']}_{t['setting']}_s{t['seed']}.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", t["path"], "-af", POLISH,
                            "-ar", "48000", "-ac", "1", dst], check=True)
            m = analyze(vload(dst), WC[lid]); w = hear(asr, dst, t["say"], lid)
            fails, dist = score_line(lid, m, w)
            if not fails:
                pc[lid].append({**t, "pre": t["m"], "m": m, "w": w, "fails": fails, "polished": dst,
                                "dist": dist + 0.5 * len(w["tolerated"])})
    print("pass after polish", {k: len(v) for k, v in pc.items()})
    sel = pick(pc)
    if not sel:
        print("no set fits the pitch window; best passing take per line instead")
        sel = {lid: min(v, key=lambda t: t["dist"]) for lid, v in pc.items() if v}
    out = {}
    for L in LINES:
        lid = L["id"]
        if lid not in sel: print("MISSING", lid); continue
        t = sel[lid]; m, w = t["m"], t["w"]
        shutil.copy(t["polished"], os.path.join(HERE, f"{lid}.wav"))
        out[lid] = {"from": f"{t['round']}/{t['setting']}/s{t['seed']}", "say": t["say"],
                    "tempo": t["pre"]["tempo"], "m": m, "w": w, "fails": t["fails"]}
        print(lid, out[lid]["from"], m["wps"], m["f0_sd_semitones"], m["f0_med"], m["pauses"], "|", w["text"])
    f0 = [v["m"]["f0_med"] for v in out.values()]
    res = {"lines": out, "consistency_st": consistency(f0), "with_earlier_final_st": consistency(f0 + OLD)}
    print("consistency", res["consistency_st"], "with earlier final", res["with_earlier_final_st"])
    dump(res, os.path.join(HERE, "final.json"))


if __name__ == "__main__":
    gen(sys.argv[2]) if sys.argv[1] == "gen" else final(sys.argv[2:])
