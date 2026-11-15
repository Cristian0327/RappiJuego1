import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'))
r=next(o for o in bpy.data.objects if o.type=='ARMATURE')
print('RIG',r.name,'MATRIX',list(map(list,r.matrix_world)),flush=True)
print('BONES',[(b.name,list(b.head_local)) for b in r.data.bones],flush=True)
