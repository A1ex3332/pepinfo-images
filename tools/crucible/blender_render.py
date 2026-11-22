# Render the Crucible physics in Blender Cycles: keyframes every piece from frames.json.
# usage (cwd holds rest.glb + frames.json): W=720 H=1280 SPP=20 THREADS=2 START=1 END=120 OUT=dir python blender_render.py
#   FRAMES=1,30,90 renders only those frames (stills check). THEME='{"color":[r,g,b,1]}' sets the jelly colour.
import bpy,json,os,math
from mathutils import Matrix,Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="rest.glb")
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.name.startswith(('floor','wall')): bpy.data.objects.remove(o)
F=json.load(open('frames.json')); C=Matrix.Rotation(math.radians(90),4,'X'); Ci=C.inverted()
def mat(l): return Matrix([l[0:4],l[4:8],l[8:12],l[12:16]]).transposed()
sc=bpy.context.scene; sc.render.fps=30; sc.frame_start=1; sc.frame_end=len(F)
objs={o.name:o for o in bpy.data.objects if o.type=='MESH'}
for o in objs.values(): o.parent=None
for f in sorted(F,key=int):
    for name,m in F[f].items():
        o=objs.get(name)
        if not o or m is None: continue
        o.matrix_world=C@mat(m)@Ci
        o.keyframe_insert('location',frame=int(f)+1); o.keyframe_insert('rotation_quaternion' if o.rotation_mode=='QUATERNION' else 'rotation_euler',frame=int(f)+1)
# materials
def P(name,**kw):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]
    for k,v in kw.items(): b.inputs[k].default_value=v
    return m
TH=json.loads(os.environ.get('THEME','{}'))
col=TH.get('color',(0.9,0.12,0.38,1))
candy=P("candy",**{"Base Color":col,"Roughness":0.1,"Subsurface Weight":0.7,"Subsurface Radius":(1,0.35,0.45),"Subsurface Scale":0.12,"Coat Weight":1.0,"Coat Roughness":0.03})
steel=P("steel",**{"Base Color":(0.9,0.9,0.92,1),"Metallic":1.0,"Roughness":0.06})
wood=P("wood",**{"Base Color":(0.16,0.08,0.035,1),"Roughness":0.4})
for n,o in objs.items():
    if n not in bpy.data.objects: continue
    mm=candy if 'frag' in n else steel if n.startswith('ball') else wood if n.startswith('board') else None
    if mm: o.data.materials.clear(); o.data.materials.append(mm)
    for p in o.data.polygons: p.use_smooth = n.startswith('ball')
sc.render.engine='CYCLES'; sc.cycles.samples=int(os.environ.get('SPP',24)); sc.cycles.use_denoising=True
sc.render.resolution_x=int(os.environ.get('W',360)); sc.render.resolution_y=int(os.environ.get('H',640))
th=int(os.environ.get('THREADS',0))
if th: sc.render.threads_mode='FIXED'; sc.render.threads=th
sc.view_settings.view_transform='Standard'; sc.view_settings.exposure=-0.5
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(0.01,0.01,0.012,1); w.node_tree.nodes["Background"].inputs[1].default_value=1
def B(v): return Vector((v[0],-v[2],v[1]))
cam=bpy.data.cameras.new("c"); cam.lens=38; cam.dof.use_dof=True; cam.dof.aperture_fstop=3.2
co=bpy.data.objects.new("cam",cam); sc.collection.objects.link(co); sc.camera=co
tg=bpy.data.objects.new("tg",None); sc.collection.objects.link(tg); cam.dof.focus_object=tg
for t,e in [(0,(1.5,1.45,2.6)),(1.2,(1.6,1.55,2.8)),(8,(-1.2,2.2,3.0))]: co.location=B(e); co.keyframe_insert('location',frame=int(t*30)+1)
for t,e in [(0,(0,0.5,0)),(8,(0,0.3,0))]: tg.location=B(e); tg.keyframe_insert('location',frame=int(t*30)+1)
c=co.constraints.new('TRACK_TO'); c.target=tg
for name,loc,en,size in [("key",(-2.5,-2,3.5),700,1.5),("rim",(1.5,3.0,1.2),450,0.8),("top",(0,0,4),250,3)]:
    L=bpy.data.lights.new(name,'AREA'); L.energy=en; L.size=size; lo=bpy.data.objects.new(name,L); sc.collection.objects.link(lo); lo.location=loc
    t=lo.constraints.new('TRACK_TO'); t.target=tg
bpy.ops.mesh.primitive_plane_add(size=60,location=(0,0,-0.001)); bpy.context.object.data.materials.append(P("fl",**{"Base Color":(0.015,0.015,0.017,1),"Roughness":0.6}))
sc.render.image_settings.file_format='PNG'
fr=os.environ.get('FRAMES')
rng=[int(x) for x in fr.split(',')] if fr else range(int(os.environ.get('START',1)),int(os.environ.get('END',len(F)))+1)
od=os.environ.get('OUT','/home/user/work/hybrid/out2')
for f in rng:
    p=f"{od}/f{f:04d}.png"
    if os.path.exists(p) and not fr: continue
    sc.frame_set(f); sc.render.filepath=p; bpy.ops.render.render(write_still=True)
