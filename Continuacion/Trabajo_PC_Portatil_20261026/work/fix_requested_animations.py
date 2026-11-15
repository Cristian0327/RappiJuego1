import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;SC='/Script/Engine.SceneComponent';SK='/Script/Engine.SkeletalMeshComponent';A='/Script/Engine.Actor';K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';ABP='/Game/Delivery/Animation/ABP_DeliveryRider.ABP_DeliveryRider_C';RUN='/Game/Delivery/Animation/ABP_DeliveryRiderRun.ABP_DeliveryRiderRun_C'
def save(bp):
 assert E.compile_blueprint(bp),bp.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Import only four validated Blender clips, never overwrite the corrected pedal sampler or unrelated clips.
s=(r/'work/import_mount_animations.py').read_text(encoding='utf-8-sig');a=s.index('entries +=');b=s.index('for name,folder,skeleton in entries:',a);s=s[:a]+s[b:];exec(compile(s,'FourValidatedMountImports','exec'),{})
# Shorten entering/exiting to .68 seconds; preserve ground exit validation.
ns={};s=(r/'work/build_pure_rider_transition_foundation.py').read_text(encoding='utf-8-sig');s=s.replace("'TransitionDuration',1.15","'TransitionDuration',.68")
# Account for the animation's 55cm lateral start offset exactly once.
needle="g.setter('SaveOldLocation','TransitionOldLocation','OldLocation')"
insert="""g.call('MountFacing','ComposeRotators',M,A='(Pitch=0,Yaw=-90,Roll=0)');g.link('entry','RootRotation','MountFacing','B');g.call('MountSide','GetForwardVector',M);g.link('MountFacing','ReturnValue','MountSide','InRot');g.call('StartOffset','Multiply_VectorFloat',M,B='-55');g.link('MountSide','ReturnValue','StartOffset','A');g.call('EntryAnchor','Subtract_VectorVector',M);g.link('OldLocation','ReturnValue','EntryAnchor','A');g.link('StartOffset','ReturnValue','EntryAnchor','B');g.call('OldAnchor','SelectVector',M);g.link('OldLocation','ReturnValue','OldAnchor','A');g.link('EntryAnchor','ReturnValue','OldAnchor','B');g.link('entry','Reverse','OldAnchor','bPickA');g.setter('SaveOldLocation','TransitionOldLocation','OldAnchor')"""
assert needle in s;s=s.replace(needle,insert)
needle="g.setter('SaveGoalLocation','TransitionGoalLocation','GoalLocation')"
insert="""g.call('ExitAnchor','Subtract_VectorVector',M);g.link('GoalLocation','ReturnValue','ExitAnchor','A');g.link('StartOffset','ReturnValue','ExitAnchor','B');g.call('GoalAnchor','SelectVector',M);g.link('ExitAnchor','ReturnValue','GoalAnchor','A');g.link('GoalLocation','ReturnValue','GoalAnchor','B');g.link('entry','Reverse','GoalAnchor','bPickA');g.setter('SaveGoalLocation','TransitionGoalLocation','GoalAnchor')"""
s=s.replace(needle,insert);exec(compile(s,'MountAnchors','exec'),ns)
# Preserve forward/backward clip sampling; entering approaches early, exiting steps away at the end.
s=(r/'work/extend_pure_rider_transition_update.py').read_text(encoding='utf-8-sig')
needle="g.link('Progress','ReturnValue','Location','Alpha')"
insert="""g.call('ApproachRatio','Divide_DoubleDouble',M,B='.3');g.link('Progress','ReturnValue','ApproachRatio','A');g.call('Approach','FClamp',M,Min='0',Max='1');g.link('ApproachRatio','ReturnValue','Approach','Value');g.call('ExitDelay','Subtract_DoubleDouble',M,B='.65');g.link('Progress','ReturnValue','ExitDelay','A');g.call('ExitRatio','Divide_DoubleDouble',M,B='.35');g.link('ExitDelay','ReturnValue','ExitRatio','A');g.call('ExitBlend','FClamp',M,Min='0',Max='1');g.link('ExitRatio','ReturnValue','ExitBlend','Value');g.call('AnchorBlend','SelectFloat',M);g.link('Exiting','ReturnValue','AnchorBlend','bPickA');g.link('ExitBlend','ReturnValue','AnchorBlend','A');g.link('Approach','ReturnValue','AnchorBlend','B');g.link('AnchorBlend','ReturnValue','Location','Alpha')"""
s=s.replace(needle,insert);exec(compile(s,'MountPoseTiming','exec'),{})
# NPCs share the same faster transition, without double lateral offset. Keep current avoidance and forward pedals.
s=(r/'work/fix_cyclist_bidirectional_avoidance.py').read_text(encoding='utf-8-sig')
s=s.replace("body=s[start:end]","body=s[start:end].replace(\"B='1.15'\",\"B='.68'\").replace(\"B='45'\",\"B='0'\")")
needle="g.build('ReceiveTick');assert E.compile_blueprint(bp)"
insert="""g.call('ForwardPedalLoop','Subtract_DoubleDouble',M,A='1');g.link('PedalLoop','ReturnValue','ForwardPedalLoop','B');g.call('ForwardCrankDegrees','Multiply_DoubleDouble',M,B='-1');g.link('CrankDegrees','ReturnValue','ForwardCrankDegrees','A')
for link in g.links:
 if link==['PedalLoop','ReturnValue','PedalPosition','A']:link[0]='ForwardPedalLoop'
 if link==['CrankDegrees','ReturnValue','CrankRotation','Pitch']:link[0]='ForwardCrankDegrees'
g.build('ReceiveTick');assert E.compile_blueprint(bp)"""
assert needle in s;s=s.replace(needle,insert);exec(compile(s,'NpcFastMount','exec'),{})
# A dedicated sprint graph uses the existing retargeted Mixamo run, while walking stays identical to NPCs.
bp=unreal.load_asset('/Game/Delivery/Animation/ABP_DeliveryRiderRun')
if not bp:bp=unreal.EditorAssetLibrary.duplicate_asset('/Game/Delivery/Animation/ABP_DeliveryRider','/Game/Delivery/Animation/ABP_DeliveryRiderRun')
clips=[unreal.load_asset('/Game/VoxelExplorer/'+n) for n in ['AN_Idle','AN_MixamoWalk','AN_BikePedal','AN_MotoRide','AN_MixamoJump']]
assert unreal.DeliveryEditorLibrary.build_character_animation_blueprint('ABP_DeliveryRiderRun',clips[0].get_editor_property('skeleton'),*clips)
s=(r/'work/migrate_rider_animation_pure_blueprint.py').read_text(encoding='utf-8-sig');s=s[s.index('d.bp=bp;g=d.Graph()'):]
s=s.replace("op('PedalPosition','Multiply_DoubleDouble',('PedalFraction','ReturnValue'),('PedalLength','ReturnValue'))", "op('ForwardPedalFraction','Subtract_DoubleDouble',None,('PedalFraction','ReturnValue'),A='1');op('PedalPosition','Multiply_DoubleDouble',('ForwardPedalFraction','ReturnValue'),('PedalLength','ReturnValue'))")
exec(compile(s,'RunEventGraph','exec'));save(bp)
R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C'
# Post-animation coordinator restores upright neutral mesh rotation on foot, but never overrides car transitions.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRiderAnimationCoordinator');d.bp=bp;g=d.Graph()
g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Player','ReturnValue','Rider','Object');g.call('Valid','IsValid',K);g.link('Rider','AsBP Blueprint Rider','Valid','Object');g.branch('HavePlayer','Valid');g.exec('entry','HavePlayer');g.exec('HavePlayer','result','else')
for id,var,owner in [('Transition','TransitionState',R),('Road','RoadActive',R),('Mounted','Riding',R),('Sprint','Sprint',R),('Mesh','Mesh','/Script/Engine.Character')]:
 g.node(id,'getfield',owner=owner,var=var);g.link('Rider','AsBP Blueprint Rider',id,'self')
