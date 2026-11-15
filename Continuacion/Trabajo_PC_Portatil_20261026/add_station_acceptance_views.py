from pathlib import Path
path=Path(__file__).resolve().parent/'scripts/map_adaptation_v2/build_current_physics.py'
source=path.read_text()
assert 'Station2Camera' not in source
source=source.replace("('MovedCars',integer)]","('MovedCars',integer),('Station2Camera',E.get_object_reference_type(unreal.CameraActor)),('Station4Camera',E.get_object_reference_type(unreal.CameraActor))]")
source=source.replace(':addvar(bp,n,t)',":addvar(bp,n,t);E.set_blueprint_variable_instance_editable(bp,n,True)")
source=source.replace("(118,'quit')","(118,'shot_station2'),(120,'shot_station4'),(122,'quit')")
needle=" elif action.startswith('shot'):\n  g.call"
assert needle in source
source=source.replace(needle,""" elif action.startswith('shot'):
  if action in ['shot_station2','shot_station4']:
   camera='Station2Camera' if action=='shot_station2' else 'Station4Camera';g.get(camera);g.call(tag+'PlayerController','GetPlayerController',G,PlayerIndex='0');g.call(tag+'View','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='0');g.link(tag+'PlayerController','ReturnValue',tag+'View','self');g.link(camera,camera,tag+'View','NewViewTarget');g.exec(tag,tag+'View');shot_start=tag+'View'
  else:shot_start=tag
  g.call""")
source=source.replace("g.exec(tag,tag+'Shot');endnode=tag+'Shot'","g.exec(shot_start,tag+'Shot');endnode=tag+'Shot'")
needle="aa.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level()"
assert needle in source
source=source.replace(needle,"""probe=aa.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
for station_id in [2,4]:
 station=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C' and a.get_editor_property('StationId')==station_id);target=station.get_actor_location()+unreal.Vector(0,0,200);at=target+station.get_actor_right_vector()*6200+unreal.Vector(0,0,3500);camera=aa.spawn_actor_from_class(unreal.CameraActor,at,unreal.MathLibrary.find_look_at_rotation(at,target));probe.set_editor_property('Station'+str(station_id)+'Camera',camera)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()""")
compile(source,str(path),'exec');path.write_text(source)
print('Station acceptance views added')
