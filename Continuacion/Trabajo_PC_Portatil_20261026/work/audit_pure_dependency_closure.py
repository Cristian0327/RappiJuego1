import unreal,json,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True);roots=['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager','/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle','/Game/World/BlueprintWorld/Traffic/BP_TrafficLane','/Game/World/BlueprintWorld/BP_WorldPresentation','/Game/Delivery/BlueprintGameplay/Vehicles/BPC_VehicleArt','/Game/Delivery/BlueprintGameplay/Vehicles/BP_DeliveryTwoWheeler','/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone','/Game/Delivery/BlueprintGameplay/UI/BP_BlueprintGaragePreview','/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore','/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore','/Game/Delivery/BlueprintGameplay/People/BP_DeliveryRecipient','/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/Delivery/BlueprintGameplay/World/BP_ResidentialRouteAssembler','/Game/World/BlueprintWorld/BP_CityGeometry','/Game/World/BlueprintWorld/BP_WorldState','/Game/Delivery/BlueprintSchema/BP_DeliveryProfile'];results=[]
for root in roots:
 queue=collections.deque([root]);parents={root:None};bad=[]
 while queue:
  at=queue.popleft()
  for dep in reg.get_dependencies(at,opts) or []:
   name=str(dep)
   if name in parents:continue
   parents[name]=at
   if name.startswith('/Script/BogotaVoxel'):
    path=[];v=name
    while v is not None:path.append(v);v=parents[v]
    bad.append(list(reversed(path)))
   elif name.startswith('/Game/'):queue.append(name)
 results.append({'root':root,'packages':len(parents),'native_paths':bad})
report={'status':'PASS' if not any(v['native_paths'] for v in results) else 'FAIL','roots':results,'main_migration_still_incomplete':True};(r/'work/pure_transitive_dependency_validation.json').write_text(json.dumps(report,indent=2));assert report['status']=='PASS',report;unreal.log('PURE_TRANSITIVE_DEPENDENCY_PASS roots='+str(len(roots)))

