import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';SC='/Script/Engine.SceneComponent';SA='/Script/Engine.SpringArmComponent';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';COORD='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRiderAnimationCoordinator.BP_BlueprintRiderAnimationCoordinator_C'
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-19_camera_rollback_sprint'
for rel in ['Delivery/BlueprintGameplay/Player/BP_BlueprintRider.uasset','Delivery/Animation/ABP_DeliveryRiderRun.uasset','VoxelExplorer/AN_Run_Mixamo.uasset','Maps/Bogota_Blueprint_Integration.umap']:
 src=r/'RappiJuego1/Content'/rel;dst=backup/rel
 if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def save(bp):
 assert E.compile_blueprint(bp),bp.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Restore the original camera calculation. Keep the fixed pose update independent of camera appearance.
bp=unreal.load_asset(R.rsplit('.',1)[0]);d.bp=bp
s=(r/'work/migrate_player_drive_camera.py').read_text(encoding='utf-8-sig');s=s[s.index("g=Graph()\nfor v in ['CameraBoom'"):s.index("reports.append(g.build('UpdateCameraRig'))")];s=s.replace('g=Graph()','g=d.Graph()').replace('/Script/BogotaVoxel.DeliveryComponent',CORE)
s=s.replace("chain=['entry','SetArm'","chain=['RestoredVisibility','SetArm'").replace("'SetFOV','result'","'SetFOV'")
exec(compile(s,'OriginalCameraCalculation','exec'))
# Reset the changes to the boom, camera and view limits that were added in the previous task.
g.get('Mesh');last='entry'
for tag,var,value in [('OriginalTarget','TargetOffset','(X=0,Y=0,Z=0)'),('OriginalProbe','ProbeSize','12'),('OriginalCollision','bDoCollisionTest','true'),('OriginalRollInheritance','bInheritRoll','true')]:
 g.node(tag,'setfield',owner=SA,var=var,defaults={var:value});g.link('CameraBoom','CameraBoom',tag,'self');g.exec(last,tag);last=tag
g.call('Manager','GetPlayerCameraManager',G,PlayerIndex='0');manager=unreal.get_default_object(unreal.PlayerCameraManager)
for tag,var,prop in [('OriginalPitchMin','ViewPitchMin','view_pitch_min'),('OriginalPitchMax','ViewPitchMax','view_pitch_max'),('OriginalRollMin','ViewRollMin','view_roll_min'),('OriginalRollMax','ViewRollMax','view_roll_max')]:
 g.node(tag,'setfield',owner='/Script/Engine.PlayerCameraManager',var=var,defaults={var:str(manager.get_editor_property(prop))});g.link('Manager','ReturnValue',tag,'self');g.exec(last,tag);last=tag
g.call('RestoredVisibility','SetVisibility',SC,bNewVisibility='true',bPropagateToChildren='false');g.link('Mesh','Mesh','RestoredVisibility','self');g.exec(last,'RestoredVisibility')
g.call('Pose','GetActorOfClass',G,ActorClass=COORD);g.exec('SetFOV','Pose');g.node('PoseType','cast',type=COORD);g.link('Pose','ReturnValue','PoseType','Object');g.call('ValidPose','IsValid',K);g.link('Pose','ReturnValue','ValidPose','Object');g.branch('HavePose','ValidPose');g.exec('Pose','HavePose');g.exec('HavePose','result','else');g.call('UpdatePose','CorrectPose',COORD);g.link('PoseType','AsBP Blueprint Rider Animation Coordinator','UpdatePose','self');g.exec('HavePose','UpdatePose');g.exec('UpdatePose','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'UpdateCameraRig',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'Dt','category':'real'}]}))
# No added NPC camera blocker remains active after reverting the camera.
g=d.Graph();g.exec('entry','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'ConfigureNpcCamera',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[]}))
g=d.Graph();g.get('Sprint');g.call('Speed','SelectFloat',M,A='650',B='140');g.link('Sprint','Sprint','Speed','bPickA');g.link('Speed','ReturnValue','result','ReturnValue');g.exec('entry','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'WalkingSpeed',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'ReturnValue','category':'real','out':True}],'pure':True,'const':True}));save(bp)
# Reimport the verified Mixamo running clip explicitly, so this cannot use a walk asset by mistake.
anim=unreal.load_asset('/Game/VoxelExplorer/AN_Run_Mixamo');before_rate=anim.get_editor_property('rate_scale');o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=anim.get_editor_property('skeleton');o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True;t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/AnimationRebuild/Upright/AN_HeroRun_Rebuilt.fbx');t.destination_path='/Game/VoxelExplorer';t.destination_name='AN_Run_Mixamo';t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert t.imported_object_paths
anim=unreal.load_asset('/Game/VoxelExplorer/AN_Run_Mixamo');anim.set_editor_property('rate_scale',1.5);assert unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False)
bp=unreal.load_asset('/Game/Delivery/Animation/ABP_DeliveryRiderRun');s=(r/'work/migrate_rider_animation_pure_blueprint.py').read_text(encoding='utf-8-sig');s=s[s.index('d.bp=bp;g=d.Graph()'):];s=s.replace("('Speed','ReturnValue'),B='390'","('Speed','ReturnValue'),B='650'").replace("Min='.35',Max='1.65'","Min='.45',Max='1.15'");s=s.replace("op('PedalPosition','Multiply_DoubleDouble',('PedalFraction','ReturnValue'),('PedalLength','ReturnValue'))","op('ForwardPedalFraction','Subtract_DoubleDouble',None,('PedalFraction','ReturnValue'),A='1');op('PedalPosition','Multiply_DoubleDouble',('ForwardPedalFraction','ReturnValue'),('PedalLength','ReturnValue'))");exec(compile(s,'SprintSpeedMatchedRunPlayback','exec'))
# Remove only the helper actor introduced for the camera change; keep all other world actors.
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);removed=0
for actor in actors.get_all_level_actors():
 if actor.get_class().get_path_name()=='/Game/Delivery/BlueprintGameplay/Player/BP_CameraObstacleSetup.BP_CameraObstacleSetup_C':actors.destroy_actor(actor);removed+=1
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/Bogota_Blueprint_Integration')
(r/'work/camera_rollback_sprint_patch.json').write_text(json.dumps({'camera':'Original arm430/530/interior240, offset45/70, smoothing3, camera lag and FOV75/78; original pitch/roll limits; no added body hiding or NPC camera blocker','sprint_cm_s':650,'walk_cm_s':140,'mixamo_source':t.filename,'previous_asset_rate':before_rate,'run_asset_rate':1.5,'run_rate_reference':650,'removed_camera_helpers':removed},indent=2));unreal.log('CAMERA_RESTORED_AND_SPRINT650_PASS')
