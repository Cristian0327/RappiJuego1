from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');info=json.loads((P/'entry_obstacle_report.json').read_text());old=unreal.Vector(*info['old']);delta=unreal.Vector(*info['new'])-old;unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);owner=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaUrbanDressing_C');bp=unreal.load_asset('/Game/World/BogotaUrban/BP_BogotaUrbanDressing');cdo=unreal.get_default_object(bp.generated_class());count=0
for component in owner.get_components_by_class(unreal.InstancedStaticMeshComponent):
 if not component.static_mesh or 'Luz' not in component.static_mesh.get_name():continue
 name=component.get_name()+'Transforms';transforms=list(cdo.get_editor_property(name))
 for i,tr in enumerate(transforms):
  if math.hypot(tr.translation.x-old.x,tr.translation.y-old.y)<100:tr.translation=tr.translation+delta;transforms[i]=tr;count+=1
 cdo.set_editor_property(name,transforms)
save(bp);aa.destroy_actor(owner);aa.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_LAMP_LENS_MOVED '+str(count))
