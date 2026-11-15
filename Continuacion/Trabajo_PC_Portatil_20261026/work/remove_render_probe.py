import unreal

world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
removed = 0
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_actor_label() == 'DEBUG_RenderProbe':
        actor.destroy_actor()
        removed += 1
unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/Maps/Bogota')
unreal.log('RENDER_PROBE_REMOVED count=' + str(removed))
