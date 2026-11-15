import unreal

unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_actor_label() == 'DEBUG_RenderProbe':
        actor.destroy_actor()
probe = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(-6400, 14400, 500), unreal.Rotator(0, 0, 0))
probe.set_actor_label('DEBUG_RenderProbe')
mesh = unreal.load_asset('/Engine/BasicShapes/Cube')
component = probe.get_component_by_class(unreal.StaticMeshComponent)
component.set_static_mesh(mesh)
component.set_material(0, unreal.load_asset('/Game/World/M_Sky'))
probe.set_actor_scale3d(unreal.Vector(4, 4, 4))
component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
unreal.EditorLevelLibrary.save_current_level()
unreal.log('RENDER_PROBE_ADDED')
