"""Copy the best 2 settings per round into rounds/ and print the rubric tables as markdown."""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"def_e45_c30"}


def row(lid, t):
    m, w = t["m"], t["w"]
    return (f"| {lid} | s{t['seed']} | {m['wps']} | {m.get('tempo', 1.0)} | {max(m['pauses'] or [0])} | "
            f"{m['f0_med']} | {m['f0_sd_semitones']} | {w['no_speech']} / {w['logprob']} | "
            f"{', '.join(t['fails']) or 'pass'} | {w['text']} |")


HEAD = ("| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |\n"
        "|---|---|---|---|---|---|---|---|---|---|")

for r in sys.argv[1:]:
    res = json.load(open(os.path.join(HERE, "work", r, "results.json")))
    sets = [s for s in res["settings"] if s["name"] not in SKIP]
    sets.sort(key=lambda s: (s["total_fails"], s["total_dist"]))
    print(f"\n### {r}\n\n| setting | exag | cfg | temp | ref | fails | dist | pitch spread st |\n|---|---|---|---|---|---|---|---|")
    for s in sets:
        print(f"| {s['name']} | {s['exaggeration']} | {s['cfg_weight']} | {s.get('temperature', 0.8)} | "
              f"{'yes' if s.get('ref') else 'no'} | {s['total_fails']} | {s['total_dist']} | {s['consistency_st']} |")
    for s in sets[:2]:
        dst = os.path.join(HERE, "rounds", r, s["name"]); os.makedirs(dst, exist_ok=True)
        print(f"\n**{s['name']}** (best take per line)\n\n{HEAD}")
        for lid, takes in s["lines"].items():
            t = takes[0]
            shutil.copy(os.path.join(HERE, "work", r, s["name"], f"{lid}_s{t['seed']}.wav"), os.path.join(dst, f"{lid}.wav"))
            print(row(lid, t))

f = json.load(open(os.path.join(HERE, "final", "final.json")))
print(f"\n### Final (after polish)\n\n| line | from | wps | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | result | Whisper |\n|---|---|---|---|---|---|---|---|---|---|---|")
for lid, v in f["lines"].items():
    m, w = v["m"], v["w"]
    print(f"| {lid} | {v['from']} | {m['wps']} | {max(m['pauses'] or [0])} | {m['lead_sil']}/{m['tail_sil']} | {m['f0_med']} | "
          f"{m['f0_sd_semitones']} | {m['clip_pct']} | {w['no_speech']} / {w['logprob']} | {', '.join(v['fails']) or 'pass'} | {w['text']} |")
print(f"\nPitch spread across the 6 final lines: **{f['consistency_st']} semitones** (limit 2).")
