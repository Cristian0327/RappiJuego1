import json,re,math,sys
from pathlib import Path
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root/'python_deps'))
from shapely.geometry import LineString,Point
source=root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
fit={v['name']:v['lane'] for v in json.loads((source/'service_lane_fit.json').read_text())}
lanes=json.loads((root/'clearance_lanes.json').read_text());lines=[LineString([p[:2] for p in q+q[:1]]) for q in lanes]
path=Path(sys.argv[1]);samples={};states={}
def vec(text):return [float(v) for v in re.findall(r'[XYZ]=([-+\d.]+)',text)]
for line in path.read_text(errors='replace').splitlines():
    if 'V2SERVICE|' in line:
        t,name,p,v,_=line.split('V2SERVICE|')[1].split('|')[:5]
        if name in fit:samples.setdefault(name,[]).append(dict(time=float(t),position=vec(p),velocity=vec(v)))
    if 'V2CYCLEDETAIL|' in line:
        x=line.split('V2CYCLEDETAIL|')[1].split('|');states[(x[1],float(x[0]))]=float(x[2])
report=[]
for name,rows in sorted(samples.items()):
    eligible=[r for r in rows if states.get((name,r['time']),0)<2];travel=0;start=None;longest=0;last_motion=None;lateral=[]
    for row in eligible:lateral.append(lines[fit[name]].distance(Point(row['position'][:2])))
    for a,b in zip(eligible,eligible[1:]):
        delta=math.dist(a['position'][:2],b['position'][:2]);travel+=delta
        if delta>25:start=None;last_motion=b['time']
        else:
            if start is None:start=a['time']
            longest=max(longest,b['time']-start)
    report.append(dict(name=name,samples=len(eligible),travel_cm=travel,last_motion_time=last_motion,longest_stationary_seconds=longest,max_lateral_cm=max(lateral,default=0),p95_lateral_cm=sorted(lateral)[min(len(lateral)-1,int(len(lateral)*.95))] if lateral else 0,last_speed=math.hypot(*eligible[-1]['velocity'][:2]) if eligible else None))
result=dict(services=report,stalled_over_110=[r['name'] for r in report if r['longest_stationary_seconds']>=110],max_lateral_cm=max([r['max_lateral_cm'] for r in report],default=0))
path.with_name(path.stem+'_service_progress.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
