import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];rows={}
for f in sorted((r/'outputs/DeliveryArt/People').glob('SK_*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f));o=next(o for o in bpy.data.objects if o.type=='MESH');uv=o.data.uv_layers.active;image=next(n.image for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');px=list(image.pixels);w,h=image.size
 top=[]
 for p in o.data.polygons:
  if min(o.data.vertices[i].co.z for i in p.vertices)<max(v.co.z for v in o.data.vertices)*.75:continue
  coord=uv.data[p.loop_indices[0]].uv;c=px[(min(h-1,int(coord.y*h))*w+min(w-1,int(coord.x*w)))*4:][:3]
  if max(c)<.32:top.append((max(o.data.vertices[i].co.z for i in p.vertices),tuple(round(x,3) for x in c),tuple(coord)))
 rows[f.stem]={'top':max(v.co.z for v in o.data.vertices),'dark_levels':sorted(set(round(t[0],3) for t in top))[-12:],'samples':list(set(t[1] for t in top))}
print(json.dumps(rows,indent=2))
