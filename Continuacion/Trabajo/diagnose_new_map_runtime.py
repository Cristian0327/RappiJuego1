import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out={};bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager');audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));out['crowd_graphs']=[g for g in audit['graphs'] if g['name'] in ['SpawnModel','ConfigureCityRoute','CreateCrowd']];ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;out['cars']=[];(r/'outputs/MapRebuild/runtime_diagnostics.json').write_text(json.dumps(out,indent=2))
for row in json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']:
 b=unreal.load_asset(row['asset']);parts=[]
 for h in ss.k2_gather_subobject_data_for_blueprint(b):
  o=lib.get_object_for_blueprint(lib.get_data(h),b)
  if isinstance(o,unreal.SkinnedMeshComponent):
   mesh=o.get_skinned_asset();parts.append({'name':o.get_name(),'mesh':mesh.get_path_name() if mesh else None,'materials':[m.get_path_name() if m else None for m in o.get_materials()]})
 out['cars'].append({'asset':row['asset'],'parts':parts})
c=unreal.get_default_object(unreal.load_class(None,'/Game/Traffic/Services/BP_PoliceRoadPatrol.BP_PoliceRoadPatrol_C'));out['police_defaults']={n:str(c.get_editor_property(n)) for n in ['DriveModel','DriveMaterial','GroundOffset','RiderModel']};mesh=unreal.load_asset('/Game/Traffic/Services/SK_PolicePatrol');out['police_materials']=[m.material_interface.get_path_name() if m.material_interface else None for m in mesh.materials]
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);city=next(a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_CityGeometry_C');city.call_method('ReceiveBeginPlay');pieces=[]
for comp in city.get_components_by_class(unreal.InstancedStaticMeshComponent):
 for i in range(comp.get_instance_count()):
  t=comp.get_instance_transform(i,world_space=True);p=t.translation;s=t.scale3d
  if abs(p.x+27000)<2100 and abs(p.y)<280 and abs(s.x)*50<2200 and abs(s.y)*50<300 and p.z+abs(s.z)*50>70 and p.z-abs(s.z)*50>=25:
   pieces.append({'location':[p.x+27000,p.y,p.z-90],'scale':[s.x,s.y,s.z],'yaw':t.rotation.rotator().yaw,'mesh':comp.static_mesh.get_path_name(),'material':comp.get_material(0).get_path_name(),'component':comp.get_name()})
out['station_template']=pieces;(r/'outputs/MapRebuild/runtime_diagnostics.json').write_text(json.dumps(out,indent=2));unreal.log('MAP_DIAGNOSTICS_READY '+str(len(pieces)))
