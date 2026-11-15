import unreal

unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if isinstance(actor, unreal.PostProcessVolume):
        settings = actor.get_editor_property('settings')
        names = [n for n in dir(settings) if 'exposure' in n.lower()]
        unreal.log('PP_EXPOSURE_PROPERTIES %s' % names)
        unreal.log('PP_SETTINGS method=%s offset=%s bias=%s min=%s max=%s unbound=%s' % (
            settings.get_editor_property('auto_exposure_method'),
            settings.get_editor_property('exposure_offset'),
            settings.get_editor_property('auto_exposure_bias'),
            settings.get_editor_property('auto_exposure_min_brightness'),
            settings.get_editor_property('auto_exposure_max_brightness'),
            actor.get_editor_property('unbound')))
