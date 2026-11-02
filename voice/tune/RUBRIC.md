# Voice take rubric (score each take, lower penalty = better)
Measure each line wav with `python vox.py <wav> <word_count>` (needs numpy + ffmpeg on PATH).
1. Words: Whisper transcript must match the line (TB-500 / T B 500, info thirty, actin, thymosin all heard). Any miss = reject.
2. Pace: hook 3.3-3.6 words/s; other lines 3.0-3.4.
3. Pauses: no internal pause > 0.30 s (hook: > 0.20 s). Lead and tail silence trimmed to <= 0.06 s.
4. Consistency: median pitch (f0_med) of all 6 lines within 2 semitones of each other (12*log2(max/min) <= 2).
5. Expressive, not flat: f0_sd_semitones 3.5-6 on each line.
6. No clipping (clip_pct 0) and no artifacts (Whisper no_speech_prob < 0.1, avg_logprob > -0.5).
