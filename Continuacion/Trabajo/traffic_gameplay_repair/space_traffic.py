from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'RepairHelpers','exec'))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);bp=use(TM);c=unreal.get_default_object(bp.generated_class());models=list(c.get_editor_property('ModelIndices'));lanes=list(c.get_editor_property('LaneIndices'));dist=[];positions=[];radii=[];metadata=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models'];centers=[unreal.Vector(*v['position']) for v in json.loads((P.parent/'urban_corrections/junction_plan.json').read_text())];routeactors=[aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i)).generated_class(),unreal.Vector()) for i in range(7)];services=[a.get_actor_location() for a in aa.get_all_level_actors() if a.get_class().get_name() in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C','BP_TwoWheelerCitizen_C']]
for i,li in enumerate(lanes):
 route=routeactors[li];length=route.call_method('RouteLength');v=length*((i*.61803398875)%1);radius=metadata[models[i]]['half_length']+100 if models[i]<len(metadata) else 500
 for attempt in range(6000):
  p=route.call_method('SamplePosition',(v,))
  if all((p-q).length()>radius+r for q,r in zip(positions,radii)) and all((p-q).length()>2600+radius for q in centers) and all((p-q).length()>radius+180 for q in services):break
  v=(v+177.7)%length
 else:raise RuntimeError('No clear initial slot '+str(i))
 positions.append(p);radii.append(radius);dist.append(v)
for a in routeactors:aa.destroy_actor(a)
leaders=[]
for i,li in enumerate(lanes):
 group=sorted([j for j in range(len(lanes)) if lanes[j]==li],key=lambda j:dist[j]);leaders.append(group[(group.index(i)+1)%len(group)])
for n in ['InitialDistances','LeaderIndices']:E.set_blueprint_variable_instance_editable(bp,n,True)
E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('InitialDistances',dist);c.set_editor_property('LeaderIndices',leaders);save(bp)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_TrafficManager_C':a.set_editor_property('InitialDistances',dist);a.set_editor_property('LeaderIndices',leaders)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();(P/'initial_traffic_spacing.json').write_text(json.dumps(dict(vehicles=len(positions),junction_exclusion_cm=2600,positions=[list(p.to_tuple()) for p in positions],half_lengths_with_clearance=radii)));unreal.log('CLEAR_TRAFFIC_SPAWNS '+str(len(positions)))
