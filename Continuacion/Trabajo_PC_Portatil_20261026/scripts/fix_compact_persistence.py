import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).parent
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C' and a.get_editor_property('StationId')==2)
c=next(c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='StationShell')
mesh=unreal.load_asset('/Game/World/BogotaUrban/Geometry/SM_Bogota_EstacionTransmi_Compacta')
assert mesh and 1100<mesh.get_bounds().box_extent.x<1300
before=c.static_mesh.get_path_name()
c.set_editor_property('static_mesh',mesh)
unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
a=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C' and a.get_editor_property('StationId')==2)
c=next(c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='StationShell')
after=c.static_mesh.get_path_name()
report=dict(before=before,after_reload=after,position=list(a.get_actor_location().to_tuple()),scale=list(a.get_actor_scale3d().to_tuple()),persisted=after==mesh.get_path_name())
(P/'compact_station_persistence.json').write_text(json.dumps(report,indent=2));assert report['persisted'],report
# Regenerate only the QA map from the corrected isolated level, preserving the current diagnostic class.
bp=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/QA/AdaptationTraffic')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic')
aa.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.log('RESUME_COMPACT_PERSISTENCE '+json.dumps(report))# Audit the actual service corridors against world-static geometry in the editor.
resume_root=P
exec(compile((P/'scripts/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
P=resume_root
b=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe');g=d.Graph()
g.node('RoadObjects','makearray',defaults={'[0]':'ObjectTypeQuery1'})
g.call('RoadSweep','SphereTraceSingleForObjects',K,Radius='70',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true')
g.link('entry','Start','RoadSweep','Start');g.link('entry','End','RoadSweep','End');g.link('RoadObjects','Array','RoadSweep','ObjectTypes');g.exec('entry','RoadSweep')
g.call('RoadHit','BreakHitResult',G);g.link('RoadSweep','OutHit','RoadHit','Hit')
g.call('RoadComponent','GetObjectName',K);g.link('RoadHit','HitComponent','RoadComponent','Object')
g.link('RoadSweep','ReturnValue','result','Blocked');g.link('RoadHit','HitActor','result','Obstacle');g.link('RoadComponent','ReturnValue','result','Component');g.link('RoadHit','ImpactPoint','result','Impact');g.exec('RoadSweep','result')
build(b,g,'QueryRoadStatic',[dict(name='Start',category='struct',object='/Script/CoreUObject.Vector'),dict(name='End',category='struct',object='/Script/CoreUObject.Vector'),dict(name='Blocked',category='bool',out=True),dict(name='Obstacle',category='object',object=A,out=True),dict(name='Component',category='string',out=True),dict(name='Impact',category='struct',object='/Script/CoreUObject.Vector',out=True)]);save(b)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic')
probe=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_AdaptationTrafficProbe_C')
source=P.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
lanes=json.loads((source/'actual_lanes.json').read_text());hits=[]
for li in [0,1,2,3,6]:
 points=lanes[li]
 for i,q in enumerate(points):
  e=points[(i+1)%len(points)];start=unreal.Vector(q[0],q[1],q[2]+120);end=unreal.Vector(e[0],e[1],e[2]+120)
  blocked,actor,component,impact=probe.call_method('QueryRoadStatic',(start,end))
  if blocked:hits.append(dict(lane=li,segment=i,actor=actor.get_name() if actor else None,label=actor.get_actor_label() if actor else None,component=component,start=list(start.to_tuple()),end=list(end.to_tuple()),impact=list(impact.to_tuple())))
(P/'lane_static_obstacles.json').write_text(json.dumps(hits,indent=2))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.log('RESUME_STATIC_CORRIDOR_AUDIT '+str(len(hits)))
