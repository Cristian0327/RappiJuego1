import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/Crowd/SK_Citizen04.blend'))
o=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
print('GROUPS',[(g.index,g.name) for g in o.vertex_groups]);print('BONES',[(b.name,b.parent.name if b.parent else '') for b in rig.data.bones])
print('HEAD_WEIGHTS', {tuple((o.vertex_groups[g.group].name,round(g.weight,3)) for g in v.groups) for v in o.data.vertices if v.co.z>150})
print('TOP', max(v.co.z for v in o.data.vertices),len(o.data.vertices))

