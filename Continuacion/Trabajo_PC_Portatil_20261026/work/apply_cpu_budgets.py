import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['optimize_traffic_clearance_fast_path.py','cache_environment_lighting.py','fix_live_moto_facing.py','build_service_distance_budget.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{'__file__':str(r/'work'/name)})
unreal.log('CPU_BUDGETS_READY')
