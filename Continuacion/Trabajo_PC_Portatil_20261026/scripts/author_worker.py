import unreal,time,json,traceback,gc
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve().parent;request=R/'author_worker_request.json';state=R/'author_worker_state.json';idle=time.monotonic()
state.write_text(json.dumps(dict(status='idle')));unreal.log('AUTHOR_WORKER_READY')
while time.monotonic()-idle<1800:
 if not request.exists():time.sleep(.5);continue
 task=json.loads(request.read_text(encoding='utf-8-sig'));request.unlink();idle=time.monotonic()
 if task.get('stop'):state.write_text(json.dumps(dict(status='stopped')));break
 script=(R/task['script']).resolve();assert script.is_relative_to(R)
 state.write_text(json.dumps(dict(status='running',script=str(script))));unreal.log('AUTHOR_JOB_START '+str(script))
 try:
  scope={'__file__':str(script),'__name__':'__main__'};exec(compile(script.read_text(encoding='utf-8-sig'),str(script),'exec'),scope);scope=None;gc.collect()
  state.write_text(json.dumps(dict(status='success',script=str(script))));unreal.log('AUTHOR_JOB_SUCCESS '+str(script))
 except Exception:
  error=traceback.format_exc();state.write_text(json.dumps(dict(status='error',script=str(script),error=error)));unreal.log_error(error)
 idle=time.monotonic();unreal.log('AUTHOR_WORKER_IDLE')
unreal.log('AUTHOR_WORKER_STOPPED')
