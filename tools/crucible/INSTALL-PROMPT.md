# Paste this into another Claude project to install the smash pipeline

Copy everything inside the box into the other project's chat.

```text
Install my "smash ASMR" 3D pipeline into this project's repo and make one test reel. It must stay free and render in the cloud (never on my PC).

Source: my vault repo A1ex3332/myknowledgevault (add it to this session if you can't see it):
- tools/crucible/ : the kit (bridge.mjs, cru, smash.py, job.py, frames.py, blender_render.py, sound.py, timeline.py, compose.py, README.md)
- .claude/skills/smash-asmr/ : the how-to skill
- .claude/skills/blender-core, blender-simulation, blender-lighting-lookdev, blender-rendering, blender-pbr-materials, blender-asset-qa (+ LICENSE-blender-agent-skills-MIT): free Blender skills from EL4CTEO/blender-skills, MIT

How it works: Crucible (npm @codepawlhq/crucible, MIT) breaks a block into up to 64 pieces and runs the physics in seconds; frames.py pulls every piece's position per frame; Blender Cycles (pip bpy 5.2.3, headless) renders the frames in a realistic ASMR look; sound.py makes the crunch and knock sounds from the physics; compose.py adds the hook text and a live piece counter at 1080x1920. Do NOT use Crucible's own renders for the final video (they look like a video game and its path tracer is too slow).

Steps:
1. Copy those folders into this repo (tools/crucible/ and .claude/skills/...) on a new branch.
2. Follow tools/crucible/README.md "Setup" in the cloud container: npm install the 5 packages, start bridge.mjs, make the bpy venv.
3. Follow .claude/skills/smash-asmr/SKILL.md to make one test smash reel that fits THIS project's niche and brand colours (change the block material/colour, the impactor and the hook text).
4. Look at the stills before the full render, and check uptime during long renders (container restarts kill them; rerunning resumes).
5. Open a PR with the kit and put the test MP4 in the project files. Don't post it anywhere; show it to me first.
Read the README gotchas before starting (GLB shear, never delete jobs/exports by hand, glue strength, subsurface shader crash).
```
