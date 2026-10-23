from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);b=unreal.load_asset(TM.split('.')[0]);c=unreal.get_default_object(b.generated_class());report=[]
for a in aa.get_all_level_actors():
 if a.get_class().get_name()!='BP_TrafficManager_C':continue
 row={}
 for n in ['InitialDistances','LeaderIndices','JunctionCentres','UrbanCrossingCenters']:
  old=list(a.get_editor_property(n));new=list(c.get_editor_property(n));row[n]=dict(instance_count=len(old),default_count=len(new),different=sum(str(x)!=str(y) for x,y in zip(old,new)))
 report.append(row);aa.destroy_actor(a)
fresh=aa.spawn_actor_from_class(b.generated_class(),unreal.Vector());fresh.set_actor_label('Tráfico de calles reales - configuración vigente');assert list(fresh.get_editor_property('InitialDistances'))==list(c.get_editor_property('InitialDistances'));assert list(fresh.get_editor_property('LeaderIndices'))==list(c.get_editor_property('LeaderIndices'));assert unreal.EditorLoadingAndSavingUtils.save_current_level();(P/'manager_instance_override_audit.json').write_text(json.dumps(report,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_MANAGER_INSTANCE_FRESH '+json.dumps(report))
