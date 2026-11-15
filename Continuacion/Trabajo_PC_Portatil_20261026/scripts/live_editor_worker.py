"""Keep one editor warm for direct PIE inspection and focused repairs."""
import unreal,json,time,traceback
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve().parent
request=root/'live_request.json';state=root/'live_state.json'
last_sample=0.;world_name=None
def vector(value):return list(value.to_tuple())
def write_state(status,**values):state.write_text(json.dumps(dict(status=status,**values),indent=2))
def game_world():return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def snapshot(world):
    rows=[]
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character):
        name=actor.get_name()
        if not any(s in name for s in ['CivilMotorcycle','PoliceMotorcycle','PoliceRoadPatrol','TwoWheelerCitizen']):continue
        movement=actor.get_editor_property('character_movement')
        row=dict(name=name,position=vector(actor.get_actor_location()),velocity=vector(actor.get_velocity()),forward=vector(actor.get_actor_forward_vector()),last_input=vector(actor.get_last_movement_input_vector()),pending_input=vector(actor.get_pending_movement_input_vector()),acceleration=vector(movement.get_current_acceleration()))
        for prop in ['max_acceleration','max_walk_speed','ground_friction','braking_deceleration_walking','tick_before_owner','use_rvo_avoidance','orient_rotation_to_movement','use_controller_desired_rotation','max_simulation_iterations','max_simulation_time_step']:
            try:row[prop]=movement.get_editor_property(prop)
            except Exception:row[prop]='unavailable'
        try:
            index=int(actor.get_editor_property('RouteIndex'));route=actor.get_editor_property('Route');row.update(index=index,goal=vector(route[index]))
        except Exception:row['route_error']=traceback.format_exc()
        for prop in ['MotorDeltaSeconds','MotorCommandDirection','MotorGoalAtInput','MotorPositionAtInput','MotorInputLimit','MotorInputScale','MotorInputIndex']:
            try:
                value=actor.get_editor_property(prop);row[prop]=vector(value) if isinstance(value,unreal.Vector) else value
            except Exception:pass
        rows.append(row)
    record=dict(wall_time=time.time(),world=world.get_path_name(),services=rows)
    (root/'live_snapshot.json').write_text(json.dumps(record,indent=2))
    with (root/'live_samples.jsonl').open('a') as stream:stream.write(json.dumps(record)+'\n')
def callback(delta):
    global last_sample,world_name
    try:
        if request.exists():
            task=json.loads(request.read_text());request.unlink();action=task.get('action','exec');write_state('running',task=task)
            subsystem=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            if action=='play':
                if task.get('map'):unreal.EditorLoadingAndSavingUtils.load_map(task['map'])
                subsystem.editor_request_begin_play()
            elif action=='stop':subsystem.editor_request_end_play()
            elif action=='exec':
                path=(root/task['script']).resolve();assert path.is_relative_to(root)
                scope=dict(unreal=unreal,root=root,world=game_world(),__file__=str(path),__name__='__main__');exec(compile(path.read_text(),str(path),'exec'),scope)
            elif action=='unregister':unreal.unregister_slate_post_tick_callback(live_callback_handle)
            write_state('success',task=task)
        world=game_world()
        if world and time.monotonic()-last_sample>=2:
            last_sample=time.monotonic();snapshot(world)
    except Exception:
        error=traceback.format_exc();write_state('error',error=error);unreal.log_error(error)
live_callback_handle=unreal.register_slate_post_tick_callback(callback)
write_state('ready');unreal.log('LIVE_EDITOR_WORKER_READY')
