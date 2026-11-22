# pepinfo (Dark Lab) Cycles render of the Crucible smash: frosted block stamped UNTESTED, steel ball labelled COA.
# Same inputs as ../blender_render.py (cwd holds rest.glb + frames.json); decals from make_labels.py in LABELS dir.
# usage: W=720 H=1280 SPP=20 THREADS=2 START=1 END=120 OUT=dir LABELS=dir python pepinfo_render.py ; FRAMES=1,12,30 for stills
import bpy, json, os, math
from mathutils import Matrix, Vector
LAB = os.environ.get('LABELS', os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="rest.glb")
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name.startswith(('floor', 'wall')): bpy.data.objects.remove(o)
F = json.load(open('frames.json')); C = Matrix.Rotation(math.radians(90), 4, 'X'); Ci = C.inverted()
def mat(l): return Matrix([l[0:4], l[4:8], l[8:12], l[12:16]]).transposed()
sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start = 1; sc.frame_end = len(F)
objs = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
for o in objs.values(): o.parent = None
def B(v): return Vector((v[0], -v[2], v[1]))
CAM0 = B((1.5, 1.45, 2.6))
# rest pose first, then bake decal UVs from rest world positions
for name, m in F['0'].items():
    o = objs.get(name)
    if o and m is not None: o.matrix_world = C @ mat(m) @ Ci
bpy.context.view_layer.update()
H = 0.45; Z0 = 0.05
for n, o in objs.items():
    me = o.data; mw = o.matrix_world
    if 'frag' in n:
        uv = me.uv_layers.new(name="decal"); mk = me.color_attributes.new("mask", 'FLOAT_COLOR', 'CORNER')
        for p in me.polygons:
            nw = (mw.to_3x3() @ p.normal).normalized(); cw = mw @ p.center
            front = 1.0 if (nw.y < -0.9 and cw.y < -H + 0.02) else 0.0
            for li in p.loop_indices:
                w = mw @ me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv = ((w.x + H) / (2 * H), (w.z - Z0) / (2 * H))
                mk.data[li].color = (front, 0, 0, 1)
    elif n.startswith('ball'):
        uv = me.uv_layers.new(name="decal"); mk = me.color_attributes.new("mask", 'FLOAT_COLOR', 'CORNER')
        c = mw.translation; v = (CAM0 - c).normalized(); up = Vector((0, 0, 1)); r = v.cross(up).normalized() * -1; u = r.cross(v).normalized() * -1
        for li, l in enumerate(me.loops):
            d = (mw @ me.vertices[l.vertex_index].co - c).normalized()
            uv.data[li].uv = (0.5 + 0.5 * d.dot(r) / 0.95, 0.5 + 0.5 * d.dot(u) / 0.95)
            mk.data[li].color = (1.0 if d.dot(v) > 0.2 else 0.0, 0, 0, 1)
for f in sorted(F, key=int):
    for name, m in F[f].items():
        o = objs.get(name)
        if not o or m is None: continue
        o.matrix_world = C @ mat(m) @ Ci
        o.keyframe_insert('location', frame=int(f) + 1)
        o.keyframe_insert('rotation_quaternion' if o.rotation_mode == 'QUATERNION' else 'rotation_euler', frame=int(f) + 1)
