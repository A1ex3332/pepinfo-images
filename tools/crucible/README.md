# Crucible kit (smash ASMR: Crucible physics, Blender Cycles picture)

Crucible (`@codepawlhq/crucible`, MIT, github.com/codepawl/crucible) is a JS 3D engine with an MCP server.
Tested in the cloud container on 2026-11-21:

| Route | Result |
|---|---|
| Crucible raster video | ~2 s/frame at 720x1280, but looks like a game engine. Lost to our Cycles chop look. |
| Crucible path tracer | ~72 s/frame at 720x1280 64 spp (CPU). Too slow for video. |
| **Crucible physics -> Blender Cycles** | **Use this.** Crucible fractures a block (Voronoi, up to 64 pieces) and runs Rapier physics in seconds; we pull every piece's matrix per frame and render in Cycles. |

## Setup (once per container)
```bash
mkdir -p ~/work/crucible && cd ~/work/crucible && npm init -y
npm i @codepawlhq/crucible three@0.187.0 @dimforge/rapier3d-compat@0.21.0 manifold-3d@3.5.4 @modelcontextprotocol/sdk
cp <repo>/tools/crucible/* . && mkdir -p jobs assets audio out
CRU_DIR=$PWD nohup node bridge.mjs > bridge.log 2>&1 &     # keeps one crucible-mcp session, port 7777
./cru scene_capabilities '{}'                               # any MCP tool: ./cru <tool> '<json>' [image.png]
python3 -m venv ~/work/bl/venv && ~/work/bl/venv/bin/pip install bpy==5.2.3
```

## Make a smash reel
```bash
python3 smash.py '{"strength":6,"g":-6}'       # build + simulate (prints glue breaks)
python3 job.py 1 '{"kind":"stills","width":360,"height":640,"duration":7,"motion":{"start":0},"quality":"realtime"}'  # fast raster contact sheet
python3 frames.py 8                             # out/rest.glb + out/frames.json (~50 s for 240 frames)
cd out && FRAMES=1,12,25,90 ~/work/bl/venv/bin/python ../blender_render.py   # check stills
# full: two nohup halves, 2 threads each (about 70 s/frame per half at 720x1280, 20 spp)
python3 ../sound.py frames.json smash.wav       # crunch + knocks driven by the physics
ffmpeg -framerate 30 -i full/f%04d.png -i smash.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest smash.mp4
```

## Gotchas
- Material `subsurface` crashes Crucible's raster shader on SwiftShader. Leave it to Blender.
- A fractured node needs uniform scale, or GLB export fails ("cannot preserve shear").
- Never delete files in `jobs/exports` by hand; the server tracks them. Restart the bridge if it complains.
- Glue `strength` 6: block loosens at once and bursts on impact (looks best). 25: the ball just sits on top.
- glTF is Y-up: Blender matrix = C @ M @ C^-1 with C = +90 deg about X (done in blender_render.py).
- Physics limits: 128 bodies, 64 cells per fracture, 10 s per bake.

## Blender skills
`.claude/skills/blender-*` are from EL4CTEO/blender-skills (MIT, commit 9e7e04a): core, simulation,
lighting-lookdev, rendering, pbr-materials, asset-qa. Their scripts run headless with our pip bpy 5.2.3
(`sys.path.insert(0, skill/scripts); import sim_setup`). Blender's own rigid body on prefractured pieces
gave a broken result in testing; prefer Crucible physics for smashes.
