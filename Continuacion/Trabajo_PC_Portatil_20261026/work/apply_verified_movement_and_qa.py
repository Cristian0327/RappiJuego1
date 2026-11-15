from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['fix_cyclist_bidirectional_avoidance.py','build_cyclist_obstacle_qa.py','build_performance60_qa.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{'__file__':str(r/'work'/name)})
unreal.log('MOVEMENT_AND_PERFORMANCE_QA_READY')
