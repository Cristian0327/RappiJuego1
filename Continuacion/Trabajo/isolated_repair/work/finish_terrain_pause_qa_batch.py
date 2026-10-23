from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for filename in ['build_pure_terrain_qa.py','build_pure_pause_qa.py','build_pure_station_passenger.py']:
 exec(compile((r/'work'/filename).read_text(encoding='utf-8-sig'),filename,'exec'),{'__name__':'__main__'})
unreal.log('TERRAIN_PAUSE_RECOVERY_BATCH_READY')