g.call('TransitionBusy','NotEqual_IntInt',M,B='0');g.link('Transition','TransitionState','TransitionBusy','A');g.call('Busy','BooleanOR',M);g.link('TransitionBusy','ReturnValue','Busy','A');g.link('Road','RoadActive','Busy','B');g.branch('Skip','Busy');g.exec('HavePlayer','Skip');g.exec('Skip','result');g.call('Velocity','GetVelocity',A);g.link('Player','ReturnValue','Velocity','self');g.call('Speed','VSizeXY',M);g.link('Velocity','ReturnValue','Speed','A');g.call('Fast','Greater_DoubleDouble',M,B='190');g.link('Speed','ReturnValue','Fast','A');g.call('Sprinting','BooleanAND',M);g.link('Fast','ReturnValue','Sprinting','A');g.link('Sprint','Sprint','Sprinting','B');g.call('OnFoot','Not_PreBool',M);g.link('Mounted','Riding','OnFoot','A');g.call('RunWanted','BooleanAND',M);g.link('Sprinting','ReturnValue','RunWanted','A');g.link('OnFoot','ReturnValue','RunWanted','B');g.call('Current','GetAnimInstance',SK);g.link('Mesh','Mesh','Current','self');g.branch('ChooseRun','RunWanted');g.exec('Skip','ChooseRun','else')
for tag,cls,pin,edge in [('Run',RUN,'AsABP Delivery Rider Run','then'),('Walk',ABP,'AsABP Delivery Rider','else')]:
 g.node(tag+'Type','cast',type=cls);g.link('Current','ReturnValue',tag+'Type','Object');g.call(tag+'Valid','IsValid',K);g.link(tag+'Type',pin,tag+'Valid','Object');g.branch(tag+'Ready',tag+'Valid');g.exec('ChooseRun',tag+'Ready',edge);g.call(tag+'Apply','SetAnimInstanceClass',SK,NewClass=cls);g.link('Mesh','Mesh',tag+'Apply','self');g.exec(tag+'Ready',tag+'Apply','else')
