# TB-500 Reel voice tuning (Chatterbox, RTX 3060)

Final: `final/voice-final.wav` (48 kHz mono, 23.2 s). All 6 lines pass every RUBRIC.md check after polish. Pitch spread is 1.58 semitones.

## Pipeline (tune.py, final.py, report.py)
- Chatterbox standard `ChatterboxTTS`, `torch.manual_seed(seed)` before every line.
- Clean step: trim lead and tail silence to 0.04 s, shorten any internal silence to a "hold" length (0.14 s for the hook, 0.24 s default, tighter where noted), and set the peak to 0.89. Raw Chatterbox output peaked above 0.99, which was the cause of every clip fail in round 1.
- From round 2: auto tempo per line. ffmpeg atempo moves wps to the middle of the target band, clamped to 0.88-1.15 (0.88-1.12 from round 3).
- Measure with `vox.py` (word count from the `text` field) and transcribe with faster-whisper small.en on the GPU, float16, beam 5. A words check fails if any key term is missing (TB-500, actin and not "acting", thymosin, info thirty, ...) or if the character similarity is under 0.9.
- Ranking: rubric fails first, then the distance outside the target bands.
- Final: `final.py` picks a passing take per line from rounds 2-4, choosing the set whose median pitches all sit in one 1.8-semitone window with the lowest total distance. It then polishes each take (highpass 80 Hz, de-esser around 6.6 kHz, compressor 3:1 at -20 dB, loudnorm -16 LUFS / -1.5 dBTP), re-measures and re-transcribes it, and joins the lines with 0.18 s gaps.
- Voice reference `ref/ref_r1.wav` (7.9 s) is the round 1 hook and heart takes from e45_c30, joined. It is Chatterbox's own output only, no real person's voice.

## Rounds and what changed

**Round 1:** 6 settings, exaggeration {0.45, 0.65, 0.85} × cfg {0.3, 0.5}, seed 42, default voice, no tempo. Best was e45_c30 with 10 fails. Higher exaggeration made the voice drift (pitch spread 5-9 semitones) and caused more mishearings ("TP500", "crabs actin"). Fails were mostly pace: the hook was too fast, and mol, verdict and end were too slow because of long full-stop pauses. Clipping came from raw peaks. Whisper heard "thymus and" for thymosin and "brick cells used" for "bricks cells use".
→ Next: lock the voice with a Chatterbox-made reference, normalize peaks, add per-line auto tempo and tighter pauses, use 3 seeds per line, and change mol's say text to "thy-mo-sin" and cells to "actin... the bricks".

**Round 2:** reference voice, auto tempo, seeds 42/7/2024. Hook, heart and end passed in every setting. Cells still failed (Whisper heard "brick cells used"). mol and verdict were still too slow (2.65-2.74 wps) even at the 1.15 tempo cap. The "default voice" control (def_e45_c30) came out identical to ref_e45_c30 because Chatterbox keeps the last reference conditionals in memory, so I dropped it from the tables.
→ Next: only cells, mol and verdict. Held pauses of 0.12 s for mol and verdict, higher cfg (0.5) and exaggeration 0.6 for faster natural pace, 4 seeds, and 4 cells phrasings.

**Round 3:** "Inside cells, it grabs actin. The bricks, cells use to crawl." passed on all 8 seeds it ran. The "bricks that cells use" phrasing also passes but adds a word that isn't in the on-screen text, so I didn't use it. e60_c50 gave the first passing mol and verdict takes. Elsewhere verdict was still slow, and Whisper sometimes heard "then" for "thin".
→ Next: only mol and verdict, 8 seeds, held pauses of 0.10 s (mol) and 0.08 s (verdict), plus a comma-phrased verdict variant.

**Round 4:** e60_c50 with 0.08 s holds passed 6 of 8 verdict seeds and 2 of 8 mol seeds, with no fails on its best takes. The comma variant ("THIN human data") made Whisper hear "Thim" and slowed the line down, so it lost.

