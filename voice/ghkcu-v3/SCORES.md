# GHK-Cu Reel v3 voice lines (Chatterbox, RTX 3060)

Files: `l1.wav` … `l6.wav`, 48 kHz mono, polished. All 6 pass every check in `../tune/RUBRIC.md` after polish.
Pitch spread across the 6 new lines is **1.24 semitones**. With the 6 TB-500 v4 lines and the 6 GHK-Cu lines it is **1.73 st**, and **1.87 st** with the TB-500 v7 line added too (limit 2).

## Setup (same locked voice as TB-500 v4 and GHK-Cu)
- `g3.py` is a copy of `../ghkcu/gk.py`. Lines, spoken text and the Whisper key phrases now come from `lines.json`, and a line can reuse an earlier take (l6 lists the GHK-Cu l6 take). Chatterbox `ChatterboxTTS`, reference `../tune/ref/ref_r1.wav`, `torch.manual_seed(seed)` per take.
- Settings 0.45/0.3 and 0.6/0.5, temp 0.8. Same clean step and auto atempo (0.88-1.12).
- Pace on the on-screen word count ("GHK" is one word). Hook (l1): 3.3-3.6 wps and no pause over 0.2 s. Other lines: 3.0-3.4 wps, pauses up to 0.3 s.
- Strict word-by-word Whisper check (small.en, beam 5). "GHK"/"G.H.K." count as GHK, and "3"/"1" as "three"/"one". Nothing else was let through, so the tolerated list is empty. "studied" for "study", "fiberblasts", "then"/"spin"/"thinned" for "thin" and "resume" for "zoom" were all failed.
- Final: same polish chain (highpass 80 Hz, de-esser, 3:1 compressor at -20 dB, loudnorm -16 LUFS / -1.5 dBTP, 48 kHz mono), then re-measure and re-hear every passing take. Pick the lowest-distance set whose median pitches, together with all 12 earlier final takes, fit one 1.9 st window.

## Final per-line scores (after polish)

| line | take | atempo | wps (target) | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | Whisper heard |
|---|---|---|---|---|---|---|---|---|---|---|
| l1 hook | r1/e45_c30/s2024 | 1.049 | 3.38 (3.3-3.6) | none | 0.02/0.00 | 145.5 | 4.61 | 0 | 0.001 / -0.224 | Your blood carries a copper peptide. What did labs find? |
| l2 | r1/e60_c50/s42 | 1.12 | 3.03 (3.0-3.4) | none | 0.02/0.00 | 139.1 | 4.48 | 0 | 0.000 / -0.267 | Labs mostly study GHK in skin. |
| l3 | r1/e45_c30/s42 | 1.092 | 3.16 | 0.18 | 0.02/0.00 | 141.6 | 4.82 | 0 | 0.000 / -0.192 | In a dish, fibroblasts, the cells that build skin made more collagen. |
| l4 | r2/e60_c50_comma/s77 | 1.12 | 3.04 | none | 0.02/0.00 | 137.9 | 4.92 | 0 | 0.001 / -0.273 | GHK is three amino acids, holding one copper atom. |
| l5 | r1/e45_c30/s2024 | 1.088 | 3.17 | 0.20 | 0.02/0.02 | 140.4 | 5.00 | 0 | 0.002 / -0.333 | mostly cell and animal studies. Human data is thin. |
| l6 | r1/e45_c30/s7 | 0.95 | 3.18 | none | 0.04/0.02 | 148.1 | 4.42 | 0 | 0.000 / -0.242 | Which peptide should we zoom into next? |

Spoken text: l2 "Labs mostly study G H K in skin." · l4 "G H K is three amino acids, holding one copper atom." (comma variant) · l1/l3/l5/l6 as on screen.
l6 is byte-identical to the GHK-Cu `../ghkcu/l6.wav` (same seed, setting and text), so it is the reused take and it still passes.

## Rounds (2 of the 3 allowed)
- **Round 1:** both settings, all 6 lines, seeds 42/7/2024/99. 26 of 48 passed. l1 passed 8/8, l3 5/8, l2 3/8 (0.45/0.3 mostly slow at the 1.12 cap, "studied" for "study"), l5 4/8, l6 2/8 (fast or flat). l4 passed 4/8, but every pass sat at 126-131 Hz, below the shared pitch window (about 137-153 Hz).
- **Round 2:** l4 only. 10 new seeds on 0.45/0.3, 0.6/0.5 and 0.6/0.5 with a comma after "acids". 16 of 30 passed, and takes at 137.9-148.8 Hz sat in the window (mostly the comma variant).
- Polish check: 43 passing takes before polish (42 new plus the reused l6), 41 after (two l4 takes dropped out). No winning take was lost.

## Notes
- If captions come from the transcript, write "GHK" as on screen. Whisper already writes it that way.
- Raw takes, per-round results and the polished pool are in `work/` (gitignored). Rerun: `python g3.py gen r1.json`, `python g3.py gen r2.json`, `python g3.py final r1 r2` (venv `%USERPROFILE%\chatterbox\venv`).
