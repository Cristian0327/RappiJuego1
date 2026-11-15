import unreal
from pathlib import Path
root=Path(__file__).resolve().parents[1];skeleton=unreal.load_asset('/Game/Crowd/SKEL_Crowd');assert skeleton
for source,name in [('AN_CrowdWalk','AN_CrowdWalk_Mixamo'),('AN_CrowdCane','AN_CrowdCane'),('AN_CrowdIdle','AN_CrowdIdle'),('AN_CrowdEnterCar','AN_CrowdEnterCar'),('AN_CrowdBoard','AN_CrowdBoard')]:
 o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=skeleton;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
 t=unreal.AssetImportTask();t.filename=str(root/'outputs/DeliveryArt/Crowd'/(source+'.fbx'));t.destination_path='/Game/Crowd';t.destination_name=name;t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert unreal.load_asset('/Game/Crowd/'+name).get_editor_property('skeleton')==skeleton

