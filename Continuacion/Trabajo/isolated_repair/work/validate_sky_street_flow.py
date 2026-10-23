import unreal,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/Revision_Cielo_Transito';out.mkdir(exist_ok=True)
report={}
try:
 exec(compile((root/'work/build_complete_sky.py').read_text(encoding='utf-8-sig'),'build_complete_sky.py','exec'))
 unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
 city=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity'),unreal.Vector())
 report['local_avoidance']=json.loads(city.validate_street_flow());unreal.log('STREET_FLOW '+str(report['local_avoidance']))
 report['crowd']=json.loads(city.validate_crowd(600));unreal.log('NEW_CROWD '+str(report['crowd']))
 # Recreate to measure traffic from its initial spawn, before the crowd long run.
 unreal.EditorLevelLibrary.destroy_actor(city)
 city=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity'),unreal.Vector())
 report['traffic']=json.loads(city.validate_traffic(600));unreal.log('NEW_TRAFFIC '+str(report['traffic']))
 report['status']='PASS' if report['local_avoidance']['failures']==0 and report['crowd']['stalled_walkers']==0 and report['crowd']['illegal_crossings']==0 and report['crowd']['pedestrian_vehicle_overlap_frames']==0 and report['traffic']['vehicles']==100 and report['traffic']['overlap_frames']==0 and report['traffic']['minimum_travel_cm']>30000 else 'FAIL'
 unreal.EditorLevelLibrary.destroy_actor(city)
except Exception:
 report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
(out/'validacion.json').write_text(json.dumps(report,indent=2),encoding='utf-8');unreal.log('SKY_STREET_REPORT '+str(report))
