"""Request ordinary PIE once; never query a game world during PIE transitions."""
import unreal,time,json,traceback
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
from pathlib import Path
R=Path(__file__).resolve().parent.parent;state_file=R/'optimization_pie_state.json';start_time=time.monotonic();requested=False;restore_time=0.;preferences={}
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);utilities=unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
performance=None
try:
 performance=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
 for prop in ['bThrottleCPUWhenNotForeground','bMonitorEditorPerformance','bDisableRealtimeViewportsInRemoteSessions']:
  preferences[prop]=performance.get_editor_property(prop);performance.set_editor_property(prop,False)
except Exception:
 unreal.log_warning('Optional editor performance preferences unavailable; keeping current settings.')
def state(status,**extra):state_file.write_text(json.dumps(dict(status=status,**extra),indent=2))
def restore(delta):
 global restore_handle
 if time.monotonic()<restore_time:return
 unreal.unregister_slate_post_tick_callback(restore_handle)
 try:
  settings=unreal.GameUserSettings.get_game_user_settings();settings.set_overall_scalability_level(0);settings.set_resolution_scale_value_ex(55);settings.set_dynamic_resolution_enabled(False);settings.set_frame_rate_limit(60);settings.apply_non_resolution_settings();settings.save_settings()
  for prop,value in preferences.items():performance.set_editor_property(prop,value)
  assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
  state('main_map_ready');unreal.log('OPTIMIZATION_PIE_MAIN_MAP_READY')
 except Exception:state('error',error=traceback.format_exc());unreal.log_error(traceback.format_exc())
def ended(simulating):
 global restore_time,restore_handle
 utilities.on_end_pie.remove_callable(ended);restore_time=time.monotonic()+3;restore_handle=unreal.register_slate_post_tick_callback(restore);state('pie_ended')
def begin(delta):
 global requested,begin_handle
 if time.monotonic()-start_time<5:return
 unreal.unregister_slate_post_tick_callback(begin_handle);requested=True;state('pie_requested');unreal.log('OPTIMIZATION_PIE_REQUESTED');level.editor_request_begin_play()
utilities.on_end_pie.add_callable(ended);begin_handle=unreal.register_slate_post_tick_callback(begin);state('ready_for_pie')
