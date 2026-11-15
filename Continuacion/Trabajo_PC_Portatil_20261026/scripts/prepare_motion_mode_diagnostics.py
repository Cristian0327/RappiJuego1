from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/build_current_traffic_causes.py';exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p),'probe_only':True})
unreal.log('MOTION_MODE_DIAGNOSTICS_READY')