def decal_mat(name, img, base_kw, paint_rgb, paint_rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; Lk = nt.links
    base = N["Principled BSDF"]
    for k, v in base_kw.items(): base.inputs[k].default_value = v
    paint = N.new("ShaderNodeBsdfPrincipled"); paint.inputs["Base Color"].default_value = (*paint_rgb, 1); paint.inputs["Roughness"].default_value = paint_rough
    paint.inputs["Emission Color"].default_value = (*paint_rgb, 1); paint.inputs["Emission Strength"].default_value = 0.35
    uvn = N.new("ShaderNodeUVMap"); uvn.uv_map = "decal"
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(os.path.join(LAB, img)); tex.extension = 'CLIP'
    att = N.new("ShaderNodeAttribute"); att.attribute_name = "mask"
    mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    sep = N.new("ShaderNodeSeparateColor")
    mix = N.new("ShaderNodeMixShader"); out = N["Material Output"]
    Lk.new(uvn.outputs[0], tex.inputs[0]); Lk.new(att.outputs["Color"], sep.inputs[0])
    Lk.new(tex.outputs["Alpha"], mul.inputs[0]); Lk.new(sep.outputs[0], mul.inputs[1])
    Lk.new(mul.outputs[0], mix.inputs[0]); Lk.new(base.outputs[0], mix.inputs[1]); Lk.new(paint.outputs[0], mix.inputs[2])
    Lk.new(mix.outputs[0], out.inputs[0])
    return m
def P(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    for k, v in kw.items(): b.inputs[k].default_value = v
    return m
frost = decal_mat("frost", "untested.png", {"Base Color": (0.80, 0.86, 0.92, 1), "Roughness": 0.32, "Transmission Weight": 0.85, "IOR": 1.31,
                  "Coat Weight": 0.4, "Coat Roughness": 0.15}, (1.0, 0.15, 0.15), 0.45)
steel = decal_mat("steel", "coa.png", {"Base Color": (0.9, 0.9, 0.92, 1), "Metallic": 1.0, "Roughness": 0.08}, (0.03, 0.75, 1.0), 0.35)
bench = P("bench", **{"Base Color": (0.018, 0.022, 0.028, 1), "Roughness": 0.28})
for n, o in objs.items():
    if n not in bpy.data.objects: continue
    mm = frost if 'frag' in n else steel if n.startswith('ball') else bench if n.startswith('board') else None
    if mm: o.data.materials.clear(); o.data.materials.append(mm)
    for p in o.data.polygons: p.use_smooth = n.startswith('ball')
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get('SPP', 24)); sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.transmission_bounces = 8
sc.render.resolution_x = int(os.environ.get('W', 360)); sc.render.resolution_y = int(os.environ.get('H', 640))
th = int(os.environ.get('THREADS', 0))
if th: sc.render.threads_mode = 'FIXED'; sc.render.threads = th
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = -0.4
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.0032, 0.0037, 0.0048, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1
cam = bpy.data.cameras.new("c"); cam.lens = 38; cam.dof.use_dof = True; cam.dof.aperture_fstop = 3.2
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
tg = bpy.data.objects.new("tg", None); sc.collection.objects.link(tg); cam.dof.focus_object = tg
for t, e in [(0, (1.5, 1.45, 2.6)), (1.2, (1.6, 1.55, 2.8)), (8, (-1.2, 2.2, 3.0))]: co.location = B(e); co.keyframe_insert('location', frame=int(t * 30) + 1)
for t, e in [(0, (0, 0.5, 0)), (8, (0, 0.3, 0))]: tg.location = B(e); tg.keyframe_insert('location', frame=int(t * 30) + 1)
c = co.constraints.new('TRACK_TO'); c.target = tg
for name, loc, en, size, col in [("key", (-2.5, -2, 3.5), 700, 1.5, (1, 0.97, 0.94)), ("rim", (1.5, 3.0, 1.2), 650, 0.8, (0.2, 0.88, 1.0)),
                                 ("top", (0, 0, 4), 220, 3, (1, 1, 1)), ("back", (-2.0, 3.5, 0.8), 300, 1.0, (0.2, 0.88, 1.0))]:
    L = bpy.data.lights.new(name, 'AREA'); L.energy = en; L.size = size; L.color = col
    lo = bpy.data.objects.new(name, L); sc.collection.objects.link(lo); lo.location = loc
    t = lo.constraints.new('TRACK_TO'); t.target = tg
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.001)); bpy.context.object.data.materials.append(P("fl", **{"Base Color": (0.006, 0.007, 0.009, 1), "Roughness": 0.6}))
sc.render.image_settings.file_format = 'PNG'
fr = os.environ.get('FRAMES')
rng = [int(x) for x in fr.split(',')] if fr else range(int(os.environ.get('START', 1)), int(os.environ.get('END', len(F))) + 1)
od = os.environ.get('OUT', 'full'); os.makedirs(od, exist_ok=True)
for f in rng:
    p = f"{od}/f{f:04d}.png"
    if os.path.exists(p) and not fr: continue
    sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
