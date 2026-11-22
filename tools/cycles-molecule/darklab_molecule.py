"""Dark Lab molecule shot ray-traced in Blender Cycles (Molecular Nodes + RDKit, CPU, free).
Real atom-by-atom model from the peptide's amino-acid sequence, macro camera drifting along the chain with depth of field,
gold carbon / cyan nitrogen / white oxygen to match the current 3D zoom Reels, opaque Dark Lab background.
usage: /opt/mn/bin/python -I darklab_molecule.py SEQ OUT_DIR W H N [samples]   (FRAMES=0,30 renders only those)"""
import sys, os, math
import numpy as np
seq, out, W, H, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
spp = int(sys.argv[6]) if len(sys.argv) > 6 else 24
os.makedirs(out, exist_ok=True)
from rdkit import Chem
from rdkit.Chem import AllChem
m = Chem.AddHs(Chem.MolFromSequence(seq))
ps = AllChem.ETKDGv3(); ps.randomSeed = 11; ps.useRandomCoords = True; ps.maxIterations = 5000
assert AllChem.EmbedMolecule(m, ps) == 0; AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
m = Chem.RemoveHs(m)
conf = m.GetConformer(); P = conf.GetPositions(); P -= P.mean(0)
u, s, vt = np.linalg.svd(P, full_matrices=False); Q = P @ vt.T
Q = np.stack([Q[:, 1], Q[:, 2], Q[:, 0]], 1)   # long axis -> Blender Z (screen vertical in a 9:16 frame)
for i, p in enumerate(Q): conf.SetAtomPosition(i, p.tolist())
sdf = os.path.join(out, "model.sdf"); Chem.MolToMolFile(m, sdf)
import bpy, molecularnodes as mn
from mathutils import Vector
cv = mn.Canvas(engine="CYCLES", resolution=(W, H), transparent=False)
cv.samples = spp
sc = bpy.context.scene
sc.cycles.device = "CPU"; sc.cycles.use_denoising = True
sc.render.threads_mode = "FIXED"; sc.render.threads = os.cpu_count()
cv.view_transform = "Standard"; cv.exposure = 0.3
mol = mn.Molecule.load(sdf)
col = {6: (255, 196, 110), 7: (60, 220, 255), 8: (245, 245, 250), 16: (255, 212, 60)}
z = [a.GetAtomicNum() for a in m.GetAtoms()]
rgba = np.array([[*[(v / 255) ** 2.2 for v in col.get(n, col[6])], 1.0] for n in z], dtype=np.float32)
mol.store_named_attribute(rgba, "BrandColor", atype="FLOAT_COLOR")
mol.add_style("ball_and_stick", color="BrandColor", sphere="Point", quality=6, scale=0.36, bond_scale=0.2)
ob = mol.object
# Molecular Nodes stores coordinates scaled (0.01 per Angstrom); measure the real extent from the evaluated mesh
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); ev = ob.evaluated_get(dg)
bb = [ob.matrix_world @ Vector(c) for c in ev.bound_box]
lo = Vector([min(v[i] for v in bb) for i in range(3)]); hi = Vector([max(v[i] for v in bb) for i in range(3)])
ctr = (lo + hi) / 2; L = (hi - lo).z; R = max((hi - lo).x, (hi - lo).y)
print("colls", [(c.name, c.hide_render) for c in bpy.data.collections]); print("extent", tuple(round(x, 3) for x in (hi - lo)))
# Dark Lab world + lights
w = bpy.data.worlds.new("darklab"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get("Background") or w.node_tree.nodes.new("ShaderNodeBackground")
if not bg.outputs[0].links: w.node_tree.links.new(bg.outputs[0], (w.node_tree.nodes.get("World Output") or w.node_tree.nodes.new("ShaderNodeOutputWorld")).inputs[0])
bg.inputs[0].default_value = (0.0032, 0.0037, 0.0048, 1); bg.inputs[1].default_value = 1
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
def light(name, loc, energy, size, colr):
    Ld = bpy.data.lights.new(name, "AREA"); Ld.energy = energy; Ld.size = size; Ld.color = colr
    lo_ = bpy.data.objects.new(name, Ld); sc.collection.objects.link(lo_); lo_.location = loc
    t = lo_.constraints.new("TRACK_TO"); t.target = ob
S = L  # scene scale
light("key", ctr + Vector((-1.2, -1.6, 0.8)) * S, 120 * S * S, 0.8 * S, (1, 0.95, 0.88))
light("rim", ctr + Vector((1.0, 1.4, 0.4)) * S, 200 * S * S, 0.4 * S, (0.2, 0.88, 1.0))
light("fill", ctr + Vector((1.6, -0.8, -0.6)) * S, 15 * S * S, 1.2 * S, (0.85, 0.9, 1.0))
# glossier atoms than the Molecular Nodes default
for mt in [x for x in bpy.data.materials if not x.name.startswith("orb")]:
    print("MAT", mt.name)
    if mt and mt.use_nodes:
        for n in mt.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Roughness"].default_value = 0.22; n.inputs["Coat Weight"].default_value = 0.7; n.inputs["Coat Roughness"].default_value = 0.08
# out-of-focus gold and cyan "bokeh" orbs behind the molecule (Dark Lab zoom look)
rs = np.random.default_rng(4)
for i in range(int(os.environ.get("ORBS", "40"))):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=float(rs.uniform(0.025, 0.07)) * L, segments=16, ring_count=8,
        location=tuple(ctr + Vector((-math.sin(0.8), math.cos(0.8), 0)) * rs.uniform(0.7, 2.0) * L + Vector((math.cos(0.8), math.sin(0.8), 0)) * rs.uniform(-1.0, 1.0) * L + Vector((0, 0, rs.uniform(-0.9, 0.9) * L))))
    em = bpy.data.materials.new(f"orb{i}"); em.use_nodes = True; nt = em.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (1, 0.72, 0.35, 1) if rs.random() < 0.8 else (0.2, 0.88, 1, 1)
    e.inputs[1].default_value = float(rs.uniform(2.5, 6)); o_ = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o_.inputs[0])
    orb = bpy.context.object; orb.data.materials.append(em)
    for c_ in list(orb.users_collection): c_.objects.unlink(orb)
    sc.collection.objects.link(orb); orb.hide_render = False
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.dof.use_dof = True; cam.dof.aperture_fstop = float(os.environ.get("FSTOP", "0.7"))
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
tg = bpy.data.objects.new("tg", None); sc.collection.objects.link(tg); cam.dof.focus_object = tg
tr = co.constraints.new("TRACK_TO"); tr.target = tg
dist = float(os.environ.get("DIST", "1.5")) * L
fr = os.environ.get("FRAMES")
rng = [int(x) for x in fr.split(",")] if fr else range(N)
for f in rng:
    k = f / max(1, N - 1)
    zt = ctr.z + (0.32 - 0.64 * k) * L               # drift down the chain
    a = 0.5 + 0.6 * k                                 # slow orbit
    tg.location = Vector((ctr.x, ctr.y, zt))
    co.location = Vector((ctr.x + math.sin(a) * dist, ctr.y - math.cos(a) * dist, zt + 0.08 * L))
    bpy.context.view_layer.update()
    if os.environ.get("DBG"):
        from bpy_extras.object_utils import world_to_camera_view
        orbs = [o for o in sc.objects if o.name.startswith("Sphere")]
        vis = [tuple(round(x, 2) for x in world_to_camera_view(sc, co, o.location)) for o in orbs]
        print("ORBS", len(orbs), sum(1 for v in vis if 0 < v[0] < 1 and 0 < v[1] < 1 and v[2] > 0), vis[:5], "cam", tuple(co.location), "ctr", tuple(ctr))
    p = os.path.join(out, f"f{f:04d}.png"); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    from PIL import Image, ImageFilter, ImageChops   # soft bloom like the current zoom Reels
    im = Image.open(p).convert("RGB"); hl = im.point(lambda v: max(0, v - 215) * 1.2)
    glow = hl.filter(ImageFilter.GaussianBlur(W / 30)); ImageChops.add(im, glow).save(p)
print("done")