Final settings per line:
- hook, heart, end: exaggeration 0.45, cfg 0.3, temp 0.8, reference voice
- cells: same settings, say text "Inside cells, it grabs actin. The bricks, cells use to crawl."
- mol and verdict: exaggeration 0.6, cfg 0.5, temp 0.8, reference voice, held pauses of 0.08-0.12 s

Remaining caveats:
- Whisper writes cells as "the bricks, cells used to crawl" ("used" for "use"). It passes the key-term and similarity check, but listen to it once.
- mol is spoken from the say text "thy-mo-sin". Whisper heard "thymosin" correctly on the final take.
- Rounds 3 and 4 only re-ran the failing lines, so their fail totals cover those lines only.
## Rubric tables

### r1

| setting | exag | cfg | temp | ref | fails | dist | pitch spread st |
|---|---|---|---|---|---|---|---|
| e45_c30 | 0.45 | 0.3 | 0.8 | no | 10 | 29.27 | 2.69 |
| e65_c30 | 0.65 | 0.3 | 0.8 | no | 13 | 30.88 | 9.31 |
| e65_c50 | 0.65 | 0.5 | 0.8 | no | 13 | 46.36 | 8.51 |
| e85_c30 | 0.85 | 0.3 | 0.8 | no | 15 | 45.93 | 5.31 |
| e45_c50 | 0.45 | 0.5 | 0.8 | no | 17 | 41.75 | 4.02 |
| e85_c50 | 0.85 | 0.5 | 0.8 | no | 17 | 67.57 | 5.32 |

**e45_c30** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| hook | s42 | 3.87 | 1.0 | 0 | 141.6 | 5.44 | 0.0 / -0.232 | pace 3.87 | TB500 is banned in pro sport, so what did it do in the lab? |
| heart | s42 | 3.43 | 1.0 | 0.24 | 137.9 | 5.6 | 0.001 / -0.156 | pace 3.43 | Mice after a heart attack, more heart muscle cells survived, and hearts worked better. |
| cells | s42 | 3.18 | 1.0 | 0.24 | 128.0 | 6.35 | 0.001 / -0.231 | words, f0sd 6.35 | Inside cells, it grabs actin. The brick cells used to crawl. |
| mol | s42 | 2.82 | 1.0 | 0.18 | 149.5 | 4.99 | 0.0 / -0.237 | words, pace 2.82 | Natural thymus and beta-4 is 43 amino acids, some TB500 is just 7 of them. |
| verdict | s42 | 2.08 | 1.0 | 0.24 | 133.3 | 5.47 | 0.001 / -0.293 | pace 2.08, clip | Mice. Rats. Cells. Thin human data. Case stays open. |
| end | s42 | 2.42 | 1.0 | 0 | 133.3 | 5.09 | 0.001 / -0.321 | pace 2.42 | Save this. Code info30 at void, link in bio. |

**e65_c30** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| hook | s42 | 4.38 | 1.0 | 0 | 117.6 | 4.71 | 0.001 / -0.23 | pace 4.38 | TB500 is banned in pro sport, so what did it do in the lab? |
| heart | s42 | 3.61 | 1.0 | 0.16 | 147.5 | 5.59 | 0.001 / -0.179 | pace 3.61 | Mice after a heart attack, more heart muscle cells survived, and hearts worked better. |
| cells | s42 | 3.5 | 1.0 | 0.18 | 185.0 | 6.26 | 0.002 / -0.262 | words, pace 3.5, f0sd 6.26 | In site cells, it grabs actin, the brick cells used to crawl. |
| mol | s42 | 2.67 | 1.0 | 0.24 | 124.0 | 5.7 | 0.0 / -0.279 | pace 2.67, clip | Natural thymosin beta-4 is 43 amino acids. Some TB500 is just 7 of them. |
| verdict | s42 | 2.85 | 1.0 | 0.22 | 201.3 | 6.58 | 0.002 / -0.36 | words, pace 2.85, f0sd 6.58 | Mice. Rats. Cells. Then human data. Case stays open. |
| end | s42 | 2.56 | 1.0 | 0.2 | 155.3 | 5.19 | 0.003 / -0.443 | pace 2.56, clip | Save this. Code info 30 at void. Link in bio. |

### r2

