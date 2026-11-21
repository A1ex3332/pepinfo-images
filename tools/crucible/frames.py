# Pull per-frame node matrices from the open Crucible scene (bridge must be running).
# usage: python3 frames.py [seconds]  -> out/rest.glb (pieces at t=0) + out/frames.json
# Never delete files in jobs/exports by hand: the server prunes them itself.
import json,subprocess,struct,os,sys
fps=30; T=float(sys.argv[1]) if len(sys.argv)>1 else 8
out={}
first=None
for f in range(int(T*fps)):
    r=json.loads(subprocess.run(['./cru','scene_export_glb',json.dumps({"motionTime":f/fps})],capture_output=True,text=True).stdout)
    if r.get('isError'): print(r); break
    p=json.loads(r['out'][0])['path']; b=open(p,'rb').read()
    L=struct.unpack('<I',b[12:16])[0]; j=json.loads(b[20:20+L])
    out[f]={n['name']:n.get('matrix') for n in j['nodes'] if 'name' in n}
    if f==0:
        import shutil; shutil.copy(p,'out/rest.glb')
json.dump(out,open('out/frames.json','w')); print(len(out),'frames')
