import json,sys,math
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'python_deps'))
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

lanes=json.loads((root/'clearance_lanes.json').read_text())
data=json.loads((root/'clearance_arc_conflicts.json').read_text())
original_count=len(data['centers']); additions=[[24873.6165,-20043.709],[-12810.6575,-2832.2425]]
for center in additions:
    junction=len(data['centers']);data['centers'].append(center)
    for li,points in enumerate(lanes):
        line=LineString([p[:2] for p in points+[points[0]]]);length=line.length;ds=np.arange(0,length,75)
        flags=np.array([line.interpolate(float(d)).distance(__import__('shapely').geometry.Point(center))<1800 for d in ds])
        if not flags.any():continue
        outside=np.where(~flags)[0];assert len(outside)
        offset=int(outside[0]);order=(np.arange(len(ds))+offset)%len(ds);inside=flags[order]
        starts=np.where(inside&~np.r_[False,inside[:-1]])[0];ends=np.where(inside&~np.r_[inside[1:],False])[0]
        for first,last in zip(starts,ends):
            entry=float(ds[order[first]]);exit=float((ds[order[last]]+75)%length);span=(exit-entry)%length
            # Existing independent reservations must not overlap this interval.
            for e in data['lanes'][li]['events']:
                if e['junction']==junction:continue
                overlap=(entry-e['entry'])%length<e['span'] or (e['entry']-entry)%length<span
                assert not overlap,('overlapping reservations',li,junction,e['junction'],entry,exit)
            a=np.array(line.interpolate((entry+100)%length).coords[0]);b=np.array(line.interpolate((entry-100)%length).coords[0]);direction=(a-b)/np.linalg.norm(a-b)
            mid=len(data['movements'])
            if li in [4,5]:
                canonical={4:0,5:1}[li]
                match=next(e for e in data['lanes'][canonical]['events'] if e['junction']==junction and abs(e['entry']-entry)<1)
                mid=match['movement']
            else:
                path=[list(line.interpolate((entry+d)%length).coords[0]) for d in np.linspace(0,span,max(3,int(span/75)+1))]
                data['movements'].append(dict(lane=li,junction=junction,entry=entry,exit=exit,path=path))
            data['lanes'][li]['events'].append(dict(junction=junction,entry=entry,exit=exit,span=span,direction=direction.tolist(),group=3,movement=mid))
            data['lanes'][li]['events'].sort(key=lambda e:e['entry'])
shapes=[];paths=[]
for movement in data['movements']:
    points=np.array(movement['path']);paths.append(LineString(points));hl=1000 if movement['lane']==6 else 340;hw=155;boxes=[]
    for i,p in enumerate(points):
        f=points[min(i+1,len(points)-1)]-points[max(i-1,0)];f/=max(np.linalg.norm(f),1e-6);n=np.array([-f[1],f[0]])
        boxes.append(Polygon([p+f*hl+n*hw,p-f*hl+n*hw,p-f*hl-n*hw,p+f*hl-n*hw]))
    shapes.append(unary_union(boxes).buffer(15))
n=len(shapes);matrix=np.eye(n,dtype=bool)
for i,a in enumerate(data['movements']):
    for j,b in enumerate(data['movements'][:i]):
        # A repeated visit to the same physical road still follows body spacing.
        same=paths[i].hausdorff_distance(paths[j])<120 and np.dot(np.array(a['path'][-1])-a['path'][0],np.array(b['path'][-1])-b['path'][0])>0
        safe=a['junction']!=b['junction'] or same or not shapes[i].intersects(shapes[j]);matrix[i,j]=matrix[j,i]=safe
data['compatible']=matrix.ravel().tolist();data['movement_count']=n
(root/'expanded_arc_conflicts.json').write_text(json.dumps(data,indent=2))
print(json.dumps(dict(original_zones=original_count,zones=len(data['centers']),movements=n,extra_centers=additions)))
