import unreal
from pathlib import Path
root=Path(__file__).resolve().parents[1];o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=unreal.load_asset('/Game/Crowd/SKEL_Crowd');o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False
o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
t=unreal.AssetImportTask();t.filename=str(root/'outputs/DeliveryArt/Crowd/AN_CrowdCane.fbx');t.destination_path='/Game/Crowd';t.destination_name='AN_CrowdCane';t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert unreal.load_asset('/Game/Crowd/AN_CrowdCane')
