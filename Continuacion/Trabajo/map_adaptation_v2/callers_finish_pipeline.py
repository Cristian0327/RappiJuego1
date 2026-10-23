from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['rebuild_clearance_callers.py','build_investigation_probe.py','verify_physical_streets.py','build_overview.py']:
 unreal.log('V2_CALLER_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
