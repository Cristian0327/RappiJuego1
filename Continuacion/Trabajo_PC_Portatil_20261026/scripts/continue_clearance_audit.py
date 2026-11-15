import unreal,json,math,sys
from pathlib import Path
R=Path(unreal.Paths.project_dir()).parent;P=R/'scripts/map_adaptation_v2';sys.path.insert(0,str(R/'python_deps'))
from shapely.geometry import Point
probe_script=P/'build_resume_diagnostics.py';exec(compile(probe_script.read_text(),'clearance_probe','exec'),{'__file__':str(probe_script)})
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic');probe=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_AdaptationTrafficProbe_C');lanes=json.loads((R/'clearance_lanes.json').read_text());hits=[]
for li in [0,1,2,3,6]:
 points=lanes[li];hl=915 if li==6 else 340
 for i,q in enumerate(points):
  end=points[(i+1)%len(points)];start=unreal.Vector(q[0],q[1],q[2]+190);finish=unreal.Vector(end[0],end[1],end[2]+190);yaw=math.degrees(math.atan2(end[1]-q[1],end[0]-q[0]));blocked,actor,component,impact=probe.call_method('QueryRoadBody',(start,finish,hl,yaw))
  if blocked:hits.append(dict(lane=li,segment=i,actor=actor.get_name() if actor else None,component=component,impact=list(impact.to_tuple())))
(R/'clearance_body_audit_first.json').write_text(json.dumps(hits,indent=2))
if hits:
 rows=json.loads((R/'route_obstacle_footprints.json').read_text());rows.extend([dict(actor=h['actor'],component=h['component'],wkt=Point(h['impact'][:2]).buffer(125).wkt,approximation=True) for h in hits]);(R/'route_obstacle_footprints.json').write_text(json.dumps(rows))
(R/'clearance_install_result.json').write_text(json.dumps(dict(static_body_audit_passed=not bool(hits),remaining_hits=len(hits)),indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('RESUME_BODY_AUDIT_FIRST '+str(len(hits)))