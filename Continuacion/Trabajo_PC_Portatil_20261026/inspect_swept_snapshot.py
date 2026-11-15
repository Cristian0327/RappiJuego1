import json, math, re
from pathlib import Path
root=Path(__file__).resolve().parent
data=root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
config=json.loads((data/'defaults.json').read_text())['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager']
models=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models']
indices=[int(i*140/80) for i in range(80)]+list(range(140,150))
fit={r['name']:r['lane'] for r in json.loads((data/'service_lane_fit.json').read_text())}
rows={};states={};causes={}
def vec(text):return [float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)',text)]
for line in (root/'traffic_resume_v14.log').read_text(errors='replace').splitlines():
    if 'V2CAR|' in line:
        r=line.split('V2CAR|',1)[1].split('|');i=int(r[1]);m=models[config['ModelIndices'][indices[i]]]
        rows['car:'+r[1]]=dict(position=vec(r[4]),yaw=float(r[5]),speed=float(r[3]),hl=m['half_length'],hw=m['half_width'])
    if 'V2SERVICE|' in line:
        r=line.split('V2SERVICE|',1)[1].split('|')
        if r[1] not in fit:continue
        f=vec(r[4]);v=vec(r[3]);rows[r[1]]=dict(position=vec(r[2]),yaw=math.degrees(math.atan2(f[1],f[0])),speed=math.hypot(*v[:2]),hl=180,hw=75)
    if 'V2CYCLEDETAIL|' in line:
        r=line.split('V2CYCLEDETAIL|',1)[1].split('|');states[r[1]]=float(r[2])
    if 'V2CAUSE|' in line:
        r=line.split('V2CAUSE|',1)[1].split('|');causes['car:'+r[1]]=r[2:]
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def sweep(a,b,margin=60):
    f=(math.cos(math.radians(a['yaw'])),math.sin(math.radians(a['yaw'])));g=(math.cos(math.radians(b['yaw'])),math.sin(math.radians(b['yaw'])))
    n=(-f[1],f[0]);m=(-g[1],g[0]);delta=[b['position'][i]-a['position'][i] for i in range(2)];lo=0;hi=5000
    for axis in [f,n,g,m]:
        radius=sum(abs(dot(direction,axis))*(body[key]+padding) for body,fw,rt in [(a,f,n),(b,g,m)] for key,direction,padding in [('hl',fw,margin),('hw',rt,10)])
        offset=dot(delta,axis);rate=dot(f,axis)
        if abs(rate)<.00001:
            if abs(offset)>radius:return 1e8
            continue
        ends=sorted([(offset-radius)/rate,(offset+radius)/rate]);lo=max(lo,ends[0]);hi=min(hi,ends[1])
    return max(0,lo-25) if hi>=lo else 1e8
report={}
for name,a in rows.items():
    if a['speed']>20 or states.get(name,0)>=2:continue
    blockers=[]
    for other,b in rows.items():
        if name==other or math.dist(a['position'][:2],b['position'][:2])>5000:continue
        gap=sweep(a,b)
        if gap<2:blockers.append(dict(name=other,gap=gap,tight_gap=sweep(a,b,20),own=a,target=b))
    if blockers:report[name]=dict(cause=causes.get(name),blockers=blockers)
(root/'swept_v14_snapshot.json').write_text(json.dumps(report,indent=2))
print(json.dumps({name:[dict(name=b['name'],tight_gap=b['tight_gap']) for b in r['blockers']] for name,r in report.items()},indent=2))
