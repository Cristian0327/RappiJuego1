from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);owner=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaUrbanDressing_C');shop=next(a for a in aa.get_all_level_actors() if a.get_name()=='BP_DeliveryStore_C_8');component=next(c for c in owner.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.get_name()=='UrbanPart0');old=component.get_instance_transform(68,True).translation;target=old+shop.get_actor_forward_vector()*600
bp=unreal.load_asset('/Game/World/BogotaUrban/BP_BogotaUrbanDressing');cdo=unreal.get_default_object(bp.generated_class());changes=[]
for component in owner.get_components_by_class(unreal.InstancedStaticMeshComponent):
 name=component.get_name()+'Transforms'
 try:transforms=list(cdo.get_editor_property(name))
 except:continue
 for i,tr in enumerate(transforms):
  if (tr.translation-old).length()<5:tr.translation=tr.translation+(target-old);transforms[i]=tr;changes.append(dict(component=component.get_name(),mesh=component.static_mesh.get_name(),index=i))
 cdo.set_editor_property(name,transforms)
save(bp);loc=owner.get_actor_location();rot=owner.get_actor_rotation();aa.destroy_actor(owner);aa.spawn_actor_from_class(bp.generated_class(),loc,rot)
for actor in aa.get_all_level_actors():
 if actor.get_class().get_name()=='BP_BogotaStreetLight_C' and (actor.get_actor_location()-old).length()<50:actor.set_actor_location(actor.get_actor_location()+target-old,False,True)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);(P/'entry_obstacle_report.json').write_text(json.dumps(dict(old=list(old.to_tuple()),new=list(target.to_tuple()),changes=changes),indent=2))
homes=json.loads((P/'homes.json').read_text());bad={r['name'][5:] for r in json.loads((P/'physical_street_audit.json').read_text())['errors'] if r['name'].startswith('home:')};homes=[h for h in homes if h['source'] not in bad];(P/'homes.json').write_text(json.dumps(homes,indent=2));unreal.log('V2_ENTRY_OBSTACLE_CLEARED homes='+str(len(homes)))
