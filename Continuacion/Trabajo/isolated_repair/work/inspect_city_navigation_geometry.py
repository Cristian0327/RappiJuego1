import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PureCityCrowd');a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();out={'world':{},'navactors':[],'geometry':[]}
for p in ['enable_navigation_system','navigation_system_config','navigation_system_config_override']:
 try:out['world'][p]=str(w.get_world_settings().get_editor_property(p))
 except Exception as e:out['world'][p]=str(e)
for actor in a.get_all_level_actors():
 if 'Nav' in actor.get_class().get_name() and not isinstance(actor,unreal.NavModifierVolume):out['navactors'].append({'class':actor.get_class().get_name(),'name':actor.get_actor_label()})
 if actor.get_class().get_name()=='BP_CityGeometry_C':
  for c in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   row={'name':c.get_name(),'nav':c.get_editor_property('can_ever_affect_navigation'),'collision':str(c.get_collision_enabled()),'profile':str(c.get_collision_profile_name()),'largest_ground':[]}
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,world_space=True)
    if t.translation.z<40 and t.scale3d.x>20 and t.scale3d.y>20:row['largest_ground'].append(str(t))
   out['geometry'].append(row)
(r/'work/city_navigation_geometry_inventory.json').write_text(json.dumps(out,indent=2));unreal.log('NAV_GEOMETRY_INVENTORY_PASS')
