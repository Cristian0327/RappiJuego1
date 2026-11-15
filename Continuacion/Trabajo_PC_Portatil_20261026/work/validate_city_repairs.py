import unreal,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
city=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity'),unreal.Vector())
start=time.monotonic()
r=json.loads(city.validate_crowd(600))
r['validation_wall_seconds']=round(time.monotonic()-start,2)
r['status']='PASS' if r['pedestrians']==864 and r['variants']==60 and r['stalled_walkers']==0 and r['minimum_travel_cm']>2000 and r['illegal_crossings']==0 and r['pedestrian_vehicle_overlap_frames']==0 and r['car_boardings']>0 and r['bus_boardings']>0 and r['bus_alightings']>0 else 'FAIL'
(root/'work/city_repairs_validation.json').write_text(json.dumps(r,indent=2))
unreal.log('CITY_REPAIRS_VALIDATION '+str(r))
unreal.EditorLevelLibrary.destroy_actor(city)
