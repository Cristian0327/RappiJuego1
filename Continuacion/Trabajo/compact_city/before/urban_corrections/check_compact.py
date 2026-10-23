import json,sys,numpy as np
from pathlib import Path
sys.path.insert(0,'urban_refresh/python_deps')
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
m=json.load(open('new_map_audit/before_spacing_expansion/manifest.json'));p=json.load(open('urban_refresh/secondary_road_plan.json'));sec=unary_union([LineString(np.array(r['samples'])/1.72).buffer(570) for r in p['secondary_roads']]);bs=[]
for r in m['instances']:
 if 'bounds' not in r or 'Relieve' in r['source']:continue
 a,b=np.array(r['bounds'])*[100,-100,100];lo=np.minimum(a,b);hi=np.maximum(a,b)
 if hi[2]-lo[2]>230 and sec.intersects(box(*lo[:2],*hi[:2])):bs.append(r['source'])
print('SECONDARY_COMPACT_BUILDING_BOX_CONFLICTS',len(bs),len(m['instances']))
