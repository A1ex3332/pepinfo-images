# Gut-science Reel v2 voice lines (Chatterbox, RTX 3060)

Files: `l1.wav` … `l6.wav`, 48 kHz mono, polished. All 6 pass every check in `../tune/RUBRIC.md`.
- l2, l3, l4 and l6 are copied unchanged from `../gut-v1/` (byte-identical). Their scores below come from `../gut-v1/final.json`.
- l1 and l5 are new renders.

The pitch spread across the 6 lines is **1.40 semitones**. Adding every earlier final take (TB-500 v4 and v7, GHK-Cu, GHK-Cu v3, gut v1) gives **1.87 st** (limit 2). The new takes did not widen the window.

## Setup (same locked voice, same steps as gut-v1)
- `gv2.py` is a copy of `../gut-v1/gv1.py`. `lines.json` holds only the two new lines. In `final.json`, the copied lines are carried over from gut-v1.
- Chatterbox `ChatterboxTTS` with reference `../tune/ref/ref_r1.wav`. `torch.manual_seed(seed)` is set per take. Settings were 0.45/0.3 and 0.6/0.5 at temp 0.8. The clean step and auto atempo (0.88-1.12) are the same as before.
- Hook (l1): 3.3-3.6 wps, no pause over 0.2 s. l5: 3.0-3.4 wps, pauses up to 0.3 s. Pace uses the on-screen word count (l1 = 9, l5 = 15).
- Strict word-by-word Whisper check (small.en, beam 5). "2"/"3" count as "two"/"three". Nothing else was let through, so the tolerated list is empty.
- Polish chain is unchanged: highpass 80 Hz, de-esser, 3:1 compressor at -20 dB, loudnorm -16 LUFS / -1.5 dBTP, 48 kHz mono. After polish, every passing take was re-measured and re-heard. Each final pick is the lowest-distance take whose median pitch, together with all 25 earlier final takes, fits one 1.9 st window (136.6-152.7 Hz).

## Final per-line scores (after polish)

| line | take | atempo | wps (target) | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | Whisper heard |
|---|---|---|---|---|---|---|---|---|---|---|
| l1 hook (new) | r1/e45_c30/s2024 | 0.975 | 3.44 (3.3-3.6) | none | 0.04/0.00 | 140.4 | 5.35 | 0 | 0.000 / -0.249 | Your stomach acid can unfold a steak. Then what? |
| l2 (gut-v1) | r1/e45_c30/s7 | 0.997 | 3.19 (3.0-3.4) | none | 0.04/0.02 | 139.7 | 4.38 | 0 | 0.001 / -0.344 | the stomach lining pumps out acid around pH 2. |
| l3 (gut-v1) | r1/e45_c30/s42 | 1.119 | 3.16 | none | 0.02/0.02 | 137.9 | 4.86 | 0 | 0.000 / -0.291 | That acid unfolds proteins, so enzymes can reach their bonds. |
| l4 (gut-v1) | r1/e45_c30/s42 | 1.103 | 3.17 | 0.16 | 0.02/0.00 | 149.5 | 5.32 | 0 | 0.001 / -0.239 | Pepsin cuts the chain into short pieces. Later, enzymes in the intestine cut them even smaller. |
| l5 (new) | r1/e60_c50/s7 | 0.922 | 3.19 (3.0-3.4) | none | 0.04/0.02 | 140.4 | 5.16 | 0 | 0.000 / -0.204 | Most protein is absorbed as single amino acids, or pieces just two or three long. |
| l6 (gut-v1) | r2/e45_c30_comma/s3 | 0.88 | 3.30 | none | 0.02/0.02 | 149.5 | 5.78 | 0 | 0.000 / -0.258 | What should we zoom into next? |

l1 and l5 are spoken exactly as on screen. l6 is still the gut-v1 comma variant: "What should we zoom into, next?".

## Rounds (1 of the 3 allowed)
- **Round 1:** both settings on l1 and l5, seeds 42/7/2024/99. Both lines passed, so I stopped there.
  - **l1:** 5/8 passed. Three failures were word errors: "the steak" twice, and once "a stick" (that take was also 3.66 wps). One of those "the steak" takes also failed on f0 sd (3.22). Two passing takes were outside the pitch window (127.5 and 158.4 Hz). That left 3 in the window: 140.4, 145.5 and 148.1 Hz.
  - **l5:** 8/8 passed. Most takes sat low (124-133 Hz), so only one was in the window (141.6 Hz before polish, 140.4 after).
- **Polish check:** 13 passing takes before polish, 13 after. Nothing dropped out.

## Notes
- If captions come from the transcript, l5 is fine as heard: Whisper writes "two or three" as words.
- Raw takes, per-round results and the polished pool are in `work/` (gitignored). To rerun: `python gv2.py gen r1.json`, then `python gv2.py final r1` (venv `%USERPROFILE%\chatterbox\venv`).
