# pepinfo smash reel (Dark Lab look)

Peptide-channel version of the smash kit. Angle: "Untested seller" (frosted block stamped UNTESTED, steel ball labelled COA,
end card on what a real third-party test checks). Allowed angle per the vault's Peptide Content Compliance Lane: lab testing / supplier red flags.
No vials, syringes, bodies, dosing or effect claims anywhere in the frame.

Run from `~/work/crucible` after the main README "Setup":
```bash
python3 smash.py '{"strength":6,"g":-6,"cells":48,"seed":5,"bally":2.6,"ballv":-1.0}'   # ball impact ~0.53 s
python3 frames.py 8
cd pep && python3 make_labels.py && cd ../out                    # pep/ = copy of this folder
FRAMES=1,14,30,200 OUT=stills LABELS=../pep W=360 H=640 SPP=16 ~/work/bl/venv/bin/python ../pep/pepinfo_render.py   # look first
# full: two nohup halves, 2 threads each, frames 1-83 and 84-165 (5.5 s; the end card holds the last frame)
W=720 H=1280 SPP=12 THREADS=2 START=1 END=83 OUT=full LABELS=../pep nohup ~/work/bl/venv/bin/python ../pep/pepinfo_render.py &
W=720 H=1280 SPP=12 THREADS=2 START=84 END=165 OUT=full LABELS=../pep nohup ~/work/bl/venv/bin/python ../pep/pepinfo_render.py &
python3 ../sound.py frames.json smash.wav 15
python3 ../pep/compose_pepinfo.py full smash.wav pepinfo-smash-untested.mp4 ../pep/card.json   # 1080x1920, -14 LUFS, 14 Mbps
```
Timing on the 4-core cloud container: about 40-70 s per frame per half at 720x1280, 12 spp (about an hour for 165 frames).
Edit `card.json` for the hook, rehook and end-card text; every on-screen word and the caption go through
`automation/instagram/audit.py` before anything is queued. On-screen text stays between the top band and 78% height.

## Engine comparison (2026-11-22)
`.claude/skills/` also holds arjun988/blender-skills v1.3.0 (MIT, commit 904f095, 94 text-only skills; `blender-director` routes).
Its tips are written for a live Blender over MCP (`blender-mcp` addon), not headless bpy, so they are used here as guidance only.
`LOOK=arjun` applies them to the same shot (AgX High Contrast, named 3-point rig, roughness micro-variation, 12 bounces, caustics);
`ENGINE=EEVEE` renders with EEVEE (needs `apt-get install libegl1 libegl-mesa0 libgbm1`; runs on software GL in the container).
Same 4 frames at 360x640: current look ~6 s/frame, arjun Cycles ~6 s/frame, arjun EEVEE ~42 s/frame.
Result: the current look (Standard view, cyan rim + back lights) keeps the brand colour and the UNTESTED stamp; AgX washed the block
to flat white and faded the stamp; EEVEE looked plasticky and was 7x slower without a GPU. Keep the default (`LOOK=base`, Cycles).
