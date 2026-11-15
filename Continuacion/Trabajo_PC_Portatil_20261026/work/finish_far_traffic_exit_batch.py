from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for filename in ['fix_pure_far_traffic_collision.py','fix_pure_road_exit_upright.py','build_pure_far_traffic_qa.py','build_pure_integrated_world_qa.py']:
 exec(compile((r/'work'/filename).read_text(encoding='utf-8-sig'),filename,'exec'),{'__name__':'__main__'})
unreal.log('FAR_TRAFFIC_EXIT_BATCH_READY')