| setting | exag | cfg | temp | ref | fails | dist | pitch spread st |
|---|---|---|---|---|---|---|---|
| ref_e55_c30 | 0.55 | 0.3 | 0.8 | yes | 4 | 12.2 | 6.21 |
| ref_e40_c30_t70 | 0.4 | 0.3 | 0.7 | yes | 4 | 12.28 | 4.81 |
| ref_e45_c30 | 0.45 | 0.3 | 0.8 | yes | 4 | 12.64 | 3.39 |

**ref_e55_c30** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| hook | s2024 | 3.45 | 0.901 | 0.16 | 156.9 | 5.26 | 0.003 / -0.237 | pass | TB500 is banned in pro sport, so what did it do in the lab? |
| heart | s42 | 3.21 | 0.991 | 0.24 | 132.2 | 5.39 | 0.0 / -0.202 | pass | Mice after a heart attack, more heart muscle cells survived, and hearts worked better. |
| cells | s42 | 3.18 | 0.925 | 0.24 | 128.5 | 5.48 | 0.002 / -0.208 | words | Inside cells, it grabs actin, the brick cells used to crawl. |
| mol | s7 | 2.71 | 1.15 | 0.2 | 151.7 | 5.28 | 0.003 / -0.257 | pace 2.71 | Natural thymosin, beta-4, is 43 amino acids. Some TB500 is just seven of them. |
| verdict | s2024 | 2.74 | 1.15 | 0.2 | 158.4 | 4.89 | 0.006 / -0.304 | pace 2.74 | Mice. Rats. Cells. Thin human data. Case stays open. |
| end | s42 | 3.17 | 1.067 | 0.2 | 183.9 | 6.0 | 0.001 / -0.314 | pass | Save this. Code info 30 at void. Link in bio. |

**ref_e40_c30_t70** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| hook | s42 | 3.59 | 0.88 | 0.16 | 130.1 | 5.44 | 0.0 / -0.204 | pass | TB500 is banned in pro sport, so what did it do in the lab? |
| heart | s42 | 3.2 | 0.982 | 0.26 | 125.0 | 4.87 | 0.001 / -0.19 | pass | Mice after a heart attack, more heart muscle cells survived, and hearts worked better. |
| cells | s42 | 3.2 | 1.107 | 0.2 | 114.3 | 4.84 | 0.001 / -0.171 | words | Inside cells, it grabs actin, the brick cells used to crawl. |
| mol | s2024 | 2.7 | 1.15 | 0.2 | 134.5 | 5.55 | 0.0 / -0.251 | pace 2.7 | Natural thymosin beta-4 is 43 amino acids. Some TB500 is just seven of them. |
| verdict | s2024 | 2.73 | 1.15 | 0.22 | 135.0 | 4.04 | 0.007 / -0.33 | pace 2.73 | Mice, rats, cells, thin human data, case stays open. |
| end | s42 | 3.17 | 1.143 | 0.16 | 150.9 | 4.29 | 0.004 / -0.358 | pass | Save this. Code info30 at void. Link in bio. |

### r3

| setting | exag | cfg | temp | ref | fails | dist | pitch spread st |
|---|---|---|---|---|---|---|---|
| ref_e60_c50_tight | 0.6 | 0.5 | 0.8 | yes | 1 | 0.0 | 4.14 |
| ref_e45_c40_that | 0.45 | 0.4 | 0.8 | yes | 2 | 1.32 | 1.35 |
| ref_e45_c30_tight | 0.45 | 0.3 | 0.8 | yes | 2 | 1.64 | 1.2 |
| ref_e45_c50_tight | 0.45 | 0.5 | 0.8 | yes | 4 | 1.0 | 4.56 |

**ref_e60_c50_tight** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| cells | s42 | 3.2 | 0.985 | 0.16 | 133.3 | 4.14 | 0.001 / -0.186 | pass | Inside cells, it grabs actin, the bricks, cells used to crawl. |
| mol | s42 | 3.17 | 1.12 | 0 | 139.1 | 4.7 | 0.001 / -0.304 | pass | Natural thymosin beta-4 is 43 amino acids. Some TB500 is just seven of them. |
| verdict | s99 | 3.0 | 1.12 | 0 | 169.3 | 4.1 | 0.003 / -0.281 | pass | Mice, rats, cells, thin human data, case stays open. |

