import json,subprocess,sys,time
def cru(tool,args):
    return json.loads(subprocess.run(['./cru',tool,json.dumps(args)],capture_output=True,text=True).stdout)
rev=int(sys.argv[1]); settings=json.loads(sys.argv[2])
r=cru('scene_render_submit',{"expectedRevision":rev,"settings":settings})
j=json.loads(r['out'][0]); print('estimate',j.get('estimate',{}).get('seconds'), j.get('quality'))
jid=j['jobId']; t=time.time()
while True:
    s=json.loads(cru('scene_render_status',{"jobId":jid})['out'][0])
    if s['state'] not in ('queued','running'): break
    time.sleep(5)
print(s['state'], round(time.time()-t,1),'s')
res=json.loads(cru('scene_render_result',{"jobId":jid})['out'][0])
for a in res.get('artifacts',[]): print(a['path'])
m=res.get('metrics',{}); print({k:m.get(k) for k in ('renderSeconds','width','height','frames','captureSeconds')})
if s['state']!='completed': print(json.dumps(s)[:2000])
