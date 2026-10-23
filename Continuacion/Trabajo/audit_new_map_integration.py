import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');out={}
city=next(a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_CityGeometry_C');city.call_method('ReceiveBeginPlay')
out['geometry']=[{'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'count':c.get_instance_count()} for c in city.get_components_by_class(unreal.InstancedStaticMeshComponent)]
for key,path in [('store','/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore'),('assembler','/Game/Delivery/BlueprintGameplay/World/BP_ResidentialRouteAssembler'),('core','/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore'),('station','/Game/Traffic/Transit/BP_StationPassenger'),('police','/Game/Traffic/Services/BP_PoliceRoadPatrol')]:
 b=unreal.load_asset(path);c=unreal.get_default_object(b.generated_class());vals={}
 for n in E.list_member_variable_names(b):
  try:v=c.get_editor_property(str(n));vals[str(n)]=str(v)[:250]
  except:pass
 out[key]=vals
out['vehicles']=[];ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for row in json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']+[{'asset':'/Game/Traffic/Services/BP_PoliceRoadPatrol'}]:
 b=unreal.load_asset(row['asset']);parts=[]
 for h in ss.k2_gather_subobject_data_for_blueprint(b):
  o=lib.get_object_for_blueprint(lib.get_data(h),b)
  if isinstance(o,unreal.SkeletalMeshComponent):
   mesh=o.get_editor_property('skeletal_mesh_asset');parts.append({'name':str(lib.get_variable_name(lib.get_data(h))),'mesh':mesh.get_path_name() if mesh else None,'materials':[m.get_path_name() if m else None for m in o.get_materials()],'mesh_materials':[m.material_interface.get_path_name() if m.material_interface else None for m in mesh.materials] if mesh else [],'scale':str(o.get_editor_property('relative_scale3d'))})
 out['vehicles'].append({'asset':row['asset'],'parts':parts})
(r/'outputs/MapRebuild/integration_audit.json').write_text(json.dumps(out,indent=2));unreal.log('NEW_MAP_INTEGRATION_AUDIT_READY')