**ref_e45_c40_that** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| cells | s2024 | 3.2 | 1.0 | 0 | 141.6 | 5.19 | 0.001 / -0.167 | pass | Inside cells, it grabs actin, the bricks that cells use to crawl. |
| mol | s99 | 2.86 | 1.12 | 0 | 133.3 | 5.67 | 0.0 / -0.275 | pace 2.86 | Natural thymosin beta-4 is 43 amino acids, some TB500 is just 7 of them. |
| verdict | s7 | 2.81 | 1.12 | 0 | 144.1 | 4.56 | 0.004 / -0.271 | pace 2.81 | mice, rats, cells, thin human data. Case stays open. |

### r4

| setting | exag | cfg | temp | ref | fails | dist | pitch spread st |
|---|---|---|---|---|---|---|---|
| ref_e60_c50_hold08 | 0.6 | 0.5 | 0.8 | yes | 0 | 0.0 | 1.41 |
| ref_e55_c50_commas | 0.55 | 0.5 | 0.8 | yes | 1 | 1.08 | 0.41 |

**ref_e60_c50_hold08** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| mol | s42 | 3.18 | 1.119 | 0 | 139.1 | 4.84 | 0.001 / -0.286 | pass | Natural thymosin beta-4 is 43 amino acids. Some TB500 is just seven of them. |
| verdict | s2024 | 3.0 | 1.12 | 0 | 150.9 | 4.17 | 0.005 / -0.289 | pass | mice, rats, cells, thin human data. Case stays open. |

**ref_e55_c50_commas** (best take per line)

| line | seed | wps | atempo | max pause s | f0 med Hz | f0 sd st | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| mol | s2024 | 3.06 | 1.12 | 0 | 125.0 | 5.89 | 0.0 / -0.27 | pass | Natural thymosin, beta-4 is 43 amino acids, some TB500 is just 7 of them. |
| verdict | s808 | 2.73 | 1.12 | 0 | 122.1 | 5.1 | 0.001 / -0.356 | pace 2.73 | mice, rats, cells, thin, human data. Case stays open. |

### Final (after polish)

| line | from | wps | max pause s | lead/tail s | f0 med Hz | f0 sd st | clip % | no_speech / logprob | result | Whisper |
|---|---|---|---|---|---|---|---|---|---|---|
| hook | r2/ref_e45_c30/s2024 | 3.43 | 0 | 0.04/0.0 | 150.9 | 4.93 | 0.0 | 0.001 / -0.231 | pass | TB500 is banned in pro sport, so what did it do in the lab? |
| heart | r2/ref_e45_c30/s42 | 3.17 | 0.24 | 0.02/0.0 | 140.4 | 5.33 | 0.0 | 0.001 / -0.196 | pass | Mice after a heart attack, more heart muscle cells survived, and hearts worked better. |
| cells | r3/ref_e45_c30_tight/s7 | 3.16 | 0 | 0.02/0.0 | 150.9 | 5.45 | 0.0 | 0.001 / -0.236 | pass | Inside cells, it grabs actin, the bricks, cells used to crawl. |
| mol | r3/ref_e60_c50_tight/s42 | 3.15 | 0 | 0.02/0.0 | 139.1 | 4.73 | 0.0 | 0.001 / -0.297 | pass | Natural thymosin beta-4 is 43 amino acids. Some TB500 is just seven of them. |
| verdict | r4/ref_e60_c50_hold08/s11 | 3.15 | 0 | 0.02/0.0 | 152.4 | 4.67 | 0.0 | 0.011 / -0.282 | pass | Mice, rats, cells, thin human data, case stays open. |
| end | r2/ref_e45_c30/s42 | 3.15 | 0.2 | 0.02/0.0 | 146.8 | 5.16 | 0.0 | 0.001 / -0.38 | pass | Save this. Code info 30 at void, link in bio. |

Pitch spread across the 6 final lines: **1.58 semitones** (limit 2).

