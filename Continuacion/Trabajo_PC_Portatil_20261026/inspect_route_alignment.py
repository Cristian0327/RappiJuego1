import json,re,math,sys
from pathlib import Path
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root/'python_deps'))
from shapely.geometry import Point,LineString
lanes=json.loads((root/'clearance_lanes.json').read_text())
fit={r['name']:r['lane'] for r in json.loads((root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2/service_lane_fit.json').read_text())}
lines=[LineString([p[:2] for p in lane+lane[:1]]) for lane in lanes]
def vec(text):return [float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)',text)]
rows={}
for line in Path(sys.argv[1]).read_text(errors='replace').splitlines():
    if 'V2ROADDETAIL|' not in line:continue
    r=line.split('V2ROADDETAIL|',1)[1].split('|');name=r[1];i=int(r[2]);goal=vec(r[3]);pos=vec(r[5]);li=fit[name];expected=lanes[li][i] if i<len(lanes[li]) else None
    rows[name]=dict(time=float(r[0]),lane=li,index=i,goal=goal,position=pos,goal_error_cm=math.dist(goal,expected) if expected else None,goal_lateral_cm=lines[li].distance(Point(goal[:2])),actor_lateral_cm=lines[li].distance(Point(pos[:2])),limit=float(r[4]))
out=sorted(rows.values(),key=lambda r:r['actor_lateral_cm'],reverse=True)
Path(sys.argv[1]).with_name(Path(sys.argv[1]).stem+'_route_alignment.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(out[:5],indent=2))
