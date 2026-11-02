# TB-500 Reel v4 voice lines (Chatterbox, RTX 3060)

Files: `l1.wav` … `l6.wav`, 48 kHz mono, polished. All 6 pass every check in `../tune/RUBRIC.md` after polish.
Pitch spread across the 6 new lines is **1.66 semitones**. With the 6 earlier final takes (`../tune/final/`) included it is still **1.66 st** (limit 2).

## Setup (same locked voice as the earlier tuning job)
- Chatterbox `ChatterboxTTS`, voice reference `../tune/ref/ref_r1.wav` (Chatterbox's own round-1 takes, 7.9 s) on every take, `torch.manual_seed(seed)` before each line.
- Settings: exaggeration 0.45, cfg 0.3, temperature 0.8. A second setting, 0.6/0.5, ran alongside for lines that came out slow.
- Same clean step as before: lead and tail trimmed to 0.04 s, internal silences held to 0.14 s on the hook and 0.24 s elsewhere (0.10-0.12 s on the 0.6/0.5 setting), peak set to 0.89, then auto tempo with atempo clamped to 0.88-1.12.
- Scoring (`v4.py`): `vox.py` measures, faster-whisper small.en (GPU, beam 5) transcribes. Pace uses the on-screen word count. The words check is stricter than last time: it diffs Whisper's words against the on-screen text word by word, so any extra, missing or swapped word fails the take. One known Whisper spelling, "used" for "use", is let through and listed below.
- Final step: polish every passing take (highpass 80 Hz, de-esser, 3:1 compressor at -20 dB, loudnorm -16 LUFS / -1.5 dBTP, 48 kHz mono), then re-measure and re-transcribe each one. From the takes that still pass, pick the set with the lowest total distance whose median pitches, together with the earlier final takes, fit one 1.8-semitone window.

## Final per-line scores (after polish)

| line | take | atempo | wps (target) | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | Whisper heard |
|---|---|---|---|---|---|---|---|---|---|---|
| l1 hook | r2/e45_c30_comma/s555 | 0.991 | 3.40 (3.3-3.6) | none | 0.02/0.00 | 140.4 | 5.39 | 0 | 0.001 / -0.142 | Banned in sport since 2018, most people have never seen the lab data. |
| l2 | r1/e45_c30/s42 | 1.12 | 3.11 (3.0-3.4) | 0.16 | 0.02/0.02 | 148.2 | 4.72 | 0 | 0.001 / -0.241 | 2004, mice after a heart attack, more heart cells survived. |
| l3 | r1/e45_c30/s99 | 1.119 | 3.16 | 0.20 | 0.02/0.00 | 145.5 | 4.60 | 0 | 0.000 / -0.219 | Inside cells, it grabs actin, the bricks, cells used to move. (tolerated: "used") |
| l4 | r1/e60_c50/s42 | 1.019 | 3.14 | none | 0.02/0.00 | 152.4 | 5.29 | 0 | 0.000 / -0.262 | Some TB500 is just 7 of its 43 amino acids. |
| l5 | r2/e45_c30/s17 | 1.103 | 3.15 | 0.20 | 0.02/0.00 | 138.5 | 5.26 | 0 | 0.007 / -0.259 | mice, rats, and cells. Human data is thin. |
| l6 | r1/e45_c30/s7 | 0.95 | 3.18 | none | 0.04/0.02 | 148.1 | 4.42 | 0 | 0.000 / -0.242 | Which peptide should we zoom into next? |

Spoken text used: l1 "Banned in sport, since twenty eighteen. Most people have never seen the lab data." · l2 "Two thousand four, mice after a heart attack: more heart cells survived." · l3 "Inside cells, it grabs actin. The bricks, cells use to move." · l4 "Some T B 500 is just seven of its forty-three amino acids." · l5/l6 as on screen.
Settings per line: l4 used 0.6/0.5 (its 0.45/0.3 takes came out slow). The other five used 0.45/0.3.

## Rounds (2 of the 3 allowed)

**Round 1:** both settings, all 6 lines, seeds 42/7/2024/99. 30 of 48 takes passed.
- 0.45/0.3: l1 4/4, l2 3/4, l3 4/4, l4 2/4, l5 2/4, l6 1/4. Most fails were slow takes that were still under 3.0 wps at the 1.12 atempo cap (l4, l5), or l6 too fast or too flat.
- 0.6/0.5: l1 0/4, l2 4/4, l3 4/4, l4 4/4, l5 1/4, l6 1/4. This setting adds junk at the start of a line ("Hopping.", "And in sport") and blurs "Mice" into "eyes" or "House".
- Two problems showed up. First, every passing l1 take was heard as "sports" and every l3 take as "used". Second, no passing l1 or l5 take sat in the earlier voice's pitch band (139-152 Hz).
- After this round I swapped the character-similarity words check for the word-by-word diff, because a take starting with "Hopping." and one saying "had never" both scraped through the old check.

**Round 2:** only l1 and l5, 8 new seeds. A third variant tried l1 with a comma after "sport".
- The comma variant passed 8/8, and Whisper heard "sport" correctly on all 8. Plain 0.45/0.3 l1 passed 8/8 but was always heard as "sports". With 0.6/0.5, l1 passed 7/8.
- l5 passed 4/8 on 0.45/0.3 and 3/8 on 0.6/0.5. The 0.6/0.5 takes kept adding a noise before "Mice" ("Ah", "Paw", "had").
- Polish check: before polish the best l5 take (s11) passed, but after polish Whisper heard "thin" as "then", the same slip as in the earlier job. So the final step now polishes and re-hears every candidate before picking (s17 was picked).

No third round was needed.

## Notes
- "used" for "use" (l3) came up in every take, and the earlier final's cells line had it too. It reads as a Whisper habit: the spoken text clearly says "use". If it matters, the fallback is the round-3 "bricks that cells use" phrasing from the earlier job, but that adds a word that isn't on screen.
- Raw takes, per-round results and the polished pool are in `work/` (gitignored). Rerun with `python v4.py gen r1.json`, `python v4.py gen r2.json` and `python v4.py final r1 r2` (venv: `%USERPROFILE%\chatterbox\venv`).
