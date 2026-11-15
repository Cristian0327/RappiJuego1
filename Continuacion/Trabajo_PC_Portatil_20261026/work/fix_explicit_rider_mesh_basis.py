import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/fix_requested_animations.py').read_text(encoding='utf-8-sig');prefix=s[:s.index('# Import only')]
# Pin-wired rotators avoid Unreal's silent fallback for named struct literals on rotator pins.
a=s.index("ns={};s=(r/'work/build_pure_rider_transition_foundation.py')");b=s.index('# NPCs share',a);ns={};exec(compile(prefix+s[a:b],'MountFoundationAndSampling','exec'),ns)
# The foundation graph retained in ns is BeginTwoWheelTransition.
foundation=ns['ns'];g=foundation['g'];bp=foundation['bp'];d=foundation['d'];E=foundation['E'];M=d.M;d.bp=bp;g.call('MountMeshBasis','MakeRotator',M,Yaw='-90')
for tag in ['GoalRotation','MountFacing']:g.link('MountMeshBasis','ReturnValue',tag,'A')
foundation['build'](g,'BeginTwoWheelTransition',[{'name':'RootLocation','category':'struct','object':'/Script/CoreUObject.Vector'},{'name':'RootRotation','category':'struct','object':'/Script/CoreUObject.Rotator'},{'name':'Reverse','category':'bool'}]);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Restore on-foot mesh rotation with an actual Make Rotator node.
u=(r/'work/extend_pure_rider_transition_update.py').read_text(encoding='utf-8-sig');u=u[:u.index("g=d.Graph()\nfor n in ['TransitionState','TransitionAge'")];ns={};exec(compile(u,'FinishTransitionSetup','exec'),ns);g=ns['g'];bp=ns['bp'];ns['d'].bp=bp;g.call('StandingMeshBasis','MakeRotator',ns['M'],Yaw='-90');g.link('StandingMeshBasis','ReturnValue','ResetRotation','NewRotation');ns['build'](g,'FinishTwoWheelTransition',[]);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Callable coordinator: running/walking selection and foot/mount orientation.
body=s[s.index('# Post-animation coordinator'):];body=body.replace("g.build('ReceiveTick');save(bp)","E.remove_function_graph(bp,'ReceiveTick');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'CorrectPose',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[]}));save(bp)");exec(compile(prefix+body,'CorrectStandingMeshBasis','exec'),{})
# Apply the same explicit basis to the NPC mounting pose, preserving avoidance and forward pedals.
a=s.index('# NPCs share');b=s.index('# A dedicated sprint',a);part=s[a:b];part=part.replace("g.call('ForwardPedalLoop'", "g.call('NpcMountBasis','MakeRotator',M,Yaw='-90');g.link('NpcMountBasis','ReturnValue','RiderYaw','B');g.call('ForwardPedalLoop'")
exec(compile(prefix+part,'NpcMountExplicitBasis','exec'),{})
exec(compile((r/'work/build_requested_fixes_qa.py').read_text(encoding='utf-8-sig'),'ExplicitBasisQA','exec'),{})
unreal.log('EXPLICIT_MESH_ROTATION_PINS_PASS')

