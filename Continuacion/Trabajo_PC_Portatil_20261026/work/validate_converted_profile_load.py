import unreal,json,hashlib
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;source=r/'RappiJuego1/Saved/SaveGames/VoxelDelivery_Profile_v1.sav';before=hashlib.sha256(source.read_bytes()).hexdigest();saved=unreal.GameplayStatics.load_game_from_slot('VoxelDelivery_Blueprint_Profile_v2',0);assert saved;bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore');core=unreal.get_default_object(bp.generated_class());core.set_editor_property('bValidation',False);core.call_method('LoadProfile');checks=[]
for field in ['Balance','BikeColor','MotoColor','BikeModel','MotoModel','Vehicle']:
 assert core.get_editor_property(field)==saved.get_editor_property(field),field;checks.append(field)
for field in ['Purchased','OwnedModels']:
 assert {str(x) for x in core.get_editor_property(field)}=={str(x) for x in saved.get_editor_property(field)},field;checks.append(field)
assert dict(core.get_editor_property('ModelColors'))==dict(saved.get_editor_property('ModelColors'));checks.append('ModelColors');assert hashlib.sha256(source.read_bytes()).hexdigest()==before;checks.append('LegacyFileUnchanged');(r/'work/converted_profile_core_load_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'legacy_file_unchanged':True,'no_blueprint_assets_saved':True},indent=2));unreal.log('CONVERTED_PROFILE_CORE_LOAD_PASS checks='+str(len(checks)))
