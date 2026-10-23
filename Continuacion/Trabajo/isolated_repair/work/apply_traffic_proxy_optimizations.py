import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['optimize_invisible_crowd_proxies.py','optimize_traffic_grid_queries.py','optimize_distant_wheel_poses.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{'__file__':str(r/'work'/name)})
unreal.log('TRAFFIC_PROXY_OPTIMIZATIONS_READY')
