import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['test_pure_traffic_junction_lookup.py','test_optimized_traffic_grid.py','build_shared_hero_walk_qa.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
unreal.log('CACHED_JUNCTION_AND_SHARED_WALK_BUILD_READY')
