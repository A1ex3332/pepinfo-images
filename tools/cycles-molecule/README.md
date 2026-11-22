# Dark Lab molecule shot in Blender Cycles

Ray-traced version of the molecule part of the 3D zoom Reels: real atom-by-atom model from the peptide's amino-acid
sequence (RDKit + Molecular Nodes, MIT), gold carbon / cyan nitrogen / white oxygen, glossy coat, out-of-focus gold and
cyan orbs, soft bloom, macro camera drifting along the chain. CPU only, free.

Setup (once per container, see automation/reels-tools/QUALITY-UPGRADES.md):
```bash
apt-get install -y libegl1 libegl-mesa0 libgbm1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6
python3.13 -m venv /opt/mn && /opt/mn/bin/pip install "molecularnodes[bpy]" rdkit pillow "nodebpy==520.30.0"
```
Render (stills first with FRAMES=0,45,89):
```bash
/opt/mn/bin/python -I darklab_molecule.py YNWNSFGLRF clip 720 1280 127 16   # kisspeptin-10, 4.2 s at 30 fps
```
About 30 s per frame at 720x1280 on the 4-core container (127 frames ~60 min) with persistent data on; samples 8 is ~55% faster again with a near-identical picture. `splice.sh` upscales, interpolates to
60 fps and drops the shot into a finished Reel between two timestamps, keeping its caption cards and audio.
Env: FSTOP (0.7), DIST (1.5 x molecule length), ORBS (40).
