from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['install_compact_station.py','integrate_navigation.py','verify_physical_streets.py','build_traffic_probe.py']:
 unreal.log('V2_FINAL_STAGE_START '+name);exec(compile((P/name).read_text(),name,'exec'),{});unreal.log('V2_FINAL_STAGE_PASS '+name)
unreal.log('V2_FINAL_STAGE_READY')
