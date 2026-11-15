from pathlib import Path
import unreal,json,traceback
R=Path(__file__).resolve().parent.parent;progress=[]
for name in ['verify_lod_scales.py','enable_skeletal_lod_streaming.py','build_graphics_settings.py','build_optimization_qa.py','build_shader_warmup.py','scale_service_significance.py','scale_store_significance.py','scale_crowd_significance.py','optimization_map_audit.py','integrate_optimization_map.py']:
 p=R/'scripts'/name
 try:
  exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
  progress.append(dict(script=name,status='success'))
 except Exception:
  progress.append(dict(script=name,status='error',error=traceback.format_exc()));(R/'optimization_authoring_steps.json').write_text(json.dumps(progress,indent=2));raise
 (R/'optimization_authoring_steps.json').write_text(json.dumps(progress,indent=2))
unreal.log('OPTIMIZATION_AUTHORING_COMPLETE')
