import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
city=next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a,unreal.BogotaCity));city.build_map_metadata()
feet=[]
for f in city.get_editor_property('map_footprints'):
 p=f.get_editor_property('center');e=f.get_editor_property('extent');feet.append([p.x,p.y,e.x,e.y])
(root/'work/city_building_footprints.json').write_text(json.dumps(feet))
unreal.log('COMMERCIAL_PLOTS_EXPORTED '+str(len(feet)))
