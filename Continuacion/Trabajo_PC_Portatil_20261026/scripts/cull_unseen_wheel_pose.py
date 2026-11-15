"""Skip only wheel bone writes off camera; retain bus articulation state and pose."""
import unreal,json,sys,shutil,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent;out=R/'AdversarialQA_20261026';backup=out/'before';rel=Path('World/BlueprintWorld/Traffic/BP_TrafficVehicle.uasset');src=Path(unreal.Paths.project_content_dir())/rel
for target,origin in [(backup/'BP_TrafficVehicle_author_before_culling.uasset',src),(backup/'BP_TrafficVehicle_original.uasset',R.parent/'BogotaVoxel/Content'/rel)]:
 if not target.exists():shutil.copy2(origin,target)
sys.path.insert(0,str(R/'Herramientas'));import blueprint_graph as d
wheel_source=(R/'work/extend_pure_traffic_wheel_pose.py').read_text(encoding='utf-8-sig');scope=dict(__file__=str(R/'work/extend_pure_traffic_wheel_pose.py'),__name__='__main__')
exec(compile(wheel_source[:wheel_source.index("g=d.Graph();g.get('Bus')")],'WheelPoseSetup','exec'),scope)
# Generate the exact existing wheel/trailer graph without rebuilding other functions.
scope['build']=lambda *a,**k:None
body=wheel_source[wheel_source.index("g=d.Graph()\nfor n in ['Body'"):];exec(compile(body,'ExistingWheelPose','exec'),scope)
improved=(R/'work/improve_bus_and_car_assets.py').read_text(encoding='utf-8-sig');patch=improved[improved.index('# The existing graph remains intact'):improved.index('# Import the two corrected')];exec(compile(patch,'ExistingTrailerTracking','exec'),scope)
b=scope['bp'];E=unreal.BlueprintEditorLibrary;known=[str(x) for x in E.list_member_variable_names(b)]
if 'ForceWheelPose' not in known:assert E.add_member_variable(b,'ForceWheelPose',E.get_basic_type_by_name('bool'))
assert E.compile_blueprint(b);g=scope['g'];g.get('ForceWheelPose');g.call('RecentlyDrawn','WasRecentlyRendered','/Script/Engine.Actor',Tolerance='.25');g.call('WheelVisible','BooleanOR',d.M);g.link('RecentlyDrawn','ReturnValue','WheelVisible','A');g.link('ForceWheelPose','ForceWheelPose','WheelVisible','B');g.branch('DrawWheels','WheelVisible')
for edge in [['PoseJoint','then','EachWheel','Exec'],['PoseBus','else','EachWheel','Exec']]:
 assert edge in g.links,edge;g.links.remove(edge);g.link(edge[0],edge[1],'DrawWheels','execute')
g.link('DrawWheels','then','EachWheel','Exec');g.exec('DrawWheels','result','else')
assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'UpdateWheelPose',json.dumps(dict(nodes=g.nodes,links=g.links,parameters=[])));assert E.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
# QA-only fixture sets preview state without exposing technical controls in the game UI.
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor);fixture=unreal.load_asset('/Game/QA/BP_WheelVisualFixture') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_WheelVisualFixture','/Game/QA',unreal.Blueprint,factory);P=b.generated_class().get_path_name();g=d.Graph();last='entry'
for name,param in [('PreviousWheelAngle','OldAngle'),('WheelAngle','Angle'),('PoseAlpha','Alpha'),('ForceWheelPose','Force')]:
 g.node(name,'setfield',owner=P,var=name);g.link('entry','Vehicle',name,'self');g.link('entry',param,name,name);g.exec(last,name);last=name
g.exec(last,'result');params=[dict(name='Vehicle',category='object',object=P)]+[dict(name=n,category='real') for n in ['OldAngle','Angle','Alpha']]+[dict(name='Force',category='bool')];assert unreal.DeliveryEditorLibrary.build_logic_graph(fixture,'Configure',json.dumps(dict(nodes=g.nodes,links=g.links,parameters=params)));assert E.compile_blueprint(fixture)
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);owner=actors.spawn_actor_from_class(fixture.generated_class(),unreal.Vector());report=[]
def rotation_delta(a,z):return sum(abs(getattr(a,k)-getattr(z,k)) for k in ['x','y','z','w'])
for spec in json.loads((R/'work/pure_traffic_vehicle_foundation.json').read_text())['models']:
 a=actors.spawn_actor_from_class(unreal.load_asset(spec['asset']).generated_class(),unreal.Vector())
 try:
  a.call_method('CacheReferencePose');a.call_method('CacheArticulation');body=a.get_component_by_class(unreal.PoseableMeshComponent);bone=list(a.get_editor_property('WheelNames'))[0];before=body.get_bone_transform_by_name(bone,unreal.BoneSpaces.COMPONENT_SPACE);assert not a.was_recently_rendered(.25)
  owner.call_method('Configure',args=(a,0.,90.,1.,False));at=a.get_actor_location();collision=a.get_actor_enable_collision();a.call_method('UpdateWheelPose');hidden=body.get_bone_transform_by_name(bone,unreal.BoneSpaces.COMPONENT_SPACE);assert rotation_delta(before.rotation,hidden.rotation)<.0001
  owner.call_method('Configure',args=(a,0.,90.,1.,True));a.call_method('UpdateWheelPose');shown=body.get_bone_transform_by_name(bone,unreal.BoneSpaces.COMPONENT_SPACE);assert rotation_delta(before.rotation,shown.rotation)>.1;assert (a.get_actor_location()-at).length()<.001;assert a.get_actor_enable_collision()==collision
  axle_ok=True
  if spec['name']=='TransMilenio':
   old=a.get_editor_property('RearAxleWorld').copy();a.set_actor_location(at+unreal.Vector(100,0,0),False,True);owner.call_method('Configure',args=(a,90.,180.,1.,False));a.call_method('UpdateWheelPose');axle_ok=(a.get_editor_property('RearAxleWorld')-old).length()>.01;assert axle_ok
  report.append(dict(model=spec['name'],offscreen_wheel_unchanged=True,preview_wheel_updates=True,position_and_collision_preserved=True,bus_tracking_preserved=axle_ok))
 finally:actors.destroy_actor(a)
audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b));assert not any(x['native_calls'] for x in audit['graphs'])
(out/'wheel_pose_culling.json').write_text(json.dumps(dict(status='PASS',models=report,scope='Blueprint VM; visibility query plus forced editor preview; gameplay routes/collision functions untouched'),indent=2));unreal.log('UNSEEN_WHEEL_POSE_VERIFIED')
