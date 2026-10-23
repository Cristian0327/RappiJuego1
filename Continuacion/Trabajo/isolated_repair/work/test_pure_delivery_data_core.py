import unreal,json,itertools,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore');c=unreal.get_default_object(bp.generated_class());schema=json.loads((r/'work/blueprint_gameplay_schema.json').read_text());fields={v['source'].split('.')[-1]:{p['friendly_name']:p['property_name'] for p in v['fields']} for v in schema['structs']};checks=[]
def ck(name,actual,expected):
 assert actual==expected,(name,actual,expected);checks.append(name)
def call(fn,*args):return c.call_method(fn,args=args)
ck('Owns_missing',call('Owns',unreal.Name('Motorcycle')),False);ck('StarterBike',call('OwnsVehicle',unreal.Name('BikeCity')),True);ck('LockedStarterMoto',call('OwnsVehicle',unreal.Name('MotoStreet')),False)
for moto,bpurchased,expected in [(False,[],1),(False,['CargoBackpack'],2),(False,['CargoWaist'],2),(False,['CargoPanniers'],1),(True,['CargoPanniers'],3),(True,['CargoBackpack','CargoWaist','CargoPanniers'],5),(False,['CargoBackpack','CargoWaist','CargoPanniers'],3)]:
 c.set_editor_property('Purchased',[unreal.Name(x) for x in bpurchased]);ck('Cargo_'+str(moto)+'_'+','.join(bpurchased),call('CargoCapacity',moto),expected)
for moto,ids in [(False,['BikePedals','BikeFrame','BikeGears','BikeMotor']),(True,['MotoTurbo','MotoAero','MotoDisplacement','MotoInjection','MotoSportEngine'])]:
 for stage in range(len(ids)+1):
  c.set_editor_property('Purchased',[unreal.Name(x) for x in ids[:stage]]);ck('VisualStage_'+str(moto)+'_'+str(stage),call('VisualStage',moto),stage)
for vehicle,boost,expected in [(0,False,1100),(0,True,1450),(1,False,1450),(1,True,2200)]:
 c.set_editor_property('Vehicle',vehicle);c.set_editor_property('BoostActive',boost);ck('Speed_'+str(vehicle)+'_'+str(boost),call('GetTopSpeed'),expected)
c.set_editor_property('Purchased',[unreal.Name('Motorcycle')]);ck('MotoUnlocked',call('OwnsVehicle',unreal.Name('MotoStreet')),True);c.set_editor_property('OwnedModels',[unreal.Name('MotoSport')]);ck('ModelOwned',call('OwnsVehicle',unreal.Name('MotoSport')),True);ck('ModelMissing',call('OwnsVehicle',unreal.Name('NoModel')),False)
c.set_editor_property('ModelColors',{unreal.Name('Low'):-9,unreal.Name('High'):9,unreal.Name('Exact'):4})
for model,expected in [('Low',0),('High',5),('Exact',4),('Missing',0)]:ck('Paint_'+model,call('GetModelColor',unreal.Name(model)),expected)
for validation,slot in [(False,'VoxelDelivery_Blueprint_Profile_v2'),(True,'VoxelDelivery_Blueprint_Automation_v2')]:c.set_editor_property('bValidation',validation);ck('Slot_'+str(validation),call('ProfileSlot'),slot)
c.set_editor_property('bHolding',True);c.set_editor_property('HoldProgress',.82);call('EndAction');ck('HoldReleased',c.get_editor_property('bHolding'),False);ck('HoldProgressReset',c.get_editor_property('HoldProgress'),0.)
# Every upgrade/vehicle field can be read through its remapped Blueprint signature.
for table,fn,struct in [('DT_Upgrades','GetUpgradeSpec','DeliveryUpgrade'),('DT_Vehicles','GetVehicleSpec','DeliveryVehicleSpec')]:
 rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/Delivery/BlueprintSchema/Tables/'+table)))
 for row in rows:
  value,found=call(fn,unreal.Name(row['Name']));ck(table+'_'+row['Name']+'_found',found,True)
  for friendly in ['Price','ModelIndex','Motorcycle','Magnitude','SortIndex','Prerequisite']:
   if friendly not in row:continue
   actual=value.get_editor_property(fields[struct][friendly]);expected=row[friendly]
   if isinstance(actual,unreal.Name):actual=str(actual)
   if isinstance(expected,float):ck(table+'_'+row['Name']+'_'+friendly,math.isclose(actual,expected,abs_tol=.000001),True)
   else:ck(table+'_'+row['Name']+'_'+friendly,actual,expected)
# Mutating and querying user-defined order records exercises nested struct and array pin remapping.
order,found=call('GetSelectedOffer');ck('EmptySelection',found,False);f=fields['DeliveryOrder'];id=unreal.GuidLibrary.new_guid();order.set_editor_property(f['ID'],id);order.set_editor_property(f['Reward'],15800);order.set_editor_property(f['Pickup'],unreal.Vector(100,200,5));order.set_editor_property(f['Dropoff'],unreal.Vector(1000,2000,5));c.set_editor_property('Offers',[order]);c.set_editor_property('SelectedOffer',id)
selected,found=call('GetSelectedOffer');ck('SelectedStruct',found,True);ck('SelectedReward',selected.get_editor_property(f['Reward']),15800);lookup,index=call('FindOffer',id);ck('OfferIndex',index,0);ck('LookupID',unreal.GuidLibrary.equal_equal_guid_guid(lookup.get_editor_property(f['ID']),id),True);missing,index=call('FindOffer',unreal.GuidLibrary.new_guid());ck('MissingOffer',index,-1);ck('ActiveEmpty',call('FindActiveOrderIndex',id),-1);ck('DuplicateRoute',call('RouteAlreadyOffered',unreal.Vector(100,200,5),unreal.Vector(1000,2000,5)),True);ck('UniqueRoute',call('RouteAlreadyOffered',unreal.Vector(300,200,5),unreal.Vector(1000,2000,5)),False)
reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);deps=[str(x) for x in reg.get_dependencies('/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore',unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)) or []];assert not any(x.startswith('/Script/BogotaVoxel') for x in deps),deps
(r/'work/pure_delivery_data_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'native_dependencies':[],'staging_not_promoted':True},indent=2));unreal.log('PURE_DELIVERY_DATA_CORE_VM_PASS checks='+str(len(checks)))
