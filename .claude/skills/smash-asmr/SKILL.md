---
name: smash-asmr
description: Make a vertical "smash" ASMR reel - a steel ball (or hammer/press) smashes a glossy jelly, crystal or soap block into dozens of pieces. Crucible (npm @codepawlhq/crucible) fractures the block and runs the physics in seconds; Blender Cycles renders every frame in the ASMR look; the crunch and knock sounds are made from the physics. Use for satisfying/ASMR reels, "smash", "shatter", "crush", "break into pieces" ideas, or when asked to use Crucible.
---

# Smash ASMR (Crucible physics, Blender Cycles picture)

Kit: `tools/crucible/` (README has setup, gotchas and timings). Blender helpers: `.claude/skills/blender-*`.
Alex approved this look on 2026-11-21 ("that looks a lot better, make stuff like that").

## Why this split
Crucible's own renders look like a game engine and its path tracer is ~72 s/frame on the cloud CPU, so never ship
Crucible pixels. Its fracture + Rapier physics is fast and deterministic: use it for the motion only.

## Steps
1. Setup once per container (README "Setup"): npm packages, `bridge.mjs` on port 7777, pip `bpy==5.2.3` venv.
2. Theme: block colour/material, impactor (ball density/speed), cells (<= 64), seed, gravity. Low gravity (g -4 to -6) reads as slow motion and suits ASMR.
3. `python3 smash.py '{"strength":6,"g":-6,"cells":64,"seed":5}'` builds and simulates. Check the printed glue breaks.
4. Fast check: `python3 job.py 1 '{"kind":"stills","width":360,"height":640,"duration":7,"motion":{"start":0},"quality":"realtime"}'`
   then tile the 8 frames and LOOK: block intact at t=0, ball hits in the first second, pieces spread, nothing falls off-frame.
5. `python3 frames.py 8` -> `out/rest.glb` + `out/frames.json`.
6. In `out/`: `FRAMES=1,12,25,90 python ../blender_render.py` (stills), then full render in two nohup halves
   (`W=720 H=1280 SPP=20 THREADS=2 START=1 END=120` and `START=121 END=240`), ~40 s/frame per half. Rerun resumes.
   The container can restart and kill renders: check `uptime` and rerun.
7. Sound: `python3 ../sound.py frames.json smash.wav`. Hook + live piece counter: write `full/timeline.json`
   (`fps`, per-frame `counts` of pieces moved > 4 cm since just before impact, `theme.hook`), then
   `python3 compose.py full smash.wav out.mp4` (copy of asmr/chop/compose.py; `timeline.py` writes the json) (1080x1920, -14 LUFS).
8. Audit loop (farm rule): blind panel per `farm/AUDITS.md`, improve, re-check, then queue.

## Queue
Same slot as chop ASMR (viralclipsreelz 20:23 UTC, files with "asmr"): `autopost/accounts/viralclipsreelz/videos/1NN-asmr-smash-<theme>.{mp4,txt,json}`,
json `{"no_audio": true, "video_volume": 100, "youtube": {...}}` (YouTube skills: search-led title, category 24).
Alternate with chop reels; never more than the usual one ASMR a day.

## Ideas
Jelly cube, glass-candy crystal, soap bar, ice block, chocolate slab, honeycomb, amethyst geode, marble egg;
impactors: steel ball, hydraulic press plate (kinematic body), bowling ball, hammer.
