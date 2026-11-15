from pathlib import Path
import unreal,json
root=Path(__file__).resolve().parent.parent
helpers=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(helpers.read_text().split('# Recovery never')[0],str(helpers),'exec'))
root=Path(__file__).resolve().parent.parent
P=root/'scripts/map_adaptation_v2'
data=json.loads((root/'expanded_arc_conflicts.json').read_text())
for li,row in enumerate(data['lanes']):
    bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(li));cdo=unreal.get_default_object(bp.generated_class())
    for name,key in [('ArcEntries','entry'),('ArcExits','exit'),('ArcJunctions','junction'),('ArcGroups','group'),('ArcMovements','movement')]:cdo.set_editor_property(name,[e[key] for e in row['events']])
    save(bp)
bp=unreal.load_asset(J.split('.')[0]);cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('ArcCompatible',data['compatible']);cdo.set_editor_property('ArcMovementCount',data['movement_count']);save(bp)
# Reproduce the installed exit-capacity graph, adding unsignalized reservations.
source=(P/'fix_exit_capacity.py').read_text();first=source.index('spec=json.loads');last=source.index("assert unreal.DeliveryEditorLibrary.build_logic_graph",first)
scope=dict(globals());scope['P']=root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
exec(compile(source[first:last],'PreserveCurrentExitCapacity','exec'),scope);spec=scope['spec']
spec['nodes'] += [dict(id='Unsignalized',kind='call',fn='EqualEqual_IntInt',owner=M,defaults={'B':'3'}),dict(id='PermittedPhase',kind='call',fn='BooleanOR',owner=M,defaults={})]
spec['links']=[['PermittedPhase','ReturnValue',c,p] if a=='Green' and ap=='ReturnValue' else [a,ap,c,p] for a,ap,c,p in spec['links']]
spec['links'] += [['ArcBestGroup','ArcBestGroup','Unsignalized','A'],['Unsignalized','ReturnValue','PermittedPhase','A'],['Green','ReturnValue','PermittedPhase','B']]
bp=unreal.load_asset(TM.split('.')[0]);assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'ArcClearance',json.dumps(spec));assert E.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class());centers=[unreal.Vector(x,y,0) for x,y in data['centers']];cdo.set_editor_property('JunctionCentres',centers);save(bp)
(root/'expanded_arc_clearance_spec.json').write_text(json.dumps(spec,indent=2))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manager=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_TrafficManager_C');manager.set_editor_property('JunctionCentres',centers);manager.set_editor_property('Junctions',[])
baseline=json.loads((root/'clearance_install_baseline.json').read_text());signals=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaServiceSignals_C')
for actor in signals.get_editor_property('RoadActors'):actor.set_editor_property('RouteIndex',baseline['indices'][actor.get_name()])
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
(P/'arc_conflicts.json').write_text(json.dumps(data))
spacing=P/'respace_clear_stoplines.py';exec(compile(spacing.read_text(),str(spacing),'exec'),{'__file__':str(spacing)})
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');manager=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_TrafficManager_C');cdo=unreal.get_default_object(bp.generated_class())
for name in ['InitialDistances','LeaderIndices']:manager.set_editor_property(name,cdo.get_editor_property(name))
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
probe=root/'scripts/build_current_traffic_causes.py';exec(compile(probe.read_text(),str(probe),'exec'),{'__file__':str(probe)})
unreal.log('MISSING_CROSSINGS_INSTALLED '+str(len(centers)))
