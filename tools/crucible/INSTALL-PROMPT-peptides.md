# Paste this into the peptide project to install the smash pipeline

Copy everything inside the box into the peptide project's chat.

```text
Install my "smash" 3D reel pipeline into this project's repo and make one test reel for the peptide channel. It must stay free and render in the cloud (never on my PC). Do not post anything; show me the test first.

Source: my vault repo A1ex3332/myknowledgevault (add it to this session if you can't see it):
- tools/crucible/ : the kit (bridge.mjs, cru, smash.py, job.py, frames.py, blender_render.py, sound.py, timeline.py, compose.py, README.md)
- .claude/skills/smash-asmr/ : the how-to skill
- .claude/skills/blender-core, blender-simulation, blender-lighting-lookdev, blender-rendering, blender-pbr-materials, blender-asset-qa (+ LICENSE-blender-agent-skills-MIT): free Blender skills (EL4CTEO/blender-skills, MIT)
- wiki/concepts/Peptide Content Compliance Lane.md : the rules every peptide post follows

How it works: Crucible (npm @codepawlhq/crucible, MIT) breaks an object into up to 64 pieces and runs the physics in seconds; frames.py pulls each piece's position per frame; Blender Cycles (pip bpy 5.2.3, headless) renders the frames realistically; sound.py makes the crunch and knock sounds from the physics; compose.py adds the hook text and a live counter at 1080x1920. Never use Crucible's own renders for the final video (they look like a video game).

Steps:
1. Copy those folders into this repo (tools/crucible/ and .claude/skills/...) on a new branch.
2. Follow tools/crucible/README.md "Setup" in the cloud container (5 npm packages, start bridge.mjs, make the bpy venv).
3. Follow .claude/skills/smash-asmr/SKILL.md to make ONE test reel in this project's brand colours. Pick one of these compliant angles (lab testing, untested sellers, claim vs evidence):
   a) "Untested seller" : a frosted block stamped UNTESTED is smashed by a steel ball labelled COA; the pieces settle and the end card says what a real third-party test checks (identity, purity, contents), citing the source.
   b) "Claim vs evidence" : a block carrying a viral nickname claim is smashed by a ball labelled EVIDENCE; captions give 2-4 cited, model-labelled findings (cell, mouse, rat or human trial) and one "what we still don't know" line.
   c) "Why storage matters" : a lab-style ice block cracks apart under a warm lamp, with cited storage facts from the shop's COA/handling page.
   Modify smash.py for the object (box, cylinder or text block) and use a kinematic press plate instead of the ball if it reads better.
4. Compliance (hard lines, run audit.py on every caption and every on-screen word):
   - No dosing, routes, reconstitution or mixing. No syringes, needles, bodies, before/after or results. No weight, appetite, belly-fat or GLP wording or products. No promises to the viewer.
   - Effects only as cited findings labelled with the model used.
   - Caption opens "Link in bio for sources #ad", #ad again after the hashtags, and "Research use only. Not for human consumption. 21+." near the end. TikTok: Branded content on.
   - Only real product photos, real COAs or generated images of the real vial if a vial appears; no smashed vials (glass + peptide reads as misuse).
5. Look at the stills before the full render; check uptime during long renders (container restarts kill them, rerunning resumes). Read the README gotchas first.
6. Open a PR with the kit and put the test MP4 in the project files with its caption. Don't post it.
```
