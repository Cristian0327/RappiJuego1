import unreal,json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
report={}
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
 if isinstance(actor,unreal.PostProcessVolume):
  s=actor.get_editor_property('settings')
  for key,value in [('override_ambient_occlusion_intensity',True),('ambient_occlusion_intensity',.65),('override_ambient_occlusion_radius',True),('ambient_occlusion_radius',75.0),('override_bloom_intensity',True),('bloom_intensity',.18)]:s.set_editor_property(key,value)
  actor.set_editor_property('settings',s)
  report[actor.get_actor_label()]={'ao':.65,'radius':75,'bloom':.18}
 if actor.get_actor_label()=='EditorPreview_Sol':
  c=actor.get_component_by_class(unreal.DirectionalLightComponent);c.set_intensity(6);c.set_editor_property('dynamic_shadow_cascades',4);c.set_editor_property('light_source_angle',2)
 if actor.get_actor_label()=='EditorPreview_Ambiente':actor.get_component_by_class(unreal.SkyLightComponent).set_intensity(3)
unreal.EditorLevelLibrary.save_current_level()
(r/'work/lighting_fix_result.json').write_text(json.dumps(report,indent=2))
unreal.log('LIGHTING_FIX_PASS '+str(report))
