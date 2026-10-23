import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=d.M;A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C'
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-19_bicycle_pedals_patrol'
for rel in ['Delivery/BlueprintGameplay/Player/BP_BlueprintRider.uasset','Delivery/Animation/ABP_DeliveryRider.uasset','VoxelExplorer/AN_Walk_InPlace.uasset','Traffic/Services/BP_TwoWheelerCitizen.uasset','Traffic/Services/SK_PolicePatrol.uasset','Maps/Bogota_Blueprint_Integration.umap']:
 src=r/'RappiJuego1/Content'/rel;dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if src.exists() and not dst.exists():shutil.copy2(src,dst)
# Normalize the hero's WALK cadence to the NPC walk; keep sprint distinct in speed.
hero=unreal.load_asset('/Game/VoxelExplorer/AN_Walk_InPlace');npc=unreal.load_asset('/Game/Crowd/AN_CrowdWalk_Mixamo');hero.set_editor_property('rate_scale',npc.get_editor_property('rate_scale'));assert unreal.EditorAssetLibrary.save_loaded_asset(hero,only_if_is_dirty=False)
bp=unreal.load_asset('/Game/Delivery/Animation/ABP_DeliveryRider')
s=(r/'work/migrate_rider_animation_pure_blueprint.py').read_text(encoding='utf-8-sig');s=s[s.index('d.bp=bp;g=d.Graph()'):]
s=s.replace("B='390'","B='140'").replace("Max='1.65'","Max='3'")
s=s.replace("op('PedalPosition','Multiply_DoubleDouble',('PedalFraction','ReturnValue'),('PedalLength','ReturnValue'))", "op('ForwardPedalFraction','Subtract_DoubleDouble',None,('PedalFraction','ReturnValue'),A='1');op('PedalPosition','Multiply_DoubleDouble',('ForwardPedalFraction','ReturnValue'),('PedalLength','ReturnValue'))")
exec(compile(s,'HeroSharedWalkAndForwardPedals','exec'))
R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C'
# Preserve the verified AnimGraph, using the NPC-equivalent hero walk and all existing other clips.
clips=[unreal.load_asset('/Game/VoxelExplorer/'+n) for n in ['AN_Idle','AN_Walk_InPlace','AN_BikePedal','AN_MotoRide','AN_MixamoJump']]
assert unreal.DeliveryEditorLibrary.build_locomotion_blueprint(hero.get_editor_property('skeleton'),*clips)
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
bp=unreal.load_asset(R.rsplit('.',1)[0]);d.bp=bp;g=d.Graph();g.get('Sprint');g.call('Speed','SelectFloat',M,A='390',B='140');g.link('Sprint','Sprint','Speed','bPickA');g.link('Speed','ReturnValue','result','ReturnValue');g.exec('entry','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'WalkingSpeed',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'ReturnValue','category':'real','out':True}],'pure':True,'const':True}));assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Rebuild the CURRENT cyclist avoidance graph and change only pedal/crank direction.
s=(r/'work/fix_cyclist_bidirectional_avoidance.py').read_text(encoding='utf-8-sig')
needle="g.build('ReceiveTick');assert E.compile_blueprint(bp)"
insert="""g.call('ForwardPedalLoop','Subtract_DoubleDouble',M,A='1');g.link('PedalLoop','ReturnValue','ForwardPedalLoop','B');g.call('ForwardCrankDegrees','Multiply_DoubleDouble',M,B='-1');g.link('CrankDegrees','ReturnValue','ForwardCrankDegrees','A')
for link in g.links:
 if link==['PedalLoop','ReturnValue','PedalPosition','A']:link[0]='ForwardPedalLoop'
 if link==['CrankDegrees','ReturnValue','CrankRotation','Pitch']:link[0]='ForwardCrankDegrees'
g.build('ReceiveTick');assert E.compile_blueprint(bp)"""
assert needle in s;s=s.replace(needle,insert);exec(compile(s,'CyclistForwardPedalsPreserveAvoidance','exec'))
# Patrols use their existing opaque pixel material for glass; no translucent windows.
mesh=unreal.load_asset('/Game/Traffic/Services/SK_PolicePatrol');mat=unreal.load_asset('/Game/Traffic/Services/M_ServiceVoxel');slots=mesh.get_editor_property('materials');glass=0
for i,slot in enumerate(slots):
 if 'Window' in str(slot.material_slot_name):slot.material_interface=mat;slots[i]=slot;glass+=1
assert glass>0;mesh.set_editor_property('materials',slots);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
# Remove seated patrol officers from all saved variants and map instances; retain street officers.
changed=[]
def remove_driver(obj):
 try:model=obj.get_editor_property('DriveModel')
 except Exception:return False
 if model and 'PolicePatrol' in model.get_name():
  obj.set_editor_property('RiderModel',None);return True
 return False
for path in unreal.EditorAssetLibrary.list_assets('/Game/Traffic/Services',recursive=True,include_folder=False):
 if path.rsplit('/',1)[-1].startswith('BP_'):
  asset=unreal.load_asset(path)
  if asset and hasattr(asset,'generated_class') and asset.generated_class() and remove_driver(unreal.get_default_object(asset.generated_class())):
   assert E.compile_blueprint(asset);assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False);changed.append(path)
