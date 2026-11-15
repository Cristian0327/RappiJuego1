import unreal,json,sys,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent;project=root/'RappiJuego1';sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
recovery=root/'Recuperacion_Migracion_Blueprints';recovery.mkdir(exist_ok=True)
for rel in ['Config/DefaultEngine.ini','Content/Maps/Bogota.umap','Content/Delivery/Core/BP_DeliveryGameMode.uasset']:
 p=project/rel;b=recovery/rel;b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():shutil.copy2(p,b)
# Inventory direct and inherited runtime bindings before changing any base class.
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
options=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
blueprints=[];references=[]
for data in registry.get_assets_by_path('/Game',recursive=True):
 deps=[str(p) for p in registry.get_dependencies(data.package_name,options) if str(p).startswith('/Script/BogotaVoxel')]
 if deps:references.append({'asset':str(data.package_name),'dependencies':deps})
 if str(data.asset_class_path.asset_name) in ['Blueprint','WidgetBlueprint','AnimBlueprint']:
  bp=data.get_asset();report=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));blueprints.append(report)
(root/'work/full_blueprint_dependencies.json').write_text(json.dumps({'status':'IN_PROGRESS','blueprints':blueprints,'direct_native_references':references},ensure_ascii=False,indent=2),encoding='utf-8')
# A GameMode based directly on the engine, with its world bootstrap in nodes.
path='/Game/Delivery/Core/BP_DeliveryGameMode'
bp=unreal.load_asset(path);assert bp
unreal.BlueprintEditorLibrary.reparent_blueprint(bp,unreal.GameModeBase)
cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('default_pawn_class',unreal.load_class(None,'/Game/Delivery/Vehicles/BP_DeliveryRider.BP_DeliveryRider_C'));cdo.set_editor_property('hud_class',unreal.BogotaHUD)
d.bp=bp;g=d.Graph();S='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary'
g.call('FindCity','GetActorOfClass',S,ActorClass='/Game/World/BP_BogotaCity.BP_BogotaCity_C');g.call('Valid','IsValid',K);g.link('FindCity','ReturnValue','Valid','Object');g.branch('HasCity','Valid');g.exec('entry','FindCity');g.exec('FindCity','HasCity');g.exec('HasCity','result','then')
g.call('Origin','MakeTransform',d.M,Scale='(X=1,Y=1,Z=1)');g.call('SpawnCity','BeginDeferredActorSpawnFromClass',S,ActorClass='/Game/World/BP_BogotaCity.BP_BogotaCity_C',SpawnTransform='(Rotation=(X=0,Y=0,Z=0,W=1),Translation=(X=0,Y=0,Z=0),Scale3D=(X=1,Y=1,Z=1))',CollisionHandlingOverride='AlwaysSpawn');g.exec('HasCity','SpawnCity','else');g.call('FinishCity','FinishSpawningActor',S,SpawnTransform='(Rotation=(X=0,Y=0,Z=0,W=1),Translation=(X=0,Y=0,Z=0),Scale3D=(X=1,Y=1,Z=1))');g.link('SpawnCity','ReturnValue','FinishCity','Actor');g.exec('SpawnCity','FinishCity');g.exec('FinishCity','result');g.link('Origin','ReturnValue','SpawnCity','SpawnTransform');g.link('Origin','ReturnValue','FinishCity','SpawnTransform');g.build('ReceiveBeginPlay')
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));(root/'work/gamemode_graph_debug.json').write_text(json.dumps(audit,indent=2));assert audit['parent']=='/Script/Engine.GameModeBase';assert any(g['name']=='ReceiveBeginPlay' and g['bytecode']>0 for g in audit['graphs']);assert not any(g['native_calls'] for g in audit['graphs'])
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();settings=world.get_world_settings();settings.set_editor_property('default_game_mode',bp.generated_class());unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
p=project/'Config/DefaultEngine.ini';s=p.read_text(encoding='utf-8-sig');s=s.replace('GlobalDefaultGameMode=/Script/BogotaVoxel.BogotaGameMode','GlobalDefaultGameMode=/Game/Delivery/Core/BP_DeliveryGameMode.BP_DeliveryGameMode_C');p.write_text(s,encoding='utf-8')
(project/'Docs/validacion_gamemode_blueprint.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
unreal.log('PURE_BLUEPRINT_GAMEMODE_PASS')
