import bpy
from pathlib import Path
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
for name in ['pelvis','thigh_l','calf_l','foot_l']:
 i=mesh.vertex_groups[name].index;v=[v.co for v in mesh.data.vertices if any(g.group==i for g in v.groups)];print(name,'head',list(rig.data.bones[name].head_local),'min',[min(p[a] for p in v) for a in range(3)],'max',[max(p[a] for p in v) for a in range(3)])
