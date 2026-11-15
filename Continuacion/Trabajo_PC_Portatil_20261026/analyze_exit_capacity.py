import json,sys,re,math
from pathlib import Path
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root/'python_deps'))
from shapely.geometry import LineString,Point
source=root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
config=json.loads((source/'defaults.json').read_text())['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager']
models=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models'];arcs=json.loads((root/'clearance_arc_conflicts.json').read_text());lanes=json.loads((root/'clearance_lanes.json').read_text());lines=[LineString([p[:2] for p in q+q[:1]]) for q in lanes]
indices=[int(i*140/80) for i in range(80)]+list(range(140,150));frames={};services={}
def vec(text):return [float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)',text)]
for text in Path(sys.argv[1]).read_text().splitlines():
    if 'V2CAR|' in text:
        t,i,d,s,p,y=text.split('V2CAR|')[1].split('|')[:6];i=int(i);model=models[config['ModelIndices'][indices[i]]];frames.setdefault(float(t),{})['car:'+str(i)]=dict(position=vec(p),yaw=float(y),distance=float(d),lane=config['LaneIndices'][indices[i]],hl=model['half_length'])
    if 'V2SERVICE|' in text:
        t,n,p,v,f=text.split('V2SERVICE|')[1].split('|')[:5]
        if not any(x in n for x in ['CivilMotorcycle','PoliceMotorcycle','PoliceRoadPatrol','TwoWheelerCitizen']):continue
        f=vec(f);services.setdefault(float(t),{})[n]=dict(position=vec(p),yaw=math.degrees(math.atan2(f[1],f[0])),hl=300 if 'Patrol' in n else 160)
time=max(frames);rows=dict(frames[time]);rows.update(services.get(time,{}));report=[]
for index in [37,56]:
    own=rows['car:'+str(index)];li=own['lane'];line=lines[li];e=min(arcs['lanes'][li]['events'],key=lambda e:(e['entry']-own['distance'])%line.length);candidates=[]
    for name,other in rows.items():
        if name=='car:'+str(index):continue
        p=Point(other['position'][:2]);mapped=line.project(p);lateral=line.distance(p)
        a,b=line.interpolate((mapped+20)%line.length),line.interpolate((mapped-20)%line.length);yaw=math.atan2(a.y-b.y,a.x-b.x);alignment=math.cos(yaw-math.radians(other['yaw']))
        ahead=(mapped-e['exit'])%line.length
        if lateral<150 and alignment>.95 and ahead<6500:candidates.append(dict(name=name,ahead=ahead,free_gap=ahead-other['hl']-190,lateral=lateral,alignment=alignment))
    report.append(dict(index=index,lane=li,event=e,stop_ahead=(e['entry']-own['distance'])%line.length-own['hl']-680,downstream=candidates))
result=dict(time=time,report=report,note='Geometric downstream candidates only; live reservation ownership still requires engine diagnostics.')
Path(sys.argv[1]).with_name(Path(sys.argv[1]).stem+'_exit_candidates.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
