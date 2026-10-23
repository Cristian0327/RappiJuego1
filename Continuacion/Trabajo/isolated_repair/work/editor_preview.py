import unreal
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
actors=unreal.EditorLevelLibrary.get_all_level_actors()
if not any(a.get_actor_label().startswith('EditorPreview_') for a in actors):
 def preview(cls,name,loc,rot=unreal.Rotator()):
  a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,loc,rot);a.set_actor_label('EditorPreview_'+name);a.set_editor_property('is_editor_only_actor',True);a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);return a
 sun=preview(unreal.DirectionalLight,'Sol',unreal.Vector(0,0,5000),unreal.Rotator(-45,-30,0));sun.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(4)
 sky=preview(unreal.StaticMeshActor,'Cielo',unreal.Vector(0,0,0));s=sky.static_mesh_component;s.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Sphere'));s.set_material(0,unreal.load_asset('/Game/World/M_Sky'));s.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);s.set_cast_shadow(False);sky.set_actor_scale3d(unreal.Vector(2200,2200,2200))
 ambient=preview(unreal.SkyLight,'Ambiente',unreal.Vector(0,0,0));ambient.get_component_by_class(unreal.SkyLightComponent).set_intensity(.8)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
 if a.get_actor_label().startswith('EditorPreview_'):a.set_actor_enable_collision(False)
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(-9200,9900,1900),unreal.Rotator(-8,65,0))
unreal.log('EDITOR_PREVIEW_READY')
