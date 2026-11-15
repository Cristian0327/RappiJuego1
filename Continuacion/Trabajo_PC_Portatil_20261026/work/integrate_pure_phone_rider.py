from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['bind_pure_rider_inputs.py','enable_pure_rider_frame.py']:
 unreal.log('PURE_PHONE_RIDER_INTEGRATION '+name)
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})
unreal.log('PURE_PHONE_RIDER_INTEGRATION_PASS')

