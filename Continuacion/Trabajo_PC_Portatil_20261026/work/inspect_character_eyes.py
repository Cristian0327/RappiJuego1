import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];report={}
for f in sorted((r/'outputs/DeliveryArt/People').glob('SK_*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f));o=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');image=next(n.image for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');px=list(image.pixels);w,h=image.size;uv=o.data.uv_layers.active
 headidx=o.vertex_groups['head'].index;headverts=[v for v in o.data.vertices if any(g.group==headidx and g.weight>.99 for g in v.groups)];colors={}
 for p in o.data.polygons:
  if not all(any(g.group==headidx and g.weight>.99 for g in o.data.vertices[vi].groups) for vi in p.vertices):continue
  coord=uv.data[p.loop_indices[0]].uv;col=tuple(round(c,3) for c in px[(min(h-1,int(coord.y*h))*w+min(w-1,int(coord.x*w)))*4:][:3]);key=str(col)
  entry=colors.setdefault(key,{'uv':list(coord),'count':0,'min':[1e8]*3,'max':[-1e8]*3});entry['count']+=1
  for vi in p.vertices:
   for a,c in enumerate(o.data.vertices[vi].co):entry['min'][a]=min(entry['min'][a],c);entry['max'][a]=max(entry['max'][a],c)
 report[f.stem]={'head_bone':list(rig.data.bones['head'].head_local),'head_min':[min(v.co[a] for v in headverts) for a in range(3)],'head_max':[max(v.co[a] for v in headverts) for a in range(3)],'colors':colors}
(r/'work/character_eye_inspection.json').write_text(json.dumps(report,indent=2))
print('EYES_INSPECTED',len(report))
