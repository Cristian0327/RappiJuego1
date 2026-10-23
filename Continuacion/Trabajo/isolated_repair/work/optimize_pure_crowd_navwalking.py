import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
p=r/'work/build_pure_crowd_manager.py';s=p.read_text(encoding='utf-8-sig');old="g.exec('HaveAI','Request')";new="g.get('CharacterMovement');g.call('NavWalking','SetMovementMode','/Script/Engine.CharacterMovementComponent',NewMovementMode='MOVE_NavWalking');g.link('CharacterMovement','CharacterMovement','NavWalking','self');g.exec('HaveAI','NavWalking');g.exec('NavWalking','Request')"
if old in s and "g.call('NavWalking','SetMovementMode'" not in s:s=s.replace(old,new)
p.write_text(s)
exec(compile(s[:s.index("f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor)")],'CrowdNavWalkingRouteSetup','exec'))
E=unreal.BlueprintEditorLibrary
for path in ['/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen']+[m['asset'] for m in json.loads((r/'work/pure_crowd_models.json').read_text())]:
 b=unreal.load_asset(path);c=unreal.get_default_object(b.generated_class());move=c.get_editor_property('character_movement');move.set_editor_property('default_land_movement_mode',getattr(unreal.MovementMode,next(n for n in dir(unreal.MovementMode) if 'NAV' in n.upper())));move.set_editor_property('project_nav_mesh_walking',True);move.set_editor_property('nav_mesh_projection_interval',.2);move.set_editor_property('sweep_while_nav_walking',True);c.get_editor_property('mesh').set_cull_distance(10000.);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
p=r/'work/build_pure_playable_world_integration.py';s=p.read_text(encoding='utf-8-sig').replace("B='18000'","B='10000'").replace("M,A='.2',B='0'","M,A='.4',B='0'").replace('set_cull_distance(18000.)','set_cull_distance(10000.)');p.write_text(s);exec(compile(s[:s.index("for path in [folder+'/BP_StreetCitizen']")],'CrowdDistancePerformancePolicy','exec'))
# New moving vehicles have collision boxes, so the existing service cache must not classify them as parked.
p=r/'work/build_service_traffic_cache.py';s=p.read_text(encoding='utf-8-sig');old="g.link('MovingOrWalking','ReturnValue','Eligible','B')";new="g.call('MigratedTraffic','ActorHasTag',A,Tag='TrafficVehicle');g.link('Each','Array Element','MigratedTraffic','self');g.call('MovingOrMigrated','BooleanOR',M);g.link('MovingOrWalking','ReturnValue','MovingOrMigrated','A');g.link('MigratedTraffic','ReturnValue','MovingOrMigrated','B');g.link('MovingOrMigrated','ReturnValue','Eligible','B')"
if old in s:s=s.replace(old,new);p.write_text(s)
exec(compile(s,'TrafficCacheMovingVehicleCompatibility','exec'))
for spec in json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']:
 b=unreal.load_asset(spec['asset']);c=unreal.get_default_object(b.generated_class());tags=[unreal.Name('TrafficVehicle')]
 if c.get_editor_property('Bus'):tags.append(unreal.Name('TransitBus'))
 if c.get_editor_property('Taxi'):tags.append(unreal.Name('Taxi'))
 c.set_editor_property('tags',tags);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
(r/'work/pure_crowd_performance_policy.json').write_text(json.dumps({'previous_integrated_mean_frame_seconds':.360355,'policy':'NavWalking with native ground projection .2sec, full rate nearby, movement .4sec when hidden beyond100m','service_cache_excludes_hidden':True,'status':'COMPILED_PENDING_RENDER_REPEAT'},indent=2));unreal.log('PURE_CROWD_NAVWALKING_PERFORMANCE_PASS')


