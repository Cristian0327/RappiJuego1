import unreal,json,hashlib
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;src=r/'RappiJuego1/Saved/SaveGames/VoxelDelivery_Profile_v1.sav';before=hashlib.sha256(src.read_bytes()).hexdigest();slot='VoxelDelivery_Blueprint_Profile_v2';report={'legacy_slot':'VoxelDelivery_Profile_v1','blueprint_slot':slot,'legacy_hash':before,'status':'PENDING'}
if unreal.GameplayStatics.does_save_game_exist(slot,0):
 report['status']='EXISTING_V2_PRESERVED'
else:
 old=unreal.GameplayStatics.load_game_from_slot('VoxelDelivery_Profile_v1',0);assert old;new=unreal.GameplayStatics.create_save_game_object(unreal.load_class(None,'/Game/Delivery/BlueprintSchema/BP_DeliveryProfile.BP_DeliveryProfile_C'));assert new
 for name in ['Balance','Purchased','BikeColor','MotoColor','OwnedModels','BikeModel','MotoModel','ModelColors']:
  new.set_editor_property(name,old.get_editor_property(name))
 vehicle=old.get_editor_property('Vehicle');new.set_editor_property('Vehicle',int(getattr(vehicle,'value',vehicle)));new.set_editor_property('Version',2);assert unreal.GameplayStatics.save_game_to_slot(new,slot,0);loaded=unreal.GameplayStatics.load_game_from_slot(slot,0);assert loaded and loaded.get_class().get_path_name()=='/Game/Delivery/BlueprintSchema/BP_DeliveryProfile.BP_DeliveryProfile_C'
 for name in ['Balance','Purchased','BikeColor','MotoColor','OwnedModels','BikeModel','MotoModel','ModelColors']:assert loaded.get_editor_property(name)==old.get_editor_property(name),name
 report.update(status='PASS',balance=loaded.get_editor_property('Balance'),purchased_count=len(loaded.get_editor_property('Purchased')),owned_models_count=len(loaded.get_editor_property('OwnedModels')),vehicle=loaded.get_editor_property('Vehicle'),version=loaded.get_editor_property('Version'))
assert hashlib.sha256(src.read_bytes()).hexdigest()==before;target=r/'RappiJuego1/Saved/SaveGames'/str(slot+'.sav');report['v2_hash']=hashlib.sha256(target.read_bytes()).hexdigest();(r/'work/blueprint_profile_conversion.json').write_text(json.dumps(report,indent=2));unreal.log('BLUEPRINT_PROFILE_CONVERSION '+report['status'])
