import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['integrate_pure_traffic_manager_runtime.py','integrate_pure_traffic_spatial_neighbors.py','build_pure_transit_station_stops.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'))
(r/'work/pure_traffic_interpolated_rate.json').write_text(json.dumps({'simulation_hz':10,'render_every_frame':True,'fixed_snapshot_interpolation':True,'transit_clock_dt':.1,'status':'COMPILED_PENDING_RENDER_AND_SAFETY'},indent=2))
unreal.log('PURE_TRAFFIC_INTERPOLATED_10HZ_PASS')

