import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/fix_requested_animations.py').read_text(encoding='utf-8-sig');prefix=s[:s.index('# Import only')];body=s[s.index('# Post-animation coordinator'):];body=body.replace("g.build('ReceiveTick');save(bp)","E.remove_function_graph(bp,'ReceiveTick');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'CorrectPose',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[]}));save(bp)");ns={};exec(compile(prefix+body,'DirectRiderPoseFunction','exec'),ns)
s=(r/'work/fix_requested_camera_morado.py').read_text(encoding='utf-8-sig');s=s[:s.index('# Configure visible character')]
needle="g.exec('BodyVisible','result')"
insert="""C='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRiderAnimationCoordinator.BP_BlueprintRiderAnimationCoordinator_C';g.call('PoseCoordinator','GetActorOfClass',G,ActorClass=C);g.exec('BodyVisible','PoseCoordinator');g.node('PoseType','cast',type=C);g.link('PoseCoordinator','ReturnValue','PoseType','Object');g.call('PoseValid','IsValid',K);g.link('PoseCoordinator','ReturnValue','PoseValid','Object');g.branch('HavePose','PoseValid');g.exec('PoseCoordinator','HavePose');g.exec('HavePose','result','else');g.call('CorrectHero','CorrectPose',C);g.link('PoseType','AsBP Blueprint Rider Animation Coordinator','CorrectHero','self');g.exec('HavePose','CorrectHero');g.exec('CorrectHero','result')"""
assert needle in s;s=s.replace(needle,insert);exec(compile(s,'PlayerOwnsPoseUpdate','exec'),{})
exec(compile((r/'work/build_requested_fixes_qa.py').read_text(encoding='utf-8-sig'),'ConnectedRiderQA','exec'),{})
unreal.log('PLAYER_POSE_DIRECT_UPDATE_PASS')
