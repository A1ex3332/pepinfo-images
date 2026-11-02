# GHK-Cu Reel voice lines (Chatterbox, RTX 3060)

Files: `l1.wav` … `l6.wav`, 48 kHz mono, polished. All 6 pass every check in `../tune/RUBRIC.md` after polish.
Pitch spread across the 6 new lines is **1.24 semitones**. With the 6 TB-500 v4 lines (`../tb500-v4/`) included it is **1.73 st** (limit 2).

## Setup (same locked voice as TB-500 v4)
- `gk.py` is a copy of `../tb500-v4/v4.py` with the GHK-Cu lines. Chatterbox `ChatterboxTTS`, voice reference `../tune/ref/ref_r1.wav` on every take, `torch.manual_seed(seed)` before each line.
- Settings: exaggeration 0.45, cfg 0.3, temperature 0.8. A second setting, 0.6/0.5, ran alongside for lines that came out slow.
- Same clean step: lead and tail trimmed, internal silences held to 0.14 s on the hook and 0.24 s elsewhere (0.08-0.12 s on 0.6/0.5), peak 0.89, auto tempo with atempo clamped to 0.88-1.12.
- Scoring: `vox.py` measures, faster-whisper small.en (GPU, beam 5) transcribes. Pace uses the on-screen word count ("GHK-Cu" counts as one word). Strict word-by-word diff of Whisper's words against the on-screen text. "GHK copper", "G.H.K. copper" and "GHK-Cu" all count as GHK-Cu, "60%" counts as "sixty percent" and "1973" as "nineteen seventy-three". No other spellings were let through, so the tolerated list is empty.
- Final step: polish every passing take (highpass 80 Hz, de-esser, 3:1 compressor at -20 dB, loudnorm -16 LUFS / -1.5 dBTP, 48 kHz mono), then re-measure and re-transcribe each one. From the takes that still pass, pick the set with the lowest total distance whose median pitches, together with the TB-500 v4 final takes, fit one 1.8-semitone window.

## Final per-line scores (after polish)

| line | take | atempo | wps (target) | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | Whisper heard |
|---|---|---|---|---|---|---|---|---|---|---|
| l1 hook | r1/e45_c30/s99 | 1.12 | 3.38 (3.3-3.6) | none | 0.04/0.02 | 144.1 | 5.88 | 0 | 0.001 / -0.268 | GHK copper drops 60% by age 60. What did it do in lab studies? |
| l2 | r1/e45_c30/s2024 | 1.029 | 3.20 (3.0-3.4) | 0.20 | 0.04/0.02 | 137.9 | 4.88 | 0 | 0.001 / -0.225 | First found in human blood in 1973, most lab work since looks at skin. |
| l3 | r1/e45_c30/s99 | 1.049 | 3.17 | 0.18 | 0.02/0.02 | 145.5 | 4.85 | 0 | 0.000 / -0.198 | In a dish, fibroblasts made more collagen, the protein that holds skin together. |
| l4 | r2/e60_c50/s555 | 1.10 | 3.16 | none | 0.04/0.00 | 145.5 | 5.25 | 0 | 0.000 / -0.252 | GHK copper is just three amino acids holding one copper atom. |
| l5 | r1/e45_c30/s2024 | 1.088 | 3.17 | 0.20 | 0.02/0.02 | 140.4 | 5.00 | 0 | 0.002 / -0.333 | mostly cell and animal studies. Human data is thin. |
| l6 | r1/e45_c30/s7 | 0.95 | 3.18 | none | 0.04/0.02 | 148.1 | 4.42 | 0 | 0.000 / -0.242 | Which peptide should we zoom into next? |

Spoken text used: l1 "G H K copper drops sixty percent by age sixty. What did it do in lab studies?" · l2 "First found in human blood in nineteen seventy-three. Most lab work since looks at skin." · l4 "G H K copper is just three amino acids, holding one copper atom." · l3/l5/l6 as on screen.
Settings per line: l4 used 0.6/0.5 because every 0.45/0.3 take of it came out slow. The other five used 0.45/0.3.

## Rounds (2 of the 3 allowed)

**Round 1:** both settings, all 6 lines, seeds 42/7/2024/99. 25 of 48 takes passed.
- 0.45/0.3: l1 1/4, l2 4/4, l3 4/4, l4 0/4, l5 2/4, l6 1/4. All four l4 takes were still at 2.75-2.86 wps with atempo at the 1.12 cap. l1 fails were "drops" heard as "dropped" or slow takes. l5 slipped "thin" to "then" or "spin".
- 0.6/0.5: l1 3/4, l2 3/4, l3 4/4, l4 0/4, l5 2/4, l6 1/4. l4 got closer (2.91-3.18) but one take was over the f0 sd limit. l5 picked up junk at the start ("Abagard, mostly…"). l6 kept coming out too fast even at the 0.88 floor.
- Pitch: l4 had no passing take, and l1 and l6 had only two passing takes each inside the TB-500 v4 pitch band.

**Round 2:** 8 new seeds on l1, l5 and l6 (0.45/0.3) and on l1, l4 and l6 (0.6/0.5), plus an l4 variant with no comma and tighter 0.08 s holds. 19 of 56 takes passed.
- l4 passed 2/8 on 0.6/0.5 and 4/8 on the tight variant. Three of those sat in the pitch band.
- l1 passed 3/8 on 0.6/0.5 and 1/8 on 0.45/0.3. Most 0.45/0.3 takes were slow at the cap or over the f0 sd limit. "dropped" for "drops" came back on 0.6/0.5.
- l5 passed 6/8 on 0.45/0.3. l6 passed 2/8 on 0.45/0.3 (the rest too flat) and 1/8 on 0.6/0.5 (too fast).
- Polish check: 42 takes passed before polish and 37 still passed after re-measuring and re-hearing. No winning take was lost.

No third round was needed.

## Notes
- Whisper hears "G H K copper" as "GHK copper" or "G.H.K. copper". If the captions are built from the transcript, write them as "GHK-Cu".
- Raw takes, per-round results and the polished pool are in `work/` (gitignored). Rerun with `python gk.py gen r1.json`, `python gk.py gen r2.json` and `python gk.py final r1 r2` (venv: `%USERPROFILE%\chatterbox\venv`).
