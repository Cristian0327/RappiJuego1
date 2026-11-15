from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for filename in ['import_build_pure_taxi_rear_doors.py','fix_pure_road_active_doors.py','optimize_pure_hidden_animation_components.py','build_pure_road_interaction_qa.py','build_pure_integrated_world_qa.py']:
 exec(compile((r/'work'/filename).read_text(encoding='utf-8-sig'),filename,'exec'),{'__name__':'__main__'})
unreal.log('TAXI_ANIMATION_BUDGET_BATCH_READY')
