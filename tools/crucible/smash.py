# Smash scene: jelly cube fractured into pieces, steel ball dropped on it (Crucible physics).
# usage: python3 smash.py '{"strength":6,"g":-6,"cells":64,"seed":5}'  (bridge must be running)
import json,subprocess,sys
def cru(tool,args,img=None):
    a=['./cru',tool,json.dumps(args)]+([img] if img else [])
    return json.loads(subprocess.run(a,capture_output=True,text=True).stdout)
S=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
recipe={"format":"crucible.scene","schemaVersion":1,
"geometries":[{"id":"cube","type":"box","bevel":0.01},{"id":"rb","type":"box","bevel":0.04},{"id":"ball","type":"sphere","segments":96,"rings":48},{"id":"back","type":"box"}],
"materials":[{"id":"candy","color":S.get("color",[0.95,0.2,0.5]),"roughness":0.08,"transmission":0.6,"thickness":0.5,"ior":1.5,"clearcoat":1,"clearcoatRoughness":0.03,"specular":1},
 {"id":"board","color":[0.30,0.18,0.10],"roughness":0.5,"pattern":{"type":"wood"}},
 {"id":"steel","color":[0.92,0.92,0.94],"metallic":1,"roughness":0.05},
 {"id":"dark","color":[0.004,0.004,0.005],"roughness":1}],
"nodes":[{"id":"board","geometry":"rb","material":"board","translation":[0,0.05,0],"scale":[4,0.1,3]},
 {"id":"block","geometry":"cube","material":"candy","translation":[0,0.5,0],"scale":[0.9,0.9,0.9]},
 {"id":"floor","geometry":"back","material":"dark","translation":[0,-0.5,0],"scale":[40,1,40]},
 {"id":"wall","geometry":"back","material":"dark","translation":[0,5,-14],"scale":[40,12,1]},
 {"id":"wall2","geometry":"back","material":"dark","translation":[-16,5,0],"scale":[1,12,40]},
 {"id":"ball","geometry":"ball","material":"steel","translation":[0.02,S.get("bally",2.2),0.02],"scale":[0.26,0.26,0.26]}],
"environment":{"setup":"studio","ground":False,"world":True,"skyTop":[0.01,0.01,0.012],"skyBottom":[0.03,0.025,0.03],"environmentIntensity":0.35,
  "fillIntensity":0.3,"ambientIntensity":0.05,"lightDirection":[-0.6,1.4,0.8],"keyIntensity":2.5,
  "spotLights":[{"position":[-2.2,3.5,2.0],"direction":[2.2,-3.0,-2.0],"angle":0.5,"penumbra":0.6,"intensity":60,"castShadow":True,"color":[1,0.95,0.9]},
                {"position":[2.5,2.2,-2.5],"direction":[-2.5,-1.7,2.5],"angle":0.5,"penumbra":0.7,"intensity":45,"color":[0.75,0.85,1.0]}]},
"effects":{"exposure":1.0,"contrast":1.15,"saturation":1.15,"vignette":0.35,"bloom":{"strength":0.25,"threshold":1.2},"ambientOcclusion":0.8,"motionBlur":{"shutter":0.02,"objects":0.6}},
"camera":{"eye":[1.4,1.5,2.4],"target":[0,0.45,0],"fov":40,"fStop":2.8}}
r=cru('scene_create',{"recipe":recipe}); 
if r.get('isError'): print(r); sys.exit(1)
rev=json.loads(r['out'][0])['revision']
D=8
ops=[{"type":"set-physics","physics":{"duration":D,"gravity":[0,S.get("g",-3.5),0],"bodies":[
   {"node":"board","type":"fixed","shape":"box","friction":0.7},
   {"node":"ball","shape":"ball","density":S.get("balld",7800),"velocity":[0,S.get("ballv",-3.0),0],"restitution":0.15,"friction":0.5}]}},
  {"type":"fracture-node","node":"block","seed":S.get("seed",5),"cells":S.get("cells",64),"strength":S.get("strength",25),"impact":[0.0,0.5,0.0],"impactRadius":0.3,"density":900,"friction":0.7},
  {"type":"set-motion","motion":{"duration":D,"loop":False,"tracks":[
    {"kind":"camera","property":"eye","interpolation":"SMOOTH","keyframes":[{"time":0,"value":[1.5,1.45,2.6]},{"time":1.2,"value":[1.6,1.55,2.8]},{"time":D,"value":[-1.2,2.2,3.0]}]},
    {"kind":"camera","property":"target","interpolation":"SMOOTH","keyframes":[{"time":0,"value":[0,0.55,0]},{"time":D,"value":[0,0.3,0]}]}]}}]
r=cru('scene_apply',{"expectedRevision":rev,"operations":ops}); o=json.loads(r['out'][0]); print('rev',o.get('revision'), r.get('isError'), str(o)[:400] if r.get('isError') else '')
i=json.loads(cru('scene_inspect',{})['out'][0]); p=i['physics']; jb=p.get('jointBreaks',[]); print('breaks',len(jb),'times',sorted(set(j['time'] for j in jb))[:12]); json.dump(p,open('phys.json','w'))
