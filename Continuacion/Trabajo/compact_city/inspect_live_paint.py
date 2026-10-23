import unreal,json
from pathlib import Path
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');spec=json.loads((Path(unreal.Paths.project_dir()).parent/'work/pure_traffic_vehicle_foundation.json').read_text())['models'];out=[]
for i,row in enumerate(spec[:4]):
 car=A.spawn_actor_from_class(unreal.load_asset(row['asset']).generated_class(),unreal.Vector(100000+i*2000,100000,20));car.call_method('ApplyPaintIndex',(i+2,));mat=car.get_editor_property('BodyMaterial');co=mat.call_method('K2_GetVectorParameterValue',(unreal.Name('BodyPaint'),));en=mat.call_method('K2_GetScalarParameterValue',(unreal.Name('PaintEnabled'),));out.append(dict(model=row['asset'],parent=mat.get_editor_property('parent').get_path_name(),color=[co.r,co.g,co.b],enabled=en,bodymaterial=str(car.get_editor_property('Body').get_material(0))))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/compact_city/live_paint_parameters.json').write_text(json.dumps(out,indent=2));print('LIVE_PAINT_PARAMETERS_READY')
