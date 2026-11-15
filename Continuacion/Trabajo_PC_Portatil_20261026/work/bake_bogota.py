import unreal,json
from pathlib import Path
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
cls=unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity')
existing=[a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class()==cls]
city=existing[0] if existing else unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector(0,0,0))
city.set_actor_label('Bogota_Ciudad_Instanciada');city.call_method('BakeCity')
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(-9000,8500,6500),unreal.Rotator(-24,50,0))
unreal.EditorLevelLibrary.save_current_level();unreal.EditorAssetLibrary.save_directory('/Game',only_if_is_dirty=False,recursive=True)
Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/BogotaVoxel/Saved/city_bake.json').write_text(json.dumps({'static_instances':city.get_editor_property('static_voxel_count'),'saved_map':'/Game/Maps/Bogota'}))
unreal.log('BOGOTA_MAP_BAKED')
