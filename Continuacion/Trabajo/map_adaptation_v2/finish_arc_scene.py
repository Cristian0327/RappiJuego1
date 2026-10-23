from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');assert 'isolated_repair' in root.parts;b=use(TM);names=['JunctionCentres','Junctions','UrbanCrossingCenters','UrbanCrossingForwards','UrbanSignalGroups','UrbanRoadWidths','UrbanStopOffsets']
for n in names:E.set_blueprint_variable_instance_editable(b,n,True)
assert E.compile_blueprint(b);save(b);c=unreal.get_default_object(b.generated_class());assert len(c.get_editor_property('JunctionCentres'))==9
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_TrafficManager_C':
  for n in names:a.set_editor_property(n,[] if n=='Junctions' else c.get_editor_property(n))
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_ARC_SCENE_READY')
