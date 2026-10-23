import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];folder=root/'outputs/DeliveryArt/Mixamo'
bpy.ops.wm.open_mainfile(filepath=str(folder/'Hero_Mixamo_Walk.blend'))
report=[]
for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
 adjacent=[[] for _ in obj.data.vertices]
 for edge in obj.data.edges:
  a,b=edge.vertices;adjacent[a].append(b);adjacent[b].append(a)
 remaining=set(range(len(adjacent)));islands=[]
 while remaining:
  stack=[remaining.pop()];island=[]
  while stack:
   i=stack.pop();island.append(i)
   for j in adjacent[i]:
    if j in remaining:remaining.remove(j);stack.append(j)
  islands.append(island)
 for island in islands:
  weights={}
  for i in island:
   for g in obj.data.vertices[i].groups:weights[g.group]=weights.get(g.group,0)+g.weight
  if not weights:continue
  dominant=max(weights,key=weights.get)
  for group in obj.vertex_groups:group.remove(island)
  obj.vertex_groups[dominant].add(island,1,'REPLACE')
 report.append({'mesh':obj.name,'rigid_parts':len(islands)})
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'Hero_Mixamo_RigidWalk.blend'))
(folder/'Hero_Mixamo_RigidReview.json').write_text(json.dumps(report,indent=2))
source=(root/'work/render_hero_mixamo_candidate.py').read_text().replace("Hero_Mixamo_Walk.blend","Hero_Mixamo_RigidWalk.blend").replace("Hero_Mixamo_Review.png","Hero_Mixamo_RigidReview.png")
exec(compile(source,str(root/'work/render_hero_mixamo_candidate.py'),'exec'))
