from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['integrate_pure_world_core_bridge.py','migrate_city_metadata_blueprint.py','build_player_interaction_runtime_test.py']:
 p=r/'work'/n;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__name__':'__main__'})
