import json,sys,re,collections
from pathlib import Path
p=Path(sys.argv[1]);frames={}
for line in p.read_text(errors='replace').splitlines():
 if 'V2CAUSE|' in line:
  t,i,near,junc,leader,owner=line.split('V2CAUSE|')[1].split('|')[:6];frames.setdefault(float(t),{})[int(i)]=dict(near=float(near),junction=float(junc),leader=float(leader),owner=owner)
for t,frame in frames.items():
 if t<100 and int(t)%20:continue
 print(round(t),dict(collections.Counter('junction' if q['junction']<10 else 'nearby' if q['near']<10 else 'leader' if q['leader']<10 else 'free' for q in frame.values())),dict(collections.Counter(q['owner'] for q in frame.values())))
if frames:
 last=frames[max(frames)];print(json.dumps(last,indent=2));p.with_name(p.stem+'_causes.json').write_text(json.dumps(frames,indent=2))
