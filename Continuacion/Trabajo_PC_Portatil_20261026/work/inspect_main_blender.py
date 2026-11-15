import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':print('MESH',o.name,len(o.data.vertices),o.parent.name if o.parent else '', [v.name for v in o.vertex_groups])
 if o.type=='ARMATURE':
  print('ARM',o.name,list(o.matrix_world))
  for b in o.data.bones:print('BONE',b.name,list(b.head_local),list(b.tail_local))
print('ACTIONS',[(a.name,list(a.frame_range)) for a in bpy.data.actions])