R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';M=d.M;A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary'
# Starter bicycle: wait for the player and profile, request a real interactable parked bike, then destroy this one-shot actor.
folder='/Game/Delivery/BlueprintGameplay/Vehicles';name='BP_StarterBicycle';bp=unreal.load_asset(folder+'/'+name)
if not bp:
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=T.create_asset(name,folder,unreal.Blueprint,f)
d.bp=bp;g=d.Graph();g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Player','ReturnValue','Rider','Object');g.call('Valid','IsValid',K);g.link('Rider','AsBP Blueprint Rider','Valid','Object');g.branch('HavePlayer','Valid');g.exec('entry','HavePlayer');g.exec('HavePlayer','result','else');g.node('Ready','getfield',owner=R,var='BlueprintReady');g.link('Rider','AsBP Blueprint Rider','Ready','self');g.branch('Bootstrapped','Ready','BlueprintReady');g.exec('HavePlayer','Bootstrapped');g.exec('Bootstrapped','result','else');g.node('Parked','getfield',owner=R,var='ParkedVehicle');g.link('Rider','AsBP Blueprint Rider','Parked','self');g.call('AlreadyPlaced','IsValid',K);g.link('Parked','ParkedVehicle','AlreadyPlaced','Object');g.node('Riding','getfield',owner=R,var='Riding');g.link('Rider','AsBP Blueprint Rider','Riding','self');g.call('AlreadyInUse','BooleanOR',M);g.link('AlreadyPlaced','ReturnValue','AlreadyInUse','A');g.link('Riding','Riding','AlreadyInUse','B');g.branch('Exists','AlreadyInUse');g.exec('Bootstrapped','Exists');g.call('Done','K2_DestroyActor',A);g.exec('Exists','Done');g.exec('Done','result');g.node('Core','getfield',owner=R,var='Delivery');g.link('Rider','AsBP Blueprint Rider','Core','self');g.node('ChooseBicycle','setfield',owner=CORE,var='Vehicle',defaults={'Vehicle':'0'});g.link('Core','Delivery','ChooseBicycle','self');g.exec('Exists','ChooseBicycle','else');g.call('Place','RequestDeliveryVehicle',R);g.link('Rider','AsBP Blueprint Rider','Place','self');g.exec('ChooseBicycle','Place');g.exec('Place','result');g.build('ReceiveTick');assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());tick=c.get_editor_property('primary_actor_tick');tick.set_editor_property('tick_interval',.25);c.set_editor_property('primary_actor_tick',tick);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);map_changes={}
for path in ['/Game/Maps/Bogota_Blueprint_Integration','/Game/QA/PureIntegratedWorld']:
 assert unreal.EditorLoadingAndSavingUtils.load_map(path);count=0
 for a in actors.get_all_level_actors():
  if remove_driver(a):count+=1
  if a.get_class().get_path_name()==bp.generated_class().get_path_name():actors.destroy_actor(a)
 actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Startup_Bicycle');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,path);map_changes[path]=count
(r/'work/bicycle_walk_patrol_patch.json').write_text(json.dumps({'status':'COMPILED_PENDING_RUNTIME','walk_speed':140,'sprint_speed':390,'hero_walk_rate_matches_npc':True,'hero_pedal_time_reversed':True,'npc_pedal_time_and_crank_reversed':True,'patrol_driver_classes_removed':changed,'map_patrols_removed':map_changes,'opaque_glass_slots':glass,'starter_bicycle_blueprint':bp.get_path_name()},indent=2));unreal.log('BICYCLE_WALK_PATROL_PATCH_COMPILED')

