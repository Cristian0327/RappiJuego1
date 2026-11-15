import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
folder=root/'outputs/DeliveryArt/Mixamo'
bpy.ops.wm.open_mainfile(filepath=str(folder/'Hero_Mixamo_Walk.blend'))
# Compare rigid per-vertex weights, never connected-island weights: this mesh is welded.
for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
 assignments=[(v.index,max(v.groups,key=lambda g:g.weight).group) for v in obj.data.vertices if v.groups]
 for group in obj.vertex_groups:group.remove([v.index for v in obj.data.vertices])
 for index,group in assignments:obj.vertex_groups[group].add([index],1.0,'REPLACE')
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'Hero_Mixamo_VertexRigid.blend'))
source=(root/'work/render_hero_mixamo_candidate.py').read_text().replace('Hero_Mixamo_Walk.blend','Hero_Mixamo_VertexRigid.blend').replace('Hero_Mixamo_Review.png','Hero_Mixamo_VertexRigidReview.png')
exec(compile(source,str(root/'work/render_hero_mixamo_candidate.py'),'exec'))
