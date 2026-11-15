import unreal

props = [n for n in dir(unreal.PostProcessSettings) if 'exposure' in n.lower() or 'brightness' in n.lower()]
unreal.log('PP_PROPERTIES ' + ','.join(props))
unreal.log('AEM_VALUES ' + ','.join([n for n in dir(unreal.AutoExposureMethod) if n.startswith('AEM_')]))
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_class().get_name() == 'PostProcessVolume':
        settings = actor.get_editor_property('settings')
        unreal.log('PP_VOLUME ' + actor.get_name())
        for p in props:
            try:
                unreal.log('PP_VALUE ' + p + '=' + str(settings.get_editor_property(p)))
            except Exception:
                pass
