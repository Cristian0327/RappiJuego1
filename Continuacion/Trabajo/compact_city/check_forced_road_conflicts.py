import json,sys,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'urban_refresh/python_deps'));from shapely.geometry import LineString
lines=json.loads((R/'compact_city/authored_street_curves.json').read_text());labels=np.load(R/'compact_city/original_labels.npy');names=json.loads((R/'compact_city/object_sources.json').read_text());im=Image.new('L',(800,1000));dr=ImageDraw.Draw(im)
for r in lines:
 p=LineString(np.array(r['samples'])[:,:2]).buffer(460,quad_segs=12);parts=[p] if p.geom_type=='Polygon' else p.geoms
 for p in parts:
  dr.polygon([((x+40000)/100,(y+50000)/100) for x,y in p.exterior.coords],fill=255)
  for hole in p.interiors:dr.polygon([((x+40000)/100,(y+50000)/100) for x,y in hole.coords],fill=0)
a=np.array(im)>0;ids,cts=np.unique(labels[a],return_counts=True);print('ROAD_CONFLICTS',len(ids)-1)
for j,n in zip(ids,cts):
 if j:print(names[j-1],n,round(n/np.sum(labels==j),2))
im.save(R/'compact_city/authored_road_reserve.png')