g.branch('AlignMounted','Mounted','Riding')
for tag in ['Run','Walk']:
 g.exec(tag+'Ready','AlignMounted');g.exec(tag+'Apply','AlignMounted')
g.call('Neutral','K2_SetRelativeRotation',SC,NewRotation='(Pitch=0,Yaw=-90,Roll=0)',bSweep='false',bTeleport='true');g.link('Mesh','Mesh','Neutral','self');g.call('NeutralBasis','MakeRotator',M,Yaw='-90');g.link('NeutralBasis','ReturnValue','Neutral','NewRotation');g.exec('AlignMounted','Neutral','else');g.call('ResetAbsolute','SetAbsolute',SC,bNewAbsoluteLocation='false',bNewAbsoluteRotation='false',bNewAbsoluteScale='false');g.link('Mesh','Mesh','ResetAbsolute','self');g.exec('Neutral','ResetAbsolute');g.call('CacheNeutral','CacheInitialMeshOffset','/Script/Engine.Character',MeshRelativeLocation='(X=0,Y=0,Z=-90)',MeshRelativeRotation='(Pitch=0,Yaw=-90,Roll=0)');g.link('Rider','AsBP Blueprint Rider','CacheNeutral','self');g.link('NeutralBasis','ReturnValue','CacheNeutral','MeshRelativeRotation');g.exec('ResetAbsolute','CacheNeutral');g.exec('CacheNeutral','result')
for id,socket in [('Left','hand_l'),('Right','hand_r'),('Pelvis','pelvis')]:
 g.call(id,'GetSocketLocation',SC,InSocketName=socket);g.link('Mesh','Mesh',id,'self')
for id,fn,inputs in [('HandSum','Add_VectorVector',[('Left','ReturnValue','A'),('Right','ReturnValue','B')]),('HandMid','Multiply_VectorFloat',[('HandSum','ReturnValue','A')]),('BoneForward','Subtract_VectorVector',[('HandMid','ReturnValue','A'),('Pelvis','ReturnValue','B')])]:
 g.call(id,fn,M,**({'B':'.5'} if id=='HandMid' else {}))
 for src,pin,dest in inputs:g.link(src,pin,id,dest)
g.call('BoneFacing','MakeRotFromX',M);g.link('BoneForward','ReturnValue','BoneFacing','X');g.call('ActorFacing','K2_GetActorRotation',A);g.link('Player','ReturnValue','ActorFacing','self');g.call('Error','NormalizedDeltaRotator',M);g.link('ActorFacing','ReturnValue','Error','A');g.link('BoneFacing','ReturnValue','Error','B');g.call('Angles','BreakRotator',M);g.link('Error','ReturnValue','Angles','InRot');g.call('Correction','MakeRotator',M);g.link('Angles','Yaw','Correction','Yaw');g.call('Align','K2_AddWorldRotation',SC,bSweep='false',bTeleport='true');g.link('Mesh','Mesh','Align','self');g.link('Correction','ReturnValue','Align','DeltaRotation');g.exec('AlignMounted','Align');g.call('Pedals','UpdatePedalLocations',R);g.link('Rider','AsBP Blueprint Rider','Pedals','self');g.exec('Align','Pedals');g.exec('Pedals','result');g.build('ReceiveTick');save(bp)
unreal.log('FAST_MOUNT_RUN_AND_ORIENTATION_PASS')



