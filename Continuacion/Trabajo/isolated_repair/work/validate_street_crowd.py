import unreal,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd';r={}
try:
 unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
 cls=unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity');city=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector())
 r=json.loads(city.validate_crowd(600));assert r['variants']==60 and r['pedestrians']==864 and r['missing_assets']==0 and r['invalid_positions']==0 and r['minimum_travel_cm']>2000,r
 assert r['crossings_completed']>0 and r['illegal_crossings']==0 and r['pedestrian_vehicle_overlap_frames']==0,r
 assert r['parked_cars']>0 and r['car_boardings']>0 and r['bus_boardings']>0 and r['bus_alightings']>0,r
 r['rigs']={}
 for i in range(60):
  mesh=unreal.load_asset('/Game/Crowd/People/SK_Citizen%02d'%i);comp=unreal.new_object(unreal.SkeletalMeshComponent);comp.set_skeletal_mesh_asset(mesh);assert comp.get_num_bones()==24
  r['rigs'][str(i)]=comp.get_num_bones()
 r['status']='PASS';unreal.EditorLevelLibrary.destroy_actor(city)
except Exception:r['status']='FAIL';r['error']=traceback.format_exc();unreal.log_error(r['error'])
(out/'validation.json').write_text(json.dumps(r,indent=2));unreal.log('CROWD_VALIDATION '+str(r))

