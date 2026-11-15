from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['fix_cyclist_bidirectional_avoidance.py','fix_live_moto_facing.py','optimize_live_visibility.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{'__file__':str(r/'work'/name)})
unreal.log('MOTO_CYCLIST_PERFORMANCE_BATCH_READY')
