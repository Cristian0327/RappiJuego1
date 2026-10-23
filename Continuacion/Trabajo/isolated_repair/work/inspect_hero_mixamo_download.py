import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'outputs/DeliveryArt/Mixamo'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(out/'Hero_Mixamo_Walk.fbx'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
report={'bones':[b.name for b in rig.data.bones],'action':rig.animation_data.action.name,'frames':list(rig.animation_data.action.frame_range),'meshes':[{'name':o.name,'vertices':len(o.data.vertices),'materials':[m.name for m in o.data.materials]} for o in meshes]}
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Hero_Mixamo_Walk.blend'))
(out/'Hero_Mixamo_Inspection.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
