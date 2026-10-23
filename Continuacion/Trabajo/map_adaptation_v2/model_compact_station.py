import bpy,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P.parent/'urban_refresh/export/SM_Bogota_EstacionTransmi.fbx'));ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);maximum=max(abs(v.co.x) for v in ob.data.vertices);assert 24<maximum<25,maximum
for v in ob.data.vertices:
 x=v.co.x
 if abs(x)>9:v.co.x=(1 if x>0 else -1)*(9+(abs(x)-9)*(12.125-9)/(maximum-9))

for v in ob.data.vertices:v.co*=100
ob.data.update();ob.name='SM_Bogota_EstacionTransmi_Compacta';bpy.ops.export_scene.fbx(filepath=str(P/'SM_Bogota_EstacionTransmi_Compacta.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR');bpy.ops.wm.save_as_mainfile(filepath=str(P/'Estacion_Compacta.blend'));print('COMPACT_STATION_PRESERVES_DOORS_AT_380CM')
