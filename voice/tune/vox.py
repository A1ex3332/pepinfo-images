import sys, subprocess, numpy as np, json
SR=16000
def load(p, ss=None, t=None):
    cmd=['ffmpeg','-v','error']+(['-ss',str(ss)] if ss is not None else [])+['-i',p]+(['-t',str(t)] if t else [])+['-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,dtype=np.float32)
def analyze(x, words=None):
    fl=int(0.02*SR); n=len(x)//fl
    fr=x[:n*fl].reshape(n,fl); rms=np.sqrt((fr**2).mean(1))+1e-9; db=20*np.log10(rms)
    peak=db.max(); speech=db>peak-35
    idx=np.where(speech)[0]
    if len(idx)==0: return {}
    a,b=idx[0],idx[-1]
    # internal pauses
    pauses=[];run=0
    for i in range(a,b+1):
        if not speech[i]: run+=1
        else:
            if run*0.02>=0.15: pauses.append(round(run*0.02,2))
            run=0
    # F0 via autocorrelation on 40ms windows
    f0=[]; w=int(0.04*SR)
    for s in range(a*fl,b*fl-w,int(0.01*SR)):
        seg=x[s:s+w]; 
        if np.sqrt((seg**2).mean())<10**((peak-25)/20): continue
        seg=seg-seg.mean(); ac=np.correlate(seg,seg,'full')[w-1:]
        lo,hi=int(SR/400),int(SR/70); k=lo+np.argmax(ac[lo:hi])
        if ac[k]>0.45*ac[0]: f0.append(SR/k)
    f0=np.array(f0)
    st=12*np.log2(f0/np.median(f0)) if len(f0) else np.array([0])
    dur=(b-a+1)*0.02
    clip=float((np.abs(x)>0.99).mean()*100)
    loud=db[speech]
    r={'dur':round(dur,2),'lead_sil':round(a*0.02,2),'tail_sil':round((n-1-b)*0.02,2),'pauses':pauses,
       'f0_med':round(float(np.median(f0)),1) if len(f0) else None,'f0_sd_semitones':round(float(st.std()),2),
       'f0_range_st_p10_p90':round(float(np.percentile(st,90)-np.percentile(st,10)),2),
       'level_sd_db':round(float(loud.std()),2),'clip_pct':round(clip,3),'peak_frame_db':round(float(peak),1)}
    if words: r['wps']=round(words/dur,2)
    return r
if __name__=='__main__':
    p=sys.argv[1]; words=int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2]!='-' else None
    ss=float(sys.argv[3]) if len(sys.argv)>3 else None; t=float(sys.argv[4]) if len(sys.argv)>4 else None
    print(json.dumps(analyze(load(p,ss,t),words)))
