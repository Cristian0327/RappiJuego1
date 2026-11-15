import sys,re,json,math
from pathlib import Path
p=Path(sys.argv[1]); frames={}; cycles={}
def vec(s): return [float(v) for v in re.findall(r'[XYZ]=([-+\d.]+)',s)]
for ln in p.read_text(errors='replace').splitlines():
 if 'V2CAR|' in ln:
  t,i,d,s,pos,y=ln.split('V2CAR|')[1].split('|')[:6]
  if int(i)<90: frames.setdefault(float(t),{})[int(i)]={'distance':float(d),'speed':float(s),'position':vec(pos)}
 if 'V2CYCLEDETAIL|' in ln:
  x=ln.split('V2CYCLEDETAIL|')[1].split('|'); cycles.setdefault(float(x[0]),{})[x[1]]=dict(state=x[2],index=x[3],goal=vec(x[4]),limit=float(x[5]),max_speed=float(x[6]),mode=x[7],position=vec(x[8]),velocity=vec(x[9]),hit_actor=x[10],hit_component=x[11],hit_point=vec(x[12]))
windows=[dict(time=t,count=len(f),moving=sum(v['speed']>20 for v in f.values())) for t,f in sorted(frames.items())]
progress=[]
for i in range(90):
 samples=[(t,f[i]) for t,f in sorted(frames.items()) if i in f]; travel=0;last_move=None;max_stop=0;stop_start=None
 for (ta,a),(tb,b) in zip(samples,samples[1:]):
  delta=math.dist(a['position'],b['position']);travel+=delta
  if delta>25: last_move=tb;stop_start=None
  else:
   if stop_start is None:stop_start=ta
   max_stop=max(max_stop,tb-stop_start)
 progress.append(dict(id=i,samples=len(samples),sampled_travel_cm=travel,last_motion_time=last_move,longest_stationary_seconds=max_stop))
r=dict(log=str(p),windows=windows,per_vehicle=progress,last_cycle_details=cycles.get(max(cycles),{}) if cycles else {})
p.with_suffix('.analysis.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(windows=windows[::6],last_window=windows[-1:] ,stalled_over_110_seconds=[v['id'] for v in progress if v['longest_stationary_seconds']>=110],last_cycle_details=r['last_cycle_details']),indent=2))