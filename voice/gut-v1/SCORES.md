# Gut-science Reel v1 voice lines (Chatterbox, RTX 3060)

Files: `l1.wav` … `l6.wav`, 48 kHz mono, polished. All 6 pass every check in `../tune/RUBRIC.md` after polish.
Pitch spread across the 6 new lines is **1.54 semitones**. With every earlier final take (TB-500 v4 and v7, GHK-Cu, GHK-Cu v3) it is **1.87 st** (limit 2).

## Setup (same locked voice)
- `gv1.py` is a copy of `../ghkcu-v3/g3.py`. Lines, spoken text and Whisper key phrases come from `lines.json`. Chatterbox `ChatterboxTTS`, reference `../tune/ref/ref_r1.wav`, `torch.manual_seed(seed)` per take.
- Settings 0.45/0.3 and 0.6/0.5, temp 0.8. Same clean step and auto atempo (0.88-1.12).
- Pace on the on-screen word count ("P H"/"pH" is one word, "Here's" is one word). Hook (l1): 3.3-3.6 wps and no pause over 0.2 s. Other lines: 3.0-3.4 wps, pauses up to 0.3 s.
- Strict word-by-word Whisper check (small.en, beam 5). "pH"/"P H" count as "ph", and "2" as "two". Nothing else was let through, so the tolerated list is empty.
- l4/l5 use the corrected text ("enzymes in the intestine", "the intestine absorbs"). The correction came in before anything was rendered.
- Final: same polish chain (highpass 80 Hz, de-esser, 3:1 compressor at -20 dB, loudnorm -16 LUFS / -1.5 dBTP, 48 kHz mono), then re-measure and re-hear every passing take. Pick the lowest-distance set whose median pitches, together with all 19 earlier final takes, fit one 1.9 st window.

## Final per-line scores (after polish)

| line | take | atempo | wps (target) | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | Whisper heard |
|---|---|---|---|---|---|---|---|---|---|---|
| l1 hook | r1/e45_c30/s42 | 1.062 | 3.42 (3.3-3.6) | none | 0.04/0.02 | 146.8 | 5.89 | 0 | 0.002 / -0.227 | your stomach shreds protein all day. Here's how. |
| l2 | r1/e45_c30/s7 | 0.997 | 3.19 (3.0-3.4) | none | 0.04/0.02 | 139.7 | 4.38 | 0 | 0.001 / -0.344 | the stomach lining pumps out acid around pH 2. |
| l3 | r1/e45_c30/s42 | 1.119 | 3.16 | none | 0.02/0.02 | 137.9 | 4.86 | 0 | 0.000 / -0.291 | That acid unfolds proteins, so enzymes can reach their bonds. |
| l4 | r1/e45_c30/s42 | 1.103 | 3.17 | 0.16 | 0.02/0.00 | 149.5 | 5.32 | 0 | 0.001 / -0.239 | Pepsin cuts the chain into short pieces. Later, enzymes in the intestine cut them even smaller. |
| l5 | r1/e45_c30/s42 | 1.009 | 3.18 | none | 0.02/0.04 | 136.8 | 5.61 | 0 | 0.000 / -0.162 | Most protein ends up as single amino acids and tiny pieces the intestine absorbs. |
| l6 | r2/e45_c30_comma/s3 | 0.88 | 3.30 | none | 0.02/0.02 | 149.5 | 5.78 | 0 | 0.000 / -0.258 | What should we zoom into next? |

Spoken text: l6 "What should we zoom into, next?" (comma variant). The other lines are spoken as on screen.

## Rounds (2 of the 3 allowed)
- **Round 1:** both settings, all 6 lines, seeds 42/7/2024/99. 39 of 48 passed. l2, l3 and l5 passed 8/8, l1 and l4 7/8. l6 passed only 1/8: it was too fast even at the 0.88 atempo floor (3.7-4.6 wps), and the one pass sat at 153.8 Hz, outside the shared pitch window.
- **Round 2:** l6 only, 8 new seeds on 0.45/0.3, on 0.45/0.3 with a comma before "next", and on 0.40/0.2. Only the comma variant slowed it enough: 5/8 passed (137.9-148.1 Hz). The plain text and 0.40/0.2 went 0/16.
- Polish check: 44 passing takes before polish, 43 after (one l4 take dropped out). No winning take was lost.

## Notes
- If captions come from the transcript, write "pH 2" as on screen. Whisper already writes it that way.
- Raw takes, per-round results and the polished pool are in `work/` (gitignored). Rerun: `python gv1.py gen r1.json`, `python gv1.py gen r2.json`, `python gv1.py final r1 r2` (venv `%USERPROFILE%\chatterbox\venv`).
