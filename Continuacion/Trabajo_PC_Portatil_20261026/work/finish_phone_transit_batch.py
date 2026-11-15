from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['optimize_pure_phone_closed_refresh.py','build_pure_transit_passenger_visual.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})
unreal.log('PHONE_AND_TRANSIT_BATCH_PASS')
