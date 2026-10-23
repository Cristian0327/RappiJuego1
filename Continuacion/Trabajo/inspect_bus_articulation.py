import bpy,json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/TrafficDetailed/SK_TransMilenio.blend'))
rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');print('BUS_BONES '+str([(b.name,tuple(b.head_local)) for b in rig.data.bones]));print('BUS_OBJECTS '+str([(x.name,x.type) for x in bpy.data.objects][:15]))
for x in bpy.data.objects:
 if x.type=='MESH':print('MESH_GROUPS '+x.name+' '+str([g.name for g in x.vertex_groups]))
