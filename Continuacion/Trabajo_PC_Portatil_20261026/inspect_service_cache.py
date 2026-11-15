import json, math, re
from pathlib import Path
root=Path(__file__).resolve().parent
poses={};roads={};cars={}
def vec(text):return [float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)',text)]
for line in (root/'traffic_resume_v14.log').read_text(errors='replace').splitlines():
    if 'V2SERVICE|' in line:
        row=line.split('V2SERVICE|',1)[1].split('|');poses[row[1]]=vec(row[2])
    if 'V2CAR|' in line:
        row=line.split('V2CAR|',1)[1].split('|');cars['car:'+row[1]]=vec(row[4])
    if 'V2ROADDETAIL|' in line:
        row=line.split('V2ROADDETAIL|',1)[1].split('|');roads[row[1]]=dict(goal=vec(row[3]),position=vec(row[5]),velocity=vec(row[6]),limit=float(row[4]),obstacle=row[7])
report={}
for name,row in roads.items():
    if math.hypot(*row['velocity'][:2])>20:continue
    p=row['position'];g=row['goal'];dx=g[0]-p[0];dy=g[1]-p[1];length=math.hypot(dx,dy)
    if not length:continue
    dx/=length;dy/=length;near=[]
    for other,q in {**poses,**cars}.items():
        if other==name:continue
        along=(q[0]-p[0])*dx+(q[1]-p[1])*dy;side=abs((q[0]-p[0])*dy-(q[1]-p[1])*dx)
        if 80<along<650 and side<140:near.append(dict(name=other,along=along,side=side))
    report[name]=dict(limit=row['limit'],static_obstacle=row['obstacle'],possible_cache_blockers=near)
print(json.dumps(report,indent=2))
(root/'service_cache_v14_candidates.json').write_text(json.dumps(report,indent=2))
