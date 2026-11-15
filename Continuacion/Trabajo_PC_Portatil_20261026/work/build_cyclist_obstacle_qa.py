from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent;s=(r/'work/build_two_wheeler_runtime_test.py').read_text(encoding='utf-8-sig');s=s.replace('BP_TestTwoWheeler','BP_TestCyclistObstacle').replace('TwoWheelerRuntimeTest','CyclistObstacleRuntime').replace("B='115'","B='25'").replace("{'name':'NextReport','default':'10'}","{'name':'NextReport','default':'5'}").replace("B='10'","B='5'").replace("o.set_editor_property('RideSeconds',5)","o.set_editor_property('RideSeconds',999)").replace("o.set_editor_property('StartParked',i%2==0)","o.set_editor_property('StartParked',False)")
s=s.replace("g.link('MetricText','ReturnValue','Print','InString')","g.call('ActorPosition','K2_GetActorLocation','/Script/Engine.Actor');g.link('Each','Array Element','ActorPosition','self');g.call('PositionText','Conv_VectorToString',STR);g.link('ActorPosition','ReturnValue','PositionText','InVec');g.call('PositionLabel','Concat_StrStr',STR,B=' position=');g.link('MetricText','ReturnValue','PositionLabel','A');g.call('FinalText','Concat_StrStr',STR);g.link('PositionLabel','ReturnValue','FinalText','A');g.link('PositionText','ReturnValue','FinalText','B');g.link('FinalText','ReturnValue','Print','InString')")
s=s.replace(" if i>=2:"," if i>=3:")
needle="a.spawn_actor_from_class(unreal.load_asset('/Game/Traffic/Services/BP_NpcFacingCoordinator')"
insertion="""for i in range(3):
 x=i*5000-7500;person=a.spawn_actor_from_class(unreal.Character,unreal.Vector(x,650,88));person.get_editor_property('capsule_component').set_collision_profile_name('Pawn');person.get_editor_property('character_movement').disable_movement()
 if i==1:
  wall=a.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x-190,350,100));wall.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));wall.set_actor_scale3d(unreal.Vector(1,7,2));wall.static_mesh_component.set_collision_profile_name('BlockAll')
 if i==2:
  person=a.spawn_actor_from_class(unreal.Character,unreal.Vector(x-100,800,88));person.get_editor_property('capsule_component').set_collision_profile_name('Pawn');person.get_editor_property('character_movement').disable_movement()
"""
s=s.replace(needle,insertion+needle);exec(compile(s,'CyclistObstacleQA','exec'))
