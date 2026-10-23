from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['finish_arc_scene.py','fix_curve_clearance.py','fix_service_traffic.py','respace_traffic.py','integrate_navigation.py','install_signals.py','build_traffic_probe.py']:
 unreal.log('V2_PIPELINE_START '+name)
 exec(compile((P/name).read_text(),name,'exec'),{})
 unreal.log('V2_PIPELINE_PASS '+name)
unreal.log('V2_LOGIC_PIPELINE_READY')
