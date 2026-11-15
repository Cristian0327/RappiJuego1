import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');E=unreal.BlueprintEditorLibrary
if 'PreviousForward' not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,'PreviousForward',E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')))
assert E.compile_blueprint(bp)
s=(r/'work/extend_pure_traffic_following.py').read_text(encoding='utf-8-sig');prefix=s[:s.index("g=d.Graph();g.setter('KeepLeader'")];exec(compile(prefix,'SnapshotSetup','exec'))
start=s.index("g=d.Graph();last='entry'");snapshot=s[start:]
snapshot=snapshot.replace("g.exec(last,'result');build(g,'SnapshotSimulation')", "g.get('PreviousYaw');g.call('SnapshotRotation','MakeRotator',M);g.link('PreviousYaw','PreviousYaw','SnapshotRotation','Yaw');g.call('SnapshotForward','GetForwardVector',M);g.link('SnapshotRotation','ReturnValue','SnapshotForward','InRot');g.setter('SaveForward','PreviousForward','SnapshotForward');g.exec(last,'SaveForward');g.exec('SaveForward','result');build(g,'SnapshotSimulation')")
exec(compile(snapshot,'CachedSnapshotDirection','exec'))
s=(r/'work/build_pure_traffic_spatial_cells.py').read_text(encoding='utf-8-sig');s=s[:s.index("build(g,'ClearanceFromVehicle'")]
s=s.replace("['PreviousPosition','PreviousYaw','HalfLength','HalfWidth']","['PreviousPosition','PreviousYaw','HalfLength','HalfWidth','PreviousForward']")
s=s.replace("['PreviousPosition','PreviousYaw','HalfLength','HalfWidth','PlayerControlled','Parked']","['PreviousPosition','PreviousYaw','HalfLength','HalfWidth','PlayerControlled','Parked','PreviousForward']")
s=s.replace("('OwnDirection','ReturnValue')","('PreviousForward','PreviousForward')").replace("('OtherDirection','ReturnValue')","('OtherPreviousForward','PreviousForward')")
exec(compile(s,'CachedClearanceDirections','exec'))
s=(r/'work/optimize_traffic_clearance_fast_path.py').read_text(encoding='utf-8-sig');s=s[s.index("g.links.remove"):s.index("bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdFarBudget')")]
exec(compile(s,'PreserveFastClearanceBranches','exec'))
unreal.log('TRAFFIC_DIRECTION_SNAPSHOT_CACHE_READY')
