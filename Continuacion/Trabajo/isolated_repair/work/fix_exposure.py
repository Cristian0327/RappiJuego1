import unreal

unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
changed = 0
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_class().get_name() != 'PostProcessVolume':
        continue
    settings = actor.get_editor_property('settings')
    settings.set_editor_property('override_auto_exposure_method', True)
    settings.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_BASIC)
    settings.set_editor_property('override_auto_exposure_bias', True)
    settings.set_editor_property('auto_exposure_bias', 0.0)
    settings.set_editor_property('override_auto_exposure_min_brightness', True)
    settings.set_editor_property('auto_exposure_min_brightness', 0.65)
    settings.set_editor_property('override_auto_exposure_max_brightness', True)
    settings.set_editor_property('auto_exposure_max_brightness', 2.5)
    settings.set_editor_property('override_auto_exposure_speed_up', True)
    settings.set_editor_property('auto_exposure_speed_up', 2.0)
    settings.set_editor_property('override_auto_exposure_speed_down', True)
    settings.set_editor_property('auto_exposure_speed_down', 2.0)
    settings.set_editor_property('override_auto_exposure_apply_physical_camera_exposure', True)
    settings.set_editor_property('auto_exposure_apply_physical_camera_exposure', False)
    actor.set_editor_property('settings', settings)
    changed += 1
unreal.EditorLevelLibrary.save_current_level()
unreal.log('EXPOSURE_FIXED volumes=' + str(changed))
