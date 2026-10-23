import unreal

unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
actors = unreal.EditorLevelLibrary.get_all_level_actors()
unreal.log('SCENE_INSPECT actors=%d' % len(actors))
for actor in actors:
    unreal.log('ACTOR %s class=%s loc=%s' % (
        actor.get_actor_label(), actor.get_class().get_name(), actor.get_actor_location()))
    for comp in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
        try:
            count = comp.get_instance_count()
        except Exception:
            count = -1
        unreal.log('HISM %s instances=%s visible=%s collision=%s mesh=%s' % (
            comp.get_name(), count, comp.is_visible(), comp.get_collision_enabled(), comp.get_editor_property('static_mesh')))
        try:
            unreal.log('HISM_CULL %s start=%s end=%s' % (
                comp.get_name(), comp.get_editor_property('instance_start_cull_distance'), comp.get_editor_property('instance_end_cull_distance')))
        except Exception as exc:
            unreal.log_warning('HISM_CULL %s unavailable=%s' % (comp.get_name(), exc))
        try:
            unreal.log('HISM_MAT %s %s' % (comp.get_name(), comp.get_material(0)))
        except Exception as exc:
            unreal.log_warning('HISM_MAT %s unavailable=%s' % (comp.get_name(), exc))
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        unreal.log('SM %s visible=%s mesh=%s mat=%s' % (comp.get_name(), comp.is_visible(), comp.get_static_mesh(), comp.get_material(0)))
unreal.log('SCENE_INSPECT_DONE')
