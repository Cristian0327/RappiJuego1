import unreal,json,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Traffic'
report={}
try:
 cls=unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity')
 actor=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector(0,0,0))
 report['simulation']=json.loads(actor.validate_traffic(600))
 report['models']={}
 for name in ['TaxiCompact','TaxiSedan','Private','SITP','TransMilenio']:
  mesh=unreal.load_asset('/Game/Traffic/SK_'+name);c=unreal.new_object(unreal.PoseableMeshComponent);c.set_skeletal_mesh(mesh)
  names=[str(c.get_bone_name(i)) for i in range(c.get_num_bones())]
  locations={n:str(c.get_bone_location_by_name(n,unreal.BoneSpaces.COMPONENT_SPACE)) for n in names}
  report['models'][name]={'bones':names,'locations':locations}
  assert all('wheel_'+str(i)+'_'+s in names for i in range(3 if name=='TransMilenio' else 2) for s in ['L','R'])
 sim=report['simulation'];assert sim['missing_models']==0;assert sim['overlap_frames']==0,sim;assert sim['minimum_travel_cm']>60000,sim;assert sim['longest_stop_seconds']<65,sim
 report['status']='PASS'
 unreal.EditorLevelLibrary.destroy_actor(actor)
except Exception:report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
(OUT/'traffic_validation.json').write_text(json.dumps(report,indent=2));unreal.log('TRAFFIC_VALIDATED '+str(report))
