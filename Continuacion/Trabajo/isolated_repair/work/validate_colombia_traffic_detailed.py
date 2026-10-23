import unreal,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/TrafficDetailed';report={}
try:
 cls=unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity');city=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector())
 report['simulation']=json.loads(city.validate_traffic(600))
 report['g66']=json.loads(city.validate_g66());assert report['g66']['boundary_checks_pass'];assert report['g66']['cooldown_violations']==0;assert 500<report['g66']['appearances']<1000
 report['models']={}
 catalog=json.loads((OUT/'fleet20_catalog.json').read_text(encoding='utf-8'));names_to_check=[s['name'] for s in catalog]+['TaxiCompact','TaxiSedan','TransMilenio','TransMilenioG66']
 assert len(catalog)==20 and not any('Willys' in n for n in names_to_check)
 for name in names_to_check:
  mesh=unreal.load_asset('/Game/Traffic/Detailed/SK_'+name);assert mesh,name
  comp=unreal.new_object(unreal.PoseableMeshComponent);comp.set_skeletal_mesh(mesh)
  names=[str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
  axles=3 if name.startswith('TransMilenio') else 2
  expected=['wheel_'+str(i)+'_'+side for i in range(axles) for side in ['L','R']]
  assert all(n in names for n in expected),(name,names)
  report['models'][name]={'bones':names,'material_slots':len(mesh.get_editor_property('materials'))}
  assert report['models'][name]['material_slots']==1
  assert all(slot.material_interface is not None for slot in mesh.get_editor_property('materials')),('missing_saved_material',name)
 sim=report['simulation'];assert sim['private_model_variants']==20;assert sim['missing_models']==0;assert sim['invalid_rigs']==0,sim;assert sim['missing_vertex_colors']==0,sim;assert sim['overlap_frames']==0,sim;assert sim['minimum_travel_cm']>60000,sim;assert sim['longest_stop_seconds']<100,sim
 report['status']='PASS';unreal.EditorLevelLibrary.destroy_actor(city)
except Exception:report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
(OUT/'traffic_validation.json').write_text(json.dumps(report,indent=2));unreal.log('DETAILED_TRAFFIC_VALIDATED '+str(report))
